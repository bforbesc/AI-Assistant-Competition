# AI-Assistant-Competition

This App was 

## Project Description 
This project aims to develop a platform for bot/AI Assistant competition that allows students to create and train their own bots to compete in various negotiation challenges. The initial focus will be on negotiation games, such as variations of the Ultimatum Game or the Prisoner's Dilemma. The platform shall provide a user-friendly interface for students to design, train, and test their Assistants, as well as a leaderboard to track their performance.

The project can be divided into 5 phases:
1. _Platform Development and Literature Review:_ Designing and creating a user-friendly interface for the AI Assistant competition platform, along with a relevant survey of the existing tools and approaches.
2. _Bot Creation and Strategy Definition:_ Providing functionalities that allow users on the platform and the results stored in a database for analysis.
4. _Performance Tracking and Leaderboard Development:_ Creating a leaderboard to rank bots based on their competition performance and display their status.
5. _Feedback and Improvement Cycle:_ Collecting user feedback for continuous improvements of the platform and the AI models.

The platform shall include the following functionalities:
1. User creation and management: Allow users to create accounts and manage their bots.
2. Bot registration and submission: Allow users to register and submit their bots for various challenges.
3. Negotiation game hosting: Conduct negotiation games on the platform and save the dialogue results for further analysis.
4. Leaderboard: Maintain and display a leaderboard to rank bots based on their performance.

This project aims to foster the development of negotiation skills and understanding of AI's role in strategic decision-making.

## Requirements for the Platform
### Functional Requirements
1. User Registration and Management: Users should be able to create accounts, log in, and manage their profiles.
2. Negotiation Game Hosting: The platform should host various negotiation games where users can submit their bots to compete.
   1. The administrator should be able to create and manage negotiation game scenarios.
   2. Negotiation games will have a defined structure, rules, and scoring system.
   3. Negotiation games will have a training and submission phase, followed by a competition phase, where bots compete against each other (e.g., in a tournament format). This will be an automated process triggered by the administrator.
3. Competition Hosting: The platform should host negotiation game competitions where users can submit their bots to compete against each other.
4. Bot Creation and Training: Users should be able to create and train their bots using various negotiation game scenarios.
5. Bot Submission: Users should be able to submit their trained bots to compete in negotiation games and competitions.
6. Leaderboard: The platform should maintain a leaderboard to rank bots based on their performance in negotiation games and competitions. Leaderboards should be per game and overall.

### Technical Requirements
1. Use streamlit for the front-end/dashboard
2. Use autogen from microsoft for the interaction among agents
3. Use a database to store user data, bot data, game data, and competition data; preferrable easy setup and maintenance


## References

- Horton, J. J. (2023). Large language models as simulated economic agents: What can we learn from homo silicus? (No. w31122). National Bureau of Economic Research.
- Manning, B. S., Zhu, K., & Horton, J. J. (2024). Automated social science: Language models as scientist and subjects (No. w32381). National Bureau of Economic Research.
- Diliara Zharikova, Daniel Kornev, Fedor Ignatov, Maxim Talimanchuk, Dmitry Evseev, Ksenya Petukhova, Veronika Smilga, Dmitry Karpov, Yana Shishkina, Dmitry Kosenko, and Mikhail Burtsev. 2023. DeepPavlov Dream: Platform for Building Generative AI Assistants. In Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 3: System Demonstrations), pages 599–607, Toronto, Canada. Association for Computational Linguistics.
- Wu, Q., Bansal, G., Zhang, J., Wu, Y., Zhang, S., Zhu, E., ... & Wang, C. (2023). Autogen: Enabling next-gen llm applications via multi-agent conversation framework.



## TODO

- **Improve documentation** - Create a How-to install document and document the code of the App, namely the most critical parts regarding 
- **Unit Tests** - Implement unit tests to ensure no breaking changes are introduced when performing new developments
- **Refactor backend code** 
- **Improve frontend**
- **Implement a student playground** - Allow students to test their agents in the platform

