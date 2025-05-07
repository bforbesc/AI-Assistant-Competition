# AI-Assistant-Competition

This App was developed with the goal of creating a platform for students to create and train their own AI assistants (bots) to compete in various negotiation challenges. The project is part of the course AI Impact on Business at Nova SBE, and the initial focus is on negotiation games, such as variations of the Ultimatum Game or the Prisoner's Dilemma. The platform provides a user-friendly interface for students to design, train, and test their Assistants, as well as a leaderboard to track their performance.

## 📖 Documentation

All of the step-by-step guides live in two places:

- **User Guide**  
  Detailed instructions for participants—account setup, bot development, submission workflow, sandbox testing, and leaderboard interpretation—can be found in  
  `user_guide/README.md`.  

- **Developer Guide**  
  Everything a contributor needs—DevContainer configuration, environment bootstrapping, database initialization, testing and contribution conventions—is documented in  
  `.devcontainer/README.md`.  

---

## 🗂 Repository Layout

At the top level you’ll see:

├── .devcontainer/ # DevContainer config + Developer Guide
├── app/ # Streamlit UI, negotiation-agent interfaces
├── services/ # Game orchestration & scoring logic
├── db/ # Schema, migrations & seed data
├── tests/ # Unit & integration tests
├── user_guide/ # Participant documentation + User Guide
└── README.md # This overview


---

## 🚀 Quickstart

### For Developers  
1. Open this folder in VS Code.  
2. When prompted, **Reopen in Container**.  
3. Inside the container, follow the steps in `.devcontainer/README.md`.

### For Participants  
1. Read `user_guide/README.md` to learn how to register, build and submit your bot, test it in the playground, and track your ranking.

---

Happy negotiating!  
