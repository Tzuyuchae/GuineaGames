import pygame
import tkinter as tk 
from tkinter import ttk, messagebox
import random
from datetime import datetime, timedelta
import json



class GuineaPig:

    def __init__(self, name, genes=None, birth_time=None, pig_id=None):
        self.id = pig_id or f"gp{random.randant(1000, 9999)}"
        self.name = name
        self.birth_time = birth_time or datetime.now()
        self.last_bred_time = None

        if genes is None:
            self.genes = self.generate_random_games()
        else:
            self.genes = genes
        self.phenotype = self.calculate_phenotype()
    
    def _generate_random_games(self):
        alleles = {
            'coat_color' : random.choices(['B', 'b'], k=2),
            'coat_length' : random.choices(['S', 's'], k=2),
            'pattern' : random.choices(['P', 'p'], k=2),
            'eye_color' : random.choices(['E', 'e'], k=2),
            'fur_type' : random.choices(['R', 'r'], k=2)
        }

        for trait in alleles:
            alleles[trait].sort(reverse=True)
        return alleles

    def calculate_phenotype(self):
        phenotype = {}
        if 'B' in self.genes['coat_color']:
            phenotype['coat_color'] = 'Brown'
        else:
            phenotype['coat_color'] = 'Black'

        if 'S' in self.genes['coat_length']:
            phenotype['coat_length'] = 'Short'
        else:
            phenotype['coat_length'] = 'Long'

        if 'P' in self.genes['pattern']:
            phenotype['pattern'] = 'Solid'
        else:
            phenotype['pattern'] = 'Spotted'

        if 'E' in self.genes['eye_color']:
            phenotype['eye_color'] = 'Dark'
        else:
            phenotype['eye_color'] = 'Red'

        if 'R' in self.genes['fur_type']:
            phenotype['fur_type'] = 'Smooth'
        else:
            phenotype['fur_type'] = 'Rough'
        
        return phenotype

    def get_age_stage(self):
        age = datetime.now() - self.birth_time
        maturity_time = timedelta(minutes=15)
        return 'adult' if age >= maturity_time else 'baby'

    def can_breed(self):
        if self.get_age_stage() == 'baby':
            return False, "Too young to breed"
        if self.last_bred_time is None:
            return True, ""
        cooldown = timedelta(minutes=30)
        time_since_breed = datetime.now() - self.last_bred_time

        if time_since_breed < cooldown:
            remaining = cooldown - time_since_breed
            mins = int(remaining.total_seconds() / 60)
            secs = int(remaining.total_seconds() % 60) 
            return False, f"Cooldown: {mins}m {secs}s remaining"
        return True, ""

    def get_genotype_string(self):
        return (f"Coat: {''.join(self.genes['coat_color'])} | "
                f"Length: {''.join(self.genes['coat_length'])} | "
                f"Pattern: {''.join(self.genes['pattern'])} | "
                f"Eyes: {''.join(self.genes['eye_color'])} | "
                f"Fur: {''.join(self.genes['fur_type'])}")

    def get_phenotype_string(self):
        return (f"{self.phenotype['coat_color']}, {self.phenotype['coat_length']}, "
                f"{self.phenotype['pattern']}, {self.phenotype['eye_color']} eyes, "
                f"{self.phenotype['fur_type']} fur")
    
class BreedingSystem:
    @staticmethod
    def breed(parent1, parent2):
        num_babies = random.randint(2, 4)
        babies = []
        for i in range(num_babies):
            baby_genes = {}
            
            for trait in parent1.genes:
                allele1 = random.choice(parent1.genes[trait])
                allele2 = random.choice(parent2.genes[trait])
                baby_genes[trait] = sorted([allele1, allele2], reverse=True)
            baby_name = f"{parent1.name[:3]}{parent2.name[:3]}_Baby{i+1}"
            baby = GuineaPig(baby_name, genes = baby_genes, birth_time=datetime.now())
            babies.append(baby)

        parent1.last_bred_time = datetime.now()
        parent2.last_bred_time = datetime.now()
        return babies

