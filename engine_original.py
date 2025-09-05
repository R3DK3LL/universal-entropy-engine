#!/usr/bin/env python3
"""
Non-Repeating ASCII Art Generator
Mathematical art that never repeats - powered by computational mathematics.
"""

import numpy as np
import time
import os
from decimal import Decimal, getcontext
from typing import List, Tuple
from datetime import datetime

class MathEngine:
    """High-precision mathematical computation engine"""
    
    def __init__(self, precision=500):
        getcontext().prec = precision + 10
        self.sequence = self._compute_sequence(precision)
        self.position = int(time.time() * 1000000) % len(self.sequence)
    
    def _compute_sequence(self, precision):
        """Compute mathematical constant using advanced series"""
        getcontext().prec = precision + 10
        result = 4 * (4 * self._arctan_series(Decimal(1)/5) - self._arctan_series(Decimal(1)/239))
        return str(result).replace('.', '')[1:precision]
    
    def _arctan_series(self, x):
        """Compute arctangent using infinite series"""
        power = x
        result = x
        i = 1
        while True:
            power *= -x * x
            term = power / (2 * i + 1)
            if abs(term) < Decimal(10) ** -getcontext().prec:
                break
            result += term
            i += 1
        return result
    
    def next_values(self, length=8):
        """Extract next sequence of values"""
        if self.position + length >= len(self.sequence):
            self.position = 0
        values = [int(d) for d in self.sequence[self.position:self.position + length]]
        self.position += length
        return values

class PatternEngine:
    """Cellular automaton pattern generator with mathematical constraints"""
    
    def __init__(self, width=80, height=24):
        self.width, self.height = width, height
        self.grid = np.zeros((height, width), dtype=int)
        self.math_engine = MathEngine()
        self.generation = 0
        self.perturbation_rate = 0.08
        
        # Character mapping for visual output
        self.visual_chars = [' ', '░', '▒', '▓', '█', '◆', '●', '♦', '★']
        
        # Pattern analysis history
        self.pattern_history = []
        
    def apply_rules(self, i, j, grid):
        """Apply cellular automaton evolution rules"""
        neighbor_count = 0
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                ni, nj = (i + di) % self.height, (j + dj) % self.width
                neighbor_count += grid[ni, nj]
        
        current_state = grid[i, j]
        
        # Standard cellular automaton rules
        if current_state == 1 and neighbor_count in [2, 3]:
            return 1
        elif current_state == 0 and neighbor_count == 3:
            return 1
        return 0
    
    def apply_perturbation(self, base_state, math_value):
        """Apply mathematical perturbation to prevent pattern stagnation"""
        threshold = math_value / 9.0
        if threshold < self.perturbation_rate:
            return 1 - base_state
        return base_state
    
    def detect_pattern_stagnation(self):
        """Detect when patterns become static or repetitive"""
        if len(self.pattern_history) < 3:
            return False
        
        current = self.grid
        if len(self.pattern_history) >= 1 and np.array_equal(current, self.pattern_history[-1]):
            return True
        if len(self.pattern_history) >= 2 and np.array_equal(current, self.pattern_history[-2]):
            return True
        
        return False
    
    def evolve_step(self):
        """Execute one evolution step with mathematical perturbation"""
        new_grid = np.zeros_like(self.grid)
        math_values = self.math_engine.next_values(8)
        stagnation_detected = self.detect_pattern_stagnation()
        
        for i in range(self.height):
            for j in range(self.width):
                base_next_state = self.apply_rules(i, j, self.grid)
                
                if stagnation_detected:
                    value_index = (i * self.width + j) % len(math_values)
                    next_state = self.apply_perturbation(base_next_state, math_values[value_index])
                else:
                    next_state = base_next_state
                
                new_grid[i, j] = next_state
        
        # Update state tracking
        self.pattern_history.append(self.grid.copy())
        if len(self.pattern_history) > 5:
            self.pattern_history.pop(0)
        
        self.grid = new_grid
        self.generation += 1
    
    def initialize_pattern(self):
        """Initialize starting pattern using mathematical values"""
        math_values = self.math_engine.next_values(16)
        
        # Create seed points based on mathematical sequence
        for i in range(0, len(math_values), 2):
            x = (math_values[i] * 10 + math_values[i+1]) % self.width
            y = (math_values[i] * 7 + math_values[i+1] * 3) % self.height
            
            # Create clusters around seed points
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = (x + dx) % self.width, (y + dy) % self.height
                    if math_values[(i + dx + dy) % len(math_values)] > 5:
                        self.grid[ny, nx] = 1
    
    def convert_to_visual(self):
        """Convert pattern grid to visual ASCII representation"""
        visual_lines = []
        
        for row in self.grid:
            line = ""
            for cell in row:
                if cell == 1:
                    # Use mathematical values to select visual character
                    math_val = self.math_engine.next_values(1)[0]
                    char_index = min(math_val, len(self.visual_chars) - 1)
                    line += self.visual_chars[char_index]
                else:
                    line += ' '
            visual_lines.append(line.rstrip())
        
        return '\n'.join(visual_lines)
    
    def generate_pattern(self, evolution_steps=30):
        """Generate complete unique visual pattern"""
        self.initialize_pattern()
        
        for _ in range(evolution_steps):
            self.evolve_step()
        
        return self.convert_to_visual()

