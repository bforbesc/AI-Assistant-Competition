# Developer Guide

This guide provides detailed information for developers and contributors to the AI Assistant Competition platform.

> **Note:** This guide assumes you have already set up your development environment as described in the [README.md](../README.md).

## Quick Links
- GitHub Repository: [https://github.com/rbelo/AI-Assistant-Competition](https://github.com/rbelo/AI-Assistant-Competition)
- Live Application: [https://ai-assistant-competition.streamlit.app/](https://ai-assistant-competition.streamlit.app/)

---

## Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Development Environment](#2-development-environment)
3. [Project Structure](#3-project-structure)
4. [Database Setup](#4-database-setup)
5. [Running the Application](#5-running-the-application)
6. [Testing & Quality Assurance](#6-testing--quality-assurance)
7. [Contributing](#7-contributing)

---

## 1. Prerequisites

- Python 3.11 (required, as specified in devcontainer)
- PostgreSQL 13+
- Node.js & npm
- Git
- Docker (optional, but recommended for consistent development environment)

### 1.1 Key Dependencies
The project requires several key Python packages:
- Streamlit 1.32.0+ (for the web interface)
- Psycopg2-binary (for PostgreSQL connection)
- PyJWT (for authentication)
- Streamlit-AgGrid (for data grid display)
- AutoGen (for agent automation)
- OpenAI (for AI model integration)
- Flask (for web services)
- Google API Client & Auth (for Google Drive integration)
- Pandas (for data manipulation)
- Matplotlib (for data visualization)
- Pytest (for testing)

A complete list of dependencies can be found in `streamlit/requirements.txt`.

---

## 2. Development Environment

The project provides multiple ways to set up your development environment:

- Using `environment.yml` for Conda environments
- Using `requirements.txt` for pip installations
- Using `.devcontainer` for VS Code development containers

Choose the method that best suits your workflow. All necessary dependencies and configurations are included in these files.

---

## 3. Project Structure

```
ai-assistant-competition/
├── streamlit/              # Main application code
│   ├── 0_Home.py          # Streamlit entrypoint
│   ├── modules/           # Core functionality modules
│   ├── pages/            # Streamlit pages
│   ├── .streamlit/       # Streamlit configuration
│   ├── requirements.txt   # Python dependencies
│   └── environment.yml    # Conda environment configuration
├── tests/                 # Test suite
├── documentation/         # User and developer guides
├── E-R_Model/            # Database entity-relationship models
├── .devcontainer/        # Development container configuration
├── Tables_AI_Negotiator.sql           # Database schema
├── Populate_Tables_AI_Negotiator.sql  # Sample data
└── README.md             # Project overview
```

---

## 4. Database Setup

### 4.1 Database Schema

The database consists of the following main tables:

- `users`: Stores user accounts and authentication information
- `bots`: Contains bot definitions and metadata
- `games`: Records game instances and configurations
- `matches`: Stores match results and outcomes
- `leaderboard`: Maintains performance metrics and rankings

For the complete schema definition, see `Tables_AI_Negotiator.sql`.

### 4.2 Initial Setup

1. Create Database:
   ```bash
   createdb ai_assistant_competition
   ```

2. Initialize Schema:
   ```bash
   psql -d ai_assistant_competition -f Tables_AI_Negotiator.sql
   ```

3. Load Sample Data (Optional):
   ```bash
   psql -d ai_assistant_competition -f Populate_Tables_AI_Negotiator.sql
   ```

4. Configure Connection:
   - Edit `streamlit/.streamlit/secrets.toml`:
     ```toml
     database = "postgresql://localhost/ai_assistant_competition"
     ```
   - Test connection:
     ```bash
     psql -d ai_assistant_competition -c "SELECT 'Connection successful' AS status;"
     ```

### 4.3 Data Management

1. User Management:
   ```bash
   python add_user_interactive.py
   ```

2. Viewing Data:
   ```bash
   # Connect to database
   psql -d ai_assistant_competition

   # List tables
   \dt

   # View users
   SELECT * FROM users;

   # View bots
   SELECT * FROM bots;

   # View matches
   SELECT * FROM matches;
   ```

### 4.4 Backup & Recovery

1. Create Backup:
   ```bash
   pg_dump ai_assistant_competition > backup.sql
   ```

2. Restore from Backup:
   ```bash
   psql -d ai_assistant_competition < backup.sql
   ```

---

## 5. Running the Application

### 5.1 Development Mode
```bash
# Navigate to the streamlit directory and run the app
cd AI-Assistant-Competition/streamlit && streamlit run 0_Home.py
```

The application will be available at `http://localhost:8501`.

> **Note:** It's important to run the app from the streamlit directory to ensure proper access to the secrets.toml file located in the .streamlit directory.

### 5.2 Production Mode
```bash
# Build the application
streamlit build

# Run with production settings
streamlit run streamlit/0_Home.py --server.port=8501 --server.address=0.0.0.0
```

---

## 6. Testing & Quality Assurance

### 6.1 Running Tests

The project uses pytest for testing. To run the tests:

```bash
# Set PYTHONPATH to include project root (required for imports to work)
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run specific test file
pytest tests/unit_tests.py

# Run specific test function
pytest tests/unit_tests.py::test_database_connection
```

> **Note:** Setting PYTHONPATH is required because the tests need to import modules from the `streamlit` directory. The test file automatically adds the project root to the Python path, but it's good practice to set it in your environment as well.

### 6.2 Test Categories

The test suite includes tests for:

1. **Authentication**
   - User login validation
   - Session management
   - Role verification

2. **Database**
   - Connection testing
   - Table verification
   - Data operations

3. **Game Features**
   - Game scoring
   - Negotiation logic
   - Student playground

4. **External Services**
   - Google Drive operations
   - Email service
   - Metrics collection

### 6.3 Test Data Setup

The project includes a metrics testing dashboard that can be used to create test data. To use it:

1. Run the test dashboard:
   ```bash
   streamlit run tests/unit_tests.py
   ```

2. Click the "Create Test Metrics Tables" button to generate sample data including:
   - Page visits and durations
   - User logins
   - Game interactions and scores
   - Prompt metrics
   - Conversation metrics
   - Deal metrics

Alternatively, you can create test data by:
- Logging in to the main app
- Visiting different pages
- Submitting prompts
- Playing games

### 6.4 Test Credentials

Tests use credentials from `streamlit/.streamlit/secrets.toml`. If the file doesn't exist, tests will run with mock data.

---

## 7. Contributing

### 7.1 Development Workflow

1. Fork the repository:
   - Go to [https://github.com/rbelo/AI-Assistant-Competition](https://github.com/rbelo/AI-Assistant-Competition)
   - Click "Fork" in the top right
   - Clone your fork:
     ```bash
     git clone https://github.com/YOUR_USERNAME/AI-Assistant-Competition.git
     cd AI-Assistant-Competition
     ```

2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. Make your changes and commit:
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

4. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

5. Create a Pull Request:
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Select your feature branch
   - Fill in the PR description
   - Submit for review

### 7.2 Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all functions
- Keep functions small and focused

### 7.3 Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Request review from maintainers
4. Address feedback
5. Merge only after approval

---

For more information about specific features or components, refer to the relevant sections in the documentation.
