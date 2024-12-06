-- Dropping tables in reverse order of dependency to ensure no foreign key violations                                 
DROP TABLE IF EXISTS professor;
DROP TABLE IF EXISTS plays;                              
DROP TABLE IF EXISTS user_;
DROP TABLE IF EXISTS round;
DROP TABLE IF EXISTS game;


-- user table
CREATE TABLE user_ (
    userID VARCHAR(50),                                          -- Unique userID (university ID), cannot be null
    email VARCHAR(100) NOT NULL,                                 -- Unique email address, cannot be null
    password VARCHAR(100) NOT NULL,                              -- Hashed password for secure login, cannot be null
    academic_year SMALLINT NOT NULL,                             -- Academic year of the user, cannot be null
    class CHAR(1) NOT NULL,                                      -- Represents the class of the user, such as 'A' or 'B', cannot be null
    timestamp_user TIMESTAMP DEFAULT CURRENT_TIMESTAMP,          -- Timestamp of account creation, defaults to the current time
    PRIMARY KEY(userID),                                         -- Set username as the primary key
    UNIQUE(email)                                                -- Enforce unique constraint on email
);

-- professor table
CREATE TABLE professor (
    userID VARCHAR(50),                                          -- Unique userID (university ID), cannot be null
    permission_level VARCHAR(20) NOT NULL,                       -- Permission level for the professor, cannot be null
    PRIMARY KEY(userID),                                         -- Set username as the primary key
    FOREIGN KEY(userID) REFERENCES user_(userID)                 -- Foreign key linking to the username in the user table
);

-- game table
CREATE TABLE game (
    game_id SERIAL,                                              -- Unique identifier for each game, auto-incremented, not null
    game_name VARCHAR(100) NOT NULL,                             -- Name of the game, cannot be null
    number_of_rounds SMALLINT NOT NULL,                          -- Number of rounds in the game, cannot be null
    num_inputs SMALLINT NOT NULL,                                -- Number of input boxes in the game, cannot be null
    timestamp_game TIMESTAMP DEFAULT CURRENT_TIMESTAMP,          -- Timestamp of game creation, defaults to the current time
    PRIMARY KEY(game_id)                                         -- Set game_id as the primary key
    -- Every game must exist in the table 'plays'
    -- Every game must exist in the table 'contains'
);

-- plays table
CREATE TABLE plays (
    userID VARCHAR(50),                                          -- Unique userID (university ID), cannot be null
    game_id SERIAL,                                              -- Unique identifier for each game, auto-incremented, not null
    PRIMARY KEY(userID, game_id),                                -- Set userID and game_id as a composite primary key
    FOREIGN KEY(userID) REFERENCES user_(userID),                -- Foreign key linking to the userID in the user table
    FOREIGN KEY(game_id) REFERENCES game(game_id)                -- Foreign key linking to the game_id in the game table
);

-- round table
CREATE TABLE round (
    game_id SERIAL,                                              -- Foreign key linking to the game_id in the game table
    round_number SMALLINT,                                       -- Number of the round in the game, cannot be null
    group1_id SMALLINT,                                          -- ID of the first group participating in the round, cannot be null
    group2_id SMALLINT,                                          -- ID of the second group participating in the round, cannot be null
    score_group1 INTEGER NOT NULL,                               -- Score of group 1 in a specific round, cannot be null
    score_group2 INTEGER NOT NULL,                               -- Score of group 2 in a specific round, cannot be null
    PRIMARY KEY(game_id, round_number, group1_id, group2_id),    -- Set game_id, round_number, group1_id, and group2_id as the composite primary keys
    FOREIGN KEY(game_id) REFERENCES game(game_id)                -- Foreign key linking to the game_id in the game table
);