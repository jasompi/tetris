from typing import Dict, Optional, List, NamedTuple
from collections import deque
import copy
import numpy as np
import random
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle

BOARD_WIDTH = 10
BOARD_HEIGHT = 20

RENDER_INTERVAL = 0.5


class Position(NamedTuple):
    y: int
    x: int
    def left(self) -> 'Position':
        return Position(self.y, self.x-1)
    def right(self) -> 'Position':
        return Position(self.y, self.x+1)
    def down(self) -> 'Position':
        return Position(self.y+1, self.x)
    def __add__(self, pos):
        return Position(self.y + pos.y, self.x + pos.x)
    def __sub__(self, pos):
        return Position(self.y - pos.y, self.x - pos.y)
    def __eq__(self, pos):
        return self.y == pos.y and self.x == pos.x

SHAPES: List[str] = ["I", "J", "L", "O", "T"]
BLOCKS: Dict[str, List[List[int]]] = {
    "I": [[1, 1, 1, 1]],
    "J": [[1, 1, 1], [0, 0, 1]],
    "L": [[1, 1, 1], [1, 0, 0]],
    "O": [[1, 1], [1, 1]],
    "T": [[1, 1, 1], [0, 1, 0]]
}
ROTATION_ADJUST: Dict[str, List[Position]] = {
        "I": [Position(-1, 1), Position(1, -2), Position(-2, 2), Position(2, -1)],
        "J": [Position(-1, 0), Position(0, 0), Position(0, 1), Position(1, -1)],
        "L": [Position(-1, 0), Position(0, 0), Position(0, 1), Position(1, -1)],
        "O": [Position(0, 0)],
        "T": [Position(-1, 0), Position(0, 0), Position(0, 1), Position(1, -1)]
}
COLORS: Dict[str, int] = {
    "I": 1,
    "J": 2,
    "L": 3,
    "O": 4,
    "T": 5
}

ACTION = ["<", ">", "@", "V"]

