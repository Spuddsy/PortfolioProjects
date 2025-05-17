import tkinter as tk
import random
import copy

# Constants for players
PLAYER_1 = 0  # Player 1 is the human
PLAYER_2 = 1  # Player 2 is the computer

# Initialize the board (6 pits per player and 2 stores)
def init_board():
    return [4, 4, 4, 4, 4, 4, 0,  # Player 1 side
            4, 4, 4, 4, 4, 4, 0]  # Player 2 side

# Check if the game is over
def is_game_over(board):
    return all(p == 0 for p in board[0:6]) or all(p == 0 for p in board[7:13])

# Get valid moves for the current player
def get_valid_moves(board, player):
    if player == PLAYER_1:
        return [i for i in range(0, 6) if board[i] > 0]  # Player 1 moves in pits 0-5
    else:
        return [i for i in range(7, 13) if board[i] > 0]  # Player 2 moves in pits 7-12

# Perform a move for the given player
def make_move(board, pit, player):
    board = copy.deepcopy(board)
    stones = board[pit]
    board[pit] = 0
    index = pit

    # Distribute stones
    while stones > 0:
        index = (index + 1) % 14
        if (player == PLAYER_1 and index == 13) or (player == PLAYER_2 and index == 6):
            continue
        board[index] += 1
        stones -= 1

    # Capture rule (only if the last stone lands in an empty pit on your side and it was empty before)
    if player == PLAYER_1 and 0 <= index <= 5 and board[index] == 1:
        opposite_index = 12 - index
        if board[opposite_index] > 0:
            board[6] += board[opposite_index] + 1
            board[opposite_index] = 0
            board[index] = 0
    elif player == PLAYER_2 and 7 <= index <= 12 and board[index] == 1:
        opposite_index = 12 - index
        if board[opposite_index] > 0:
            board[13] += board[opposite_index] + 1
            board[opposite_index] = 0
            board[index] = 0

    return board


# Minimax AI (Computer's decision making)
def minimax(board, depth, maximizing_player):
    if depth == 0 or is_game_over(board):
        return board[6] - board[13], -1

    if maximizing_player:
        max_eval = float('-inf')
        best_move = -1
        for move in get_valid_moves(board, PLAYER_1):
            new_board = make_move(board, move, PLAYER_1)
            eval, _ = minimax(new_board, depth - 1, False)
            if eval > max_eval:
                max_eval = eval
                best_move = move
        return max_eval, best_move
    else:
        min_eval = float('inf')
        best_move = -1
        for move in get_valid_moves(board, PLAYER_2):
            new_board = make_move(board, move, PLAYER_2)
            eval, _ = minimax(new_board, depth - 1, True)
            if eval < min_eval:
                min_eval = eval
                best_move = move
        return min_eval, best_move

# Random AI (Player 2 random moves)
def random_move(board):
    valid_moves = get_valid_moves(board, PLAYER_2)
    return random.choice(valid_moves)

class MancalaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mancala")
        
        # Initialize the board
        self.board = init_board()
        self.current_player = PLAYER_1
        self.ai_mode = "minimax"  # Default AI mode for Player 2 is minimax
        self.best_move = None  # To track the best move for Player 1 (AI Assistant)

        # Create frames
        self.top_frame = tk.Frame(root)
        self.middle_frame = tk.Frame(root)
        self.bottom_frame = tk.Frame(root)
        self.log_frame = tk.Frame(root)

        self.top_frame.pack()
        self.middle_frame.pack()
        self.bottom_frame.pack()
        self.log_frame.pack()

        # Game mode selection
        self.game_mode_label = tk.Label(self.log_frame, text="Select Game Mode for Player 2:")
        self.game_mode_label.pack()
        
        self.ai_mode_var = tk.StringVar(value="minimax")
        self.ai_mode_dropdown = tk.OptionMenu(self.log_frame, self.ai_mode_var, "minimax", "random", command=self.update_ai_mode)
        self.ai_mode_dropdown.pack()

        # Store labels
        self.store2 = tk.Label(self.middle_frame, text=f"P2 Away\n{self.board[13]}", width=8, height=4, bg="lightblue", relief="ridge", font=("Arial", 10, "bold"))
        self.store1 = tk.Label(self.middle_frame, text=f"P1 Home\n{self.board[6]}", width=8, height=4, bg="lightgreen", relief="ridge", font=("Arial", 10, "bold"))

        self.store2.grid(row=0, column=0, rowspan=2)
        self.store1.grid(row=0, column=8, rowspan=2)

        # Player 2 pits (top row)
        self.p2_buttons = []
        for i in range(12, 6, -1):
            btn = tk.Button(self.top_frame, text=str(self.board[i]), width=6, height=2, state="disabled", relief="groove", bg="lightblue", font=("Arial", 10))
            btn.grid(row=0, column=12 - i)
            self.p2_buttons.append(btn)

        # Player 1 pits (bottom row)
        self.p1_buttons = []
        for i in range(0, 6):
            btn = tk.Button(self.bottom_frame, text=str(self.board[i]), width=6, height=2, command=lambda i=i: self.on_pit_click(i), relief="groove", bg="lightgreen", font=("Arial", 10))
            btn.grid(row=0, column=i)
            self.p1_buttons.append(btn)

        # Game status / log label
        self.status = tk.Label(self.log_frame, text="Player 1's turn", height=2, font=("Arial", 12, "italic"))
        self.status.pack()

        # New Game Button
        self.new_game_button = tk.Button(self.log_frame, text="New Game", command=self.reset_game, bg="lightgray", font=("Arial", 10, "bold"))
        self.new_game_button.pack(pady=5)

    def update_ai_mode(self, selected_mode):
        self.ai_mode = selected_mode
        print(f"AI Mode for Player 2 is now set to: {self.ai_mode}")

    def on_pit_click(self, pit_index):
        if self.current_player == PLAYER_1:
            self.status.config(text=f"Player 1 clicked pit {pit_index}")
            self.board = make_move(self.board, pit_index, PLAYER_1)
            self.update_board()

        # Check if the game is over after Player 1's move
        if is_game_over(self.board):
            self.end_game()
            return

        # Switch to Player 2 (computer)
        self.current_player = PLAYER_2
        self.status.config(text="Computer is thinking...")

        # Computer makes a move
        if self.ai_mode == "minimax":
            _, best_move = minimax(self.board, 4, False)
        elif self.ai_mode == "random":
            best_move = random_move(self.board)

        self.board = make_move(self.board, best_move, PLAYER_2)

        # Show what move the computer made
        self.status.config(text=f"Computer played pit {best_move}")

        self.update_board()

        # Check if the game is over after Player 2's move
        if is_game_over(self.board):
            self.end_game()
            return

        # Switch back to Player 1
        self.current_player = PLAYER_1
        self.status.config(text=f"Computer played pit {best_move}.\n")
        self.highlight_best_move()

        
    
    def end_game(self):
        # Display final game results
        self.status.config(text="Game Over!")
        if self.board[6] > self.board[13]:
            self.status.config(text="Player 1 wins!")
        elif self.board[6] < self.board[13]:
            self.status.config(text="Computer wins!")
        else:
            self.status.config(text="It's a tie!")

    def update_board(self):
        # Update the buttons based on the new board state
        for i in range(0, 6):
            self.p1_buttons[i].config(text=str(self.board[i]))
        for i in range(7, 13):
            self.p2_buttons[12 - i].config(text=str(self.board[i]))
        
        # Update stores
        self.store1.config(text=f"P1 Home\n{self.board[6]}")
        self.store2.config(text=f"P2 Away\n{self.board[13]}")
        
        if self.current_player == PLAYER_1:
            self.highlight_best_move()

    def highlight_best_move(self):
        # Get the best move for Player 1 (AI assistant's suggestion)
        _, self.best_move = minimax(self.board, 4, True)

        # Reset all pits to their original color
        for btn in self.p1_buttons:
            btn.config(bg="lightgreen")
        
        # Highlight the best move
        self.p1_buttons[self.best_move].config(bg="yellow")  # Highlight the suggested pit
    
    def reset_game(self):
        self.board = init_board()
        self.current_player = PLAYER_1
        self.status.config(text="Player 1's turn")
        self.update_board()

if __name__ == "__main__":
    root = tk.Tk()
    game = MancalaGUI(root)
    root.mainloop()
