-- Inserting Ricardo Almeida (for testing)
INSERT INTO user_ (userID, email, password, academic_year, class) 
VALUES ('nova199317', 'ricardo.almeida2210@gmail.com', '<hashed_password_for_ricardo>', 2024, 'A');

-- Inserting Rodrigo Belo
INSERT INTO user_ (userID, email, password, academic_year, class)
VALUES ('nova199032', 'rodrigo.belo@novasbe.pt', '<hashed_password_for_rodrigo>', 2008, 'B');

-- Inserting Lénia Mestrinho
INSERT INTO user_ (userID, email, password, academic_year, class)
VALUES ('nova196331', 'lenia.mestrinho@novasbe.pt', '<hashed_password_for_lenia>', 2000, 'A');

-- Inserting Ricardo Almeida into professor's table (for testing)
INSERT INTO professor (userID, permission_level) 
VALUES ('nova199317', 'regular');

-- Inserting Rodrigo Belo into professor's table
INSERT INTO professor (userID, permission_level) 
VALUES ('nova199032', 'master');

-- Inserting Lénia Mestrinho into professor's table
INSERT INTO professor (userID, permission_level) 
VALUES ('nova196331', 'regular');