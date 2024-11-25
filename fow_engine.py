import chess
import sqlite3
from output_processor import OutputProcessor
####CURRENTLY AM TESTING THIS USING THE BUTTON IN THE GUI#######
################################################################
# FIX/REPLACE SCORING AND EVALUATION FUNCTIONS, FIGURE OUT HOW TO
###TEST GETTING MINIMAX TO GIVE US TOP K MOVES FOR OPPONENT, FIGURE OUT HOW TO PROPERLY REMOVE "GUESS" PIECES FROM OUR TRACKING TABLE WHEN THE ACTUAL PIECE IS VISIBLE
##IMPORT CAPTURED MATERIAL FROM GUI - FIX POSITION SCORING - VISUAL REPRESENTATION OF GUESSED POSITIONS -
###################################################################################################

class FoW_Engine1:
    def __init__(self, connection):#ADD UR STUFF HERE
        self.connection = sqlite3.connect("fogofwar.db")
        self.cursor = self.connection.cursor()

    def run_engine(self, biases_dictionary): # biases_dictionary needs to be implemented to file, but it is a dictionary based on the json that the LLM makes based on user_input
        """Main loop for the chess engine."""
        turn = 0
        self.board = chess.Board()
        self.board.clear()
        # step 1: read in visible table from front end, if it's the first move populate the table with all starting positions, track moves we made or can see
        # step 2: if it's after first move, calculate where opponent might have their pieces, ignore otherwise
        # step 3: update the piece table with lesser probability for all positions of top k opponent moves,update "known" positions prob
        # step 4: parse through all possible moves from the piece tracking table, testing depth only needs to be like 9 or so right now
        # step 5: decide on the move that produces the optimal scoring for the player, then print/send this move back to GUI
        # step 6: wait on some kind of signal from front end to reset this process, end game when front end tells us it's over




        self.initialize_visible_pieces()
        print("visible pieces initialized")

        self.evaluate_moves()
        print("moves evaluated")

        self.suggest_player_move()
        print("move suggested")




        # notes: our table cannot access the data from the game on where the opponents are if they aren't visible (duh)
        # this engine will not make moves or send any information back to the front end, other than a recommendation
        # it would be cool to visually represent where the engine is predicting the opponents pieces somehow, so we can compare how it's performing with reality

    def initialize_visible_pieces(self):
        """Initialize the visible pieces from the database."""
        initial_setup = [
            ('A', 1, '', '', False, 1.0),
            ('B', 1, '', '', False, 1.0),
            ('C', 1, '', '', False, 1.0),
            ('D', 1, '', '', False, 1.0),
            ('E', 1, '', '', False, 1.0),
            ('F', 1, '', '', False, 1.0),
            ('G', 1, '', '', False, 1.0),
            ('H', 1, '', '', False, 1.0),
            ('A', 2, '', '', False, 1.0),
            ('B', 2, '', '', False, 1.0),
            ('C', 2, '', '', False, 1.0),
            ('D', 2, '', '', False, 1.0),
            ('E', 2, '', '', False, 1.0),
            ('F', 2, '', '', False, 1.0),
            ('G', 2, '', '', False, 1.0),
            ('H', 2, '', '', False, 1.0),
            ('A', 3, '', '', False, 1.0),
            ('B', 3, '', '', False, 1.0),
            ('C', 3, '', '', False, 1.0),
            ('D', 3, '', '', False, 1.0),
            ('E', 3, '', '', False, 1.0),
            ('F', 3, '', '', False, 1.0),
            ('G', 3, '', '', False, 1.0),
            ('H', 3, '', '', False, 1.0),
            ('A', 4, '', '', False, 1.0),
            ('B', 4, '', '', False, 1.0),
            ('C', 4, '', '', False, 1.0),
            ('D', 4, '', '', False, 1.0),
            ('E', 4, '', '', False, 1.0),
            ('F', 4, '', '', False, 1.0),
            ('G', 4, '', '', False, 1.0),
            ('H', 4, '', '', False, 1.0),
            ('A', 5, '', '', False, 1.0),
            ('B', 5, '', '', False, 1.0),
            ('C', 5, '', '', False, 1.0),
            ('D', 5, '', '', False, 1.0),
            ('E', 5, '', '', False, 1.0),
            ('F', 5, '', '', False, 1.0),
            ('G', 5, '', '', False, 1.0),
            ('H', 5, '', '', False, 1.0),
            ('A', 6, '', '', False, 1.0),
            ('B', 6, '', '', False, 1.0),
            ('C', 6, '', '', False, 1.0),
            ('D', 6, '', '', False, 1.0),
            ('E', 6, '', '', False, 1.0),
            ('F', 6, '', '', False, 1.0),
            ('G', 6, '', '', False, 1.0),
            ('H', 6, '', '', False, 1.0),
            ('A', 7, 'B', 'p', False, 1.0),
            ('B', 7, 'B', 'p', False, 1.0),
            ('C', 7, 'B', 'p', False, 1.0),
            ('D', 7, 'B', 'p', False, 1.0),
            ('E', 7, 'B', 'p', False, 1.0),
            ('F', 7, 'B', 'p', False, 1.0),
            ('G', 7, 'B', 'p', False, 1.0),
            ('H', 7, 'B', 'p', False, 1.0),
            ('A', 8, 'B', 'r', False, 1.0),
            ('B', 8, 'B', 'n', False, 1.0),
            ('C', 8, 'B', 'b', False, 1.0),
            ('D', 8, 'B', 'q', False, 1.0),
            ('E', 8, 'B', 'k', False, 1.0),
            ('F', 8, 'B', 'b', False, 1.0),
            ('G', 8, 'B', 'n', False, 1.0),
            ('H', 8, 'B', 'r', False, 1.0)
        ]

        # Check if the table exists
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM sqlite_master
            WHERE type = 'table' AND name = 'FoW_chessboard';
        """)

        table_exists = self.cursor.fetchone()[0] > 0

        # If the table doesn't exist, create it and insert the initial setup
        if not table_exists:
            # Create table with unique constraint during creation
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS FoW_chessboard (
                    col CHAR(1),
                    rw INTEGER,
                    color CHAR(1),
                    piece CHAR(1),
                    visW INTEGER,  -- BOOLEAN substitute; use 0 and 1 for False and True
                    prob FLOAT,
                    UNIQUE(col, rw)  -- Unique constraint added here
                );
            """)
            self.connection.commit()

            # Insert the initial setup data into the table
            query = "INSERT INTO FoW_chessboard (col, rw, color, piece, visW, prob) VALUES (?, ?, ?, ?, ?, ?)"
            self.cursor.executemany(query, initial_setup)
            self.connection.commit()

            # Additional logic to repopulate visible pieces (if needed)
            # This part depends on how you want to initialize the board's pieces or update them during the game.
            self.cursor.execute("""
                INSERT OR REPLACE INTO FoW_chessboard (col, rw, color, piece, visW, prob)
                SELECT col, rw, color, piece, visW, 1.0
                FROM chessboard
                WHERE visW = 1;
            """)
            self.connection.commit()

        else:
            # If the table exists, just update the visible pieces
            self.cursor.execute("""
                INSERT OR REPLACE INTO FoW_chessboard (col, rw, color, piece, visW, prob)
                SELECT col, rw, color, piece, visW, 1.0
                FROM chessboard
                WHERE visW = 1;
            """)
            self.cursor.execute("""DELETE FROM FoW_chessboard WHERE rw = 7 AND piece = 'p' AND col IN ( SELECT col FROM FoW_chessboard WHERE rw < 7 AND piece = 'p' );""")
            self.connection.commit()
    
    def evaluate_moves(self):
        """Evaluate all possible moves for opponent pieces using minimax and update the visible_chessboard table."""
        # Fetch visible pieces
        self.cursor.execute("SELECT col, rw, color, piece, visW, prob FROM FoW_chessboard;")
        FoW_chessboard = self.cursor.fetchall()


        # Populate the board with visible pieces
        for col, rw, color, piece, vis, prob in FoW_chessboard:
            square = chess.square(ord(col) - ord('A'), rw - 1)
            if piece == '':
                self.board.remove_piece_at(square)

            if color == 'W':
                self.board.set_piece_at(square, chess.Piece.from_symbol(piece.upper()))
            elif color == 'B' :
                self.board.set_piece_at(square, chess.Piece.from_symbol(piece.lower()))
            else:
                continue
        print("board with visible pieces")
        print(self.board)
        move_evaluations = []
        # Evaluate moves for opponent pieces
        self.board.turn = chess.BLACK



        alpha = float('-inf')
        beta = float('inf')
        for move in self.board.legal_moves:
            self.board.push(move)
            score, first_move = self.TOP3minimax(1, alpha, beta, False, move)
            self.board.pop()
            move_evaluations.append((score, first_move))
            move_evaluations.sort(key=lambda x: x[0])
            print(move_evaluations)
            top_3_moves = move_evaluations[:3]
            print(top_3_moves)

        for score, move in top_3_moves:
            print(f"Move: {score}, Score: {move}")


            # Update probabilities for the current positions and insert new moves THIS WILL ALSO NEED A WAY TO REMOVE OUR "GUESS"
            # PIECES FROM THE DATASHEET IN THE EVENT THAT WE ACTUALLY SEE WHERE IT WAS MOVED TO: DO WE NEED TO ALTER PIECE TYPES FURTHER (BISHOP1, BISHOP2)
            # IS THERE A WAY TO LOG POSSIBLE MOVES A TRACE THEM BACK TO ITS VISIBLE POSITION?

            from_square = move.from_square
            to_square = move.to_square
            piece = self.board.piece_at(from_square)
            # Check if the target square is visible
            to_col = chr(chess.square_file(to_square) + ord('A'))
            to_row = chess.square_rank(to_square) + 1
            print(to_col, to_row)
            self.cursor.execute("SELECT visW FROM FoW_chessboard WHERE col = ? AND rw = ?;", (to_col, to_row))
            is_visible = self.cursor.fetchone()

            # If the move goes to a non-visible square, add it to the table
            if not is_visible or not is_visible[0]:
                self.cursor.execute("""INSERT OR IGNORE INTO FoW_chessboard (col, rw, color, piece, visW, prob) VALUES (?, ?, ?, ?, ?, 0.5) """, (to_col, to_row, 'B', piece.symbol(), 0))

                self.cursor.execute("""UPDATE FoW_chessboard SET prob = 0.5 WHERE col = ? AND rw = ? """, (to_col, to_row))
                self.connection.commit()
                # Update current position probability to 0.5: THIS SHOULD BE A VARIABLE PROBABILITY IN THE FUTURE
                from_col = chr(chess.square_file(from_square) + ord('A'))
                from_row = chess.square_rank(from_square) + 1
                self.cursor.execute("""UPDATE FoW_chessboard SET prob = 0.5 WHERE col = ? AND rw = ? """, (from_col, from_row))
                self.connection.commit()

                self.board.set_piece_at(to_square, piece)

        print("Moves evaluated and visible_chessboard updated with new probabilities.")
        print(self.board)


    def TOP3minimax(self, depth, alpha, beta, maximizing_player, first_move=None):
        if depth == 0 or not self.board.legal_moves:
            evaluation = self.evaluate_board()
            print(f"EVALUATION for {first_move}: {evaluation}")
            return evaluation, first_move

        if maximizing_player:
            self.board.turn = chess.WHITE
        else:
            self.board.turn = chess.BLACK

        moves = sorted(self.board.legal_moves, key=lambda move: self.heuristic_sort(self.board, move),
                       reverse=maximizing_player)

        best_move = None
        if maximizing_player:
            max_eval = float('-inf')
            for move in moves[:3]:
                self.board.push(move)
                print("MAX MOVE", move)
                eval, _ = self.TOP3minimax(depth - 1, alpha, beta, False, first_move or move)
                self.board.pop()
                if eval > max_eval:
                    max_eval = eval
                    best_move = first_move or move  # Track the first move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    print("beta prune")
                    break  # Beta cutoff
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in moves[:3]:
                self.board.push(move)
                print("MIN MOVE", move)
                eval, _ = self.TOP3minimax(depth - 1, alpha, beta, True, first_move or move)
                self.board.pop()
                if eval < min_eval:
                    min_eval = eval
                    best_move = first_move or move  # Track the first move
                beta = min(beta, eval)
                if beta <= alpha:
                    print("alpha prune")
                    break  # Alpha cutoff
            return min_eval, best_move

    def minimax(self, depth, maximizing_player):
        """Minimax algorithm to evaluate moves with scoring."""
        for move in self.board.legal_moves:
            if depth == 0:
                return self.evaluate_board()  # Evaluate the board state with updated scoring

            if maximizing_player:
                self.board.turn = chess.WHITE
                max_eval = float('-inf')

                self.board.push(move)
                eval = self.minimax(depth - 1, False)
                self.board.pop()
                max_eval = max(max_eval, eval)
                return max_eval
            else:
                self.board.turn = chess.BLACK
                min_eval = float('inf')

                self.board.push(move)
                eval = self.minimax(depth - 1, True)
                self.board.pop()
                min_eval = min(min_eval, eval)
                return min_eval


    def suggest_player_move(self):
        """Suggest a move to the player based on the minimax algorithm."""
        best_move = None
        best_value = float('-inf')
        self.board.turn = chess.WHITE

        for move in self.board.legal_moves:
            self.board.push(move)
            move_value = self.minimax(9, True)  # Adjust depth as necessary
            self.board.pop()

            if move_value > best_value:
                best_value = move_value
                best_move = move

        if best_move:
            col = chr(chess.square_file(best_move.from_square) + ord('A'))
            rw = chess.square_rank(best_move.from_square) + 1
            piece = self.board.piece_at(best_move.from_square).symbol()
            move_suggestion = f"Suggested Move: Move {piece} from {col}{rw} to {chr(chess.square_file(best_move.to_square) + ord('A'))}{chess.square_rank(best_move.to_square) + 1}."
            processor = OutputProcessor()
            chat_response = OutputProcessor.main(processor, move_suggestion)
            print(chat_response)
        else:
            print("I have no suggestions at the moment.")


    def heuristic_sort(self, board, move):
        """Evaluate the current board state based on piece value, position, and probability."""
        evaluation: float = 0.00
        self.board.push(move)
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                piece_value = self.get_piece_value(piece)
                position_score = self.get_position_score(square, piece.color)
                if piece.symbol().lower() == 'k':  # Penalize king moves in early/midgame
                        position_score -= 200

                # Retrieve probability score from the database
                col = chr(chess.square_file(square) + ord('A'))
                rw = chess.square_rank(square) + 1
                self.cursor.execute("SELECT prob FROM FoW_chessboard WHERE col = ? AND rw = ?;", (col, rw))
                probability_result = self.cursor.fetchone()
                probability_score = probability_result[0] if probability_result else 1.0  # Default to 1.0 if not found
                score = (piece_value + position_score) * probability_score
                if self.board.is_capture(move):
                    score * 2
                evaluation += score

        self.board.pop()
        return evaluation
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
                self.cursor.execute("SELECT prob FROM FoW_chessboard WHERE col = ? AND rw = ?;", (col, rw))
                probability_result = self.cursor.fetchone()
                probability_score = probability_result[0] if probability_result else 1.0  # Default to 1.0 if not found
                score = (piece_value + position_score) * probability_score

                evaluation += score

        return evaluation


    def get_piece_value(self, piece):
        """Return the value of a piece."""
        value = 0
        if piece == "P":
            value = 10
        if piece == "N":
            value = 30
        if piece == "B":
            value = 30
        if piece == "R":
            value = 50
        if piece == "Q":
            value = 90
        if piece == "K":
            value = 0
        if piece == "p":
            value = -10
        if piece == "n":
            value = -30
        if piece == "b":
            value = -30
        if piece == "r":
            value = -50
        if piece == "q":
            value = -90
        if piece == "k":
            value = 0

        return value

    def get_position_score(self, square, is_white):
        """Return a score based on the piece's position on the board."""
        file = chess.square_file(square)
        rank = chess.square_rank(square)
        piece = self.board.piece_at(square)
        piece_type = piece.symbol().upper()
        index = (7 - rank) * 8 + file
        position_values = {
            'P': ( 0,  0,  0,  0,  0,  0,  0,  0,
                   5, 10, 10, -5, -5, 10, 10,  5,
                   1,  5,  5, 10, 10,  5,  5,  1,
                   0,  0, 10, 20, 20, 10,  0,  0,
                   1,  1,  10, 25, 25,  10,  1,  1,
                   5,  5,  5,  5,  5,  5,  5,  5,
                  10, 10, 10, 10, 10, 10, 10, 10,
                   0,  0,  0,  0,  0,  0,  0,  0),
            'N': (-50, -40, -30, -30, -30, -30, -40, -50,
                  -40, -20,   0,   5,   5,   0, -20, -40,
                  -30,   5,  10,  15,  15,  10,   5, -30,
                  -30,  10,  15,  20,  20,  15,  10, -30,
                  -30,   5,  15,  20,  20,  15,   5, -30,
                  -30,  10,  10,  15,  15,  10,  10, -30,
                  -40, -20,   0,   5,   5,   0, -20, -40,
                  -50, -30, -30, -30, -30, -30, -30, -50),
            'B':    (-20, -10, -10, -10, -10, -10, -10, -20,
                      -10,   5,   0,   0,   0,   0,   5, -10,
                      -10,  10,  10,  10,  10,  10,  10, -10,
                      -10,   0,  10,  20,  20,  10,   0, -10,
                      -10,   5,  15,  20,  20,  15,   5, -10,
                      -10,  10,  10,  20,  20,  10,  10, -10,
                      -10,   5,   0,  10,  10,   0,   5, -10,
                      -20, -10, -10, -10, -10, -10, -10, -20),
            'R': ( 0,  0,  5, 10, 10,  5,  0,  0,
                   0,  0,  5, 10, 10,  5,  0,  0,
                   0,  0,  5, 10, 10,  5,  0,  0,
                   0,  0,  5, 10, 10,  5,  0,  0,
                   5, 10, 10, 10, 10, 10, 10,  5,
                  10, 15, 15, 15, 15, 15, 15, 10,
                  15, 20, 20, 20, 20, 20, 20, 15,
                   0,  0,  5, 10, 10,  5,  0,  0),
            'Q': (-20, -10, -10, -10, -10, -10, -10, -20,
                  -10,   0,   0,   5,   5,   0,   0, -10,
                  -10,   0,   5,   5,   5,   5,   0, -10,
                  -10,   0,   5,  10,  10,   5,   0, -10,
                  -10,   0,   5,  10,  10,   5,   0, -10,
                  -10,   5,   5,   5,   5,   5,   5, -10,
                  -10,   0,   5,   0,   0,   0,   0, -10,
                  -20, -10, -10, -10, -10, -10, -10, -20),
            'K': (-30, -40, -40, -50, -50, -40, -40, -30,
                  -30, -40, -40, -50, -50, -40, -40, -30,
                  -30, -40, -40, -50, -50, -40, -40, -30,
                  -30, -40, -40, -50, -50, -40, -40, -30,
                  -20, -30, -30, -40, -40, -30, -30, -20,
                  -10, -20, -20, -20, -20, -20, -20, -10,
                   20,  20,   -10,   -10,   -10,  -10,  20,  20,
                   20,  30,  10,   0,   0,  10,  30,  20),
                    }
        if not is_white:
            index = 63 - index
        position_values_piece = position_values.get(piece_type)
        ppv = position_values_piece[index]

        if is_white:
            return ppv
        else:
            return -ppv


        pass