class Block:
    def __init__(self, shape: str, pos: Position = Position(0, BOARD_WIDTH//2 - 1)):
        self.shape: str = shape
        self.cells: np.ndarray = np.array(BLOCKS[shape], dtype=np.int8) * COLORS[shape]
        self.pos: Position = pos  # Top Left corner
        self.rotation_count: int = 0
    
    @property
    def width(self) -> int:
        return self.cells.shape[1]
    
    @property
    def height(self) -> int:
        return self.cells.shape[0]
        
    def try_rotate(self) -> 'Block':
        result = copy.copy(self)
        result.rotate()
        return result

    def rotate(self):
        self.cells = np.rot90(self.cells, -1)
        (y, x) = self.pos + ROTATION_ADJUST[self.shape][self.rotation_count%len(ROTATION_ADJUST[self.shape])]
        self.pos = Position(max(0, y), min(max(0, x), BOARD_WIDTH - self.width))
        self.rotation_count += 1

    def move_left(self):
        self.pos = self.pos.left()
    
    def move_right(self):
        self.pos = self.pos.right()
            
    def move_down(self):
        self.pos = self.pos.down()
        
class Board:
    def __init__(self):
        self.reset()

    def reset(self):
        self.score = 0
        self.block_count = 0
        self.gameover = False
        self.cells = np.zeros((BOARD_HEIGHT, BOARD_WIDTH), dtype=np.int8)
        self._drop_pos: Optional[Position] = None
        self.new_block()

    @property
    def level(self):
        return self.block_count // 50 + 1

    def new_block(self, shape: str = ""):
        ### Return False if Game Over
        if self.gameover:
            return
        if not shape in SHAPES:
            shape = random.choice(SHAPES)
        self.block: Block = Block(shape)
        self.block_count += 1
        self._drop_pos = None
        self.gameover = self.block.pos == self.drop_pos
    
    def freeze(self) -> int:
        y, x = self.block.pos
        h, w = self.block.cells.shape
        self.cells[y:y+h, x:x+w] += self.block.cells
        if self.gameover:
            return -1000
        clear_row = []
        reward = 0
        for i in range(y, y+h):
            if np.all(self.cells[i] > 0):
                clear_row.append(i)
        if len(clear_row) > 0:
            reward = len(clear_row) * (10 + len(clear_row) - 1) 
            self.cells = np.vstack([np.zeros((len(clear_row), BOARD_WIDTH), dtype=np.int8), np.delete(self.cells, clear_row, axis=0)])
            if np.all(self.cells == 0):
                reward += 100
        self.score += reward
        return reward

    def conflict(self, pos: Position, block_cell: np.ndarray) -> bool:
        h, w = block_cell.shape
        if pos.x < 0 or pos.x + w > BOARD_WIDTH or pos.y + h > BOARD_HEIGHT:
            return True
        return np.any(self.cells[pos.y:pos.y+h, pos.x:pos.x+w] * block_cell > 0)

    @property    
    def drop_pos(self) -> Position:
        if self._drop_pos is None:
            block = copy.copy(self.block)
            while not self.conflict(block.pos.down(), block.cells):
                block.move_down()
            self._drop_pos = block.pos
        return self._drop_pos

    def perform(self, action: str):
        if self.gameover:
            return
        match action:
            case '<':
                if not self.conflict(self.block.pos.left(), self.block.cells):
                    self.block.move_left()
                    self._drop_pos = None
                
            case '>':
                if not self.conflict(self.block.pos.right(), self.block.cells):
                    self.block.move_right()
                    self._drop_pos = None
            
            case '@':
                block = self.block.try_rotate()
                if not self.conflict(block.pos, block.cells):
                    self.block = block
                    self._drop_pos = None
            
            case 'v':
                if not self.conflict(self.block.pos.down(), self.block.cells):
                    self.block.move_down()
                    
            case _:
                self.new_block(action)

    def state(self) -> np.ndarray:
        cells = self.cells.copy()
        y, x = self.block.pos
        h, w = self.block.cells.shape
        cells[y:y+h, x:x+w] += self.block.cells
        return cells
    
    def __repr__(self):
        return str(self.state())


def plot_board(board: Board):
    """Plot the Tetris board using matplotlib."""
    colors = ['white', 'red', 'orange', 'yellow', 'green', 'blue']
    cmap = ListedColormap(colors)
    
    plt.clf()
    ax = plt.gca()
    
    # Plot the board state
    ax.imshow(board.state(), cmap=cmap, vmin=0, vmax=5)
    
    # Draw grid lines between cells (constrained to board area)
    for x in range(BOARD_WIDTH + 1):
        ax.vlines(x - 0.5, -0.5, BOARD_HEIGHT - 0.5, color='gray', linewidth=0.5)
    for y in range(BOARD_HEIGHT + 1):
        ax.hlines(y - 0.5, -0.5, BOARD_WIDTH - 0.5, color='gray', linewidth=0.5)
    
    # Draw thick border around the board
    border = Rectangle((-0.5, -0.5), BOARD_WIDTH, BOARD_HEIGHT,
                       fill=False, edgecolor='black', linewidth=3)
    ax.add_patch(border)
    
    # Display level and score to the right of the board
    text_x = BOARD_WIDTH + 1
    ax.text(text_x, 2, f"Level", fontsize=12, fontweight='bold', ha='left', va='center')
    ax.text(text_x, 4, f"{board.level}", fontsize=14, ha='left', va='center')
    ax.text(text_x, 7, f"Score", fontsize=12, fontweight='bold', ha='left', va='center')
    ax.text(text_x, 9, f"{board.score}", fontsize=14, ha='left', va='center')
    
    # Display Game Over message if game is over
    if board.gameover:
        ax.text(BOARD_WIDTH / 2 - 0.5, BOARD_HEIGHT / 2 - 0.5, "GAME OVER",
                fontsize=20, fontweight='bold', ha='center', va='center',
                color='white', bbox=dict(boxstyle='round', facecolor='red', alpha=0.8))
        ax.text(BOARD_WIDTH / 2 - 0.5, BOARD_HEIGHT / 2 + 1.5, "Press ENTER to restart",
                fontsize=10, ha='center', va='center',
                color='white', bbox=dict(boxstyle='round', facecolor='darkred', alpha=0.8))
    
    # Remove axes, ticks, and spines
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(-0.5, BOARD_WIDTH - 0.5)
    ax.set_ylim(BOARD_HEIGHT - 0.5, -0.5)
    ax.set_aspect('equal')
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Remove extra space
    plt.tight_layout(pad=0)
    plt.pause(0.001)
    plt.show()

def play_board(board: Board, action: str) -> bool:
    ### return False if game over
    drop_pos = board.drop_pos
    if action == 'V' or (action == 'v' and board.block.pos == drop_pos):
        for _ in range(drop_pos.y - board.block.pos.y):
            board.perform('v')
            plot_board(board)
            time.sleep(RENDER_INTERVAL/10)
        board.freeze()
        board.new_block()
    elif action == '.':
        board.reset()
    else:
        board.perform(action)
    plot_board(board)

def testGame(board: Board):
    actions = ">>@@>>>>+<@<<<@<@<+vv@v@vvv@vvv@vvv@vvvv@@@vvvv"
    plot_board(board)
    for action in actions:
        board.perform(action)
        plot_board(board)
        time.sleep(RENDER_INTERVAL)
    
def testRotation(board):
    for shape in SHAPES:
        board.new_block(shape)
        plot_board(board)
        time.sleep(RENDER_INTERVAL)
        for i in range(8):
            board.perform('@')
            plot_board(board)
            time.sleep(RENDER_INTERVAL)
        for i in range(4):    
            board.perform('v')
            plot_board(board)
            time.sleep(RENDER_INTERVAL)
        for i in range(8):
            board.perform('@')
            plot_board(board)
            time.sleep(RENDER_INTERVAL)

KEY_ACTION_MAP = {
    'left': '<',
    'right': '>',
    'up': '@',
    'down': 'V',
    ' ': 'v',
    'enter': '.'
}

# Action queue to prevent re-entrancy issues from plt.pause()
action_queue: deque = deque()

def on_key_press(event, board: Board):
    """Handle keyboard events for the Tetris game.
    
    Actions are queued instead of executed immediately to prevent
    re-entrancy issues when plt.pause() processes events.
    """
    key = event.key

    # When game is over, only accept 'enter' to reset or 'escape' to exit
    if board.gameover:
        if key == 'enter':
            action_queue.append('.')  # Reset game
        elif key == 'escape':
            plt.close()
        return

    # Queue actions instead of executing immediately
    if key in KEY_ACTION_MAP:
        action_queue.append(KEY_ACTION_MAP[key])
    elif key == 'escape':
        plt.close()  # This is safe to execute immediately
    # Number keys for creating new blocks
    elif key in ['0', '1', '2', '3', '4', '5']:
        num = int(key)
        if num == 0:
            action_queue.append('')  # Random block (handled by board.perform default case)
        else:
            action_queue.append(SHAPES[num - 1])  # Specific shape


if __name__ == '__main__':
    plt.ion()  # Enable interactive mode
    fig = plt.figure()
    board = Board()
    
    def auto_drop(frame):
        """Automatically drop the block one step every interval.
        
        Also processes any queued actions from keyboard input.
        """
        # Process all queued actions first
        while action_queue:
            action = action_queue.popleft()
            play_board(board, action)
        
        # Don't auto-drop if game is over
        if board.gameover:
            return []
        
        # Then do auto-drop
        play_board(board, 'v')
        return []
    
    # Connect keyboard handler
    fig.canvas.mpl_connect('key_press_event', lambda event: on_key_press(event, board))
    
    # Create animation timer - interval in milliseconds (RENDER_INTERVAL * 1000)
    ani = FuncAnimation(fig, auto_drop, interval=int(RENDER_INTERVAL * 1000),
                        cache_frame_data=False, save_count=0)
    
    # Keep the window open and responsive to keyboard input
    plt.show(block=True)
