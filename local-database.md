# PostgreSQL Database for AI Assistant Competition - Setup and Management

## 1. Installing PostgreSQL

### On macOS with Homebrew:
```bash
# Install PostgreSQL
brew install postgresql

# Start PostgreSQL service
brew services start postgresql
```

### On Windows:
- Download the PostgreSQL installer from https://www.postgresql.org/download/windows/
- Follow the installation wizard and remember the admin password you set.

### On Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

## 2. Create Database
```bash
# Create database for the project
createdb ai_assistant_competition

# On Windows you might need to connect via psql first:
# psql -U postgres 
# CREATE DATABASE ai_assistant_competition;
# \q
```

## 3. Create Tables
Run the SQL scripts from the Tables_AI_Negotiator.sql file:
```bash
# Create tables from SQL file
psql -d ai_assistant_competition -f Tables_AI_Negotiator.sql

# Optional: Add test data
psql -d ai_assistant_competition -f Populate_Tables_AI_Negotiator.sql
```

## 4. Configure Streamlit Secrets for Local Database
Create or edit the .streamlit/secrets.toml file located within the streamlit directory. For local development, ensure the database key points correctly to your local PostgreSQL instance.

```toml
# .streamlit/secrets.toml

# --- Database Connection for Local Development ---
database = "postgresql://localhost/ai_assistant_competition"

# --- Other Secrets ---
# Google Drive API credentials (sensitive information, keep private)
drive = """
{
  "type": "service_account",
  "project_id": "",
  "private_key_id": "",
  "private_key": "",
  "client_email": "",
  "client_id": "",
  "auth_uri": "",
  "token_uri": "",
  "auth_provider_x509_cert_url": "",
  "client_x509_cert_url": "",
  "universe_domain": ""
}
"""
folder_id = ""

# Email settings
mail = ""
mail_api = ""
app_link = "http://localhost:8501"
```

**Important**: Ensure the database connection string is correct for your local setup. The Streamlit application reads this file to connect to the database.

## 5. Test Database Connection
Use this command to test the connection to your database from your terminal:
```bash
psql -d ai_assistant_competition -c "SELECT 'Connection successful' AS status;"
# If using username/password: psql -U YOUR_USERNAME -d ai_assistant_competition -c "SELECT 'Connection successful' AS status;" (you might be prompted for password)
```

## 6. Database Management

### 6.1. Adding Users (with Script)
To add a new user (student or professor) to the local database, you can use the provided Python script add_user_interactive.py (ensure it is located in the main project directory AI-Assistant-Competition/). This script automatically handles the correct password hashing.

- **Check Script Configuration**: Open add_user_interactive.py and ensure the DB_CONNECTION_STRING variable near the beginning of the file is correctly configured for your local database (just like in secrets.toml, possibly including username/password if needed).
- **Install Dependencies** (if not already done):
```bash
# Make sure you are in your virtual environment (e.g., venv)
pip install psycopg2-binary python-dotenv 
```
(python-dotenv is optional if you prefer not to use a .env file for the connection string).
- **Run the Script**: Navigate to the main project directory (AI-Assistant-Competition/) in your terminal and run:
```bash
python add_user_interactive.py
```
- **Enter User Data**: The script will prompt you to enter all necessary information for the new user (User ID, Email, Password, Group ID, Academic Year, Class). Provide the data when prompted.

### 6.2. Viewing the Database
```bash
# Connect to the database
psql -d ai_assistant_competition
# If using username/password: psql -U YOUR_USERNAME -d ai_assistant_competition 

# Useful psql commands:
# \dt          - List tables
# SELECT * FROM user_; - View users (passwords will be hashed)
# \d user_     - Show user_ table schema
# \q           - Exit psql
```

### 6.3. Creating a Backup
```bash
# Create database backup
pg_dump ai_assistant_competition > backup.sql
# If using username/password: pg_dump -U YOUR_USERNAME -d ai_assistant_competition > backup.sql
```

## 7. Delete Database
When you no longer need the project or want to reset the database:
```bash
# Terminate connections to the database (important before dropping)
psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='ai_assistant_competition';"
# If using username/password: psql -U YOUR_USERNAME -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='ai_assistant_competition';"

# Delete database
dropdb ai_assistant_competition
# If using username/password: dropdb -U YOUR_USERNAME ai_assistant_competition

# On Windows, you might need to use psql to drop the database:
# psql -U postgres 
# DROP DATABASE ai_assistant_competition;
# \q
```

## 8. Completely Uninstall PostgreSQL

### On macOS:
```bash
# Stop PostgreSQL service
brew services stop postgresql

# Uninstall PostgreSQL
brew uninstall postgresql

# Delete database directory (optional, deletes ALL data!)
rm -rf /usr/local/var/postgres # Be careful with this command!
```

### On Windows:
- Use the Control Panel → Programs → Uninstall a program feature.
- Select PostgreSQL and uninstall.

### On Linux (Ubuntu/Debian):
```bash
sudo systemctl stop postgresql
sudo apt remove --purge postgresql postgresql-contrib
sudo rm -rf /var/lib/postgresql/ # Be careful with this command!
sudo userdel -r postgres # Remove the default postgres user
```

## Troubleshooting Notes:
- **If the database connection doesn't work** (neither in Streamlit nor in the add_user_interactive.py script):
  - Is the PostgreSQL service running? (Check with `brew services list` on macOS or `systemctl status postgresql` on Linux).
  - Is the connection string in .streamlit/secrets.toml AND in add_user_interactive.py correct (including username/password if required for your setup)?
  - Do you have the necessary permissions in PostgreSQL to connect to the ai_assistant_competition database?
  - Is a firewall potentially blocking the connection (unlikely for localhost connections)?
- **For Google Drive API error messages**:
  - Is the service account JSON provided in .streamlit/secrets.toml correctly formatted?
  - Is the Google Drive API enabled in your Google Cloud project associated with the service account?
  - Does the service account's email address have appropriate permissions (e.g., "Editor" rights) for the specified folder_id in Google Drive?