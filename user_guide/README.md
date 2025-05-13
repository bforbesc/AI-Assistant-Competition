# AI Assistant Competition – User Manual

Welcome! This guide walks **students** through every step of the AI Assistant Competition platform:

1. [Registration & Account Setup](registration.md)  
2. [Dashboard Overview](registration.md#dashboard-overview)  
3. [Building Your First Bot](bot_creation.md)  
4. [Submitting & Managing Bots](submission.md)  
5. [Playground & Pre-Submission Testing](playground.md)  
6. [Viewing Results & the Leaderboard](leaderboard.md)  

Each chapter includes examples, troubleshooting tips, and best practices. If you encounter any issues not covered here, please raise a ticket in the course’s issue tracker or ask your teaching assistant.

---

> **Tip:** Bookmark this folder locally or in your browser so you can quickly return to any section as you develop, test, and refine your negotiator bots.  
# 1. Registration & Dashboard Overview

Before you can deploy an AI negotiator, you need an account. This section covers:

- Account creation  
- Email verification  
- Dashboard tour  

---

## 1.1 Create Your Account

1. **Navigate** to `<platform-url>/register`.  
2. **Fill in**:
   - **University ID** (e.g. “s123456”)  
   - **Institutional email** (`@nova-sbe.pt`)  
   - **Password** (min 8 chars; include uppercase, lowercase, number)  
3. **Submit** and watch for a “Success” banner.

> **Example:**  
> If you see “User already exists,” it means you or a teammate used that ID before—contact support to reset your password.

---

## 1.2 Email Verification

Within **5 minutes** you’ll receive a confirmation link.  
- **Check spam** if you don’t see it.  
- **Resend** only if 10 minutes have passed to avoid lockouts.

Click the link to activate your account. You’ll be redirected to the login page.

---

## 1.3 Dashboard Tour

Once logged in, you’re presented with four panels:

1. **My Bots**  
   - Lists all your bots (Draft, Submitted, Tested)  
   - **Actions**: Edit, Delete, View logs  

2. **Create New Bot**  
   - Launches the Bot Wizard (see [Building Your First Bot](bot_creation.md)).  

3. **Competitions**  
   - Shows active tournaments, submission deadlines, and rules for each game template.

4. **Leaderboard**  
   - Live rankings across all games or filtered by template (see [Leaderboard](leaderboard.md) for interpretation).

> **Nuance:**  
> Instructors can open special “challenge windows.” If you don’t see a competition listed, check its start date or ask for access.

---

Proceed to [Building Your First Bot](bot_creation.md) when you’re ready to code your negotiator.  

# 2. Building Your First Bot

This chapter guides you through **designing**, **structuring**, and **uploading** your Python-based negotiation agent.

---

## 2.1 Choose a Game Template

At the top of the Bot Wizard, select from templates such as:

- **Ultimatum Game** (two-player division of resources)  
- **Prisoner’s Dilemma** (iterated cooperation vs. defection)  

Each template pre-loads:
- A **skeleton agent** you can extend  
- Default **scoring logic**  

---

## 2.2 Folder & File Structure

Your bot must adhere to this minimal layout:

my_bot/
├── agent.py # Entry point: must define class MyAgent
├── requirements.txt # third-party libraries (e.g. openai, numpy)
└── README.md # brief description & usage


- **`agent.py`** must export a class with:
  ```python
  class MyAgent(Negotiator):
      def propose(self, state) -> Offer:
          # state.game, state.history, state.role, etc.
          return Offer(…)
      def respond(self, offer: Offer) -> bool:
          # accept or reject
          return True
  
Dependencies in requirements.txt avoid runtime import errors.

Common Pitfall:
If your code uses extra modules (e.g. pandas), but you forget to list them, your bot will fail with ModuleNotFoundError during evaluation.

## 2.3 Example: A Fairness-First Agent

# agent.py
from competition import Negotiator, Offer

class MyAgent(Negotiator):
    def propose(self, state):
        total = state.game.pot
        # Always split evenly
        return Offer([total//2, total - total//2])

    def respond(self, offer):
        # Accept any split ≥ 40%
        my_share = offer.shares[state.role_index]
        return my_share >= 0.4 * state.game.pot
        
This simple heuristic often scores well in repeated-play Prisoner’s Dilemma by appearing fair but defecting if the opponent offers you less than 40%.

## 2.4 Finalizing & Naming

In the wizard, Upload your zipped my_bot/ folder—or point to a GitHub URL.

Assign a unique name, e.g. alice_fairbot_v1.

Click Save as Draft to verify no immediate errors.

Once uploaded, your bot appears under My Bots with status Draft. Proceed to testing or move directly to submission.


---

### `user_manual/submission.md`

```markdown
# 3. Submitting & Managing Your Bots

After drafting and testing, you’ll **submit** your bot to active competitions. This section covers:

- Submission workflow  
- Versioning  
- Common submission errors  

---

## 3.1 Submission Workflow

1. Under **My Bots**, locate your **Draft** entry.  
2. Click **Submit to Competition**.  
3. In the dialog:
   - **Select Competition** (e.g. “Ultimatum—Week 3”)  
   - **Review Rules & Deadline**  
4. Confirm—your bot status changes to **Submitted**.

> **Heads-up:**  
> Once submitted, you cannot edit that version. If you discover a bug, create a new draft version and re-submit before the deadline.

---

## 3.2 Versioning & Naming Conventions

- **Draft v1**, **Draft v2**, etc., appear in chronological order.  
- **Rename** your bot before submission to reflect the version:  
  > `alice_fairbot_v2_debugged`  

This helps you and reviewers distinguish performance changes across versions.

---

## 3.3 Submission Errors & Troubleshooting

| Error Message                               | Cause                                           | Remedy                              |
|---------------------------------------------|-------------------------------------------------|-------------------------------------|
| `Invalid ZIP structure`                     | Folder nested too deeply                        | Zip only the `my_bot` root          |
| `ModuleNotFoundError: openai`               | Missing in `requirements.txt`                   | Add `openai` and re-upload          |
| `Timeout during evaluation`                 | Bot took > 5 seconds to propose or respond      | Optimize code or simplify logic     |
| `RuleViolation: Illegal offer detected`     | Offer outside allowed bounds (per game template)| Check `Offer` constructor arguments |

---

## 3.4 Managing Multiple Submissions

- Use **Filters** (by template or date) in **My Bots** to compare performance of different versions side-by-side.  
- **Delete** unused drafts to keep your workspace clean.

When the competition window closes, only the **latest** Submitted version is evaluated.

---

Proceed to [Playground & Pre-Submission Testing](playground.md) for sandbox trials.  

# 4. Playground & Pre-Submission Testing

Before the official tournament, stress-test your bot in the **Playground**:

- Run head-to-head matches  
- Inspect detailed logs  
- Tune parameters  

---

## 4.1 Entering the Playground

1. From the top menu, select **Playground**.  
2. Choose any two bots:
   - Your own drafts  
   - Public sample bots (e.g. `fair_split_demo`, `tit_for_tat`)  
3. Select the **Game Template** and **Number of Rounds**.  
4. Click **Run**.

---

## 4.2 Interpreting Logs & Analytics

After execution, you’ll see:

- **Dialogue Transcript**  
  - Each offer, acceptance/rejection, timestamp  
  - Use **Export** (CSV) to analyze offline
- **Round-by-Round Scores**  
  - Your bot’s score vs. opponent’s  
  - Aggregate statistics (mean, variance)
- **Heatmaps & Charts** (if enabled)  
  - Cooperation rate over time  
  - Offer distributions

> **Insight:**  
> A bot that “learns” will often start conservatively then escalate offers. A flat line of 50/50 offers may be too predictable.

---

## 4.3 Iterative Tuning

1. **Adjust logic** in `agent.py`.  
2. **Increment version** in your bot name.  
3. **Re-upload** and **Re-test**.  

Repeat until you find a balance of **aggressiveness** vs. **fairness** that maximizes your average payoff.

---

## 4.4 Common Pitfalls

- **State Leakage:** If your bot stores state in global variables without clearing between runs, results will be skewed. Always initialize in `__init__`.  
- **Non-Determinism:** Randomized strategies can yield high variance. Seed your RNG (e.g. `random.seed(42)`) during testing to reproduce failures.

---

When satisfied, navigate back to **My Bots** and follow [Submission steps](submission.md).  

# 5. Viewing Results & the Leaderboard

Once competitions conclude, your performance is summarized in the **Leaderboard**:

- Ranking methodology  
- Metrics explained  
- Transcript archives  

---

## 5.1 Accessing the Leaderboard

- Click **Leaderboard** in the top menu.  
- Use filters:
  - **Game Template** (e.g. Ultimatum, Prisoner’s Dilemma)  
  - **Semester** or **Week**  
  - **Your cohort** vs. **All participants**

---

## 5.2 Understanding Metrics

| Column         | Definition                                                                  |
| -------------- | ----------------------------------------------------------------------------|
| **Rank**       | Your position by descending _average score_                                  |
| **Avg. Score** | Mean payoff per round across all matches                                    |
| **Win Rate**   | Percentage of matches where your bot’s total score > opponent’s             |
| **Std Dev**    | Variation in your scores (lower = more consistent)                          |
| **Matches**    | Number of head-to-head games played                                          |

> **Debate:**  
> Some argue that **Win Rate** overemphasizes outliers (one big win skews perception). Others prefer **Avg. Score** for its granular view. Consider both when evaluating strategies.

---

## 5.3 Drill-Down: Match Transcripts

- Click any **Rank** or **Avg. Score** cell to see detailed **dialogue logs**.  
- Export the full transcript as JSON or CSV for offline analysis.

> **Use Case:**  
> Compare your best-performing match (high score) with your worst to identify flip points where your logic failed.

---

## 5.4 Fairness & Tiebreakers

- **Ties** on Avg. Score are broken by **lower Std Dev** (more consistent bots rank higher).  
- If still tied, earliest submission wins (encourages early entry).

> **Exception:**  
> If you suspect a tiebreaker was applied incorrectly, file an issue immediately—timestamps and logs are immutable once the window closes.

---

## 5.5 Post-Tournament Reflection

1. **Review your code** alongside other published sample bots (if available).  
2. **Discuss** your strategy in the course forum:  
   - Why did you choose your acceptance threshold?  
   - How might you adapt in a real-world negotiation scenario?  
3. **Iterate** for the next competition window!

---

Congratulations on completing the user journey. We look forward to seeing your bots in action and your strategic insights in the debrief sessions!  
