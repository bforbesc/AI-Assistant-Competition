-- Dropping tables in reverse order of dependency to ensure no foreign key violations
DROP TABLE IF EXISTS GameParameters;
DROP TABLE IF EXISTS GameRounds;
DROP TABLE IF EXISTS UserGames;
DROP TABLE IF EXISTS Game;
DROP TABLE IF EXISTS GameTypes;
DROP TABLE IF EXISTS Professors;
DROP TABLE IF EXISTS Leaderboard;
DROP TABLE IF EXISTS Users;


-- USERS TABLE
CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,                           -- Unique identifier for each user
    username VARCHAR(50) UNIQUE NOT NULL,                 -- Unique username, cannot be null
    email VARCHAR(100) UNIQUE NOT NULL,                   -- Unique email address, cannot be null
    password VARCHAR(255) NOT NULL,                       -- Hashed password for secure login
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP        -- Timestamp of account creation, defaults to current time
);

-- PROFESSORS TABLE
CREATE TABLE Professors (
    professor_id SERIAL PRIMARY KEY,                      -- Unique identifier for each professor
    user_id INTEGER UNIQUE NOT NULL REFERENCES Users(user_id),   -- Foreign key linking to the Users table
    password VARCHAR(255) NOT NULL,                       -- Hashed password for secure login
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP        -- Timestamp of professor account creation
);

-- GAME TYPES TABLE
CREATE TABLE GameTypes (
    game_type_id SERIAL PRIMARY KEY,                      -- Unique identifier for each game type
    game_type_name VARCHAR(50) UNIQUE NOT NULL,           -- Name of the game type (e.g., "Ultimatum Game", "Custom Game")
    description TEXT,                                     -- Description of the game type
    created_by INTEGER REFERENCES Professors(user_id),    -- User ID of professor who created the game type
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP        -- Timestamp of game type creation
);

-- GAME PARAMETERS TABLE
CREATE TABLE GameParameters (
    parameter_id SERIAL PRIMARY KEY,                      -- Unique identifier for each game parameter
    game_type_id INTEGER REFERENCES GameTypes(game_type_id),  -- Foreign key linking to the game type
    parameter_name VARCHAR(50) NOT NULL,                  -- Name of the parameter (e.g., "reward_cooperate")
    parameter_value VARCHAR(255),                         -- Value for the parameter, stored as text for flexibility
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP        -- Timestamp of parameter creation
);

-- GAME TABLE
CREATE TABLE Game (
    game_id SERIAL PRIMARY KEY,                           -- Unique identifier for each game
    game_type_id INTEGER NOT NULL REFERENCES GameTypes(game_type_id),  -- Link to specific game type
    player_1_id INTEGER NOT NULL REFERENCES Users(user_id),            -- Foreign key for Player 1
    player_2_id INTEGER NOT NULL REFERENCES Users(user_id),            -- Foreign key for Player 2
    player_1_choice VARCHAR(10),                          -- Choice made by Player 1 (e.g., "Cooperate")
    player_2_choice VARCHAR(10),                          -- Choice made by Player 2
    outcome VARCHAR(50),                                  -- Summary of game outcome (e.g., "Player 1 Wins")
    player_1_score NUMERIC,                               -- Final score for Player 1
    player_2_score NUMERIC,                               -- Final score for Player 2
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,       -- Timestamp of game creation
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP        -- Timestamp of last game update
);

-- LEADERBOARD TABLE
CREATE TABLE Leaderboard (
    leaderboard_id SERIAL PRIMARY KEY,                    -- Unique identifier for each leaderboard entry
    user_id INTEGER NOT NULL REFERENCES Users(user_id),   -- Foreign key linking to the user
    total_score NUMERIC DEFAULT 0,                        -- Total score accumulated by the user across games
    games_played INTEGER DEFAULT 0,                       -- Number of games played by the user
    ranking_criteria VARCHAR(50),                         -- Criteria used for ranking
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP      -- Timestamp of last leaderboard update
);

-- GAME ROUNDS TABLE
CREATE TABLE GameRounds (
    round_id SERIAL PRIMARY KEY,                          -- Unique identifier for each game round
    game_id INTEGER NOT NULL REFERENCES Game(game_id),    -- Foreign key linking to a specific game
    round_number INTEGER NOT NULL,                        -- Sequential number of the round within a game
    player_1_score NUMERIC DEFAULT 0,                     -- Score for Player 1 in this round
    player_2_score NUMERIC DEFAULT 0,                     -- Score for Player 2 in this round
    outcome VARCHAR(50),                                  -- Result of the round (e.g., "Both Cooperated")
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP        -- Timestamp of round creation
);

-- USER GAMES TABLE
CREATE TABLE UserGames (
    user_game_id SERIAL PRIMARY KEY,                      -- Unique identifier for each user-game relationship
    user_id INTEGER NOT NULL REFERENCES Users(user_id),   -- Foreign key linking to the user
    game_id INTEGER NOT NULL REFERENCES Game(game_id),    -- Foreign key linking to the game
    role VARCHAR(10),                                     -- Role of the user in the game (e.g., "Player 1" or "Player 2")
    final_score NUMERIC DEFAULT 0,                        -- Final score for this user in this specific game
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP        -- Timestamp of user-game entry creation
);
