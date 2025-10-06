import streamlit as st
import requests
import pandas as pd
import mysql.connector

#Actual url of third party API
LIVE_url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"
SERIES_url = "https://cricbuzz-cricket.p.rapidapi.com/series/v1/international"
SCORECARD_base_url = "https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{match_id}/scard"
PLAYER_SEARCH_URL = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/search"
PLAYER_INFO_URL = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}"
PLAYER_BATTING_url = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}/batting"
PLAYER_BOWLING_url = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}/bowling"

HEADERS = {
	"x-rapidapi-key": "f8bf8dacb2mshd6096437314f303p1db366jsnafa146b2676c",
	"x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}


# --- Page Setup ---
st.set_page_config(
    page_title="🏏Cricbuzz LiveStats Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------- MySQL Setup -------------------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Revdesi@2302",
        database="cricbuzz_db"
    )

# --- Navigation (Sidebar) ---

st.sidebar.title("🏏 Cricket Dashboard")
page = st.sidebar.selectbox(
    "Choose a page:",
    ["🔴Live Scores", "👤Player Stats","SQL Analytics", "CRUD Operations"]
)
st.sidebar.markdown("___")

#page Description
if page == "🔴Live Scores":
    st.sidebar.info("""
    **Live Scores Page:**
    - Real-time match data
    - Detailed scorecards
    - series information
    - Interactive match selection                
""")
elif page == "👤Player Stats":
    st.sidebar.info("""
    **Player Stats Page:**
    -Search any Cricket player
    -Career statistics across formats
    -comprehensive player profiles               
""")
elif page == "📊 SQL Analytics":
    st.sidebar.info("""
    **SQl Analytics Page:**
    - 20 practice query execution
    - Real Cricket Database
    - Download results as csv
    """) 
else:
    st.sidebar.info("""
    **CRUD Operation page**
    - Create new Player records
    - Update Player information
    - Delete Player records
    """)

# # --- API Functions ---
@st.cache_data
def fetch_live_data():
    response = requests.get(LIVE_url, headers=HEADERS)
    return response.json() if response.status_code == 200 else None

@st.cache_data
def fetch_series_data():
    response = requests.get(SERIES_url, headers=HEADERS)
    return response.json() if response.status_code == 200 else None


@st.cache_data(ttl=60) # Cache for 60 seconds since scores update frequently
def fetch_scorecard(match_id):
    """Fetches the detailed scorecard for a given match ID."""
    # 👇 CORRECTED URL construction using the template
    scorecard_url = SCORECARD_base_url.format(match_id=match_id)
    
    try:
        response = requests.get(url=scorecard_url, headers=HEADERS)
        if response.status_code == 200:
            return response.json()
        else:
            # Include the URL in the error message for easy debugging
            st.error(f"❌ Failed to fetch scorecard (Status: {response.status_code}). URL: {scorecard_url}. Check API Key and Match ID.")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"🌐 Network error while fetching scorecard: {e}")
        return None

@st.cache_data
def search_player(name):
    try:
        res = requests.get(PLAYER_SEARCH_URL, headers=HEADERS, params={"plrN": name})
        return res.json() if res.status_code == 200 else None
    except:
        return None

@st.cache_data
def fetch_player_info(player_id):
    try:
        res = requests.get(PLAYER_INFO_URL.format(player_id=player_id), headers=HEADERS)
        return res.json() if res.status_code == 200 else None
    except:
        return None

# ------------------- API Functions -------------------
@st.cache_data
def fetch_player_batting(player_id):
    try:
        res = requests.get(PLAYER_BATTING_url.format(player_id=player_id), headers=HEADERS)
        return res.json() if res.status_code == 200 else None
    except:
        return None

@st.cache_data
def fetch_player_bowling(player_id):
    try:
        res = requests.get(PLAYER_BOWLING_url.format(player_id=player_id), headers=HEADERS)
        return res.json() if res.status_code == 200 else None
    except:
        return None


