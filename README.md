# AI Assistant Competition 

Welcome to the AI Assistant Competition platform—a learning environment where students design, train, and deploy AI negotiators to compete in classical negotiation challenges (e.g., Ultimatum Game, Prisoner’s Dilemma). This document serves both as a quickstart for participants and a detailed guide for developers and contributors. 

This App was developed to create a platform for students to create and train their own AI assistants (bots) to compete in various negotiation challenges. The project is part of the course "AI Impact on Business" at Nova SBE, and its initial focus is on negotiation games, such as variations of the Ultimatum Game or the Prisoner's Dilemma. The platform offers a user-friendly interface that enables students to design, train, and test their Assistants, along with a leaderboard to track their performance.

---

## Table of Contents
1. [Overview](#overview)  
2. [Participant Guide](#participant-guide)  
   - [1. Create an Account](#1-create-an-account)  
   - [2. Dashboard Tour](#2-dashboard-tour)  
   - [3. Building a Bot](#3-building-a-bot)  
   - [4. Submitting Your Bot](#4-submitting-your-bot)  
   - [5. Running in the Playground](#5-running-in-the-playground)  
   - [6. Viewing Results & Leaderboard](#6-viewing-results--leaderboard)  
3. [Developer & Contributor Guide](#developer--contributor-guide)  
   - [Prerequisites](#prerequisites)  
   - [Local Setup](#local-setup)  
   - [Database Initialization](#database-initialization)  
   - [Running the App](#running-the-app)  
   - [Project Structure](#project-structure)  
   - [Testing](#testing)  
   - [Contributing](#contributing)  
4. [Roadmap & Feedback](#roadmap--feedback)  
5. [References](#references)

---

## Overview
This platform empowers students to explore negotiation strategies by coding AI agents and evaluating them in structured games. Key features:

- **Multi-agent negotiation**: Host head‑to‑head matches across diverse game templates.
- **Training & evaluation**: Iteratively refine your bot in a sandbox environment.
- **Leaderboard & analytics**: Track performance metrics across rounds and semesters.
- **Extensible architecture**: Plug in new games, roles, and scoring rules.

---

## Participant Guide

### 1. Create an Account
1. Navigate to the registration page (`/register`).  
2. Provide your university ID, institutional email, and a secure password.  
3. Verify your account via the confirmation link sent to your email.

### 2. Dashboard Tour
On login, you’ll see:

- **My Bots**: List of bots you’ve built, status (Draft, Submitted, Tested).  
- **Create New Bot**: Wizard to define a Python-based negotiation agent.  
- **Competitions**: Upcoming tournaments and open submission windows.  
- **Leaderboard**: Live rankings for each game and overall performance.

### 3. Building a Bot
1. Click **Create New Bot**.  
2. Select a game template (e.g., Ultimatum, Prisoner’s Dilemma).  
3. Provide your bot’s source folder or zip file following our [bot template API specification](/docs/bot_spec.md).  
4. Upload and name your bot. It appears under **My Bots** with status **Draft**.

### 4. Submitting Your Bot
1. In **My Bots**, select the bot and choose **Submit to Competition**.  
2. Pick the target game and confirm submission before the deadline.  
3. After submission, your bot’s status changes to **Pending**. You’ll be notified when matches complete.

### 5. Running in the Playground
Before official submission, test your bot:

- Go to **Playground**.  
- Choose any registered bot (yours or public samples).  
- Run a quick match and inspect detailed dialogue logs and analytics (e.g., offers made, acceptance rates).

### 6. Viewing Results & Leaderboard
After each tournament, visit **Leaderboard** to see:
- Rank, win rate, average score per role.  
- Detailed match history and conversation transcripts.

---

## Developer & Contributor Guide

### Prerequisites
- **Python 3.10+**  
- **PostgreSQL 13+** (or MySQL as an alternative)  
- **Node.js & npm** (for any front‑end build tasks)  
- **Streamlit** (UI framework)  
- **Autogen** (Microsoft multi-agent toolkit)

### Local Setup
1. **Clone the repo**:
   ```bash
   git clone https://github.com/your-org/ai-assistant-competition.git
   cd ai-assistant-competition

2. **Create and activate a virtual environment**
- For Windowns:
        python -m venv .venv
     .\.venv\Scripts\activate
- For macOS/Linux
       python3 -m venv .venv
  source .venv/bin/activate

3. **Install dependencies**
pip install --upgrade pip
pip install -r requirements.txt

4. **Configure environment variables**
- Copy the example file and update credentials:

cp .env.example .env

Edit .env to set:

DATABASE_URL=postgres://USER:PASSWORD@localhost:5432/ai_competition
SECRET_KEY=your_secret_key_here

## Database Initialization

Initialize your database schema and optional seed data:

psql $DATABASE_URL -f db/schema.sql
psql $DATABASE_URL -f db/seeds.sql   # (optional) load test users & sample games

## Running the App

streamlit run app/main.py

## Project Structure

ai-assistant-competition/
├── app/
│   ├── main.py          # Streamlit entrypoint
│   ├── agents/          # Bot interface and templates
│   ├── db/              # Schema and seed scripts
│   ├── services/        # Game orchestration & scoring logic
│   ├── utils/           # Helpers (authentication, validation)
│   └── ui/              # Shared UI components
├── tests/               # Unit tests suite
├── requirements.txt     # Python dependencies
├── db/
│   ├── schema.sql       # DDL definitions
│   └── seeds.sql        # Sample data
└── README.md            # Project overview & guides

## Testing

1. Ensure your virtual environment is active.
2. Run all unit tests and view coverage:
pytest --cov=app

## Contributing

We welcome pull requests! Please follow these steps:

1. Fork the repository.

2. Create a feature branch:

git checkout -b feature/my-new-feature

3. Write code & tests, adhering to PEP8 style and adding unit tests.

4. Run tests locally: pytest.

5. Submit a Pull Request, describing your changes and linking to any issue.

Refer to CONTRIBUTING.md for detailed guidelines.


Happy negotiating! 