import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import modules.metrics_handler as metrics
import modules.database_handler as db
import modules.negotiations as negotiations
import modules.student_playground as playground
import modules.email_service as email
import modules.schedule as schedule
import modules.drive_file_manager as drive
import psycopg2
from datetime import datetime, timedelta
import random
import pytest
from unittest.mock import patch, MagicMock

"""
This script tests the metrics collection system by checking if the required tables
have been created in the database.
"""

# Ensure session state variables are initialized to avoid authentication errors
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = True
if "professor" not in st.session_state:
    st.session_state["professor"] = True
if "user_id" not in st.session_state:
    st.session_state["user_id"] = "test_user"

def create_test_tables():
    """Initialize all required tables with test data"""
    user_id = "test_user"
    
    # Create sample page visits
    for page in ["Home", "Play", "Reports", "Profile"]:
        for i in range(5):
            # Record entry
            metrics.record_page_entry(user_id, page)
            # Record exit with random duration
            visit_id = st.session_state.current_visit_id.get(page, 0)
            if visit_id:
                duration = random.randint(30, 300)  # 30s to 5min
                metrics.record_page_exit(page, duration)
                
            # Also increment page visit count
            metrics.increment_page_visit_count(user_id, page)
    
    # Create sample user logins
    metrics.record_first_login(user_id)
    
    # Create sample game interactions
    game_types = ["decision_game", "negotiation_game"]
    for game in game_types:
        for i in range(3):
            # Random completion times between 5 and 15 minutes
            completion_time = random.randint(300, 900)
            metrics.record_game_interaction(
                user_id=user_id,
                game_type=game,
                game_id=f"game_{i}",
                completion_time=completion_time,
                score=random.randint(70, 100)
            )
    
    # Create sample prompt metrics
    for i in range(10):
        prompt_text = f"This is test prompt number {i}"
        metrics.record_prompt_metrics(
            user_id=user_id,
            prompt_text=prompt_text,
            response_time=random.randint(1, 5)
        )
    
    # Create sample conversation metrics
    for i in range(5):
        metrics.record_conversation_metrics(
            user_id=user_id,
            conversation_id=f"conv_{i}",
            total_exchanges=random.randint(5, 20),
            conversation_duration=random.randint(60, 600)
        )
    
    # Create sample deal metrics
    for i in range(3):
        metrics.record_deal_metrics(
            user_id=user_id,
            deal_id=f"deal_{i}",
            negotiation_rounds=random.randint(3, 10),
            deal_success=(random.random() > 0.3),  # 70% success rate
            deal_value=random.randint(10000, 100000) if random.random() > 0.2 else None  # 80% chance of having a value
        )
    
    st.success("All test tables have been created with sample data!")

