USE fogofwar;

CREATE TABLE chessboard (
	col CHAR(1),
	rw INT,
    color char(1),
    piece CHAR(1),
	vis BOOLEAN
);

INSERT INTO chessboard(col,rw,color,piece,vis) 
VALUES
('A', 1, 'W', 'R', true),
('B', 1, 'W', 'N', true),
('C', 1, 'W', 'B', true),
('D', 1, 'W', 'Q', true),
('E', 1, 'W', 'K', true),
('F', 1, 'W', 'B', true),
('G', 1, 'W', 'N', true),
('H', 1, 'W', 'R', true),
('A', 2, 'W', 'P', true),
('B', 2, 'W', 'P', true),
('C', 2, 'W', 'P', true),
('D', 2, 'W', 'P', true),
('E', 2, 'W', 'P', true),
('F', 2, 'W', 'P', true),
('G', 2, 'W', 'P', true),
('H', 2, 'W', 'P', true),
('A', 3, '', '', true),
('B', 3, '', '', true),
('C', 3, '', '', true),
('D', 3, '', '', true),
('E', 3, '', '', true),
('F', 3, '', '', true),
('G', 3, '', '', true),
('H', 3, '', '', true),
('A', 4, '', '', true),
('B', 4, '', '', true),
('C', 4, '', '', true),
('D', 4, '', '', true),
('E', 4, '', '', true),
('F', 4, '', '', true),
('G', 4, '', '', true),
('H', 4, '', '', true),
('A', 5, '', '', true),
('B', 5, '', '', true),
('C', 5, '', '', true),
('D', 5, '', '', true),
('E', 5, '', '', true),
('F', 5, '', '', true),
('G', 5, '', '', true),
('H', 5, '', '', true),
('A', 6, '', '', true),
('B', 6, '', '', true),
('C', 6, '', '', true),
('D', 6, '', '', true),
('E', 6, '', '', true),
('F', 6, '', '', true),
('G', 6, '', '', true),
('H', 6, '', '', true),
('A', 7, 'B', 'P', true),
('B', 7, 'B', 'P', true),
('C', 7, 'B', 'P', true),
('D', 7, 'B', 'P', true),
('E', 7, 'B', 'P', true),
('F', 7, 'B', 'P', true),
('G', 7, 'B', 'P', true),
('H', 7, 'B', 'P', true),
('A', 8, 'B', 'R', true),
('B', 8, 'B', 'N', true),
('C', 8, 'B', 'B', true),
('D', 8, 'B', 'Q', true),
('E', 8, 'B', 'K', true),
('F', 8, 'B', 'B', true),
('G', 8, 'B', 'N', true),
('H', 8, 'B', 'R', true);

SELECT * FROM chessboard;

# UPDATE chess SET color = '', piece = '' WHERE col = %s AND rw = %s

# we would need to set the color system based on if it is player 1 or player 2's turn and make the %s go to CAP
# UPDATE chess SET color = '--based on player turn--', piece = %s.upper() WHERE col = %s AND rw = %s

# DROP TABLE chessboard










