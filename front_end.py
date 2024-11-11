import tkinter as tk
from tkinter import messagebox
import chess
import chess.pgn
import mysql.connector
from dummy_function import dummy
from fow_engine import FoW_Engine1

class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Two-Player Chess Game")
        
        # Chess board size
        self.board_size = 8
        self.square_size = 64  # Size of each square in pixels

        self.moves = ""
        
        # Initialize MySQL database connection
        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="maggie", 
            database="fogofwar"
        )
        self.cursor = self.connection.cursor()

        # creates the table chessboard
        self.cursor.execute("DROP TABLE IF EXISTS chessboard")
        self.cursor.execute("CREATE TABLE chessboard (col CHAR(1), rw INT, color char(1), piece CHAR(1), vis BOOLEAN)")
        print("Table is created")
        self.connection.commit()
        self.refill_board()
        self.cursor.execute("ALTER TABLE chessboard ADD CONSTRAINT chk_color_vis CHECK (NOT(color = 'W' AND vis = false));")

        # Initialize python-chess board
        self.board = chess.Board()

        self.turn_label = tk.Label(self.root, text="White's Turn", font=16)
        self.turn_label.pack()

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
        print_button.pack(side=tk.LEFT)

        # Creates a button that prints all legal board moves **debug feautre** 
        print_legal_moves_button = tk.Button(self.root, text="Print Legal Moves", command=lambda: self.print_legal_moves(list(self.board.legal_moves)))
        print_legal_moves_button.pack(side=tk.LEFT)

        # Makes it so you can hit Escape to leave the game
        self.root.bind("<Escape>", lambda event: self.quit_game())

        # Create a button to print the moves made in the game
        self.move_list = []
        print_moves_button = tk.Button(self.root, text="Print Move History", command=self.print_moves)
        print_moves_button.pack(side=tk.LEFT)

        # Track selected square and moves
        self.selected_square = None

        # Track whose turn it is (True for white, False for black)
        self.is_white_turn = True
        
        # Track dots for move indicators
        self.move_dots = []

        # Tracks captured peices
        self.captured_pieces = {"white": [], "black": []}
        print_captured_button = tk.Button(self.root, text="Print Captured Pieces", command=self.print_captured_pieces)
        print_captured_button.pack(side=tk.LEFT)

        # Button that suggests move
        # self.suggest_move_button = tk.Button(self.root, text="Make Suggestion", command=lambda: dummy(list(self.board.legal_moves)))
        # self.suggest_move_button.pack(side=tk.LEFT)
        # self.update_suggest_button_state()

        self.suggest_move_button = tk.Button(self.root, text="Make Suggestion",command=self.start_engine)
        self.suggest_move_button.pack(side=tk.LEFT)
        self.update_suggest_button_state()

        # ran here once to set up original visibility for player 1
        self.update_visibility(list(self.board.legal_moves))

    def start_engine(self):
        # Create an instance of FoW_Engine1, passing the connection
        engine = FoW_Engine1(self.connection)
        # Run the engine
        engine.run_engine()
    
    def update_turn_label(self):
        current_turn = "White's Turn" if self.is_white_turn else "Black's Turn"
        self.turn_label.config(text=current_turn)
    
    def print_captured_pieces(self):
        """Print the captured pieces for both players."""
        print(f"Captured White Pieces: {self.captured_pieces['white']}")
        print(f"Captured Black Pieces: {self.captured_pieces['black']}")

    def update_suggest_button_state(self):
        if self.is_white_turn:
            self.suggest_move_button.config(state=tk.NORMAL)
        else:
            self.suggest_move_button.config(state=tk.DISABLED)


    # make this an accessible list throughout code
    def print_legal_moves(self, legal_moves):
        print(legal_moves)
        print(len(legal_moves))

    def quit_game(self):
        # Resets the SQL table
        self.cursor.execute("DROP TABLE chessboard")
        print("Table has been dropped")
        self.connection.commit()
        # Close the MySQL connection
        self.connection.close()
        # Close the GUI window
        self.root.quit()
        print("Game ended")

    # refills the board at the beginning of the game
    def refill_board(self):
        # # Delete all existing rows in the chess table
        # self.cursor.execute("TRUNCATE TABLE chessboard")

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
            ('A', 7, 'B', 'p', True),
            ('B', 7, 'B', 'p', True),
            ('C', 7, 'B', 'p', True),
            ('D', 7, 'B', 'p', True),
            ('E', 7, 'B', 'p', True),
            ('F', 7, 'B', 'p', True),
            ('G', 7, 'B', 'p', True),
            ('H', 7, 'B', 'p', True),
            ('A', 8, 'B', 'r', True),
            ('B', 8, 'B', 'n', True),
            ('C', 8, 'B', 'b', True),
            ('D', 8, 'B', 'q', True),
            ('E', 8, 'B', 'k', True),
            ('F', 8, 'B', 'b', True),
            ('G', 8, 'B', 'n', True),
            ('H', 8, 'B', 'r', True)
        ]

        query = "INSERT INTO chessboard (col, rw, color, piece, vis) VALUES (%s, %s, %s, %s, %s)"
        self.cursor.executemany(query, initial_setup)
        self.connection.commit()

        print("Board has been filled with initial chess setup.")

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
                    piece_str = piece.symbol().lower() if piece.color else piece.symbol()
                    image = self.piece_images.get(f"{'w' if piece.color else 'b'}{piece_str.lower()}")
                    if image:
                        x = col * self.square_size
                        y = row * self.square_size
                        self.canvas.create_image(x + self.square_size // 2, y + self.square_size // 2, 
                                                 image=image, tags="piece")

    def on_square_click(self, event):
        """Handle click events to select and move pieces."""
        col = 7-(event.x // self.square_size)
        row = 7-(event.y // self.square_size)
        col = 7 - col # reverse the column mapping
        clicked_square = chess.square(col, row)
        # placed here so that it is storing the current player's moves and not the next player

        # Clear existing move dots when clicking a new square
        for dot in self.move_dots:
            self.canvas.delete(dot)
        self.move_dots = []

        if self.selected_square is None:
            # Select the piece if any
            piece = self.board.piece_at(clicked_square)
            if piece and piece.color == self.is_white_turn:  # Ensure the player selects their own piece
                self.selected_square = clicked_square
                # Display possible moves for the selected piece
                self.show_possible_moves(clicked_square)
        else:
            # Try to make a move
            move = chess.Move(self.selected_square, clicked_square)
            if move in self.board.legal_moves:
                captured_piece = self.board.piece_at(clicked_square)
                if captured_piece:
                    piece_color = 'white' if captured_piece.color else 'black'
                    self.captured_pieces[piece_color].append(captured_piece.symbol().upper())
                
                self.board.push(move)
                self.update_pieces()

                # Store the move in the move list
                if self.is_white_turn:
                    self.move_list.append(move.uci())

                # Update the database
                self.update_database(self.selected_square, clicked_square)
                # updates the visibility part of the database for player 1's perspective only
                # I have it set to not because where it is located it will see the next player 1's move options therefore after the piece is moved
                if not self.is_white_turn:
                    self.update_visibility(list(self.board.legal_moves))
                
                # Check for game-ending conditions
                if self.check_game_over():
                    return

                # Switch turns between players and functionalites
                self.is_white_turn = not self.is_white_turn
                self.update_suggest_button_state()
                self.update_turn_label()
            else:
                messagebox.showerror("Illegal Move", "That move is not legal.")

            # Reset selected square
            self.selected_square = None
    
    def show_possible_moves(self, square):
        """Show dots on squares where the selected piece can move."""
        for move in self.board.legal_moves:
            if move.from_square == square:
                # Calculate the position of the destination square
                to_col = chess.square_file(move.to_square)
                to_row = 7 - chess.square_rank(move.to_square)
                
                # Place a dot in the center of each possible move square
                x = to_col * self.square_size + self.square_size // 2
                y = to_row * self.square_size + self.square_size // 2
                dot = self.canvas.create_oval(
                    x - 5, y - 5, x + 5, y + 5,
                    fill="blue", tags="dot" # the dots are blue and will stay blue lol
                )
                self.move_dots.append(dot)

    # rough draft of the logic
    def update_visibility(self, legal_moves):
        """Update the visibility of the squares. Loop through the table, if the square (rw, col) is not in legal_moves then vis=false."""
        self.cursor.execute("SELECT * FROM chessboard;")
        results = self.cursor.fetchall()
        # makes the move list full of the to_square values (A1, B1, etc)
        move_list = [chess.square_name(move.to_square).upper() for move in legal_moves]
        # debug print
        print("Legal Moves =", move_list)
        # iterates over each row in the table
        for row in results:
            # makes the sqare value in the A1, B1 format
            square = row[0] + str(row[1]) # row[0] = col, row[1] = rw
            # pulls the color value
            color = row[2]
            # sees if the square value is in the move list
            if square in move_list:
                print(square, "is a legal move")
                self.cursor.execute("UPDATE chessboard SET vis = true WHERE col = %s AND rw = %s", (row[0], row[1]))
            # if the square is not in the move_list then it is not a legal move which means it should not be seen to player 1
            else:
                # makes sure the check constraint is avoided
                if color == 'W':
                    print(square, "is occupied by a white piece")
                else:
                    print(square, "is not a legal move")
                    self.cursor.execute("UPDATE chessboard SET vis = false WHERE col = %s AND rw = %s", (row[0], row[1]))
            
                    
    def update_database(self, from_square, to_square):
        """Update the MySQL database after a move."""
        from_col = chr(chess.square_file(from_square) + ord('A'))
        from_row = chess.square_rank(from_square) + 1
        to_col = chr(chess.square_file(to_square) + ord('A'))
        to_row = chess.square_rank(to_square) + 1

        # Get the piece to move
        piece = self.board.piece_at(to_square).symbol()

        # Clear the 'from' position in the database
        self.cursor.execute(
            "UPDATE chessboard SET color = '', piece = '' WHERE col = %s AND rw = %s",
            (from_col, from_row)
        )
        
        if self.is_white_turn:
        # Set the 'to' position in the database
            self.cursor.execute(
                "UPDATE chessboard SET color = 'W', piece = %s WHERE col = %s AND rw = %s",
                (piece, to_col, to_row)
            )
        else:
            self.cursor.execute(
                "UPDATE chessboard SET color = 'B', piece = %s WHERE col = %s AND rw = %s",
                (piece, to_col, to_row)
            )

        # Commit the changes
        self.connection.commit()

    def check_game_over(self):
        """Check if the game is over (checkmate, stalemate, etc.)."""
        if self.board.is_checkmate():
            winner = "Black" if not self.is_white_turn else "White"
            messagebox.showinfo("Checkmate", f"{winner} wins!")
            self.quit_game()
            print(self.moves)
            return True
        elif self.board.is_stalemate():
            messagebox.showinfo("Stalemate", "It's a draw!")
            self.quit_game()
            print(self.moves)
            return True
        elif self.board.is_insufficient_material():
            messagebox.showinfo("Draw", "Insufficient material for checkmate!")
            self.quit_game()
            print(self.moves)
            return True
        return False
    
    def print_moves(self):
        """Print the moves made so far in the game."""
        print("Moves made in the game: ")
        for move in self.move_list:
            print(move)

    def print_board_state(self):
        """Print the current board state (for debugging purposes)."""
        self.cursor.execute("SELECT * FROM chessboard;")
        results = self.cursor.fetchall()
        for row in results:
            print(row)  # Print each row to the console

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessGUI(root)
    root.mainloop()