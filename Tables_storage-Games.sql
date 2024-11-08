CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE Game (
    game_id SERIAL PRIMARY KEY,
    game_type VARCHAR(50) NOT NULL,
    player_1_id INTEGER NOT NULL REFERENCES Users(user_id),
    player_2_id INTEGER NOT NULL REFERENCES Users(user_id),
    offer NUMERIC,
    acceptance BOOLEAN,
    player_1_choice VARCHAR(10),
    player_2_choice VARCHAR(10),
    outcome VARCHAR(50),
    player_1_score NUMERIC,
    player_2_score NUMERIC,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Leaderboard (
    leaderboard_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES Users(user_id),
    total_score NUMERIC DEFAULT 0,   -- Total score accumulated across games
    games_played INTEGER DEFAULT 0,  -- Number of games played by the user
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE GameRounds (
    round_id SERIAL PRIMARY KEY,
    game_id INTEGER NOT NULL REFERENCES Game(game_id),  -- Links to a specific game
    round_number INTEGER NOT NULL,                      -- Round sequence number
    player_1_score NUMERIC DEFAULT 0,                   -- Score or earnings for Player 1 in this round
    player_2_score NUMERIC DEFAULT 0,                   -- Score or earnings for Player 2 in this round
    outcome VARCHAR(50),                                -- Result of the round (e.g., "Both Defected")
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE UserGames (
    user_game_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES Users(user_id),
    game_id INTEGER NOT NULL REFERENCES Game(game_id),
    role VARCHAR(10),               -- Role of the user in the game, e.g., "Player 1" or "Player 2"
    final_score NUMERIC DEFAULT 0,   -- Final score for this user in this game
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);