# ------------------ Scorecard Display ------------------ #
def display_tabular_scorecard(scorecard_data):
    # Handle both "scoreCard" and "scorecard"
    innings_data = scorecard_data.get("scoreCard") or scorecard_data.get("scorecard")

    if not innings_data:
        st.warning("📢 Detailed scorecard is not yet available for this match.")
        st.info("""
        Possible reasons:
        - Match has not started yet
        - Match is in progress but scorecard data not published
        - API delay in updating scorecard
        """)
        return

    innings_tabs = st.tabs([f"Innings {i+1}" for i in range(len(innings_data))])

    for idx, inning in enumerate(innings_data):
        with innings_tabs[idx]:
            team = inning.get("batTeamDetails", {}).get("batTeamName", "Unknown Team")
            st.subheader(f"🏏 {team} Batting")

            # Batting table
            batsmen = inning.get("batTeamDetails", {}).get("batsmenData", {})
            if batsmen:
                st.table([
                    {
                        "Batsman": b.get("batName", ""),
                        "Runs": b.get("runs", 0),
                        "Balls": b.get("balls", 0),
                        "4s": b.get("fours", 0),
                        "6s": b.get("sixes", 0),
                        "SR": b.get("strikeRate", 0)
                    }
                    for b in batsmen.values()
                ])
            else:
                st.info("No batting data available yet.")

            # Bowling table
            st.subheader("🎯 Bowling Against")
            bowlers = inning.get("bowlTeamDetails", {}).get("bowlersData", {})
            if bowlers:
                st.table([
                    {
                        "Bowler": b.get("bowlName", ""),
                        "Overs": b.get("overs", 0),
                        "Mdns": b.get("maidens", 0),
                        "Runs": b.get("runs", 0),
                        "Wkts": b.get("wickets", 0),
                        "Econ": b.get("economy", 0)
                    }
                    for b in bowlers.values()
                ])
            else:
                st.info("No bowling data available yet.")

            # Extras
            extras = inning.get("extrasData", {})
            if extras:
                st.info(
                    f"**Extras:** {extras.get('total', 0)} "
                    f"(b {extras.get('byes', 0)}, lb {extras.get('legByes', 0)}, "
                    f"nb {extras.get('noBalls', 0)}, wd {extras.get('wides', 0)})"
                )

            # Fall of Wickets
            fow = inning.get("wicketsData", [])
            if fow:
                st.subheader("📉 Fall of Wickets")
                st.table([
                    {
                        "Batsman": w.get("batName", ""),
                        "Score": w.get("scoreAtDismissal", ""),
                        "Over": w.get("overNum", "")
                    }
                    for w in fow
                ])
            else:
                st.info("No fall-of-wickets data yet.")



# PAGE 1 LIVE SCORE

