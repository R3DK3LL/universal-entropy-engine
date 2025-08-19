# Non-Repeating ASCII Art Generator

**Mathematical art that never repeats - guaranteed.**

Every execution creates ASCII art patterns that are mathematically unique and will never occur again.

## Quick Start

```bash
python ascii_art.py
```

## Examples

```
    ░▒▓█◆●♦★░▒▓█◆●♦★░▒▓█◆●♦★░▒▓█◆●♦★░▒▓█◆●♦★░▒▓█◆●♦★░▒▓█◆●♦★░▒▓█
    ▒▓█◆●♦★░▒▓█◆●♦★░▒▓█◆●♦★░▒▓█◆●♦★░▒▓█◆●♦★░▒▓█◆●♦★░▒▓█◆●♦★░▒▓█◆
    █◆●♦★░▒▓█◆●♦★░▒▓█◆●♦★░▒▓█◆●♦★░▒▓█◆●♦★░▒▓█◆●♦★░▒▓█◆●♦★░▒▓█◆●
    ◆●♦★░▒▓█◆●♦★░▒▓█◆●♦★░▒▓█◆●♦★░▒▓█◆●♦★░▒▓█◆●♦★░▒▓█◆●♦★░▒▓█◆●♦
```

*Each pattern is completely unique and will never repeat.*

## Usage Options

### Basic Generation
```bash
python ascii_art.py
```

### Multiple Patterns
```bash
python ascii_art.py multi
```

### Save to Files
```bash
python ascii_art.py save
```

### Interactive Mode
```bash
python engine.py
```

## How It Works

This generator uses advanced mathematical computation combined with cellular automaton evolution to create patterns that are:

- **Mathematically unique** - Based on infinite non-repeating mathematical sequences
- **Computationally generated** - Uses cellular automaton evolution rules
- **Visually diverse** - Multiple character sets and pattern densities
- **Guaranteed non-repeating** - Mathematical impossibility of duplication

## Technical Details

The system combines:
- High-precision mathematical constant computation
- Cellular automaton pattern evolution
- Mathematical perturbation to prevent pattern stagnation
- Time-based seeding for additional uniqueness

## Requirements

- Python 3.6+
- NumPy

```bash
pip install numpy
```

## File Structure

```
non-repeating-ascii-art/
├── engine.py          # Core generation engine
├── ascii_art.py       # Simple command-line interface
└── README.md          # This file
```

## Why Non-Repeating?

The mathematical foundation ensures that each generated pattern is unique:

1. **Infinite mathematical sequences** provide non-repeating source data
2. **Time-based positioning** ensures different starting points
3. **Cellular automaton evolution** creates complex emergent patterns
4. **Mathematical perturbation** prevents pattern convergence

The combination of these factors makes pattern repetition mathematically impossible.

## Contributing

Feel free to submit issues or pull requests. Some areas for enhancement:

- Additional character sets for different visual styles
- Color output support for terminal environments
- Pattern analysis and classification
- Export to different image formats

## License

MIT License - Feel free to use and modify for your projects.

---

*Generate infinite unique art with mathematical precision.*
