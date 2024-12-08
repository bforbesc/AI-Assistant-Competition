----------------------------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------- INSERT USERS ----------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------

-- Inserting Ricardo Almeida (for testing)
INSERT INTO user_ (userID, email, password, academic_year, class) 
VALUES ('nova199317', 'ricardo.almeida2210@gmail.com', '<hashed_password_for_ricardo>', 2024, 'A');

-- Inserting Carolina Paiva (for testing)
INSERT INTO user_ (userID, email, password, academic_year, class) 
VALUES ('nova199318', 'carolinapaivafifi@gmail.com', '<hashed_password_for_carolina>', 2024, 'A');

-- Inserting António Almeida (for testing)
INSERT INTO user_ (userID, email, password, academic_year, class) 
VALUES ('nova199319', 'antonio.c.almeida@tecnico.ulisboa.pt', '<hashed_password_for_antonio>', 2024, 'A');

-- Inserting Martim Penim (for testing)
INSERT INTO user_ (userID, email, password, academic_year, class) 
VALUES ('nova199320', 'martim.penim@tecnico.ulisboa.pt', '<hashed_password_for_martim>', 2024, 'A');

-- Inserting Rodrigo Belo
INSERT INTO user_ (userID, email, password, academic_year, class)
VALUES ('nova199032', 'rodrigo.belo@novasbe.pt', '<hashed_password_for_rodrigo>', 2008, 'B');

-- Inserting Lénia Mestrinho
INSERT INTO user_ (userID, email, password, academic_year, class)
VALUES ('nova196331', 'lenia.mestrinho@novasbe.pt', '<hashed_password_for_lenia>', 2000, 'A');

----------------------------------------------------------------------------------------------------------------------------------------------
---------------------------------------------- INSERT PROFESSORS -----------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------

-- Inserting Ricardo Almeida into professor's table (for testing)
INSERT INTO professor (userID, permission_level) 
VALUES ('nova199317', 'regular');

-- Inserting Carolina Paiva into professor's table (for testing)
INSERT INTO professor (userID, permission_level)
VALUES ('nova199318', 'regular');

-- Inserting António Almeida into professor's table (for testing)
INSERT INTO professor (userID, permission_level)
VALUES ('nova199319', 'regular');

-- Inserting Martim Penim into professor's table (for testing)
INSERT INTO professor (userID, permission_level) 
VALUES ('nova199320', 'regular');

-- Inserting Rodrigo Belo into professor's table
INSERT INTO professor (userID, permission_level) 
VALUES ('nova199032', 'master');

-- Inserting Lénia Mestrinho into professor's table
INSERT INTO professor (userID, permission_level) 
VALUES ('nova196331', 'regular');