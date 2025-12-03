import pygame
import random
import os
from minigame.settings import TILE_SIZE, RED


class Player:
    def __init__(self, x=0, y=0, color=RED, seed=None, guinea_pig_data=None):
        self.pos_x = x
        self.pos_y = y
        self.seed = seed
        self.guinea_pig_data = guinea_pig_data

        # --- NAME ---
        if isinstance(guinea_pig_data, dict):
            self.name = guinea_pig_data.get("name", "Player")
        else:
            self.name = getattr(guinea_pig_data, "name", "Player")

        # --- STATS: SPEED & ENDURANCE ---
        # Handle both dict-style and object-style pigs
        if isinstance(guinea_pig_data, dict):
            raw_speed = guinea_pig_data.get("speed", 50)
            raw_endurance = guinea_pig_data.get("endurance", 50)
        else:
            raw_speed = getattr(guinea_pig_data, "speed", 50)
            raw_endurance = getattr(guinea_pig_data, "endurance", 50)

        # Clamp to a sane range
        raw_speed = max(20, min(100, raw_speed))
        raw_endurance = max(20, min(100, raw_endurance))

        # Debug: see stats for each run
        print(
            f"[Minigame Player] Using stats for '{self.name}': "
            f"speed={raw_speed}, endurance={raw_endurance}"
        )

        # --- MOVEMENT PHYSICS (same endurance model as now) ---

        # Speed → base & min delays (higher speed = smaller delay = faster)
        speed_norm = (raw_speed - 40) / (90 - 40)  # approx 0..1
        speed_norm = max(0.0, min(1.0, speed_norm))

        base_slow = 320
        base_fast = 160
        self.BASE_DELAY = int(base_slow - (base_slow - base_fast) * speed_norm)

        min_slow = 220
        min_fast = 100
        self.MIN_DELAY = int(min_slow - (min_slow - min_fast) * speed_norm)

        # Endurance: how long we can stay at MIN_DELAY before fatigue
        # Map endurance 40–90 -> about 2s–6s at full speed
        end_norm = (raw_endurance - 40) / (90 - 40)
        end_norm = max(0.0, min(1.0, end_norm))
        self.ENDURANCE_LIMIT = int(2000 + 4000 * end_norm)  # ms at top speed

        # Fatigue penalty: much slower when tired
        self.FATIGUE_DELAY = self.BASE_DELAY + 200

        # Momentum / fatigue state
        self.current_delay = self.BASE_DELAY
        self.last_move_time = 0
        self.momentum_start_time = 0
        self.at_top_speed_since = 0
        self.is_moving = False
        self.is_fatigued = False

        # 🔸 NEW: endurance recovery cooldown
        self.recovery_start_time = 0
        self.RECOVERY_COOLDOWN = 2000  # ms to fully recover endurance after resting

        # --- COLOR ---
        coat_color_name = None
        if isinstance(guinea_pig_data, dict):
            coat_color_name = guinea_pig_data.get("color") or guinea_pig_data.get(
                "coat_color"
            )
        else:
            phenotype = getattr(guinea_pig_data, "phenotype", None)
            if phenotype and isinstance(phenotype, dict):
                coat_color_name = phenotype.get("coat_color")
            else:
                coat_color_name = getattr(guinea_pig_data, "color", None)

        if coat_color_name:
            self.color = self._get_color_from_name(coat_color_name)
        else:
            self.color = color

        # --- ROBUST IMAGE LOADING ---
        base_path = os.path.dirname(os.path.abspath(__file__))

        paths_to_check = [
            os.path.join(base_path, "../images/player.png"),
            os.path.join(base_path, "../../images/player.png"),
            os.path.join(base_path, "assets/images/player.png"),
        ]

        self.image = None
        for p in paths_to_check:
            if os.path.exists(p):
                try:
                    raw_image = pygame.image.load(p).convert_alpha()
                    self.image = pygame.transform.scale(raw_image, (TILE_SIZE, TILE_SIZE))
                    print(f"Player: Loaded sprite from {p}")
                    break
                except Exception as e:
                    print(f"Player: Error loading {p}: {e}")

        if self.image is None:
            print("Player: Could not find sprite. Using Fallback.")
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill((255, 0, 255))  # Magenta for visibility
            pygame.draw.rect(self.image, self.color, (4, 4, TILE_SIZE - 8, TILE_SIZE - 8))

        self.rect = self.image.get_rect()

    def _get_color_from_name(self, color_name):
        color_map = {
            "brown": (139, 69, 19),
            "white": (255, 255, 255),
            "orange": (255, 165, 0),
            "black": (50, 50, 50),
            "gray": (128, 128, 128),
            "gold": (255, 215, 0),
            "red": RED,
        }
        return color_map.get(str(color_name).lower(), RED)

    def handle_input(self, maze):
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()

        dx, dy = 0, 0
        wants_to_move = False

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
            wants_to_move = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
            wants_to_move = True
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
            wants_to_move = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
            wants_to_move = True

        if wants_to_move:
            # Starting a new movement press?
            if not self.is_moving:
                self.is_moving = True
                self.momentum_start_time = now

                # 🔹 If we're fatigued, check if we finished the cooldown
                if self.is_fatigued:
                    if now - self.recovery_start_time >= self.RECOVERY_COOLDOWN:
                        # Fully recovered after resting long enough
                        self.is_fatigued = False
                        self.current_delay = self.BASE_DELAY
                        self.at_top_speed_since = 0
                    else:
                        # Still recovering → move, but at fatigued speed
                        self.current_delay = self.FATIGUE_DELAY
                else:
                    # Not fatigued → start from base speed
                    self.current_delay = self.BASE_DELAY
                    self.at_top_speed_since = 0

            time_moving = now - self.momentum_start_time

            if not self.is_fatigued:
                # Accelerate from BASE_DELAY down to MIN_DELAY over time
                max_bonus = self.BASE_DELAY - self.MIN_DELAY  # positive ms
                acceleration_bonus = min(
                    max_bonus, int(time_moving / 200) * 30
                )  # every 200ms, 30ms bonus

                target_delay = self.BASE_DELAY - acceleration_bonus
                self.current_delay = max(self.MIN_DELAY, target_delay)

                # Once at top speed, track how long we've been there (for endurance)
                if self.current_delay <= self.MIN_DELAY:
                    if self.at_top_speed_since == 0:
                        self.at_top_speed_since = now
                    if (now - self.at_top_speed_since) > self.ENDURANCE_LIMIT:
                        # Hit endurance wall → fatigue kicks in
                        self.is_fatigued = True
                        self.current_delay = self.FATIGUE_DELAY
            else:
                # Fatigued movement: always slow until cooldown completes
                self.current_delay = self.FATIGUE_DELAY

            # Apply movement if enough time passed
            if now - self.last_move_time >= self.current_delay:
                move_success = self.move(dx, dy, maze)
                self.last_move_time = now
                if not move_success:
                    self.reset_momentum(now)
        else:
            # Key released → start resting; endurance cooldown begins
            if self.is_moving:
                self.reset_momentum(now)

    def reset_momentum(self, now):
        """
        Stop current movement.
        Endurance does NOT reset instantly anymore.
        Instead, we start a cooldown timer; after RECOVERY_COOLDOWN ms of rest,
        endurance/fatigue will fully reset when the player moves again.
        """
        self.is_moving = False
        self.current_delay = self.BASE_DELAY
        self.at_top_speed_since = 0

        # If we were fatigued, we stay fatigued here; recovery is time-based.
        # If we weren't fatigued, this is just a normal stop.
        self.recovery_start_time = now

    def move(self, dx, dy, maze):
        new_x = self.pos_x + dx
        new_y = self.pos_y + dy

        if not maze.is_wall(new_x, new_y):
            self.pos_x = new_x
            self.pos_y = new_y
            return True
        return False

    def add_player(self, grid):
        if self.seed is not None:
            random.seed(self.seed)

        spawn_points = []
        for y, row in enumerate(grid):
            for x, tile in enumerate(row):
                if tile == "0":
                    spawn_points.append((x, y))

        new_grid = [list(row) for row in grid]

        if spawn_points:
            player_x, player_y = random.choice(spawn_points)
            new_grid[player_y][player_x] = "P"
            self.pos_x = player_x
            self.pos_y = player_y

        return ["".join(row) for row in new_grid]

    def player_pos(self):
        return (self.pos_x, self.pos_y)

    def draw(self, screen, offset_x=0, offset_y=0):
        """Draw player with centering offset."""
        pixel_x = self.pos_x * TILE_SIZE + offset_x
        pixel_y = self.pos_y * TILE_SIZE + offset_y
        self.rect.topleft = (pixel_x, pixel_y)

        if self.is_fatigued:
            tinted_img = self.image.copy()
            tinted_img.fill((100, 0, 0, 100), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(tinted_img, self.rect)
        else:
            screen.blit(self.image, self.rect)