class BreedingApp:
    def __init__(self, name, genes=None, birth_time=None, pig_id=None):
        self.id = pig_id or f"gp_{random.randint(1000, 9999)}"
        self.name = name
        self.birth_time = birth_time or datetime.now()
        self.last_bred_time = None

        if genes is None:
            self.genes = self._generate_random_genes()
        else:
            self.genes = genes
        
        self.phenotype = self._calculate_phenotype()
    
    def _generate_random_genes(self):
        alleles = {
            'coat_color': random.choices(['B', 'b'], k=2),
            'coat_length': random.choices(['S', 's'], k=2),
            'pattern': random.choices(['P', 'p'], k=2),
            'eye_color': random.choices(['E', 'e'], k=2),
            'fur_type': random.choices(['R', 'r'], k=2)
        }
        for trait in alleles:
            alleles[trait].sort(reverse=True)
        return alleles

    def _calculate_phenotype(self):
        if 'B' in self.genes['coat_color']:
            phenotype['coat_color'] = 'Brown'
        else:
            phenotype['coat_color'] = 'Black'
        
        if 'S' in self.genes['coat_length']:
            phenotype['coat_length'] = 'Short'
        else:
            phenotype['coat_length'] = 'Long'
        
        if 'P' in self.genes['pattern']:
            phenotype['pattern'] = 'Solid'
        else:
            phenotype['pattern'] = 'Spotted'
        
        if 'E' in self.genes['eye_color']:
            phenotype['eye_color'] = 'Dark'
        else:
            phenotype['eye_color'] = 'Red'
        
        if 'R' in self.genes['fur_type']:
            phenotype['fur_type'] = 'Smooth'
        else:
            phenotype['fur_type'] = 'Rough'
        
        return phenotype
    
    def get_age_stage(self):
        """Determine if guinea pig is baby or adult"""
        age = datetime.now() - self.birth_time
        maturity_time = timedelta(minutes=15)  
        return 'adult' if age >= maturity_time else 'baby'
    
    def can_breed(self):
        """Check if guinea pig can breed (adult + cooldown passed)"""
        if self.get_age_stage() == 'baby':
            return False, "Too young to breed"
        
        if self.last_bred_time is None:
            return True, ""
        
        cooldown = timedelta(minutes=30)  
        time_since_breed = datetime.now() - self.last_bred_time
        
        if time_since_breed < cooldown:
            remaining = cooldown - time_since_breed
            mins = int(remaining.total_seconds() / 60)
            secs = int(remaining.total_seconds() % 60)
            return False, f"Cooldown: {mins}m {secs}s remaining"
        
        return True, ""
    
    def get_genotype_string(self):
        """Return formatted genotype string"""
        return (f"Coat: {''.join(self.genes['coat_color'])} | "
                f"Length: {''.join(self.genes['coat_length'])} | "
                f"Pattern: {''.join(self.genes['pattern'])} | "
                f"Eyes: {''.join(self.genes['eye_color'])} | "
                f"Fur: {''.join(self.genes['fur_type'])}")
    
    def get_phenotype_string(self):
        """Return formatted phenotype string"""
        return (f"{self.phenotype['coat_color']}, {self.phenotype['coat_length']}, "
                f"{self.phenotype['pattern']}, {self.phenotype['eye_color']} eyes, "
                f"{self.phenotype['fur_type']} fur")


class BreedingSystem:
    """Handles breeding logic and genetic inheritance"""
    
    @staticmethod
    def breed(parent1, parent2):
        """Breed two guinea pigs and generate offspring"""
        # Generate 2-4 babies
        num_babies = random.randint(2, 4)
        babies = []
        
        for i in range(num_babies):
            baby_genes = {}
            
            for trait in parent1.genes:
                allele1 = random.choice(parent1.genes[trait])
                allele2 = random.choice(parent2.genes[trait])
                baby_genes[trait] = sorted([allele1, allele2], reverse=True)
            
            # Generate baby name
            baby_name = f"{parent1.name[:3]}{parent2.name[:3]}_Baby{i+1}"
            baby = GuineaPig(baby_name, genes=baby_genes, birth_time=datetime.now())
            babies.append(baby)
        
        # Update parent breeding times
        parent1.last_bred_time = datetime.now()
        parent2.last_bred_time = datetime.now()
        
        return babies


