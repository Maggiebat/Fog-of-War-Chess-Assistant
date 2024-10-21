import tkinter as tk
from tkinter import messagebox
import chess
import mysql.connector
import time

class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Two-Player Chess Game")
        
        # Chess board size
        self.board_size = 8
        self.square_size = 64  # Size of each square in pixels
        
        # Initialize MySQL database connection
        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="maggie", 
            database="chessboard"
        )
        self.cursor = self.connection.cursor()

        # Initialize python-chess board
        self.board = chess.Board()

        # Create Canvas to draw chessboard
        self.canvas = tk.Canvas(self.root, width=self.board_size * self.square_size, 
                                height=self.board_size * self.square_size)
        self.canvas.pack()

        # Load piece images
        self.piece_images = self.load_piece_images()

        # Draw the chessboard
        self.draw_board()

        # Place pieces on the board
        self.update_pieces()

        # Bind click events to the board
        self.canvas.bind("<Button-1>", self.on_square_click)

        # Creates a button that prints the board state **debug feature**
        print_button = tk.Button(self.root, text="Print Board State", command=self.print_board_state)
        print_button.pack()

        # Makes it so you can hit Escape to leave the game
        self.root.bind("<Escape>", lambda event: self.quit_game())

        # Track selected square and moves
        self.selected_square = None

        # Track whose turn it is (True for white, False for black)
        self.is_white_turn = True


    def quit_game(self):
        # Resets the SQL table
        self.reset_board()
        # Close the MySQL connection
        self.connection.close()
        # Close the GUI window
        self.root.quit()
        print("Game ended")

    def reset_board(self):
        # Delete all existing rows in the chess table
        self.cursor.execute("TRUNCATE TABLE chessboard")

        # Repopulate the table with the initial chessboard setup and set visible to TRUE
        initial_setup = [
            ('A', 1, 'W', 'R', True),
            ('B', 1, 'W', 'N', True),
            ('C', 1, 'W', 'B', True),
            ('D', 1, 'W', 'Q', True),
            ('E', 1, 'W', 'K', True),
            ('F', 1, 'W', 'B', True),
            ('G', 1, 'W', 'N', True),
            ('H', 1, 'W', 'R', True),
            ('A', 2, 'W', 'P', True),
            ('B', 2, 'W', 'P', True),
            ('C', 2, 'W', 'P', True),
            ('D', 2, 'W', 'P', True),
            ('E', 2, 'W', 'P', True),
            ('F', 2, 'W', 'P', True),
            ('G', 2, 'W', 'P', True),
            ('H', 2, 'W', 'P', True),
            ('B', 3, '', '', True),
            ('C', 3, '', '', True),
            ('D', 3, '', '', True),
            ('A', 3, '', '', True),
            ('E', 3, '', '', True),
            ('F', 3, '', '', True),
            ('G', 3, '', '', True),
            ('H', 3, '', '', True),
            ('H', 3, '', '', True),
            ('A', 4, '', '', True),
            ('B', 4, '', '', True),
            ('C', 4, '', '', True),
            ('D', 4, '', '', True),
            ('E', 4, '', '', True),
            ('F', 4, '', '', True),
            ('G', 4, '', '', True),
            ('H', 4, '', '', True),
            ('A', 5, '', '', True),
            ('B', 5, '', '', True),
            ('C', 5, '', '', True),
            ('D', 5, '', '', True),
            ('E', 5, '', '', True),
            ('F', 5, '', '', True),
            ('G', 5, '', '', True),
            ('H', 5, '', '', True),
            ('A', 6, '', '', True),
            ('B', 6, '', '', True),
            ('C', 6, '', '', True),
            ('D', 6, '', '', True),
            ('E', 6, '', '', True),
            ('F', 6, '', '', True),
            ('G', 6, '', '', True),
            ('H', 6, '', '', True),
            ('A', 7, 'B', 'P', True),
            ('B', 7, 'B', 'P', True),
            ('C', 7, 'B', 'P', True),
            ('D', 7, 'B', 'P', True),
            ('E', 7, 'B', 'P', True),
            ('F', 7, 'B', 'P', True),
            ('G', 7, 'B', 'P', True),
            ('H', 7, 'B', 'P', True),
            ('A', 8, 'B', 'R', True),
            ('B', 8, 'B', 'N', True),
            ('C', 8, 'B', 'B', True),
            ('D', 8, 'B', 'Q', True),
            ('E', 8, 'B', 'K', True),
            ('F', 8, 'B', 'B', True),
            ('G', 8, 'B', 'N', True),
            ('H', 8, 'B', 'R', True)
        ]

        query = "INSERT INTO chess (col, rw, color, piece, vis) VALUES (%s, %s, %s, %s, %s)"
        self.cursor.executemany(query, initial_setup)
        self.connection.commit()

        print("Board has been reset to initial state with all pieces visible.")

    # Loads the photos so that the GUI has chess pieces on the board
    def load_piece_images(self):
        """Load piece images from files (you can use any chess piece images here)."""
        pieces = ["wp", "wr", "wn", "wb", "wq", "wk", "bp", "br", "bn", "bb", "bq", "bk"]
        piece_images = {}
        for piece in pieces:
            piece_images[piece] = tk.PhotoImage(file=f"images/{piece}.png")
        return piece_images

    def draw_board(self):
        """Draw the chessboard on the canvas."""
        colors = ["#f5ffff", "#363838"]  # Light and dark squares
        for row in range(self.board_size):
            for col in range(self.board_size):
                color = colors[(row + col) % 2]
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

    def update_pieces(self):
        """Place pieces on the board according to the current board state."""
        # Clear all existing pieces from the board
        self.canvas.delete("piece")

        # Place pieces on the board
        for row in range(8):
            for col in range(8):
                piece = self.board.piece_at(chess.square(col, 7 - row))
                if piece:
                    piece_str = piece.symbol().lower() if piece.color else piece.symbol().upper()
                    image = self.piece_images.get(f"{'w' if piece.color else 'b'}{piece_str.lower()}")
                    if image:
                        x = col * self.square_size
                        y = row * self.square_size
                        self.canvas.create_image(x + self.square_size // 2, y + self.square_size // 2, 
                                                 image=image, tags="piece")

    def on_square_click(self, event):
        """Handle click events to select and move pieces."""
        col = event.x // self.square_size
        row = event.y // self.square_size
        clicked_square = chess.square(col, 7 - row)

        if self.selected_square is None:
            # Select the piece if any
            piece = self.board.piece_at(clicked_square)
            if piece and piece.color == self.is_white_turn:  # Ensure the player selects their own piece
                self.selected_square = clicked_square
        else:
            # Try to make a move
            move = chess.Move(self.selected_square, clicked_square)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.update_pieces()

                # Update the database
                self.update_database(self.selected_square, clicked_square)

                # Check for game-ending conditions
                if self.check_game_over():
                    return

                # Switch turns between players
                self.is_white_turn = not self.is_white_turn
            else:
                messagebox.showerror("Illegal Move", "That move is not legal.")

            # Reset selected square
            self.selected_square = None

    def update_database(self, from_square, to_square):
        """Update the MySQL database after a move."""
        from_col = chr(chess.square_file(from_square) + ord('A'))
        from_row = 8 - chess.square_rank(from_square)
        to_col = chr(chess.square_file(to_square) + ord('A'))
        to_row = 8 - chess.square_rank(to_square)

        # Get the piece to move
        piece = self.board.piece_at(to_square).symbol().upper()

        # Clear the 'from' position in the database
        self.cursor.execute(
            "UPDATE chess SET piece = "", WHERE col = %s AND rw = %s",
            (from_col, from_row)
        )
        
        if self.is_white_turn:
        # Set the 'to' position in the database
            self.cursor.execute(
                "UPDATE chess SET color = 'W', piece = %s WHERE col = %s AND rw = %s",
                (piece, to_col, to_row)
            )
        else:
            self.cursor.execute(
                "UPDATE chess SET color = 'B', piece = %s WHERE col = %s AND rw = %s",
                (piece, to_col, to_row)
            )

        # Commit the changes
        self.connection.commit()

    def check_game_over(self):
        """Check if the game is over (checkmate, stalemate, etc.)."""
        if self.board.is_checkmate():
            winner = "White" if not self.is_white_turn else "Black"
            messagebox.showinfo("Checkmate", f"{winner} wins!")
            self.reset_board()
            return True
        elif self.board.is_stalemate():
            messagebox.showinfo("Stalemate", "It's a draw!")
            self.reset_board()
            return True
        elif self.board.is_insufficient_material():
            messagebox.showinfo("Draw", "Insufficient material for checkmate!")
            self.reset_board()
            return True
        return False

    def print_board_state(self):
        """Print the current board state (for debugging purposes)."""
        self.cursor.execute("SELECT * FROM chessboard;")
        results = self.cursor.fetchall()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessGUI(root)
    root.mainloop()
  