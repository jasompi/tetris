# Tetris

A classic Tetris game implementation in Python using NumPy and Matplotlib.

## Features

- Classic Tetris gameplay with standard piece shapes (I, J, L, O, T)
- Real-time visualization using Matplotlib
- Keyboard controls for movement and rotation
- Score and level tracking
- Line clearing with bonus rewards
- Auto-drop mechanic with adjustable speed

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
# Clone the repository
git clone <your-repo-url>
cd tetris

# Install dependencies with uv
uv sync

# Or install manually with pip
pip install numpy>=2.3.5 matplotlib>=3.8.0
```

## Running the Game

```bash
# Using uv
uv run tetris.py

# Or with Python directly
python tetris.py
```

## Controls

| Key | Action |
|-----|--------|
| ← → | Move piece left/right |
| ↑ | Rotate piece clockwise |
| ↓ | Hard drop (instant drop to bottom) |
| Space | Soft drop (move down one step) |
| Enter | Restart game (when game over) |
| Esc | Exit game |
| 0-5 | Spawn specific piece (0=random, 1-5=I/J/L/O/T) |

## Scoring

- Clear 1 line: 10 points
- Clear 2 lines: 20 + 1 = 21 points
- Clear 3 lines: 30 + 2 = 32 points
- Clear 4 lines: 40 + 3 = 43 points
- Clear entire board: +100 bonus points

## Requirements

- Python >= 3.12
- numpy >= 2.3.5
- matplotlib >= 3.8.0

## License

MIT License - see [LICENSE](LICENSE) file for details.
