"""
Student Playground Module for AI Assistant Competition Platform

This module adds a playground feature to the platform, allowing students to:
1. Test their AI agents in a sandbox environment
2. Run practice negotiations with their own agents
3. Experiment with different prompts and configurations
4. View and analyze results without affecting official game scores
"""

import streamlit as st
import re
import time
import autogen
import random
from datetime import datetime
import hashlib
from modules.database_handler import get_group_id_from_user_id, get_class_from_user_id
from modules.drive_file_manager import get_text_from_file_without_timestamp, overwrite_text_file

# Function for cleaning dialogue messages to remove agent name prefixes
def clean_agent_message(agent_name_1, agent_name_2, message):
    if not message:  # Handle possible empty messages
        return ""

    # Define a regex pattern to match "Agent_name: " at the start of the message for either agent
    pattern = rf"^\s*(?:{re.escape(agent_name_1)}|{re.escape(agent_name_2)})\s*:\s*"

    # Use regex substitution to remove the pattern from the message
    clean_message = re.sub(pattern, "", message, flags=re.IGNORECASE)

    return clean_message


# Function to create and run test negotiations
def run_playground_negotiation(role1_prompt, role2_prompt, role1_name, role2_name,
                               starting_message, num_turns, api_key, model="gpt-4o-mini",
                               negotiation_termination_message="Pleasure doing business with you"):
    # Configure agents
    config_list = {"config_list": [{"model": model, "api_key": api_key}],
                   "temperature": 0.3, "top_p": 0.5}

    role1_agent = autogen.ConversableAgent(
        name=f"{role1_name}",
        llm_config=config_list,
        human_input_mode="NEVER",
        chat_messages=None,
        system_message=role1_prompt + f" When the negotiation is finished, say {negotiation_termination_message}. This is a short conversation, you will have about {num_turns} opportunities to intervene.",
        is_termination_msg=lambda msg: negotiation_termination_message in msg["content"]
    )

    role2_agent = autogen.ConversableAgent(
        name=f"{role2_name}",
        llm_config=config_list,
        human_input_mode="NEVER",
        chat_messages=None,
        system_message=role2_prompt + f" When the negotiation is finished, say {negotiation_termination_message}. This is a short conversation, you will have about {num_turns} opportunities to intervene.",
        is_termination_msg=lambda msg: negotiation_termination_message in msg["content"]
    )

    # Initialize chat
    chat = role1_agent.initiate_chat(
        role2_agent,
        clear_history=True,
        max_turns=num_turns,
        message=starting_message
    )

    # Process chat history for display
    negotiation_text = ""
    for i in range(len(chat.chat_history)):
        clean_msg = clean_agent_message(role1_agent.name, role2_agent.name,
                                        chat.chat_history[i]['content'])
        formatted_msg = chat.chat_history[i]['name'] + ': ' + clean_msg + '\n\n'
        negotiation_text += formatted_msg

    return negotiation_text, chat.chat_history


# Save playground negotiation results for future reference
def save_playground_results(user_id, class_, group_id, role1_name, role2_name,
                            negotiation_text):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"Playground_Class{class_}_Group{group_id}_{timestamp}"
    overwrite_text_file(negotiation_text, filename, remove_timestamp=False)
    return filename


# Load previous playground negotiation results
def load_playground_results(user_id, class_, group_id):
    pattern = f"Playground_Class{class_}_Group{group_id}"
    return get_text_from_file_without_timestamp(pattern)


# Main playground page function
def display_student_playground():
    st.title("AI Agent Playground")

    # Check if user is authenticated
    if not st.session_state.get('authenticated', False):
        st.warning("Please login first to access the Playground.")
        return

    # Get user details
    user_id = st.session_state.get('user_id', '')
    class_ = get_class_from_user_id(user_id)
    group_id = get_group_id_from_user_id(user_id)

    # Playground tabs
    tab1, tab2, tab3 = st.tabs(["Create Test", "My Tests", "Playground Help"])

    with tab1:
        st.header("Create New Test Negotiation")

        with st.form(key="playground_form"):
            col1, col2 = st.columns(2)

            with col1:
                role1_name = st.text_input("Role 1 Name", value="Buyer")
                role1_value = st.number_input("Role 1 Reservation Value", value=20)
                role1_prompt = st.text_area("Role 1 Prompt", height=200,
                                            value=f"You are a buyer negotiating to purchase an item. Your reservation value is {role1_value}, which means you won't pay more than this amount. Try to negotiate the lowest price possible.")

            with col2:
                role2_name = st.text_input("Role 2 Name", value="Seller")
                role2_value = st.number_input("Role 2 Reservation Value", value=10)
                role2_prompt = st.text_area("Role 2 Prompt", height=200,
                                            value=f"You are a seller negotiating to sell an item. Your reservation value is {role2_value}, which means you won't accept less than this amount. Try to negotiate the highest price possible.")

            st.subheader("Negotiation Settings")
            starting_message = st.text_input("Starting Message", value="Hello, I'm interested in negotiating with you.")
            num_turns = st.slider("Maximum Turns", min_value=5, max_value=30, value=15)
            model = st.selectbox("Model", options=["gpt-4o-mini", "gpt-4o"], index=0)
            api_key = st.text_input("OpenAI API Key", type="password")
            save_results = st.checkbox("Save Results", value=True)

            submit_button = st.form_submit_button("Run Test Negotiation")

        if submit_button:
            if not api_key:
                st.error("Please provide an OpenAI API key to run the negotiation")
                return

            with st.spinner("Running negotiation test..."):
                try:
                    negotiation_text, chat_history = run_playground_negotiation(
                        role1_prompt, role2_prompt, role1_name, role2_name,
                        starting_message, num_turns, api_key, model
                    )

                    # Display results
                    st.success("Test negotiation completed!")
                    st.subheader("Negotiation Results")
                    st.text_area("Negotiation Transcript", negotiation_text, height=400)

                    # Save results if requested
                    if save_results:
                        filename = save_playground_results(
                            user_id, class_, group_id, role1_name, role2_name,
                            negotiation_text
                        )
                        st.success(f"Results saved successfully! Reference ID: {filename}")

                except Exception as e:
                    st.error(f"An error occurred during the negotiation: {str(e)}")

    with tab2:
        st.header("My Previous Tests")

        # Load and display previous tests
        previous_tests = load_playground_results(user_id, class_, group_id)

        if previous_tests:
            st.text_area("Previous Test Results", previous_tests, height=400)
        else:
            st.info("You don't have any previous playground tests. Create a new test to see results here.")

    with tab3:
        st.header("Playground Help")

        st.markdown("""
        ### How to Use the AI Agent Playground

        This playground allows you to test and refine your AI agents before submitting them to official competitions.

        #### Creating Effective Prompts

        1. **Be specific about goals**: Clearly state what your agent should try to accomplish
        2. **Define constraints**: Set reservation values and other limitations
        3. **Add context**: Provide background information that helps the agent understand the scenario
        4. **Include negotiation strategies**: Guide your agent on how to approach the negotiation

        #### Best Practices

        - Test different versions of your prompts to see which performs better
        - Try various negotiation scenarios with different reservation values
        - Analyze successful negotiations to improve your agent's performance
        - Use realistic values and constraints that match official competition settings

        #### Tips for Official Competitions

        - Prompts that perform well in the playground often translate to success in competitions
        - Balance between being too specific (limiting flexibility) and too vague (causing unpredictable behavior)
        - Consider how your agent will interact with opponents using different strategies
        """)