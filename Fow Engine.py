import chess

def run_engine(self):
    """Main loop for the chess engine."""
    self.initialize_visible_pieces()

    while True:

        if self.check_game_over():
            break

        self.evaluate_moves(k=5, depth=3)

        ## ##self.cursor.execute("SELECT col, rw, color, piece FROM visible_chessboard ORDER BY probability DESC LIMIT 1;")
        ##opponent_move = self.cursor.fetchone()

        if opponent_move:
            from_col = opponent_move[0]
            from_row = opponent_move[1]
            piece_color = opponent_move[2]
            piece = opponent_move[3]

            # Check if the move is known or unknown
            if piece_color == "unknown":
                move_description = "Unknown"
            else:
                # Convert from_col and from_row to a move
                move = self.convert_to_move(from_col, from_row)
                if move:
                    # Execute the move
                    self.board.push(move)
                    self.update_pieces()  # Update GUI

                    # Log the move in history
                    move_description = f"{piece_color} moved {piece} from {from_col}{from_row} to {move.to_square}."
                    self.track_move(move_description)

    self.suggest_player_move()

def initialize_visible_pieces(self):
    """Initialize the visible pieces from the database."""
    # Clear existing visible pieces
    self.cursor.execute("TRUNCATE TABLE FoW_chessboard;")

    # Repopulate the visible pieces table
    self.cursor.execute("INSERT INTO FoW_chessboard SELECT * FROM chessboard WHERE vis = TRUE;")
    self.connection.commit()


def convert_to_move(self, from_col, from_row):
    """Convert from_col and from_row to a chess Move object."""
    # Logic to determine the move based on the current state of the board and the piece
    from_square = chess.square(ord(from_col) - ord('A'), from_row - 1)
    legal_moves = list(self.board.legal_moves)

    for move in legal_moves:
        if move.from_square == from_square:
            return move
    return None


def track_move(self, description):
    """Track the move history."""
    #FINISH THIS