if page == "🔴Live Scores":
    st.title("🏏Cricbuzz LiveStats Dashboard")
    
    #Fetch Data
    with st.spinner("Fetching live cricket data..."):
        live_data = fetch_live_data()
        series_data = fetch_series_data()
        
    # Build Series Map
    series_map = {}
    if series_data and "seriesMapProto" in series_data:
        for category in series_data.get("seriesMapProto", []):
            for s in category.get("series", []):
                series_map[s["id"]] = {
                    "series_name": s.get("name", "unknown Series"),
                    "host_country": s.get("hostCountry", "unknown"),
                    "season": s.get("season", "unknown"),
                    "match_type": s.get("matchType", "unknown")
                }
    #Build Match List
    matches =[]
    if live_data and "typeMatches" in live_data:
        for type_match in live_data.get("typeMatches", []):
            match_type = type_match.get("matchType", "unknown")
            
            for series_match in type_match.get("seriesMatches", []):
                if "seriesAdWrapper" in series_match:
                    series_data_item = series_match["seriesAdWrapper"]
                elif "series" in series_match:
                    series_data_item = series_match
                else:
                    continue
                    
                series_id = series_data_item.get("seriesId")
                series_name = series_data_item.get("seriesName", "unknown Series")
                
                for match in series_data_item.get("matches", []):
                    info = match.get("matchInfo", {})
                    score = match.get("matchScore", {})
                    
                    match_id = info.get("matchId")
                    if not match_id:
                        continue
                        
                    team1 = info.get("team1", {}).get("teamName", "Team 1")
                    team2 = info.get("team2", {}).get("teamName", "Team 2")
                    match_desc = info.get("matchDesc", "")
                    state = info.get("state", "")
                    
                    status_text = f" ({state})" if state else ""
                    match_label = f"{team1} vs{team2} - {match_desc}{status_text}"
                    
                    matches.append({
                        "label": match_label,
                        "info": info,
                        "score": score,
                        "series_id": series_id,
                        "series_name": series_name,
                        "match_id": match_id,
                        "match_type": match_type
                    })
                    
                    
    #No matches check
    if not matches:
        st.warning("⚠️ No live matches found at the moment.")
        st.info("This could be because:")
        st.write("- No matches are currently live")
        st.write("- API rate limits have been reached")
        st.write("-Network connectivity issues")

        if st.checkbox("Show debug information"):
            st.json(live_data)
        st.stop()
        
    #Select Match
    st.markdown("### 🎯select a Match")
    selected_label = st.selectbox("Available Matches:", [m["label"] for m in matches])
    
    selected_match = None
    for match in matches:
        if match["label"] == selected_label:
            selected_match = match
            break
    
    if selected_match:
        info = selected_match["info"]
        score = selected_match["score"]
        series_id = selected_match["series_id"]
        match_id = selected_match["match_id"]
        
        #Display Match Info
        st.markdown(f"### 🏏 {info.get('team1', {}).get('teamName', '')} vs {info.get('team2', {}).get('teamName', '')}")
        st.write(f"🗒️ **Match:** {info.get('matchDesc', 'N/A')}")
        st.write(f"🏆 **Format:** {info.get('matchFormat', 'N/A')}")
        st.write(f"📬 **Venue:** {info.get('venueInfo', {}).get('ground', 'Unknown')}")
        st.write(f" **City:** {info.get('venueInfo', {}).get('city', 'Unknown')}")
        st.write(f" **State:** {info.get('state', 'N/A')}")
        st.write(f"📢 **Status:** {info.get('status', 'No Status')}")

        # Scores
        st.markdown("### 🏏 Current Scores")

        team1_scores = score.get("team1Score", {})
        team2_scores = score.get("team2Score", {})

        if team1_scores or team2_scores:
            score_col1, score_col2 = st.columns(2)
            # Team 1 scores
            with score_col1:
                st.markdown(f"**{team1}**")
                for inning_key in ["inngs1", "inngs2"]:
                    if inning_key in team1_scores:
                        inning = team1_scores[inning_key]
                        runs = inning.get("runs", 0)
                        wickets = inning.get("wickets", 0)
                        overs = inning.get("overs", 0)
                        st.write(f"{inning_key}: {runs}/{wickets} ({overs} ov)")

            # Team 2 scores
            with score_col2:
                st.markdown(f"**{team2}**")
                for inning_key in ["inngs1", "inngs2"]:
                    if inning_key in team2_scores:
                        inning = team2_scores[inning_key]
                        runs = inning.get("runs", 0)
                        wickets = inning.get("wickets", 0)
                        overs = inning.get("overs", 0)
                        st.write(f"{inning_key}: {runs}/{wickets} ({overs} ov)")
        else:
            st.warning("No score data available yet for this match.")
            
            
        st.markdown("### 📊 Detailed Scorecard")
        if st.button("🔄 Refresh Scorecard"):
            scorecard_data = fetch_scorecard(match_id)
            if scorecard_data:
                display_tabular_scorecard(scorecard_data)
            with st.expander("🛠 Raw JSON Data (For Debugging)"):
                st.json(scorecard_data)
        else:
            st.warning("⚠️ Detailed scorecard is not available yet.")


