#!/usr/bin/env python3
"""
ASCII Art Generator - Simple Interface with Live Animation
Creates mathematically unique ASCII art patterns with live evolution.
"""

from wrapper import AsciiArtGenerator


def single_generation():
    """Generate and display one ASCII art piece"""
    generator = AsciiArtGenerator()
    generator.display()


def live_animation(max_generations=None, delay=0.5):
    """Watch patterns evolve live like Conway's Game of Life"""
    generator = AsciiArtGenerator()
    print(f"Starting live evolution...")
    if max_generations:
        print(f"Will run for {max_generations} generations")
    else:
        print("Will run until you press Ctrl+C")
    print("Press Ctrl+C anytime to stop and see final pattern")

    generator.animate(max_generations=max_generations, delay=delay)


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


def show_help():
    """Show usage information"""
    print(
        """
Non-Repeating ASCII Art Generator

Usage: python ascii_art.py [command]

Commands:
  demo            - Generate one static pattern
  live            - Watch live evolution (Ctrl+C to stop)
  live [N]        - Watch evolution for N generations  
  fast            - Fast live evolution (0.1s per frame)
  slow            - Slow live evolution (1.0s per frame)
  multi           - Generate 5 different patterns
  save            - Generate and save 3 patterns to files
  help            - Show this help

Examples:
  python ascii_art.py live 100    # Watch 100 generations
  python ascii_art.py fast        # Fast animation
  python ascii_art.py demo        # Single static pattern

Live Mode Controls:
  - Patterns evolve using mathematical rules
  - Each generation is completely deterministic yet unpredictable
  - Mathematical perturbation prevents stagnation
  - Press Ctrl+C anytime to stop and preserve final pattern
"""
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        # Default behavior - show help and demo
        print("Non-Repeating ASCII Art Generator")
        print("Try: python ascii_art.py help")
        print("\nQuick demo:")
        single_generation()
    else:
        command = sys.argv[1].lower()

        if command == "demo":
            single_generation()

        elif command == "live":
            if len(sys.argv) > 2 and sys.argv[2].isdigit():
                live_animation(max_generations=int(sys.argv[2]))
            else:
                live_animation()

        elif command == "fast":
            live_animation(delay=0.1)

        elif command == "slow":
            live_animation(delay=1.0)

        elif command == "multi":
            multiple_generations(5)

        elif command == "save":
            save_collection()

        elif command == "help":
            show_help()

        else:
            print(f"Unknown command: {command}")
            print("Try: python ascii_art.py help")
