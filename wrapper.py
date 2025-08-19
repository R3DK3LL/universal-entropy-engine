#!/usr/bin/env python3
import sys
import os

# Add path to private repo so we can import from it
sys.path.append('../non-repeating-ascii-art-blackbox/')

# Import everything from private repo
from engine import AsciiArtGenerator as PrivateGenerator

class AsciiArtGenerator:
    """Public wrapper that delegates to private engine"""
    
    def __init__(self):
        self._private_gen = PrivateGenerator()
    
    def create(self, steps=None):
        """Create static art"""
        return self._private_gen.create(steps)
    
    def display(self, show_info=True):
        """Display static art"""
        return self._private_gen.display(show_info)
    
    def save_to_file(self, filename=None):
        """Save art to file"""
        return self._private_gen.save_to_file(filename)
    
    def animate(self, max_generations=None, delay=0.5):
        """Live animation mode"""
        return self._private_gen.animate(max_generations, delay)