# ------------------- PAGE 2: Player Stats ------------------- #
if page == "👤Player Stats":
    st.title("👤 Player Stats")

    # Search input with placeholder and message
    st.info("🔍 Enter full player name to search (e.g., Virat Kohli, Babar Azam)")
    player_name = st.text_input("Enter Player Name:", placeholder="e.g., Virat Kohli")

    # Helper function to safely convert stats to DataFrame
    def stats_to_dataframe(stats):
        """
        Converts the API stat 'values' into a pandas DataFrame.
        Works for nested dicts or flat dicts.
        """
        if not stats:
            return pd.DataFrame()

        # 'stats' could be a dict
        if isinstance(stats, dict):
            return pd.DataFrame(list(stats.items()), columns=["Stat", "Value"])

        # 'stats' could be a list of dicts (e.g., per match type)
        if isinstance(stats, list):
            df_list = []
            for s in stats:
                values = s.get("values", {})
                if isinstance(values, dict):
                    temp_df = pd.DataFrame(list(values.items()), columns=["Stat", "Value"])
                    temp_df["Match Type"] = s.get("matchType", "")
                    df_list.append(temp_df)
            if df_list:
                return pd.concat(df_list, ignore_index=True)

        # fallback: try converting to DataFrame directly
        return pd.DataFrame(stats)

    # Search player
    if player_name:
        search_results = search_player(player_name)
        if search_results and "player" in search_results:
            players = search_results["player"]
            if not players:
                st.warning("No players found. Make sure you entered the full name correctly.")
            else:
                # Player selection
                options = {f"{p['name']} ({p.get('teamName','')})": p["id"] for p in players}
                selected = st.selectbox("Select Player:", list(options.keys()))
                player_id = options[selected]

                # Fetch basic info
                player_info = fetch_player_info(player_id)
                if player_info:
                    # --- Player Header Info ---
                    st.subheader(player_info.get("name", "Unknown"))
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("🏳️ Country", player_info.get("country", "N/A"))
                    col2.metric("🎭 Role", player_info.get("role", "N/A"))
                    col3.metric("📝 Batting", player_info.get("bat", "N/A"))
                    col4.metric("🎯 Bowling", player_info.get("bowl", "N/A"))

                    st.markdown("---")

                    # --- Show stats on demand ---
                    st.write("### 📊 View Career Stats")
                    stat_choice = st.radio(
                        "Select Stat Type:",
                        ["Select...", "Batting Stats", "Bowling Stats"]
                    )

                    if stat_choice == "Batting Stats":
                        batting_stats = fetch_player_batting(player_id)
                        if batting_stats and "values" in batting_stats:
                            st.markdown(f"#### 🏏 Batting Stats for {player_info.get('name','')}")
                            df = stats_to_dataframe(batting_stats["values"])
                            if not df.empty:
                                st.dataframe(df)
                            else:
                                st.info("No batting stats available for this player.")
                        else:
                            st.info("No batting stats available for this player.")

                    elif stat_choice == "Bowling Stats":
                        bowling_stats = fetch_player_bowling(player_id)
                        if bowling_stats and "values" in bowling_stats:
                            st.markdown(f"#### 🎯 Bowling Stats for {player_info.get('name','')}")
                            df = stats_to_dataframe(bowling_stats["values"])
                            if not df.empty:
                                st.dataframe(df)
                            else:
                                st.info("No bowling stats available for this player.")
                        else:
                            st.info("No bowling stats available for this player.")

                else:
                    st.error("Player info not available")
        else:
            st.warning("No players found")



