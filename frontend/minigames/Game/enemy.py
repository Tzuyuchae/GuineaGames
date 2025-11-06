### FIX ME ###
    # We need to implement an enemy that chases the player around the maze
    # and causes the player to lose if they come into contact with it.

class Enemy:
    def __init__(self, pos_x, pos_y):
        self.position = [pos_x, pos_y]
    
    def move_towards_player(self, player_pos, maze):
        """Move the enemy one step towards the player if possible."""
        # Simple logic to move towards the player
        if self.position[0] < player_pos[0] and maze.is_wall(self.position[0] + 1, self.position[1]) == False:
            self.position[0] += 1
        elif self.position[0] > player_pos[0] and maze.is_wall(self.position[0] - 1, self.position[1]) == False:
            self.position[0] -= 1
        elif self.position[1] < player_pos[1] and maze.is_wall(self.position[0], self.position[1] + 1) == False:
            self.position[1] += 1
        elif self.position[1] > player_pos[1] and maze.is_wall(self.position[0], self.position[1] - 1) == False:
            self.position[1] -= 1
    
    def get_position(self):
        return self.position
    
    