import re
import autogen

from modules.database_handler import insert_round_data, update_round_data, get_error_matchups
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


def create_chat(game_id, order, team1, team2, starting_message, num_turns, summary_prompt, round, user, summary_agent, summary_termination_message):

    chat = team1["Agent 1"].initiate_chat(
        team2["Agent 2"],
        clear_history = True,
        max_turns=num_turns,
        message=starting_message
    )

    negotiation = ""
    summ = ""

    for i in range(len(chat.chat_history)):

        clean_msg = clean_agent_message(team1["Agent 1"].name, team2["Agent 2"].name, chat.chat_history[i]['content'])
        
        f = chat.chat_history[i]['name'] + ': ' + clean_msg + '\n\n\n'
        negotiation += f

        if i >= (len(chat.chat_history) - 4):
            summ += f

    summary_eval = user.initiate_chat(
        summary_agent,
        clear_history = True,
        max_turns=1,
        message = summ + summary_prompt 
    )
    
    negotiation += "\n" + summary_eval.chat_history[1]['content']
    if order == "same":
        filename = f"Game{game_id}_Round{round}_{team1['Name']}_{team2['Name']}.txt" 
    elif order == "opposite":
        filename = f"Game{game_id}_Round{round}_{team2['Name']}_{team1['Name']}.txt" 
    overwrite_text_file(negotiation, filename, remove_timestamp=False)

    if summary_eval.chat_history[1]['content'].startswith(summary_termination_message):

        deal = float(re.findall(r'-?\d+(?:[.,]\d+)?', summary_eval.chat_history[1]['content'])[0].replace(",","."))

        return deal
    
    else: return -1


def create_agents(game_id, order, teams, values, name_roles, config_list, negotiation_termination_message):

    team_info = []

    if order == "same":
        role_1, role_2 = name_roles[0].replace(" ", ""), name_roles[1].replace(" ", "")

    elif order == "opposite":
        role_1, role_2 = name_roles[1].replace(" ", ""), name_roles[0].replace(" ", "")

    if config_list["config_list"][0]["model"] == "gpt-4o-mini": words = 15

    elif config_list["config_list"][0]["model"] == "gpt-4o": words = 25

    else: words = 15

    for team in teams:

        submission = get_text_from_file_without_timestamp(f'Game{game_id}_Class{team[0]}_Group{team[1]}') 

        value1 = int(next((value for value in values if value[0] == team[0] and int(value[1]) == team[1]), None)[2])
        value2 = int(next((value for value in values if value[0] == team[0] and int(value[1]) == team[1]), None)[3])
    
        prompts = [part.strip() for part in submission.split('#_;:)')]

        if order == "opposite": 
            aux_val = value1
            value1 = value2
            value2 = aux_val
            prompts = prompts[::-1]

        new_team = {"Name": f'Class{team[0]}_Group{team[1]}',
                    "Value 1": value1,
                    "Value 2": value2,
                    "Agent 1": autogen.ConversableAgent(
                                name=f"Class{team[0]}_Group{team[1]}_{role_1}",
                                llm_config=config_list,
                                human_input_mode="NEVER",
                                chat_messages=None,
                                system_message = prompts[0] + f"When the negotiation is finished, say {negotiation_termination_message}. This is a short conversation, you will have about 10 opportunities to intervene. Try to keep your answers concise, try not to go over {words} words.",
                                is_termination_msg=lambda msg: negotiation_termination_message in msg["content"]
                                ),

                    "Agent 2": autogen.ConversableAgent(
                                name=f"Class{team[0]}_Group{team[1]}_{role_2}",
                                llm_config=config_list,
                                human_input_mode="NEVER",
                                chat_messages=None,
                                system_message = prompts[1] + f'When the negotiation is finished, say {negotiation_termination_message}. This is a short conversation, you will have about 10 opportunities to intervene. Try to keep your answers concise, try not to go over {words} words.',
                                is_termination_msg=lambda msg: negotiation_termination_message in msg["content"]
                                )                
                    }
        
        team_info.append(new_team)

    return team_info