# ------------------- PAGE 3: SQL Analytics ------------------- #
if page == "SQL Analytics":
    st.title("📊 SQL Analytics")
    st.info("Select a predefined SQL query from the dropdown to get results from your cricket database.")

    # --- Predefined SQL queries ---
    sql_questions = {
        "1. List all players": "SELECT * FROM players LIMIT 50;",
        "2. Top 10 run scorers": "SELECT player_name, runs FROM players ORDER BY runs DESC LIMIT 10;",
        "3. Top 10 wicket takers": "SELECT player_name, wickets FROM players ORDER BY wickets DESC LIMIT 10;",
        "4. List all teams": "SELECT * FROM teams;",
        "5. Team performance ranking": "SELECT * FROM team_performance ORDER BY wins DESC;",
        "6. Matches played by India": "SELECT * FROM matches WHERE team1_id=1 OR team2_id=1;",
        "7. Matches with no result": "SELECT * FROM matches WHERE result LIKE '%no result%';",
        "8. Players with highest strike rate": "SELECT player_name, strike_rate FROM players ORDER BY strike_rate DESC LIMIT 10;",
        "9. Players with best economy rate": "SELECT player_name, economy FROM players ORDER BY economy ASC LIMIT 10;",
        "10. Players with best batting average": "SELECT player_name, batting_average FROM players ORDER BY batting_average DESC LIMIT 10;",
        "11. Matches won by India": "SELECT * FROM matches WHERE result LIKE 'India%won%';",
        "12. Matches won by Australia": "SELECT * FROM matches WHERE result LIKE 'Australia%won%';",
        "13. Matches won by Nepal": "SELECT * FROM matches WHERE result LIKE 'Nepal%won%';",
        "14. Matches at a specific venue": "SELECT * FROM matches WHERE venue_id=1;",
        "15. Players in top 10 for runs and wickets": "SELECT player_name, runs, wickets FROM players ORDER BY runs DESC, wickets DESC LIMIT 10;",
        "16. All series": "SELECT * FROM series;",
        "17. Matches in last 30 days": "SELECT * FROM matches WHERE match_date >= CURDATE() - INTERVAL 30 DAY;",
        "18. Players by country": "SELECT player_name, country FROM players ORDER BY country;",
        "19. Players with 50+ runs in a match": "SELECT * FROM match_scores WHERE runs >=50;",
        "20. Players with 5+ wickets in a match": "SELECT * FROM match_scores WHERE wickets >=5;",
        "21. Teams with most wins": "SELECT team_name, wins FROM team_performance ORDER BY wins DESC LIMIT 5;",
        "22. Teams with most losses": "SELECT team_name, losses FROM team_performance ORDER BY losses DESC LIMIT 5;",
        "23. Players with centuries": "SELECT player_name, hundreds FROM players WHERE hundreds >0 ORDER BY hundreds DESC;",
        "24. Players with fifties": "SELECT player_name, fifties FROM players WHERE fifties >0 ORDER BY fifties DESC;",
        "25. Upcoming matches": "SELECT * FROM matches WHERE match_date >= CURDATE() ORDER BY match_date ASC;"
    }

    # --- Dropdown for selection ---
    selected_question = st.selectbox("Choose a SQL Query:", list(sql_questions.keys()))

    # --- Execute and display results ---
    if selected_question:
        query = sql_questions[selected_question]
        try:
            # Use cached connection for performance
            conn = get_db_connection()
            df = pd.read_sql(query, conn)
            conn.close()

            if df.empty:
                st.warning("⚠️ No records returned for this query.")
            else:
                st.subheader("Query Result")
                st.write(f"**Executed Query:** `{query}`")
                st.dataframe(df, use_container_width=True)

                # CSV download button
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Download Result as CSV",
                    data=csv,
                    file_name="query_result.csv",
                    mime="text/csv"
                )

        except mysql.connector.Error as e:
            st.error(f"Database Error: {e}")
        except Exception as e:
            st.error(f"Unexpected Error: {e}")