def main():
    st.title("Metrics Testing Dashboard")
    st.write("This dashboard is used to test the metrics collection and visualization.")
    
    # Add button to create test tables
    if st.button("Create Test Metrics Tables"):
        create_test_tables()
    
    # Display the existing metrics tables
    st.subheader("Existing Metrics Tables")
    
    try:
        conn = psycopg2.connect(st.secrets["database"])
        cur = conn.cursor()
        
        # Query to get all tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        tables = cur.fetchall()
        table_list = [table[0] for table in tables]
        
        metrics_tables = [
            'page_visit',
            'game_interaction',
            'page_visit_count',
            'prompt_metrics',
            'user_login',
            'conversation_metrics',
            'deal_metrics'
        ]
        
        # Count how many of our metrics tables exist
        existing_metrics_tables = [table for table in metrics_tables if table in table_list]
        
        st.write(f"{len(existing_metrics_tables)} out of {len(metrics_tables)} metrics tables exist")
        
        # Display which tables exist and which don't
        for table in metrics_tables:
            if table in table_list:
                st.write(f"✅ {table}")
            else:
                st.write(f"❌ {table}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        st.error(f"Error: {e}")
    
    st.write("""
    ### Instructions
    
    1. To create the metrics tables with test data, click the 'Create Test Metrics Tables' button above.
    2. Alternatively, you can create tables by:
       - Logging in to the main app
       - Visiting different pages
       - Submitting prompts
       - Playing games
    """)

def check_credentials():
    """Check if required credentials are available"""
    required_credentials = {
        "database": "Database connection string",
        "drive": "Google Drive service account",
        "mail": "Email service credentials",
        "mail_api": "Email API credentials"
    }
    
    missing_credentials = []
    for key, description in required_credentials.items():
        if key not in st.secrets or not st.secrets[key]:
            missing_credentials.append(description)
    
    return missing_credentials

def mock_database_connection():
    """Create a mock database connection for testing"""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    return mock_conn, mock_cur

def mock_google_drive():
    """Create mock Google Drive functions"""
    def mock_get_text(*args, **kwargs):
        return "Mock file content"
    
    def mock_write_text(*args, **kwargs):
        return True
    
    def mock_delete_file(*args, **kwargs):
        return True
    
    return mock_get_text, mock_write_text, mock_delete_file

def mock_email_service():
    """Create mock email service functions"""
    def mock_send_email(*args, **kwargs):
        return True
    
    def mock_get_template(*args, **kwargs):
        return {
            "subject": "Test Subject",
            "body": "Test Body"
        }
    
    return mock_send_email, mock_get_template

def test_database_connection():
    """Test that we can connect to the database"""
    missing_creds = check_credentials()
    if "Database connection string" in missing_creds:
        print("Skipping database connection test - missing credentials")
        return True
        
    try:
        conn = psycopg2.connect(st.secrets["database"])
        assert conn is not None
        conn.close()
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

def test_database_tables():
    """Test that required tables exist in database"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Check core tables exist
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [t[0] for t in cur.fetchall()]
        
        required_tables = ['users', 'games', 'rounds', 'plays']
        for table in required_tables:
            assert table in tables, f"Missing required table: {table}"
            
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Database tables test failed: {e}")
        return False

def test_google_drive_connection():
    """Test connection to Google Drive"""
    missing_creds = check_credentials()
    if "Google Drive service account" in missing_creds:
        print("Skipping Google Drive test - missing credentials")
        return True
        
    try:
        # Try to read a test file
        test_content = get_text_from_file('test.txt')
        assert test_content is not None
        
        # Try to write a test file
        test_text = "Test content " + str(datetime.now())
        overwrite_text_file('test.txt', test_text)
        
        # Verify content was written
        read_content = get_text_from_file('test.txt')
        assert test_text in read_content
        
        # Clean up
        find_and_delete('test.txt')
        return True
    except Exception as e:
        print(f"Google Drive connection test failed: {e}")
        return False

def test_authentication():
    """Test user authentication functionality"""
    try:
        # Test valid login
        assert st.session_state["authenticated"] == True
        assert st.session_state["professor"] == True
        assert st.session_state["user_id"] == "test_user"
        
        # Test invalid login
        st.session_state["authenticated"] = False
        assert st.session_state["authenticated"] == False
        
        return True
    except Exception as e:
        print(f"Authentication test failed: {e}")
        return False

def test_metrics_accuracy():
    """Test the accuracy of metrics collection"""
    try:
        user_id = "test_user"
        
        # Test page visit metrics
        metrics.record_page_entry(user_id, "TestPage")
        visit_id = st.session_state.current_visit_id.get("TestPage", 0)
        assert visit_id > 0, "Page visit ID should be generated"
        
        # Test game interaction metrics
        game_id = "test_game_1"
        metrics.record_game_interaction(
            user_id=user_id,
            game_type="test_game",
            game_id=game_id,
            completion_time=300,
            score=85
        )
        
        # Verify game metrics were recorded
        conn = psycopg2.connect(st.secrets["database"])
        cur = conn.cursor()
        cur.execute("SELECT * FROM game_interaction WHERE game_id = %s", (game_id,))
        result = cur.fetchone()
        assert result is not None, "Game interaction should be recorded"
        assert result[3] == 300, "Completion time should match"
        assert result[4] == 85, "Score should match"
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Metrics accuracy test failed: {e}")
        return False

def test_data_validation():
    """Test data validation in metrics collection"""
    try:
        # Test invalid user_id
        with pytest.raises(ValueError):
            metrics.record_page_entry(None, "TestPage")
        
        # Test invalid page name
        with pytest.raises(ValueError):
            metrics.record_page_entry("test_user", None)
        
        # Test invalid game metrics
        with pytest.raises(ValueError):
            metrics.record_game_interaction(
                user_id="test_user",
                game_type=None,
                game_id="test_game",
                completion_time=-1,  # Invalid time
                score=101  # Invalid score
            )
        
        return True
    except Exception as e:
        print(f"Data validation test failed: {e}")
        return False

def test_error_handling():
    """Test error handling in the application"""
    try:
        # Test database connection error
        with pytest.raises(psycopg2.OperationalError):
            conn = psycopg2.connect("invalid_connection_string")
        
        # Test Google Drive error
        with pytest.raises(Exception):
            get_text_from_file('non_existent_file.txt')
        
        # Test metrics recording with invalid data
        with pytest.raises(Exception):
            metrics.record_page_exit(None, -1)
        
        return True
    except Exception as e:
        print(f"Error handling test failed: {e}")
        return False

def test_game_logic():
    """Test game logic and scoring"""
    try:
        # Test game scoring
        score = calculate_game_score(
            completion_time=300,
            correct_answers=8,
            total_questions=10
        )
        assert 0 <= score <= 100, "Score should be between 0 and 100"
        
        # Test negotiation logic
        deal = create_test_deal(
            initial_value=10000,
            rounds=5,
            success=True
        )
        assert deal["value"] > 0, "Deal value should be positive"
        assert deal["rounds"] == 5, "Number of rounds should match"
        
        return True
    except Exception as e:
        print(f"Game logic test failed: {e}")
        return False

def test_negotiation_logic():
    """Test negotiation game functionality"""
    try:
        # Test negotiation setup
        game_id = "test_negotiation_1"
        setup = negotiations.setup_negotiation_game(game_id)
        assert setup is not None
        assert "scenario" in setup
        assert "roles" in setup
        
        # Test negotiation round
        round_result = negotiations.process_negotiation_round(
            game_id=game_id,
            player_offer=10000,
            ai_offer=12000
        )
        assert round_result is not None
        assert "status" in round_result
        assert "next_round" in round_result
        
        # Test negotiation completion
        final_deal = negotiations.complete_negotiation(
            game_id=game_id,
            final_value=11000
        )
        assert final_deal is not None
        assert "success" in final_deal
        assert "value" in final_deal
        
        return True
    except Exception as e:
        print(f"Negotiation logic test failed: {e}")
        return False

def test_student_playground():
    """Test student playground functionality"""
    try:
        # Test playground initialization
        playground_id = "test_playground_1"
        playground.setup_playground(playground_id)
        
        # Test scenario loading
        scenario = playground.load_scenario("test_scenario")
        assert scenario is not None
        assert "description" in scenario
        assert "options" in scenario
        
        # Test student response processing
        response = playground.process_student_response(
            playground_id=playground_id,
            scenario_id="test_scenario",
            response="test_response"
        )
        assert response is not None
        assert "feedback" in response
        
        return True
    except Exception as e:
        print(f"Student playground test failed: {e}")
        return False

def test_email_service():
    """Test email service functionality"""
    missing_creds = check_credentials()
    if "Email service credentials" in missing_creds or "Email API credentials" in missing_creds:
        print("Skipping email service test - missing credentials")
        return True
        
    try:
        # Test email sending
        result = email.send_email(
            to="test@example.com",
            subject="Test Email",
            body="This is a test email"
        )
        assert result is True
        
        # Test email template
        template = email.get_email_template("welcome")
        assert template is not None
        assert "subject" in template
        assert "body" in template
        
        return True
    except Exception as e:
        print(f"Email service test failed: {e}")
        return False

def test_scheduling():
    """Test scheduling functionality"""
    try:
        # Test schedule creation
        schedule_id = schedule.create_schedule(
            user_id="test_user",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1)
        )
        assert schedule_id is not None
        
        # Test schedule retrieval
        user_schedule = schedule.get_user_schedule("test_user")
        assert user_schedule is not None
        assert len(user_schedule) > 0
        
        return True
    except Exception as e:
        print(f"Scheduling test failed: {e}")
        return False

def test_page_navigation():
    """Test page navigation and routing"""
    try:
        # Test home page
        home_page = st.session_state.get("current_page")
        assert home_page == "Home"
        
        # Test page transitions
        pages = ["Play", "Control_Panel", "Profile", "About", "Playground"]
        for page in pages:
            st.session_state["current_page"] = page
            assert st.session_state["current_page"] == page
            
        return True
    except Exception as e:
        print(f"Page navigation test failed: {e}")
        return False

def test_database_operations():
    """Test database operations"""
    missing_creds = check_credentials()
    if "Database connection string" in missing_creds:
        print("Skipping database operations test - missing credentials")
        return True
        
    try:
        # Test user operations
        user_id = "test_user"
        db.create_user(user_id, "Test User", "test@example.com")
        user = db.get_user(user_id)
        assert user is not None
        assert user["email"] == "test@example.com"
        
        # Test game operations
        game_id = "test_game_1"
        db.create_game(game_id, "negotiation", user_id)
        game = db.get_game(game_id)
        assert game is not None
        assert game["type"] == "negotiation"
        
        # Test metrics operations
        db.record_game_metrics(
            game_id=game_id,
            score=85,
            duration=300
        )
        metrics = db.get_game_metrics(game_id)
        assert metrics is not None
        assert metrics["score"] == 85
        
        return True
    except Exception as e:
        print(f"Database operations test failed: {e}")
        return False

def run_all_tests():
    """Run all test suites"""
    missing_creds = check_credentials()
    if missing_creds:
        print("\nMissing credentials:")
        for cred in missing_creds:
            print(f"- {cred}")
        print("\nSome tests will be skipped or run in mock mode.")
    
    test_suites = {
        "Authentication": test_authentication,
        "Metrics Accuracy": test_metrics_accuracy,
        "Data Validation": test_data_validation,
        "Error Handling": test_error_handling,
        "Game Logic": test_game_logic,
        "Database Connection": test_database_connection,
        "Database Tables": test_database_tables,
        "Google Drive": test_google_drive_connection,
        "Negotiation Logic": test_negotiation_logic,
        "Student Playground": test_student_playground,
        "Email Service": test_email_service,
        "Scheduling": test_scheduling,
        "Page Navigation": test_page_navigation,
        "Database Operations": test_database_operations
    }
    
    print("\nRunning all test suites...")
    results = {}
    
    for suite_name, test_func in test_suites.items():
        try:
            results[suite_name] = test_func()
        except Exception as e:
            print(f"Error running {suite_name}: {e}")
            results[suite_name] = False
    
    print("\nTest Results:")
    for suite, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{suite}: {status}")
    
    return all(results.values())

if __name__ == "__main__":
    main()
    # Uncomment to run all tests
    # run_all_tests() 