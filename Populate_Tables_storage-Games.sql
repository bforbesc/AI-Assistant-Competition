-- Inserting Ricardo Almeida (for testing)
INSERT INTO Users (username, email, password) 
VALUES ('Ricardo Almeida', 'ricardo.almeida2210@gmail.com', '<hashed_password_for_ricardo>')
RETURNING user_id;

-- Inserting Rodrigo Belo
INSERT INTO Users (username, email, password) 
VALUES ('Rodrigo Belo', 'rodrigo.belo@novasbe.pt', '<hashed_password_for_rodrigo>')
RETURNING user_id;

-- Inserting Lénia Mestrinho
INSERT INTO Users (username, email, password) 
VALUES ('Lénia Mestrinho', 'lenia.mestrinho@novasbe.pt', '<hashed_password_for_lenia>')
RETURNING user_id;

-- Inserting Ricardo Almeida into Professors table (for testing)
INSERT INTO Professors (user_id, password) 
VALUES (1, '<hashed_password_for_ricardo>');

-- Inserting Rodrigo Belo into Professors table
INSERT INTO Professors (user_id, password) 
VALUES (2, '<hashed_password_for_rodrigo>');

-- Inserting Lénia Mestrinho into Professors table
INSERT INTO Professors (user_id, password) 
VALUES (3, '<hashed_password_for_lenia>');