# ------------------- PAGE 4: CRUD Operations ------------------- #
if page == "CRUD Operations":
    st.title("📝 CRUD Operations")
    st.info("Create, Read, Update, or Delete player records in your cricket database.")

    operation = st.selectbox("Choose Operation:", ["Create", "Read", "Update", "Delete"])

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # ------------------- CREATE ------------------- #
        if operation == "Create":
            st.subheader("➕ Add New Player")
            with st.form("create_player_form"):
                player_name = st.text_input("Player Name")
                matches = st.number_input("Matches", min_value=0)
                innings = st.number_input("Innings", min_value=0)
                runs = st.number_input("Runs", min_value=0)
                avg_runs = st.number_input("Average Runs", min_value=0.0, step=0.1)
                submitted = st.form_submit_button("Insert Player")

                if submitted:
                    if not player_name.strip():
                        st.warning("Please enter a player name.")
                    else:
                        cursor.execute("""
                            INSERT INTO most_runs_stats (player_name, matches, innings, runs, avg_runs)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (player_name, matches, innings, runs, avg_runs))
                        conn.commit()
                        st.success(f"✅ Player '{player_name}' inserted successfully.")

        # ------------------- READ ------------------- #
        elif operation == "Read":
            st.subheader("📋 View All Players")
            cursor.execute("SELECT * FROM most_runs_stats")
            rows = cursor.fetchall()
            if rows:
                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No records found.")

        # ------------------- UPDATE ------------------- #
        elif operation == "Update":
            st.subheader("✏️ Update Player Info")
            cursor.execute("SELECT player_id, player_name FROM most_runs_stats")
            players = cursor.fetchall()

            if not players:
                st.info("No players available to update.")
            else:
                player_options = {f"{p['player_name']} (ID:{p['player_id']})": p['player_id'] for p in players}
                selected = st.selectbox("Select Player to Update:", list(player_options.keys()))
                player_id = player_options[selected]

                with st.form("update_player_form"):
                    player_name = st.text_input("Player Name")
                    matches = st.number_input("Matches", min_value=0)
                    innings = st.number_input("Innings", min_value=0)
                    runs = st.number_input("Runs", min_value=0)
                    avg_runs = st.number_input("Average Runs", min_value=0.0, step=0.1)
                    submitted = st.form_submit_button("Update Player")

                    if submitted:
                        cursor.execute("""
                            UPDATE most_runs_stats
                            SET player_name=%s, matches=%s, innings=%s, runs=%s, avg_runs=%s
                            WHERE player_id=%s
                        """, (player_name, matches, innings, runs, avg_runs, player_id))
                        conn.commit()
                        if cursor.rowcount > 0:
                            st.success(f"✅ Player ID {player_id} updated successfully.")
                        else:
                            st.warning("⚠️ No player found with this ID.")

        # ------------------- DELETE ------------------- #
        elif operation == "Delete":
            st.subheader("🗑 Delete Player")
            cursor.execute("SELECT player_id, player_name FROM most_runs_stats")
            players = cursor.fetchall()

            if not players:
                st.info("No players available to delete.")
            else:
                player_options = {f"{p['player_name']} (ID:{p['player_id']})": p['player_id'] for p in players}
                selected = st.selectbox("Select Player to Delete:", list(player_options.keys()))
                player_id = player_options[selected]

                if st.button("Delete Player"):
                    cursor.execute("DELETE FROM most_runs_stats WHERE player_id=%s", (player_id,))
                    conn.commit()
                    if cursor.rowcount > 0:
                        st.success(f"✅ Player ID {player_id} deleted successfully.")
                    else:
                        st.warning("⚠️ No player found with this ID.")

        conn.close()

    except mysql.connector.Error as e:
        st.error(f"Database Error: {e}")
    except Exception as e:
        st.error(f"Unexpected Error: {e}")