def create_chats(game_id, config_list, name_roles, order, teams, values, num_rounds, starting_message, num_turns, negotiation_termination_message, summary_prompt, summary_termination_message):

    schedule = berger_schedule([f'Class{i[0]}_Group{i[1]}' for i in teams], num_rounds) 

    team_info = create_agents(game_id, order, teams, values, name_roles, config_list, negotiation_termination_message)
    
    user = autogen.UserProxyAgent(
        name="User",
        llm_config=config_list,   
        human_input_mode = "NEVER",
        is_termination_msg=lambda msg: summary_termination_message in msg["content"],
        code_execution_config = {"work_dir": "repo", "use_docker": False}
    )

    summary_agent = autogen.AssistantAgent(
        name = "Summary_Agent",
        llm_config=config_list,
        human_input_mode="NEVER",
        is_termination_msg=lambda msg: summary_termination_message in msg["content"],
        system_message = f"You will be asked to answer a quick question regarding the outcome of a negotiation. You will be provided with the last 4 interactions of the negotiation and your answer should be based on them. Your answer must be of the type {summary_termination_message}, just adding the value agreed, as in '{summary_termination_message} x', x being the value. Make sure the conversation has ended with {negotiation_termination_message}, otherwise the negotiation has not been finalized and there was no agreement. If this happens, i.e., if the final message does not include {negotiation_termination_message}, your answer should be '{summary_termination_message} -1'."  
    )

    max_retries = 10

    errors_matchups = []

    for round_, round_matches in enumerate(schedule, 1):  

        for match in round_matches:
            
            # Identify the two teams that play in each match of the round, by their id
            team1 = next((team for team in team_info if team["Name"] == match[0]), None)
            team2 = next((team for team in team_info if team["Name"] == match[1]), None)

            class_group_1 = team1["Name"].split("_")
            class1 = class_group_1[0][5:]
            group1 = class_group_1[1][5:]

            class_group_2 = team2["Name"].split("_")
            class2 = class_group_2[0][5:]
            group2 = class_group_2[1][5:]

            insert_round_data(game_id, round_, class1, group1, class2, group2, -1, -1, -1, -1)

            # Attempt to create the first chat
            for attempt in range(max_retries):
                try:

                    if attempt%2==0: c = " "
                    else: c = ""
                        
                    starting_message += c
                    
                    # First chat
                    deal = create_chat(game_id, order, team1, team2, starting_message, num_turns, summary_prompt, round_, user, summary_agent, summary_termination_message) 

                    if deal == -1:
                        score1_team1 = 0
                        score1_team2 = 0

                        update_round_data(game_id, round_, class1, group1, class2, group2, score1_team1, score1_team2, order) 

                    else:

                        if order == "same":

                            if deal > team2["Value 2"]:
                                score1_team1 = 0
                                score1_team2 = 1

                            elif deal < team1["Value 1"]:
                                score1_team1 = 1
                                score1_team2 = 0

                            else:
                                score1_team2 = round((deal - team1["Value 1"])/(team2["Value 2"] - team1["Value 1"]), 4)
                                score1_team1 = 1 - score1_team2

                            # update_round_data(game_id, round_, class1, group1, class2, group2, score1_team1, score1_team2, order)

                        elif order == "opposite":
                            
                            if deal > team1["Value 1"]:
                                score1_team1 = 1
                                score1_team2 = 0

                            elif deal < team2["Value 2"]: 
                                score1_team1 = 0
                                score1_team2 = 1

                            else:
                                score1_team1 = round((deal - team2["Value 2"])/(team1["Value 1"] - team2["Value 2"]), 4)
                                score1_team2 = 1 - score1_team1

                        update_round_data(game_id, round_, class1, group1, class2, group2, score1_team1, score1_team2, order) 

                    break  # Exit retry loop on success

                except Exception:                    
                    if attempt == max_retries - 1:
                        if order == "same": errors_matchups.append((round_, team1["Name"], team2["Name"]))
                        elif order == "opposite": errors_matchups.append((round_, team2["Name"], team1["Name"]))

            # Attempt to create the second chat
            for attempt in range(max_retries):
                try:

                    if attempt%2==0: c = " "
                    else: c= ""

                    starting_message += c

                    # Second chat
                    deal = create_chat(game_id, order, team2, team1, starting_message, num_turns, summary_prompt, round_, user, summary_agent, summary_termination_message)

                    if order == "same":

                        if deal == -1:
                            score2_team1 = 0
                            score2_team2 = 0
                                
                        elif deal > team1["Value 2"]:
                            score2_team1 = 1
                            score2_team2 = 0

                        elif deal < team2["Value 1"]: 
                            score2_team1 = 0
                            score2_team2 = 1

                        else:
                            score2_team1 = round((deal - team2["Value 1"])/(team1["Value 2"] - team2["Value 1"]), 4)
                            score2_team2 = 1 - score2_team1

                        update_round_data(game_id, round_, class1, group1, class2, group2, score2_team1, score2_team2, "opposite")

                    elif order == "opposite":

                        if deal == -1:
                            score2_team1 = 0
                            score2_team2 = 0
                        
                        elif deal > team2["Value 1"]:
                            score2_team1 = 0
                            score2_team2 = 1

                        elif deal < team1["Value 2"]:
                            score2_team1 = 1
                            score2_team2 = 0

                        else:
                            score2_team2 = round((deal - team1["Value 2"])/(team2["Value 1"] - team1["Value 2"]), 4)
                            score2_team1 = 1 - score2_team2

                        update_round_data(game_id, round_, class1, group1, class2, group2, score2_team1, score2_team2, "same")
                        
                    break  # Exit retry loop on success

                except Exception:                    
                    if attempt == max_retries - 1:
                        if order == "same": errors_matchups.append((round_, team2["Name"], team1["Name"]))
                        elif order == "opposite": errors_matchups.append((round_, team1["Name"], team2["Name"]))
            
    # error messages
    if not errors_matchups: return "All negotiations were completed successfully!"

    else: 
        
        error_message = "The following negotiations were unsuccessful:\n\n"

        for match in errors_matchups:
            error_message += f"- Round {match[0]} - {match[1]} ({name_roles[0]}) vs {match[2]} ({name_roles[1]});\n"

        return error_message
    

