import chess
import mysql.connector
####CURRENTLY AM TESTING THIS USING THE BUTTON IN THE GUI#######
################################################################
# FIX/REPLACE SCORING AND EVALUATION FUNCTIONS, FIGURE OUT HOW TO
###TEST GETTING MINIMAX TO GIVE US TOP K MOVES FOR OPPONENT, FIGURE OUT HOW TO PROPERLY REMOVE "GUESS" PIECES FROM OUR TRACKING TABLE WHEN THE ACTUAL PIECE IS VISIBLE
##IMPORT CAPTURED MATERIAL FROM GUI - FIX POSITION SCORING - VISUAL REPRESENTATION OF GUESSED POSITIONS -
###################################################################################################

class FoW_Engine1:


    def __init__(self, connection):#ADD UR STUFF HERE
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.connection = mysql.connector.connect(host="localhost", user="root", password="Kade", database="fogofwar")



    def run_engine(self):
        """Main loop for the chess engine."""
        move = 0
        self.board = chess.Board()
        print("Board initialized")
        # step 1: read in visible table from front end, if it's the first move populate the table with all starting positions, track moves we made or can see

        self.initialize_visible_pieces()
        print("visible pieces initialized")

        #while True:
        #if self.check_game_over():
        #break

        # step 1: read in visible table from front end, if it's the first move populate the table with all starting positions, track moves we made or can see
        self.update_pieces_table()
        print("pieces table updated")
        # step 2: if it's after first move, calculate where opponent might have their pieces, ignore otherwise
        if move > 0:
            self.evaluate_moves()
            print("moves evaluated")
        # step 3: update the piece table with lesser probability for all positions of top k opponent moves,update "known" positions prob
        # step 4: parse through all possible moves from the piece tracking table, testing depth only needs to be like 9 or so right now
        # step 5: decide on the move that produces the optimal scoring for the player, then print/send this move back to GUI
            self.suggest_player_move()
            print("move suggested")
        # step 6: wait on some kind of signal from front end to reset this process, end game when front end tells us it's over

             # notes: our table cannot access the data from the game on where the opponents are if they arent visible (duh)
            # this engine will not make moves or send any information back to the front end, other than a reccomendation
            # it would be cool to visually represent where the engine is predicting the opponents pieces somehow, so we can compare how it's performing with reality
        else:
            print("first move dummy")




    def initialize_visible_pieces(self):
        """Initialize the visible pieces from the database."""
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS FoW_chessboard (col CHAR(1),rw INT,color CHAR(1),piece CHAR(1), prob FLOAT);""")
        # Clear existing visible pieces
        self.cursor.execute("TRUNCATE TABLE FoW_chessboard;")

        # Fetch visible pieces from the existing chessboard
        self.cursor.execute("SELECT col, rw, color, piece FROM chessboard WHERE vis = TRUE;")
        visible_pieces = self.cursor.fetchall()


        # Repopulate the visible pieces table
        self.cursor.execute("""
            INSERT INTO FoW_chessboard (col, rw, color, piece, prob)
            SELECT col, rw, color, piece, NULL FROM chessboard WHERE vis = TRUE;
        """)
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
        # FINISH THIS


    def update_pieces_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS FoW_chessboard (col CHAR(1),rw INT,color CHAR(1),piece CHAR(1), prob FLOAT);""")

        # Fetch visible pieces from the existing chessboard
        self.cursor.execute("SELECT col, rw, color, piece FROM chessboard WHERE vis = TRUE;")
        visible_pieces = self.cursor.fetchall()
        print("c1")
        # Prepare data for insert
        for col, rw, color, piece in visible_pieces:
            # Check if the piece already exists
            self.cursor.execute("SELECT EXISTS(SELECT 1 FROM FoW_chessboard WHERE col = %s AND rw = %s);", (col, rw))
            exists = self.cursor.fetchone()[0]
            print("c2")
            if exists:
                # Update the existing piece
                self.cursor.execute("""UPDATE FoW_chessboard SET color = %s, piece = %s, prob = %s WHERE col = %s AND rw = %s""", (color, piece, 1.0, col, rw))
                print("c3")
            else:
                # Insert a new piece
                self.cursor.execute("""INSERT INTO FoW_chessboard (col, rw, color, piece, prob) VALUES (%s, %s, %s, %s, %s)""", (col, rw, color, piece, 1.0))
                print("c4")
        # Commit the changes
        self.connection.commit()


    def evaluate_moves(self):
        """Evaluate all possible moves for opponent pieces using minimax and update the visible_chessboard table."""
        # Fetch visible pieces
        self.cursor.execute("SELECT col, rw, color, piece FROM chessboard;")
        FoW_chessboard = self.cursor.fetchall()

        # Create a chess board object to evaluate moves
        board = chess.Board()

        # Populate the board with visible pieces
        for col, rw, color, piece in FoW_chessboard:
            square = chess.square(ord(col) - ord('A'), rw - 1)
            if color == 'W':
                board.set_piece_at(square, chess.Piece.from_symbol(piece.lower()))
            else:
                board.set_piece_at(square, chess.Piece.from_symbol(piece.upper()))

        player_color = chess.WHITE
        opponent_color = chess.BLACK
        top_moves = []

        # Evaluate moves for opponent pieces
        for move in board.legal_moves:
            from_square = move.from_square
            piece = board.piece_at(from_square)

            #Evaluate moves using top3minimax
            top_moves = self.TOP3minimax(9, player_color)


        # Update probabilities for the current positions and insert new moves THIS WILL ALSO NEED A WAY TO REMOVE OUR "GUESS"
        # PIECES FROM THE DATASHEET IN THE EVENT THAT WE ACTUALLY SEE WHERE IT WAS MOVED TO: DO WE NEED TO ALTER PIECE TYPES FURTHER (BISHOP1, BISHOP2)
        # IS THERE A WAY TO LOG POSSIBLE MOVES A TRACE THEM BACK TO ITS VISIBLE POSITION?
        for move, score in top_moves:
            from_square = move.from_square
            to_square = move.to_square

            # Check if the target square is visible
            to_col = chr(chess.square_file(to_square) + ord('A'))
            to_row = chess.square_rank(to_square) + 1
            self.cursor.execute("SELECT vis FROM chessboard WHERE col = %s AND rw = %s;", (to_col, to_row))
            is_visible = self.cursor.fetchone()

            # If the move goes to a non-visible square, add it to the table
            if not is_visible or not is_visible[0]:
                self.cursor.execute("""INSERT INTO FoW_chessboard (col, rw, color, piece, probability) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE probability = 0.5 """, (to_col, to_row, piece.color, piece.symbol().upper(), 0.5))

                # Update current position probability to 0.5: THIS SHOULD BE A VARIABLE PROBABILITY IN THE FUTURE
                from_col = chr(chess.square_file(from_square) + ord('A'))
                from_row = chess.square_rank(from_square) + 1
                self.cursor.execute("""UPDATE FoW_chessboard SET probability = 0.5 WHERE col = %s AND rw = %s """,
                                    (from_col, from_row))
        # Commit changes
        self.connection.commit()
        print("Moves evaluated and visible_chessboard updated with new probabilities.")

    def TOP3minimax(self, depth, maximizing_player):
        #TOP3minimax algorithm to evaluate moves for the minimizing player, returns best three moves for black to play
        ####THIS IS VERY MESSED UP RN
            if depth == 0:
                evaluation = self.evaluate_board()  # Evaluate the board state
                print(f"Depth {depth} evaluation: {evaluation}")  # Debugging line
                return evaluation

            if maximizing_player:
                max_eval = float('-inf')
                for move in self.board.legal_moves:
                    self.board.push(move)
                    eval = self.TOP3minimax(depth - 1, False)  # Call for minimizing player
                    self.board.pop()
                    if isinstance(eval, float):
                        max_eval = max(max_eval, eval)
                    else:
                        print(f"Warning: Expected a float evaluation, got {type(eval)}")
                    print(f"Maximizing Player - Depth {depth} max_eval: {max_eval}")
                return max_eval
            else:
                    min_eval = float('inf')
                    for move in self.board.legal_moves:
                        self.board.push(move)
                        eval = self.minimax(depth - 1, True)
                        self.board.pop()
                        min_eval = min(min_eval, eval)
                    return min_eval

                #return top_moves
    def minimax(self, depth, maximizing_player):
        """Minimax algorithm to evaluate moves with scoring."""
        if depth == 0:
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
        evaluation: float = 0.00
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                piece_value = self.get_piece_value(piece)
                position_score = self.get_position_score(square, piece.color)

                # Retrieve probability score from the database
                col = chr(chess.square_file(square) + ord('A'))
                rw = chess.square_rank(square) + 1
                self.cursor.execute("SELECT prob FROM FoW_chessboard WHERE col = %s AND rw = %s;", (col, rw))
                probability_result = self.cursor.fetchone()
                probability_score = probability_result[0] if probability_result else 1.0  # Default to 1.0 if not found

                # Combine scores HERE
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
            'K': [0, 0, 0, 0, 0, 10, 20, 30],  # King
        }

        piece = self.board.piece_at(square)
        piece_type = piece.symbol().upper()

        if is_white:
            return position_values.get(piece_type, [0] * 8)[chess.square_rank(square)]
        else:
            # For black pieces, invert the position scoring
            return position_values.get(piece_type, [0] * 8)[7 - chess.square_rank(square)]


        pass
