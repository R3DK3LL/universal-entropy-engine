#!/usr/bin/env python3
"""
ASCII Art Generator - Simple Interface
Creates mathematically unique ASCII art patterns.
"""

from engine import AsciiArtGenerator


def single_generation():
    """Generate and display one ASCII art piece"""
    generator = AsciiArtGenerator()
    generator.display()


def multiple_generations(count=3):
    """Generate multiple unique pieces"""
    generator = AsciiArtGenerator()

    print("Generating multiple unique ASCII art pieces...\n")

    for i in range(count):
        print(f"\nGeneration {i+1}:")
        print("-" * 50)
        result = generator.create()
        print(result["art"])
        print(f"Steps: {result['steps']} | Position: {result['sequence_position']}")

        if i < count - 1:
            input("\nPress Enter for next generation...")


def save_collection():
    """Generate and save multiple pieces to files"""
    generator = AsciiArtGenerator()

    files = []
    for i in range(3):
        filename = generator.save_to_file()
        files.append(filename)
        print(f"Generated {filename}")

    print(f"\nCreated {len(files)} unique ASCII art files.")
    return files


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "demo":
            single_generation()
        elif command == "multi":
            multiple_generations(5)
        elif command == "save":
            save_collection()
        else:
            print("Usage: python ascii_art.py [demo|multi|save]")
    else:
        # Default behavior
        single_generation()