def create_all_error_chats(game_id, config_list, name_roles, order, values, starting_message, num_turns, negotiation_termination_message, summary_prompt, summary_termination_message):

    matches = get_error_matchups(game_id)

    teams1 = [i[1] for i in matches]
    teams2 = [i[2] for i in matches]

    unique_teams = set(tuple(item) for item in (teams1 + teams2))
    teams = [list(team) for team in unique_teams]
    
    team_info = create_agents(game_id, order, teams, values, name_roles, config_list, negotiation_termination_message)

    user = autogen.UserProxyAgent(
        name="User",
        llm_config=config_list,   
        human_input_mode = "NEVER",
        is_termination_msg=lambda msg: summary_termination_message in msg["content"],
        code_execution_config = {"work_dir": "repo", "use_docker": False}
    )

    summary_agent = autogen.AssistantAgent(
        name = "Summary_Agent",
        llm_config=config_list,
        human_input_mode="NEVER",
        is_termination_msg=lambda msg: summary_termination_message in msg["content"],
        system_message = f"You will be asked to answer a quick question regarding the outcome of a negotiation. You will be provided with the last 4 interactions of the negotiation and your answer should be based on them. Your answer must be of the type {summary_termination_message}, just adding the value agreed, as in '{summary_termination_message} x', x being the value. Make sure the conversation has ended with {negotiation_termination_message}, otherwise the negotiation has not been finalized and there was no agreement. If this happens, i.e., if the final message does not include {negotiation_termination_message}, your answer should be '{summary_termination_message} -1'."  
    )

    max_retries = 10

    errors_matchups = []
    
    for match in matches:
        
        team1 = next((team for team in team_info if team["Name"] == f"Class{match[1][0]}_Group{match[1][1]}"), None)
        team2 = next((team for team in team_info if team["Name"] == f"Class{match[2][0]}_Group{match[2][1]}"), None)

        if match[3] == 1:

            for attempt in range(max_retries):
                try:

                    if attempt%2==0: c = " "
                    else: c = ""
                        
                    starting_message += c
                    
                    if order == "same":

                        deal = create_chat(game_id, order, team1, team2, starting_message, num_turns, summary_prompt, match[0], user, summary_agent, summary_termination_message)

                        if deal == -1:
                            score1_team1 = 0
                            score1_team2 = 0

                        else:

                            if deal > team2["Value 2"]:
                                score1_team1 = 0
                                score1_team2 = 1

                            elif deal < team1["Value 1"]:
                                score1_team1 = 1
                                score1_team2 = 0

                            else:
                                score1_team2 = round((deal - team1["Value 1"])/(team2["Value 2"] - team1["Value 1"]), 4)
                                score1_team1 = 1 - score1_team2

                    elif order == "opposite":

                        deal = create_chat(game_id, order, team2, team1, starting_message, num_turns, summary_prompt, match[0], user, summary_agent, summary_termination_message)

                        if deal == -1:
                            score1_team1 = 0
                            score1_team2 = 0

                        else:

                            if deal > team2["Value 1"]:
                                score1_team1 = 0
                                score1_team2 = 1

                            elif deal < team1["Value 2"]:
                                score1_team1 = 1
                                score1_team2 = 0

                            else:
                                score1_team2 = round((deal - team1["Value 2"])/(team2["Value 1"] - team1["Value 2"]), 4)
                                score1_team1 = 1 - score1_team2

                    update_round_data(game_id, match[0], match[1][0], match[1][1], match[2][0], match[2][1], score1_team1, score1_team2, "same")

                    break

                except Exception:
                    
                    if attempt == max_retries - 1:
                    
                        errors_matchups.append((match[0], team1["Name"], team2["Name"]))

        if match[4] == 1:

            for attempt in range(max_retries):
                
                try:

                    if attempt%2==0: c = " "
                    else: c= ""

                    starting_message += c

                    if order == "same":

                        deal = create_chat(game_id, order, team2, team1, starting_message, num_turns, summary_prompt, match[0], user, summary_agent, summary_termination_message)

                        if deal == -1:
                            score2_team1 = 0
                            score2_team2 = 0

                        else:

                            if deal > team1["Value 2"]:
                                score2_team1 = 1
                                score2_team2 = 0

                            elif deal < team2["Value 1"]:
                                score2_team1 = 0
                                score2_team2 = 1

                            else:
                                score2_team1 = round((deal - team2["Value 1"])/(team1["Value 2"] - team2["Value 1"]), 4)
                                score2_team2 = 1 - score2_team1
                    
                    elif order == "opposite":

                        deal = create_chat(game_id, order, team1, team2, starting_message, num_turns, summary_prompt, match[0], user, summary_agent, summary_termination_message)

                        if deal == -1:
                            score2_team1 = 0
                            score2_team2 = 0

                        else:

                            if deal > team1["Value 1"]:
                                score2_team1 = 1
                                score2_team2 = 0

                            elif deal < team2["Value 2"]:
                                score2_team1 = 0
                                score2_team2 = 1

                            else:
                                score2_team1 = round((deal - team2["Value 2"])/(team1["Value 1"] - team2["Value 2"]), 4)
                                score2_team2 = 1 - score2_team1
                    
                    update_round_data(game_id, match[0], match[1][0], match[1][1], match[2][0], match[2][1], score2_team1, score2_team2, "opposite")
                    
                    break  

                except Exception:
                    
                    if attempt == max_retries - 1:
                    
                        errors_matchups.append(( match[0], team2["Name"], team1["Name"]))

    if not errors_matchups: return "All negotiations were completed successfully!"

    else: 
        
        error_message = "The following negotiations were unsuccessful:\n\n"

        for match in errors_matchups:
            error_message += f"- Round {match[0]} - {match[1]} ({name_roles[0]}) vs {match[2]} ({name_roles[1]});\n"

        return error_message