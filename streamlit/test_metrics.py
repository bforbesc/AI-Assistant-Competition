import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import modules.metrics_handler as metrics
import psycopg2
from datetime import datetime, timedelta
import random

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

if __name__ == "__main__":
    main() 