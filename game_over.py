import tkinter as tk
from tkinter import messagebox
import sqlite3

class GameOver: 
    def __init__(self, root, cursor, connection, board):
        self.root = root
        self.board = board
        self.connection = connection
        self.cursor = cursor

    def quit_game(self):
        # Resets the SQLite table
        self.cursor.execute("DROP TABLE IF EXISTS chessboard")  # Safely drops the table if it exists
        print("Table chessboard has been dropped")
        self.connection.commit()
        self.cursor.execute("DROP TABLE IF EXISTS captured")  # Safely drops the table if it exists
        print("Table captured has been dropped")
        self.connection.commit()

        # Close the SQLite connection
        self.connection.close()
        print("SQLite connection closed")

        # Close the GUI window
        self.root.quit()
        print("Game ended")

    def check_game_over(self, is_white_turn):
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