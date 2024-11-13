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
        self.connection = mysql.connector.connect(host="localhost", user="root", password="maggie", database="fogofwar")

    def run_engine(self):
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
            ('A', 7, 'B', 'p', True, 1.0),
            ('B', 7, 'B', 'p', True, 1.0),
            ('C', 7, 'B', 'p', True, 1.0),
            ('D', 7, 'B', 'p', True, 1.0),
            ('E', 7, 'B', 'p', True, 1.0),
            ('F', 7, 'B', 'p', True, 1.0),
            ('G', 7, 'B', 'p', True, 1.0),
            ('H', 7, 'B', 'p', True, 1.0),
            ('A', 8, 'B', 'r', True, 1.0),
            ('B', 8, 'B', 'n', True, 1.0),
            ('C', 8, 'B', 'b', True, 1.0),
            ('D', 8, 'B', 'q', True, 1.0),
            ('E', 8, 'B', 'k', True, 1.0),
            ('F', 8, 'B', 'b', True, 1.0),
            ('G', 8, 'B', 'n', True, 1.0),
            ('H', 8, 'B', 'r', True, 1.0)
        ]
        #self.cursor.execute("TRUNCATE TABLE FoW_chessboard;")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS FoW_chessboard (col CHAR(1),rw INT,color CHAR(1),piece CHAR(1), visW BOOLEAN, prob FLOAT DEFAULT 1.0);""")

        # Repopulate the visible pieces table
        self.cursor.execute("""INSERT INTO FoW_chessboard (col, rw, color, piece, visW, prob) SELECT col, rw, color, piece, visW, 1.0 FROM chessboard WHERE visW = TRUE;""")

        query = "INSERT INTO FoW_chessboard (col, rw, color, piece, visW, prob) VALUES (%s, %s, %s, %s, %s, %s)"
        self.cursor.executemany(query, initial_setup)

        self.connection.commit()

    def evaluate_moves(self):
        """Evaluate all possible moves for opponent pieces using minimax and update the visible_chessboard table."""
        # Fetch visible pieces
        self.cursor.execute("SELECT col, rw, color, piece, visW, prob FROM FoW_chessboard;")
        FoW_chessboard = self.cursor.fetchall()


        # Populate the board with visible pieces
        for col, rw, color, piece, vis, prob in FoW_chessboard:
            square = chess.square(ord(col) - ord('A'), rw - 1)
            if not color:
                continue
            if color == 'W':
                self.board.set_piece_at(square, chess.Piece.from_symbol(piece.upper()))
            else:
                self.board.set_piece_at(square, chess.Piece.from_symbol(piece.lower()))
        print("board with visible pieces")
        print(self.board)
        top_scores = []
        top_moves = []
        # Evaluate moves for opponent pieces
        self.board.turn = chess.BLACK
        for move in self.board.legal_moves:
            print(move)


            #Evaluate moves using top3minimax
            print("Checking minimaxTOP3")
            score = float(self.TOP3minimax(3, False))
            top_scores.append(score)
            top_moves.append(move)
            move_score_pairs = list(zip(top_scores, top_moves))
            move_score_pairs.sort(key=lambda x: x[0], reverse=True)
            top_3_moves = move_score_pairs[:3]
            print(top_3_moves)
        for score, move in top_3_moves:
            print(f"Move: {move}, Score: {score}")


            # Update probabilities for the current positions and insert new moves THIS WILL ALSO NEED A WAY TO REMOVE OUR "GUESS"
            # PIECES FROM THE DATASHEET IN THE EVENT THAT WE ACTUALLY SEE WHERE IT WAS MOVED TO: DO WE NEED TO ALTER PIECE TYPES FURTHER (BISHOP1, BISHOP2)
            # IS THERE A WAY TO LOG POSSIBLE MOVES A TRACE THEM BACK TO ITS VISIBLE POSITION?

            from_square = move.from_square
            to_square = move.to_square
            piece = self.board.piece_at(from_square)
            # Check if the target square is visible
            to_col = chr(chess.square_file(to_square) + ord('A'))
            to_row = chess.square_rank(to_square) + 1
            self.cursor.execute("SELECT visW FROM FoW_chessboard WHERE col = %s AND rw = %s;", (to_col, to_row))
            is_visible = self.cursor.fetchone()

            # If the move goes to a non-visible square, add it to the table
            if not is_visible or not is_visible[0]:
                self.cursor.execute("""INSERT INTO FoW_chessboard (col, rw, color, piece, prob) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE prob = 0.5 """, (to_col, to_row, piece.color, piece.symbol().upper(), 0.5))

                # Update current position probability to 0.5: THIS SHOULD BE A VARIABLE PROBABILITY IN THE FUTURE
                from_col = chr(chess.square_file(from_square) + ord('A'))
                from_row = chess.square_rank(from_square) + 1
                self.cursor.execute("""UPDATE FoW_chessboard SET prob = 0.5 WHERE col = %s AND rw = %s """,(from_col, from_row))
                self.board.set_piece_at(to_square, piece)

        # Commit changes
        self.connection.commit()
        print("Moves evaluated and visible_chessboard updated with new probabilities.")
        print(self.board)

    def TOP3minimax(self, depth, maximizing_player):
        #TOP3minimax algorithm to evaluate moves for the minimizing player, returns best three moves for black to play
        ####THIS IS VERY MESSED UP RN
        top_score = float('inf')
        for move in self.board.legal_moves:
            if depth == 0:
                evaluation = self.evaluate_board()
                print(f"Depth {depth} evaluation: {evaluation}")
                min_eval = self.evaluate_board()
                return min_eval


            if not self.board.legal_moves:
                print(f"No legal moves, evaluating as draw at depth {depth}")
                return self.evaluate_board()

            if maximizing_player:
                self.board.turn = chess.WHITE
                #print("max player move")
                max_eval = float('-inf')

                print(move)
                print(depth)
                self.board.push(move)
                depth = depth-1
                eval = self.TOP3minimax(depth, False)
                self.board.pop()
                if isinstance(eval, float):
                    max_eval = max(max_eval, eval)
                else:
                    print(f"Warning: Expected a float evaluation, got {type(eval)}")
                    print(f"Maximizing Player - Depth {depth} max_eval: {max_eval}")
                return max_eval
            else:
                    #print("min player move")
                    self.board.turn = chess.BLACK
                    min_eval = float('inf')

                    print(move)
                    print(depth)
                    self.board.push(move)
                    depth = depth - 1
                    eval = self.TOP3minimax(depth, True)
                    self.board.pop()
                    min_eval = min(min_eval, eval)
                    if eval < min_eval:
                        min_eval = eval

                    #print(f"Min Player - Depth {depth} min_eval: {min_eval}")
                    return min_eval

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

                if self.cursor.nextset():
                    pass

                # Combine scores HERE
                score = (piece_value + position_score) * probability_score

                if piece.color:  # White pieces
                    evaluation += score

                else:  # Black pieces
                    evaluation -= score


        return evaluation


    def get_piece_value(self, piece):
        """Return the value of a piece."""
        value = 0
        if piece == "P":
            value = 1
        if piece == "N":
            value = 3
        if piece == "B":
            value = 3
        if piece == "R":
            value = 5
        if piece == "Q":
            value = 9
        if piece == "K":
            value = 1000
        if piece == "p":
            value = -1
        if piece == "n":
            value = -3
        if piece == "b":
            value = -3
        if piece == "r":
            value = -5
        if piece == "q":
            value = -9
        if piece == "k":
            value = -1000

        return value


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