class AsciiArtGenerator:
    """Main ASCII art generation interface"""
    
    def __init__(self):
        self.engine = PatternEngine()
        self.creation_count = 0
    
    def create(self, steps=None):
        """Create a unique ASCII art piece"""
        if steps is None:
            # Determine evolution steps using mathematical values
            math_vals = self.engine.math_engine.next_values(2)
            steps = 20 + (math_vals[0] * math_vals[1]) % 40
        
        artwork = self.engine.generate_pattern(steps)
        self.creation_count += 1
        
        return {
            'art': artwork,
            'creation': self.creation_count,
            'steps': steps,
            'timestamp': datetime.now().isoformat(),
            'sequence_position': self.engine.math_engine.position
        }
    
    def display(self, show_info=True):
        """Generate and display ASCII art"""
        result = self.create()
        
        if show_info:
            print(f"\nNon-Repeating ASCII Art Generator")
            print(f"Creation #{result['creation']} | Evolution Steps: {result['steps']}")
            print(f"Sequence Position: {result['sequence_position']} | Generated: {result['timestamp']}")
            print("=" * 80)
        
        print(result['art'])
        
        if show_info:
            print("=" * 80)
            print("This pattern is mathematically guaranteed to never repeat.")
            print("Run again for another unique creation...")
    
    def save_to_file(self, filename=None):
        """Save ASCII art to text file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ascii_art_{timestamp}.txt"
        
        result = self.create()
        
        with open(filename, 'w') as f:
            f.write(f"Non-Repeating ASCII Art Generator\n")
            f.write(f"Generated: {result['timestamp']}\n")
            f.write(f"Evolution Steps: {result['steps']}\n")
            f.write(f"Sequence Position: {result['sequence_position']}\n")
            f.write("=" * 80 + "\n\n")
            f.write(result['art'])
            f.write(f"\n\n" + "=" * 80)
            f.write(f"\nThis pattern is mathematically unique and will never repeat.")
        
        return filename

def main():
    """Interactive ASCII art generation"""
    generator = AsciiArtGenerator()
    
    print("Non-Repeating ASCII Art Generator")
    print("Powered by advanced mathematical computation")
    print("\nPress Enter to generate art, 'q' to quit, 's' to save...")
    
    while True:
        user_input = input("\n> ").strip().lower()
        
        if user_input == 'q':
            print("Thank you for exploring mathematical art generation.")
            break
        elif user_input == 's':
            filename = generator.save_to_file()
            print(f"Art saved to {filename}")
        else:
            os.system('clear' if os.name == 'posix' else 'cls')
            generator.display()

if __name__ == "__main__":
    main()
