# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Tetris game implementation in Python using NumPy for game logic and Matplotlib for visualization and user input.

## Running the Game

```bash
# Using Python directly
python tetris.py

# Or using uv
uv run tetris.py
```

## Controls

- Arrow keys: Left/Right to move, Up to rotate, Down to hard drop
- Space: Soft drop (one step down)
- Enter: Reset game (when game over)
- Escape: Exit
- Number keys 0-5: Spawn specific blocks (0 = random, 1-5 = I/J/L/O/T shapes)

## Architecture

### Core Components

**Block** (`tetris.py:59-93`)
- Represents a single Tetris piece with shape, position, and rotation state
- Uses numpy arrays for cell representation colored by `COLORS` dict
- Position is tracked via top-left corner (y, x coordinates)
- `ROTATION_ADJUST` dict handles position correction after rotation to keep blocks on-board

**Board** (`tetris.py:94-191`)
- Manages the 10x20 game grid using a numpy array
- Handles collision detection via `conflict()` method
- Line clearing with reward calculation: `len(clear_row) * (10 + len(clear_row) - 1)`
- Special +100 reward when entire board is cleared
- `drop_pos` property calculates where current block would land (cached for performance)

**Game Loop** (`tetris.py:334-360`)
- Uses `matplotlib.animation.FuncAnimation` for auto-drop timing
- Action queue (`action_queue`) prevents re-entrancy issues from `plt.pause()` event processing
- Keyboard events are queued in `on_key_press()` and processed in `auto_drop()` callback

### Key Design Patterns

1. **Coordinate System**: Position uses (y, x) not (x, y) - y is row, x is column
2. **Conflict Detection**: Board cells and block cells are multiplied to detect overlap (both must be non-zero)
3. **Render Separation**: `plot_board()` is pure rendering, `play_board()` handles game state updates
4. **Action Encoding**: String-based actions ('<', '>', '@', 'v', 'V') for movement/rotation

### Testing Functions

- `testGame()`: Runs a hardcoded sequence of moves
- `testRotation()`: Tests all piece rotations through 8 cycles

## Dependencies

- Python >= 3.12
- numpy >= 2.3.5
- matplotlib >= 3.8.0

Package management uses `uv` with `pyproject.toml` and `uv.lock`.
