import chess
import sqlite3

class UpdateVisibility:
    def update_visibility_white(self, legal_moves):
        """Update the visibility of the squares. Loop through the table, if the square (rw, col) is not in legal_moves then visW=false."""
        self.cursor.execute("SELECT * FROM chessboard;")
        results = self.cursor.fetchall()
        
        # Create a list of legal moves in the form of squares (e.g., A1, B1, etc.)
        move_list = [chess.square_name(move.to_square).upper() for move in legal_moves]
        print(f"Legal moves for white: {move_list}")
        
        # Iterate over each row in the chessboard table
        for row in results:
            # Combine the column (col) and row (rw) to create the square identifier (e.g., A1, B1)
            square = row[0] + str(row[1])  # row[0] = col, row[1] = rw
            
            # Check if the square is a legal move
            if square in move_list:
                # Update visibility to true for legal moves
                self.cursor.execute("UPDATE chessboard SET visW = true WHERE col = ? AND rw = ?", (row[0], row[1]))
            else:
                # If the square is not in the move_list, it should not be visible to the white player
                # Skip updating if the square is white and avoid violating constraints
                if row[2] != 'W':  # Only update non-white pieces (color != 'W')
                    self.cursor.execute("UPDATE chessboard SET visW = false WHERE col = ? AND rw = ?", (row[0], row[1]))

        # Commit the updates after looping through all rows
        self.connection.commit()  # Explicit commit for SQLite
        print("Visibility for white player updated.")

    def update_visibility_black(self, legal_moves):
        """Update the visibility of the squares. Loop through the table, if the square (rw, col) is not in legal_moves then visB=false."""
        self.cursor.execute("SELECT * FROM chessboard;")
        results = self.cursor.fetchall()
        
        # Create a list of legal moves in the form of squares (e.g., A1, B1, etc.)
        move_list = [chess.square_name(move.to_square).upper() for move in legal_moves]
        print(f"Legal moves for black: {move_list}")
        
        # Iterate over each row in the chessboard table
        for row in results:
            # Combine the column (col) and row (rw) to create the square identifier (e.g., A1, B1)
            square = row[0] + str(row[1])  # row[0] = col, row[1] = rw
            
            # Check if the square is a legal move
            if square in move_list:
                # Update visibility to true for legal moves
                self.cursor.execute("UPDATE chessboard SET visB = true WHERE col = ? AND rw = ?", (row[0], row[1]))
            else:
                # If the square is not in the move_list, it should not be visible to the black player
                # Skip updating if the square is black and avoid violating constraints
                if row[2] != 'B':  # Only update non-black pieces (color != 'B')
                    self.cursor.execute("UPDATE chessboard SET visB = false WHERE col = ? AND rw = ?", (row[0], row[1]))

        # Commit the updates after looping through all rows
        self.connection.commit()  # Explicit commit for SQLite
        print("Visibility for black player updated.")
