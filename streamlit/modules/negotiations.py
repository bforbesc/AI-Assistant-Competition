import re
import autogen

from modules.database_handler import insert_round_data
from modules.drive_file_manager import get_text_from_file_without_timestamp, overwrite_text_file
from modules.schedule import berger_schedule

# Function for cleaning of the dialogue messages that may include in the message "Agent Name:"
def clean_agent_message(agent_name_1, agent_name_2, message):
    
    if not message:  # Handle possible empty messages
        return ""

    # Define a regex pattern to match "Agent_name: " at the start of the message for either agent
    pattern = rf"^\s*(?:{re.escape(agent_name_1)}|{re.escape(agent_name_2)})\s*:\s*"

    # Use regex substitution to remove the pattern from the message
    clean_message = re.sub(pattern, "", message, flags=re.IGNORECASE)

    return clean_message

def create_chat(game_id, team1, team2, starting_message, num_turns, summary_prompt, round, user, summary_agent):

    chat = team1["Agent 1"].initiate_chat(
        team2["Agent 2"],
        clear_history = True,
        max_turns=num_turns,       
        summary_method="reflection_with_llm",       
        summary_prompt=summary_prompt,    
        message=starting_message 
    )

    negotiation = ""

    for i in range(len(chat.chat_history)):

        clean_msg = clean_agent_message(team1["Agent 1"].name, team2["Agent 2"].name, chat.chat_history[i]['content'])
        
        f = chat.chat_history[i]['name'] + ': ' + clean_msg + '\n\n\n'
        negotiation += f

    summary_eval = user.initiate_chat(
        summary_agent,
        clear_history = True,
        max_turns=1,
        message = negotiation + summary_prompt 
    )
    
    negotiation += "\n" + summary_eval.chat_history[1]['content']
    filename = f"Game{game_id}_Round{round}_{team1['Name']}_{team2['Name']}" 
    overwrite_text_file(negotiation, filename)
    
    return None

def create_agents(game_id, teams, config_list, negotiation_termination_message):

    team_info = []
    for team in teams:

        submission = get_text_from_file_without_timestamp(f'Game{game_id}_Group{team}') 

        buyer_pattern = re.compile(r'Buyer:\s*(.*?)(?=\n\n|$)', re.DOTALL)
        seller_pattern = re.compile(r'Seller:\s*(.*?)(?=\n\n|$)', re.DOTALL)

        buyer_content = buyer_pattern.search(submission).group(1).strip()
        seller_content = seller_pattern.search(submission).group(1).strip()

        matches = [buyer_content, seller_content]
      
        new_team = {"Name": f'Group{team}',
                    "Prompt 1": matches[0],
                    "Prompt 2": matches[1],
                    "Agent 1": autogen.ConversableAgent(
                                name=f"Group{team}_Buyer",
                                llm_config={"config_list": config_list},
                                human_input_mode="NEVER",
                                chat_messages=None,
                                system_message = matches[0] + f"When the negotiation is finished, say {negotiation_termination_message}. This is a short conversation, you will have about 10 opportunities to intervene in the conversation. Also, try to keep your answers concise, try not to go over 15 words.",
                                is_termination_msg=lambda msg: negotiation_termination_message in msg["content"]
                                ),

                    "Agent 2": autogen.ConversableAgent(
                                name=f"Group{team}_Seller",
                                llm_config={"config_list": config_list},
                                human_input_mode="NEVER",
                                chat_messages=None,
                                system_message = matches[1] + f'When the negotiation is finished, say {negotiation_termination_message}. This is a short conversation, you will have about 10 opportunities to intervene in the conversation. Also, try to keep your answers concise, try not to go over 15 words.',
                                is_termination_msg=lambda msg: negotiation_termination_message in msg["content"]
                                )                
                    }
        
        team_info.append(new_team)

    return team_info

def create_chats(game_id, config_list, teams, num_rounds, starting_message, num_turns, negotiation_termination_message, summary_prompt, summary_termination_message):

    schedule = berger_schedule(['Group'+str(i) for i in teams], num_rounds)

    team_info = create_agents(game_id, teams, config_list, negotiation_termination_message)

    user = autogen.UserProxyAgent(
        name="User",
        llm_config={"config_list": config_list},   
        human_input_mode = "NEVER",
        is_termination_msg=lambda msg: summary_termination_message in msg["content"],
        code_execution_config = {"work_dir": "repo", "use_docker": False}
    )

    summary_agent = autogen.AssistantAgent(
        name = "Summary_Agent",
        llm_config={"config_list": config_list},
        human_input_mode="NEVER",
        is_termination_msg=lambda msg: summary_termination_message in msg["content"],
        system_message = f"You will be asked to answer a quick question regarding the outcome of a negotiation you will have access to. Your answer must be of the type {summary_termination_message}. If there was no agreement use the value -1, other wise just add the value to the answer as in '{summary_termination_message} x'. Make sure the conversation has ended with {negotiation_termination_message}, otherwise the negotiation has not been finalized." 
    )

    max_retries = 10

    for round, round_matches in enumerate(schedule, 1):  # round_index is 1-based

        for match in round_matches:
            
            # Identify the two teams that play in each match of the round, by their id
            team1 = next((team for team in team_info if team["Name"] == match[0]), None)
            team2 = next((team for team in team_info if team["Name"] == match[1]), None)

            # Attempt to create the first chat
            for attempt in range(max_retries):
                try:

                    if attempt%2==0: c = " "
                    else: c = ""
                        
                    starting_message += c
                    
                    # First chat
                    #create_chat(team1, team2, starting_message, num_turns, summary_prompt, round, user, summary_agent) 
                    
                    break  # Exit retry loop on success

                except Exception as e:
                    print(f"Error during first chat creation between {team1['Name']} and {team2['Name']} on attempt {str(attempt + 1)}: {e}")
                    if attempt == max_retries - 1:
                        print(f"Max retries reached for first chat {team1['Name']} -> {team2['Name']}. Skipping...")

            # Attempt to create the second chat
            for attempt in range(max_retries):
                try:

                    if attempt%2==0: c = " "
                    else: c= ""

                    starting_message += c
                    # Second chat
                    #create_chat(team2, team1, starting_message, num_turns, summary_prompt, round, user, summary_agent)
                    
                    break  # Exit retry loop on success

                except Exception as e:
                    print(f"Error during second chat creation between {team2['Name']} and {team1['Name']} on attempt {str(attempt + 1)}: {e}")
                    if attempt == max_retries - 1:
                        print(f"Max retries reached for second chat {team2['Name']} -> {team1['Name']}. Skipping...")

            #insert_round_data(game_id, round, int(team1["Name"][5:]), int(team2["Name"][5:]), 0, 0)