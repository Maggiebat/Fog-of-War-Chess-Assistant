USE fogofwar;
-- This chessboard is for player 1's perspective not for the board as a whole
CREATE TABLE chessboard (
	col CHAR(1),
	rw INT,
    color char(1),
    piece CHAR(1),
	visW BOOLEAN,
	visB BOOLEAN
);

INSERT INTO chessboard(col, rw, color, piece, visW, visB) 
VALUES
('A', 1, 'W', 'R', true, true),
('B', 1, 'W', 'N', true, true),
('C', 1, 'W', 'B', true, true),
('D', 1, 'W', 'Q', true, true),
('E', 1, 'W', 'K', true, true),
('F', 1, 'W', 'B', true, true),
('G', 1, 'W', 'N', true, true),
('H', 1, 'W', 'R', true, true),
('A', 2, 'W', 'P', true, true),
('B', 2, 'W', 'P', true, true),
('C', 2, 'W', 'P', true, true),
('D', 2, 'W', 'P', true, true),
('E', 2, 'W', 'P', true, true),
('F', 2, 'W', 'P', true, true),
('G', 2, 'W', 'P', true, true),
('H', 2, 'W', 'P', true, true),
('A', 3, '', '', true, true),
('B', 3, '', '', true, true),
('C', 3, '', '', true, true),
('D', 3, '', '', true, true),
('E', 3, '', '', true, true),
('F', 3, '', '', true, true),
('G', 3, '', '', true, true),
('H', 3, '', '', true, true),
('A', 4, '', '', true, true),
('B', 4, '', '', true, true),
('C', 4, '', '', true, true),
('D', 4, '', '', true, true),
('E', 4, '', '', true, true),
('F', 4, '', '', true, true),
('G', 4, '', '', true, true),
('H', 4, '', '', true, true),
('A', 5, '', '', true, true),
('B', 5, '', '', true, true),
('C', 5, '', '', true, true),
('D', 5, '', '', true, true),
('E', 5, '', '', true, true),
('F', 5, '', '', true, true),
('G', 5, '', '', true, true),
('H', 5, '', '', true, true),
('A', 6, '', '', true, true),
('B', 6, '', '', true, true),
('C', 6, '', '', true, true),
('D', 6, '', '', true, true),
('E', 6, '', '', true, true),
('F', 6, '', '', true, true),
('G', 6, '', '', true, true),
('H', 6, '', '', true, true),
('A', 7, 'B', 'p', true, true),
('B', 7, 'B', 'p', true, true),
('C', 7, 'B', 'p', true, true),
('D', 7, 'B', 'p', true, true),
('E', 7, 'B', 'p', true, true),
('F', 7, 'B', 'p', true, true),
('G', 7, 'B', 'p', true, true),
('H', 7, 'B', 'p', true, true),
('A', 8, 'B', 'r', true, true),
('B', 8, 'B', 'n', true, true),
('C', 8, 'B', 'b', true, true),
('D', 8, 'B', 'q', true, true),
('E', 8, 'B', 'k', true, true),
('F', 8, 'B', 'b', true, true),
('G', 8, 'B', 'n', true, true),
('H', 8, 'B', 'r', true, true);

-- fow aspect so that if color of piece = 'W' then the visibility cannot be set to false (it will always be visible)
ALTER TABLE chessboard
ADD CONSTRAINT chk_color_visW
CHECK (NOT(color = 'W' AND visW = false));

ALTER TABLE chessboard ADD CONSTRAINT chk_color_visB CHECK (NOT(color = 'B' AND visB = false));

CREATE TABLE IF NOT EXISTS FoW_chessboard (col CHAR(1),rw INT,color CHAR(1),piece CHAR(1), vis BOOLEAN, prob FLOAT DEFAULT 1.0);









