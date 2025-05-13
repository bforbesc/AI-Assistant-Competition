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
- OpenAI 1.76.0+ (for AI model integration)
- PyAutoGen 0.8.7+ (for agent automation)
- Pandas 2.2.3+ (for data manipulation)
- Psycopg2-binary 2.9.10+ (for PostgreSQL connection)
- Google API Client 2.167.0+ (for Google Drive integration)

A complete list of dependencies can be found in `requirements.txt`.

---

## 2. Development Environment

### 2.1 Option 1: Using Dev Container (Recommended)

The project includes a dev container configuration that provides a consistent development environment. To use it:

1. Install prerequisites:
   - Docker Desktop
   - VS Code with Remote Containers extension

2. Clone and open the repository:
   ```bash
   git clone https://github.com/rbelo/AI-Assistant-Competition.git
   cd AI-Assistant-Competition
   ```

3. Open in VS Code and click "Reopen in Container"

The dev container will automatically:
- Set up Python 3.11
- Install all required dependencies
- Configure VS Code extensions
- Start the development server

### 2.2 Option 2: Manual Setup

If you prefer to set up manually:

1. Install Python 3.11:
   ```bash
   # On macOS with Homebrew:
   brew install python@3.11
   
   # On Ubuntu/Debian:
   sudo apt update
   sudo apt install python3.11 python3.11-venv
   ```

2. Create and activate virtual environment:
   ```bash
   # Create virtual environment
   python3.11 -m venv .venv

   # Activate virtual environment
   # On Windows:
   .\.venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### 2.3 Option 3: Using Conda

If you prefer using Conda for environment management:

1. Install Miniconda or Anaconda if you haven't already:
   ```bash
   # Download Miniconda (recommended for most users)
   # Visit: https://docs.conda.io/en/latest/miniconda.html
   ```

2. Create and activate the conda environment:
   ```bash
   # Create environment from environment.yml
   conda env create -f environment.yml

   # Activate the environment
   conda activate ai-assistant-env
   ```

   The environment will be created with Python 3.11 and all dependencies from requirements.txt will be installed.

4. Configure environment:
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Update with your settings
   # Required environment variables:
   # - DATABASE_URL
   # - SECRET_KEY
   # - OPENAI_API_KEY
   # - GOOGLE_APPLICATION_CREDENTIALS
   ```

---

## 3. Project Structure

```
ai-assistant-competition/
├── streamlit/              # Main application code
│   ├── 0_Home.py          # Streamlit entrypoint
│   ├── modules/           # Core functionality modules
│   ├── pages/            # Streamlit pages
│   └── .streamlit/       # Streamlit configuration
├── tests/                 # Test suite
│   └── unit_tests.py      # Unit tests
├── documentation/         # User and developer guides
├── E-R_Model/            # Database entity-relationship models
├── .devcontainer/        # Development container configuration
├── Tables_AI_Negotiator.sql           # Database schema
├── Populate_Tables_AI_Negotiator.sql  # Sample data
├── requirements.txt       # Python dependencies
├── environment.yml       # Conda environment configuration
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
streamlit run app/main.py
```

The application will be available at `http://localhost:8501`.

### 5.2 Production Mode
```bash
# Build the application
streamlit build

# Run with production settings
streamlit run app/main.py --server.port=8501 --server.address=0.0.0.0
```

---

## 6. Testing & Quality Assurance

### 6.1 Running Tests

The project includes a comprehensive test suite in the `tests` directory. To run the tests:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app

# Run specific test file
pytest tests/unit_tests.py

# Run specific test function
pytest tests/unit_tests.py::test_database_connection
```

### 6.2 Test Categories

The test suite includes:

1. **Unit Tests** (`tests/unit_tests.py`):
   - Database connection and operations
   - Authentication and authorization
   - Game and negotiation logic
   - Metrics collection and validation
   - Email service integration
   - Google Drive operations
   - Student playground functionality

### 6.3 Writing Tests

When adding new features, follow these guidelines:

1. **Test Structure**:
   ```python
   def test_feature_name():
       # Arrange
       setup_test_environment()
       
       # Act
       result = function_under_test()
       
       # Assert
       assert result == expected_value
   ```

2. **Database Tests**:
   ```python
   def test_database_operation():
       # Use test database
       with test_db_connection() as conn:
           result = perform_operation(conn)
           assert result is not None
   ```

### 6.4 Test Data

The test suite includes functions to generate test data:

```python
# Create test tables with sample data
create_test_tables()

# Generate specific test scenarios
generate_test_metrics()
generate_test_games()
```

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