class BreedingApp:
    """Main application GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Guinea Pig Breeding System")
        self.root.geometry("900x700")
        
        self.guinea_pigs = self._create_starter_population()
        self.selected_parent1 = None
        self.selected_parent2 = None
        
        self._create_ui()
        self._update_guinea_pig_lists()
    
    def _create_starter_population(self):
        """Create initial guinea pigs"""
        names = ["Fluffy", "Patches", "Squeaky", "Nibbles", "Cocoa", "Snowball"]
        pigs = []
        for name in names:
            pig = GuineaPig(name)
            if random.random() > 0.3:
                pig.birth_time = datetime.now() - timedelta(minutes=20)
            pigs.append(pig)
        return pigs
    
    def _create_ui(self):
        """Create the user interface"""

        title = tk.Label(self.root, text="🐹 Guinea Pig Breeding Center 🐹", 
                        font=("Arial", 18, "bold"), pady=10)
        title.pack()
        
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left_frame = tk.LabelFrame(main_frame, text="Parent 1", font=("Arial", 12, "bold"))
        left_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        self.parent1_listbox = tk.Listbox(left_frame, height=10, font=("Courier", 9))
        self.parent1_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.parent1_listbox.bind('<<ListboxSelect>>', self._on_parent1_select)
        
        self.parent1_info = tk.Text(left_frame, height=8, width=35, font=("Courier", 8))
        self.parent1_info.pack(fill=tk.BOTH, padx=5, pady=5)
        
        right_frame = tk.LabelFrame(main_frame, text="Parent 2", font=("Arial", 12, "bold"))
        right_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        self.parent2_listbox = tk.Listbox(right_frame, height=10, font=("Courier", 9))
        self.parent2_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.parent2_listbox.bind('<<ListboxSelect>>', self._on_parent2_select)
        
        self.parent2_info = tk.Text(right_frame, height=8, width=35, font=("Courier", 8))
        self.parent2_info.pack(fill=tk.BOTH, padx=5, pady=5)
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        breed_btn = tk.Button(self.root, text="🧬 BREED SELECTED PARENTS 🧬", 
                            command=self._breed_selected, font=("Arial", 14, "bold"),
                            bg="#4CAF50", fg="white", pady=10)
        breed_btn.pack(pady=10)
        
        offspring_frame = tk.LabelFrame(self.root, text="Offspring", font=("Arial", 12, "bold"))
        offspring_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.offspring_text = tk.Text(offspring_frame, height=10, font=("Courier", 9))
        self.offspring_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        refresh_btn = tk.Button(self.root, text="🔄 Refresh Status", 
                               command=self._update_guinea_pig_lists)
        refresh_btn.pack(pady=5)
    
    def _update_guinea_pig_lists(self):
        """Update the listboxes with current guinea pig status"""

        self.parent1_listbox.delete(0, tk.END)
        self.parent2_listbox.delete(0, tk.END)
        
        for pig in self.guinea_pigs:
            age = pig.get_age_stage()
            can_breed, reason = pig.can_breed()
            status = "✓" if can_breed else "✗"
            
            display_text = f"{status} {pig.name} ({age})"
            if not can_breed and reason:
                display_text += f" - {reason}"
            
            self.parent1_listbox.insert(tk.END, display_text)
            self.parent2_listbox.insert(tk.END, display_text)
    
    def _on_parent1_select(self, event):
        """Handle parent 1 selection"""
        selection = self.parent1_listbox.curselection()
        if selection:
            idx = selection[0]
            self.selected_parent1 = self.guinea_pigs[idx]
            self._display_pig_info(self.selected_parent1, self.parent1_info)
    
    def _on_parent2_select(self, event):
        """Handle parent 2 selection"""
        selection = self.parent2_listbox.curselection()
        if selection:
            idx = selection[0]
            self.selected_parent2 = self.guinea_pigs[idx]
            self._display_pig_info(self.selected_parent2, self.parent2_info)
    
    def _display_pig_info(self, pig, text_widget):
        """Display detailed pig information"""
        text_widget.delete(1.0, tk.END)
        
        info = f"Name: {pig.name}\n"
        info += f"ID: {pig.id}\n"
        info += f"Age: {pig.get_age_stage()}\n"
        info += f"\nPhenotype:\n{pig.get_phenotype_string()}\n"
        info += f"\nGenotype:\n{pig.get_genotype_string()}\n"
        
        can_breed, reason = pig.can_breed()
        info += f"\nBreeding Status: {'Ready' if can_breed else reason}"
        
        text_widget.insert(1.0, info)
    
    def _breed_selected(self):
        """Breed the selected parents"""
        if not self.selected_parent1 or not self.selected_parent2:
            messagebox.showwarning("Selection Error", "Please select both parents!")
            return
        
        if self.selected_parent1.id == self.selected_parent2.id:
            messagebox.showwarning("Selection Error", "Cannot breed a guinea pig with itself!")
            return
        
        can_breed1, reason1 = self.selected_parent1.can_breed()
        can_breed2, reason2 = self.selected_parent2.can_breed()
        
        if not can_breed1:
            messagebox.showwarning("Breeding Error", f"Parent 1: {reason1}")
            return
        
        if not can_breed2:
            messagebox.showwarning("Breeding Error", f"Parent 2: {reason2}")
            return
        
        babies = BreedingSystem.breed(self.selected_parent1, self.selected_parent2)
        
        self.guinea_pigs.extend(babies)
        
        self._display_offspring(babies)
        
        self._update_guinea_pig_lists()
        
        messagebox.showinfo("Success!", f" {len(babies)} baby guinea pigs were born! ")
    
    def _display_offspring(self, babies):
        """Display information about newborn guinea pigs"""
        self.offspring_text.delete(1.0, tk.END)
        
        output = f"=== {len(babies)} NEW BABIES BORN ===\n"
        
        for i, baby in enumerate(babies, 1):
            output += f"Baby #{i}: {baby.name}\n"
            output += f"  Appearance: {baby.get_phenotype_string()}\n"
            output += f"  Genetics: {baby.get_genotype_string()}\n"
            output += f"  Will mature in: 15 minutes\n\n"
        
        self.offspring_text.insert(1.0, output)


def main():
    root = tk.Tk()
    app = BreedingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
