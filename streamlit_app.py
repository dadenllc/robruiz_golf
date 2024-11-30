import streamlit as st
import random
import pandas as pd
import sqlite3

# Tournament Information
tournament_name = "Rob Ruiz Birthday Golf Tournament"
password = "RobIsGreat2024!@"

# Initial Player Names
player_names = [
    "Alice Johnson", "Bob Smith", "Charlie Brown", "David Wilson", "Ella Thompson",
    "Frank Harris", "Grace Lee", "Henry Martinez", "Isla Davis", "Jack Miller",
    "Katie White", "Liam Scott", "Mia Lewis", "Noah Walker", "Olivia Young"
]

# Randomly assign players to teams
random.shuffle(player_names)
teams = {
    "Team A": player_names[:5],
    "Team B": player_names[5:10],
    "Team C": player_names[10:]
}

# Anonymize player names
anon_names = [f"Player {i+1}" for i in range(len(player_names))]
anon_teams = {
    "Team A": anon_names[:5],
    "Team B": anon_names[5:10],
    "Team C": anon_names[10:]
}

# Create a SQLite database to store scores
conn = sqlite3.connect('golf_tournament.db')
c = conn.cursor()

# Create scores table if it does not exist
c.execute('''
CREATE TABLE IF NOT EXISTS scores (
    player TEXT,
    team TEXT,
    round_1 INTEGER,
    round_2 INTEGER,
    round_3 INTEGER
)
''')
conn.commit()

# Insert initial player data if table is empty
c.execute("SELECT COUNT(*) FROM scores")
if c.fetchone()[0] == 0:
    for i, player in enumerate(anon_names):
        team = "Team A" if i < 5 else "Team B" if i < 10 else "Team C"
        c.execute("INSERT INTO scores (player, team, round_1, round_2, round_3) VALUES (?, ?, ?, ?, ?)", (player, team, 0, 0, 0))
    conn.commit()

# Load scores into a DataFrame
scores_df = pd.read_sql_query("SELECT * FROM scores", conn)

# Streamlit App
st.title(tournament_name)

# Display Tournament Rules
st.header("Tournament Rules")
st.write(
    f"""
    Welcome to the {tournament_name}! This is a special "blind" tournament where players are randomly assigned to teams each day, 
    but the team compositions are kept secret until the very end. Each player will play 3 rounds of golf, and their scores will be 
    tracked anonymously throughout the tournament. At the end of the tournament, the teams will be revealed and the winning team 
    will be announced!

    Players are encouraged to focus on their individual performance without knowing their teammates, ensuring a fair and fun competition for everyone.
    The leaderboard will display anonymized player scores until the big reveal at the end of the tournament. Good luck, and may the best team win!
    """
)

# Password-protected Admin Section for Score Entry
st.header("Admin: Enter Scores")
admin_password = st.text_input("Enter Admin Password", type="password")

if admin_password == password:
    st.success("Access Granted. You can now enter the scores.")
    for i in range(len(scores_df)):
        scores_df.at[i, "round_1"] = st.number_input(f"{scores_df.at[i, 'player']} - Round 1 Score", min_value=0, step=1, value=scores_df.at[i, "round_1"])
        scores_df.at[i, "round_2"] = st.number_input(f"{scores_df.at[i, 'player']} - Round 2 Score", min_value=0, step=1, value=scores_df.at[i, "round_2"])
        scores_df.at[i, "round_3"] = st.number_input(f"{scores_df.at[i, 'player']} - Round 3 Score", min_value=0, step=1, value=scores_df.at[i, "round_3"])

    # Save scores to the database
    for i in range(len(scores_df)):
        c.execute("UPDATE scores SET round_1 = ?, round_2 = ?, round_3 = ? WHERE player = ?", 
                  (scores_df.at[i, "round_1"], scores_df.at[i, "round_2"], scores_df.at[i, "round_3"], scores_df.at[i, "player"]))
    conn.commit()
    st.write("Scores have been updated and saved.")

# Leaderboard Section
st.header("Leaderboard")

# Calculate Total Scores
scores_df["Total Score"] = scores_df[["round_1", "round_2", "round_3"]].sum(axis=1)
team_scores = scores_df.groupby("team")["Total Score"].sum().reset_index()

# Display Team Leaderboard
st.subheader("Team Leaderboard")
st.table(team_scores.sort_values(by="Total Score"))

# Display Individual Scores (Anonymized)
st.subheader("Individual Scores (Anonymized)")
st.table(scores_df[["player", "team", "Total Score"]].sort_values(by="Total Score"))

# Password-protected Reveal Names Section
st.header("Reveal Player Names")
reveal_password = st.text_input("Enter Password to Reveal Names", type="password", key="reveal")

if reveal_password == password:
    st.success("Access Granted. Revealing player names.")
    # Display Scores with Real Names
    real_names_df = scores_df.copy()
    real_names_df["player"] = player_names
    st.table(real_names_df[["player", "team", "Total Score"]].sort_values(by="Total Score"))
else:
    st.write("Enter the correct password to reveal player names.")

# Close the database connection
conn.close()
