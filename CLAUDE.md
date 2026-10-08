# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Tetris in Python: NumPy for game logic, Matplotlib for rendering and keyboard input. All game code lives in `tetris.py`. `main.py` is the unused `uv init` stub; `agent_player.py` is currently an empty placeholder.

## Commands

```bash
uv sync            # install dependencies
uv run tetris.py   # run the game (opens a Matplotlib window)
```

There is no test suite, linter, or build step configured. `testGame()` and `testRotation()` in `tetris.py` are visual smoke tests that drive a `Board` through scripted actions; they aren't wired to anything, so call them manually (e.g. temporarily from `__main__`) with a `Board()` instance.

## Architecture

### Layering

- **`Board` / `Block` / `Position`** are pure game state with no Matplotlib dependency. `Board` can be driven headlessly via `perform()`, `freeze()`, `new_block()`, and `state()`; `freeze()` returns the reward for the placed piece (−1000 on game over), which makes it usable by non-GUI players.
- **`plot_board()`** is pure rendering (board, grid, score/level, next-piece preview via `render_next_block_preview()`, game-over overlay). It calls `plt.pause()`, which pumps the GUI event loop.
- **`play_board()`** sits between them: it handles hard drop (animated step-by-step, then `freeze()` + `new_block()`), reset, and otherwise delegates to `board.perform()`, then re-renders. Because it always calls `plot_board()`, it is not headless.

### Game loop and input

- `FuncAnimation` fires `auto_drop()` every `RENDER_INTERVAL` seconds; it drains `action_queue` then performs one `'v'` step.
- `on_key_press()` only *enqueues* actions. This is deliberate: `plt.pause()` inside rendering processes events, so executing actions directly in the key handler would re-enter game logic mid-update.
- A `'v'` when the block is already at `drop_pos` is treated as a landing (freeze + next block) in `play_board()`.

### Action encoding

| Action | Meaning | Handled in |
|---|---|---|
| `<` `>` | move left/right | `Board.perform` |
| `@` | rotate clockwise | `Board.perform` |
| `v` | step down one row (lands if already at bottom) | `Board.perform` / `play_board` |
| `V` | hard drop | `play_board` only |
| `.` | reset | `play_board` only |
| any other string | `new_block(action)` — a shape letter spawns that shape, anything else (e.g. `''`, `'+'`) spawns `next_shape` | `Board.perform` default case |

Note the fallthrough: passing `V` or `.` straight to `Board.perform()` spawns a new block instead of dropping/resetting.

### Key details

- Coordinates are `(y, x)` — row, column. `Block.pos` is the top-left corner of the block's bounding box.
- Only 5 shapes (I, J, L, O, T — no S/Z). Cell values equal the shape's `COLORS` index (1–5), and `plot_board` uses a 6-entry colormap with `vmin=0, vmax=5`; adding a shape requires updating `SHAPES`, `BLOCKS`, `ROTATION_ADJUST`, `COLORS`, the colormap, and the number-key handler.
- Rotation is `np.rot90(cells, -1)` plus a per-shape, per-rotation offset from `ROTATION_ADJUST` (cycled by `rotation_count`), then clamped to the board. There are no wall kicks; a rotation that conflicts is simply rejected.
- Collision (`conflict()`): bounds check, then element-wise product of the board slice and block cells — any non-zero product is an overlap.
- `drop_pos` is cached in `_drop_pos`; any code that changes the block's x position, rotation, or the board must reset `_drop_pos = None`.
- Game over is detected at spawn: if the new block's spawn position already equals its `drop_pos`.
- Scoring: `n` cleared rows give `n * (10 + n - 1)`; +100 if the board is empty afterward. Level is `block_count // 50 + 1` and is display-only (does not change drop speed).
- `Position.__sub__` has a bug (`self.x - pos.y`); it's currently unused.