def update_pieces_table(self):

    self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS FoW_chessboard (col CHAR(1),rw INT,color CHAR(1),piece CHAR(1), prob FLOAT);""")

    # Fetch visible pieces from the existing chessboard
    self.cursor.execute("SELECT col, rw, color, piece FROM chessboard WHERE vis = TRUE;")
    visible_pieces = self.cursor.fetchall()

    # Prepare data for upsert (update or insert)
    for col, rw, color, piece in visible_pieces:
        # Check if the piece already exists
        self.cursor.execute("SELECT EXISTS(SELECT 1 FROM visible_chessboard WHERE col = %s AND rw = %s);", (col, rw))
        exists = self.cursor.fetchone()[0]

        if exists:
            # Update the existing piece
            self.cursor.execute("""
                   UPDATE visible_chessboard
                   SET color = %s, piece = %s, probability = %s
                   WHERE col = %s AND rw = %s
               """, (color, piece, 1.0, col, rw))
        else:
            # Insert a new piece
            self.cursor.execute("""
                   INSERT INTO visible_chessboard (col, rw, color, piece, probability)
                   VALUES (%s, %s, %s, %s, %s)
               """, (col, rw, color, piece, 1.0))


    self.evaluate_moves(k=3)
    # Commit the changes
    self.connection.commit()


def evaluate_moves(self, k=5, depth=3):
    """Evaluate all possible moves for opponent pieces using minimax and update the visible_chessboard table."""
    # Fetch visible pieces
    self.cursor.execute("SELECT col, rw, color, piece FROM FoW_chessboard;")
    visible_pieces = self.cursor.fetchall()

    # Create a chess board object to evaluate moves
    board = chess.Board()

    # Populate the board with visible pieces
    for col, rw, color, piece in visible_pieces:
        square = chess.square(ord(col) - ord('A'), rw - 1)
        if color == 'W':
            board.set_piece_at(square, chess.Piece.from_symbol(piece.lower()))
        else:
            board.set_piece_at(square, chess.Piece.from_symbol(piece.upper()))

    # Determine opponent color
    opponent_color = chess.WHITE if self.is_white_turn else chess.BLACK
    top_moves = []

    # Evaluate moves for opponent pieces
    for square in board.legal_moves:
        piece = board.piece_at(square)

        if piece and piece.color == opponent_color:
            # Evaluate moves using minimax
            for move in board.legal_moves:
                board.push(move)
                score = self.minimax(board, depth, float('-inf'), float('inf'), False)
                board.pop()

                # Store the move with its score
                top_moves.append((move, score))

    # Sort moves by score and take the top k
    top_moves = sorted(top_moves, key=lambda x: x[1], reverse=True)[:k]

    # Update probabilities for the current positions and insert new moves
    for move, score in top_moves:
        from_square = move.from_square
        to_square = move.to_square

        # Update current position probability to 0.5
        from_col = chr(chess.square_file(from_square) + ord('A'))
        from_row = chess.square_rank(from_square) + 1
        self.cursor.execute("""
            UPDATE FoW_chessboard
            SET probability = 0.5
            WHERE col = %s AND rw = %s
        """, (from_col, from_row))

        # Check if the target square is visible
        to_col = chr(chess.square_file(to_square) + ord('A'))
        to_row = chess.square_rank(to_square) + 1
        self.cursor.execute("SELECT vis FROM chessboard WHERE col = %s AND rw = %s;", (to_col, to_row))
        is_visible = self.cursor.fetchone()

        # If the move goes to a non-visible square, add it to the table
        if not is_visible or not is_visible[0]:
            self.cursor.execute("""
                INSERT INTO FoW_chessboard (col, rw, color, piece, probability)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE probability = 0.5
            """, (to_col, to_row, piece.color, piece.symbol().upper(), 0.5))

    # Commit changes
    self.connection.commit()
    print("Moves evaluated and visible_chessboard updated with new probabilities.")

def minimax(self, depth, maximizing_player):
    """Minimax algorithm to evaluate moves with scoring."""
    if depth == 0 or self.check_game_over():
        return self.evaluate_board()  # Evaluate the board state with updated scoring

    if maximizing_player:
        max_eval = float('-inf')
        for move in self.board.legal_moves:
            self.board.push(move)
            eval = self.minimax(depth - 1, False)
            self.board.pop()
            max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = float('inf')
        for move in self.board.legal_moves:
            self.board.push(move)
            eval = self.minimax(depth - 1, True)
            self.board.pop()
            min_eval = min(min_eval, eval)
        return min_eval

def suggest_player_move(self):
    """Suggest a move to the player based on the minimax algorithm."""
    best_move = None
    best_value = float('-inf')

    for move in self.board.legal_moves:
        self.board.push(move)
        move_value = self.minimax(3, False)  # Adjust depth as necessary
        self.board.pop()

        if move_value > best_value:
            best_value = move_value
            best_move = move

    if best_move:
        col = chr(chess.square_file(best_move.from_square) + ord('A'))
        rw = chess.square_rank(best_move.from_square) + 1
        piece = self.board.piece_at(best_move.from_square).symbol()
        move_suggestion = f"Suggested Move: Move {piece} from {col}{rw} to {chr(chess.square_file(best_move.to_square) + ord('A'))}{chess.square_rank(best_move.to_square) + 1}."
        print(move_suggestion)


def evaluate_board(self):
    """Evaluate the current board state based on piece value, position, and probability."""
    evaluation = 0

    for square in chess.SQUARES:
        piece = self.board.piece_at(square)
        if piece:
            piece_value = self.get_piece_value(piece)
            position_score = self.get_position_score(square, piece.color)

            # Retrieve probability score from the database
            col = chr(chess.square_file(square) + ord('A'))
            rw = chess.square_rank(square) + 1
            self.cursor.execute("SELECT probability FROM FoW_chessboard WHERE col = %s AND rw = %s;", (col, rw))
            probability_result = self.cursor.fetchone()
            probability_score = probability_result[0] if probability_result else 1.0  # Default to 1.0 if not found

            # Combine scores
            score = (piece_value + position_score) * probability_score

            if piece.color:  # White pieces
                evaluation += score
            else:  # Black pieces
                evaluation -= score

    return evaluation

def get_piece_value(self, piece):
        """Return the value of a piece."""
        values = {
            'p': 1,
            'n': 3,
            'b': 3,
            'r': 5,
            'q': 9,
            'k': 1000
        }
        return values.get(piece.symbol().lower(), 0)
def get_position_score(self, square, is_white):
    """Return a score based on the piece's position on the board."""
    # Example position values for pawns (can be customized)
    position_values = {
        # Each piece's position value can be customized here
        'P': [0, 0, 5, 10, 15, 20, 25, 30],  # Pawn
        'N': [0, 5, 10, 15, 15, 10, 5, 0],  # Knight
        'B': [0, 5, 10, 15, 15, 10, 5, 0],  # Bishop
        'R': [0, 5, 10, 15, 20, 25, 30, 0],  # Rook
        'Q': [0, 0, 0, 0, 10, 20, 30, 40],  # Queen
        'K': [0, 0, 0, 0, 0, 10, 20, 30],    # King
    }

    piece = self.board.piece_at(square)
    piece_type = piece.symbol().upper()

    if is_white:
        return position_values.get(piece_type, [0] * 8)[chess.square_rank(square)]
    else:
        # For black pieces, invert the position scoring
        return position_values.get(piece_type, [0] * 8)[7 - chess.square_rank(square)]