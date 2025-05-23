# AI Assistant Competition 

A learning platform for students to design, train, and deploy AI negotiators to compete in classical negotiation challenges (e.g., Ultimatum Game, Prisoner's Dilemma). This project is part of the course "AI Impact on Business" at Nova SBE, offering a user-friendly interface for students to design, train, and test their AI assistants, along with a leaderboard to track their performance.

---

## Project Overview

### Key Features
- **Multi-agent negotiation**: Host head‑to‑head matches across diverse game templates
- **Training & evaluation**: Iteratively refine your bot in a sandbox environment
- **Leaderboard & analytics**: Track performance metrics across rounds and semesters
- **Extensible architecture**: Plug in new games, roles, and scoring rules

### Technical Stack
- **Frontend**: Streamlit for interactive dashboard
- **AI Framework**: Microsoft's AutoGen for agent interactions
- **Database**: PostgreSQL for data persistence
- **Testing**: pytest for comprehensive test coverage

---

## Getting Started

### For Students
1. Read the [User Guide](documentation/USER_GUIDE.md) for:
   - Registration and account setup
   - Dashboard overview
   - Building and submitting bots
   - Testing and leaderboard
2. Register and create your account
3. Start building your first bot
4. Test in the playground
5. Submit to competitions

### For Developers
1. Read the [Developer Guide](documentation/DEVELOPER_GUIDE.md) for:
   - Setup and installation
   - Development environment
   - Running the application
   - Testing and contribution workflow
2. Set up your development environment
3. Initialize the database
4. Run the application locally

---

## Project Structure

```
ai-assistant-competition/
├── streamlit/              # Main application code
│   ├── 0_Home.py          # Streamlit entrypoint
│   ├── modules/           # Core functionality modules
│   │   ├── metrics_handler.py
│   │   ├── database_handler.py
│   │   ├── negotiations.py
│   │   ├── student_playground.py
│   │   ├── email_service.py
│   │   ├── drive_file_manager.py
│   │   ├── game_modes.py
│   │   └── schedule.py
│   ├── pages/            # Streamlit pages
│   └── .streamlit/       # Streamlit configuration
├── tests/                # Test suite
│   └── unit_tests.py     # Unit tests
├── documentation/        # User and developer guides
├── E-R_Model/           # Database entity-relationship models
├── .devcontainer/       # Development container configuration
├── Tables_AI_Negotiator.sql           # Database schema
├── Populate_Tables_AI_Negotiator.sql  # Sample data
├── requirements.txt      # Python dependencies
├── environment.yml      # Conda environment configuration
└── README.md            # Project overview
```

---

## Contributing

We welcome contributions! Please see our [Developer Guide](documentation/DEVELOPER_GUIDE.md#9-contribution-workflow) for details on:
- Setting up your development environment
- Code style and standards
- Testing requirements
- Pull request process

---

## References

- Horton, J. J. (2023). Large language models as simulated economic agents: What can we learn from homo silicus? (No. w31122). National Bureau of Economic Research.
- Manning, B. S., Zhu, K., & Horton, J. J. (2024). Automated social science: Language models as scientist and subjects (No. w32381). National Bureau of Economic Research.
- Diliara Zharikova, Daniel Kornev, Fedor Ignatov, Maxim Talimanchuk, Dmitry Evseev, Ksenya Petukhova, Veronika Smilga, Dmitry Karpov, Yana Shishkina, Dmitry Kosenko, and Mikhail Burtsev. 2023. DeepPavlov Dream: Platform for Building Generative AI Assistants. In Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 3: System Demonstrations), pages 599–607, Toronto, Canada. Association for Computational Linguistics.
- Wu, Q., Bansal, G., Zhang, J., Wu, Y., Zhang, S., Zhu, E., ... & Wang, C. (2023). Autogen: Enabling next-gen llm applications via multi-agent conversation framework.
