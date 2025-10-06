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
elif page == "📊SQL Analytics":
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
def fetch_live_data(ttl=300):
    response = requests.get(LIVE_url, headers=HEADERS)
    return response.json() if response.status_code == 200 else None

@st.cache_data
def fetch_series_data(ttl=300):
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

# PAGE 1 LIVE SCORE

if page == "🔴Live Scores":
    st.title("🏏 Cricbuzz LiveStats Dashboard")
    
    # Fetch Data
    with st.spinner("Fetching live cricket data..."):
        live_data = fetch_live_data()
        series_data = fetch_series_data()
        
    # Build Series Map
    series_map = {}
    if series_data and "seriesMapProto" in series_data:
        for category in series_data.get("seriesMapProto", []):
            for s in category.get("series", []):
                series_map[s["id"]] = {
                    "series_name": s.get("name", "Unknown Series"),
                    "host_country": s.get("hostCountry", "Unknown"),
                    "season": s.get("season", "Unknown"),
                    "match_type": s.get("matchType", "Unknown")
                }

    # Build Match List
    matches = []
    if live_data and "typeMatches" in live_data:
        for type_match in live_data.get("typeMatches", []):
            match_type = type_match.get("matchType", "Unknown")
            
            for series_match in type_match.get("seriesMatches", []):
                if "seriesAdWrapper" in series_match:
                    series_data_item = series_match["seriesAdWrapper"]
                elif "series" in series_match:
                    series_data_item = series_match
                else:
                    continue
                    
                series_id = series_data_item.get("seriesId")
                series_name = series_data_item.get("seriesName", "Unknown Series")
                
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
                    match_label = f"{team1} vs {team2} - {match_desc}{status_text}"

                    # 🎨 Add color badge for match type
                    format_color = {
                        "T20": "#007bff",   # Blue
                        "T20I": "#007bff",
                        "ODI": "#28a745",   # Green
                        "TEST": "#dc3545",  # Red
                    }.get(match_type.upper(), "#6c757d")

                    match_label_colored = (
                        f"{match_label} "
                        f"<span style='background-color:{format_color}; "
                        f"color:white; padding:3px 8px; border-radius:6px; "
                        f"font-size:12px;'> {match_type} </span>"
                    )

                    matches.append({
                        "label": match_label,
                        "label_colored": match_label_colored,
                        "info": info,
                        "score": score,
                        "series_id": series_id,
                        "series_name": series_name,
                        "match_id": match_id,
                        "match_type": match_type
                    })
                    
    # No matches check
    if not matches:
        st.warning("⚠️ No live matches found at the moment.")
        st.info("This could be because:")
        st.write("- No matches are currently live")
        st.write("- API rate limits have been reached")
        st.write("- Network connectivity issues")

        if st.checkbox("Show debug information"):
            st.json(live_data)
        st.stop()
        
    # Select Match
    st.markdown("### 🎯 Select a Match")

    # Show colored labels in dropdown (display HTML)
    options_html = [m["label_colored"] for m in matches]
    options_text = [m["label"] for m in matches]

    # Workaround: Streamlit selectbox doesn't render HTML, so show below manually
    selected_label = st.selectbox("Available Matches:", options_text)

    # Find selected match
    selected_match = next((m for m in matches if m["label"] == selected_label), None)
    
    if selected_match:
        info = selected_match["info"]
        score = selected_match["score"]
        series_id = selected_match["series_id"]
        match_id = selected_match["match_id"]
        match_type = selected_match["match_type"]

        # 🎨 Colored format badge setup
        format_color = {
            "T20": "#007bff",
            "T20I": "#007bff",
            "ODI": "#28a745",
            "TEST": "#dc3545",
        }.get(match_type.upper(), "#6c757d")
        
        # Display Match Info
        st.markdown(f"### 🏏 {info.get('team1', {}).get('teamName', '')} vs {info.get('team2', {}).get('teamName', '')}")
        st.write(f"🗒️ **Match:** {info.get('matchDesc', 'N/A')}")

        # ✅ Fixed match format line with color badge
        match_format = info.get("matchFormat") or match_type or "Unknown"
        st.markdown(
            f"🏆 **Format:** <span style='color:{format_color}; font-weight:bold'>{match_format}</span>",
            unsafe_allow_html=True
        )

        st.write(f"📬 **Venue:** {info.get('venueInfo', {}).get('ground', 'Unknown')}")
        st.write(f"**City:** {info.get('venueInfo', {}).get('city', 'Unknown')}")
        st.write(f"**State:** {info.get('state', 'N/A')}")
        st.write(f"📢 **Status:** {info.get('status', 'No Status')}")

        # Scores
        st.markdown("### 🏏 Current Scores")

        team1_scores = score.get("team1Score", {})
        team2_scores = score.get("team2Score", {})

        if team1_scores or team2_scores:
            score_col1, score_col2 = st.columns(2)
            # Team 1 scores
            with score_col1:
                st.markdown(f"**{info.get('team1', {}).get('teamName', 'Team 1')}**")
                for inning_key in ["inngs1", "inngs2"]:
                    if inning_key in team1_scores:
                        inning = team1_scores[inning_key]
                        runs = inning.get("runs", 0)
                        wickets = inning.get("wickets", 0)
                        overs = inning.get("overs", 0)
                        st.write(f"{inning_key}: {runs}/{wickets} ({overs} ov)")

            # Team 2 scores
            with score_col2:
                st.markdown(f"**{info.get('team2', {}).get('teamName', 'Team 2')}**")
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

    # Helper function to safely convert stats to DataFrame and add match type badges
    def stats_to_dataframe_with_badge(stats):
        """
        Converts API stats 'values' into a DataFrame and adds color-coded match type badges
        """
        if not stats:
            return pd.DataFrame()

        rows = []

        for s in stats:
            values = s.get("values", {})
            match_type = s.get("matchType", "Unknown")
            # Color badge for match type
            format_color = {
                "T20": "#007bff",
                "T20I": "#007bff",
                "ODI": "#28a745",
                "TEST": "#dc3545",
            }.get(match_type.upper(), "#6c757d")

            # Convert stats dict into rows with badge
            for k, v in values.items():
                rows.append({
                    "Stat": k,
                    "Value": v,
                    "Match Type": f"<span style='color:white; background-color:{format_color}; "
                                  f"padding:2px 6px; border-radius:4px;'>{match_type}</span>"
                })

        if rows:
            df = pd.DataFrame(rows)
            return df
        return pd.DataFrame()

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
                            df = stats_to_dataframe_with_badge(batting_stats["values"])
                            if not df.empty:
                                # Allow HTML to render colored badges
                                st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
                            else:
                                st.info("No batting stats available for this player.")
                        else:
                            st.info("No batting stats available for this player.")

                    elif stat_choice == "Bowling Stats":
                        bowling_stats = fetch_player_bowling(player_id)
                        if bowling_stats and "values" in bowling_stats:
                            st.markdown(f"#### 🎯 Bowling Stats for {player_info.get('name','')}")
                            df = stats_to_dataframe_with_badge(bowling_stats["values"])
                            if not df.empty:
                                st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
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
    st.title("🧮 SQL Analytics Dashboard")
    st.caption("Explore 25 SQL query insights directly from your Cricbuzz database.")

    # --- Question list --- #
    question_list = [
        "Q1 - Find all players who represent India",
        "Q2 - Show all matches played recently",
        "Q3 - Top 10 highest run scorers in ODI cricket",
        "Q4 - Venues with more than 30,000 capacity",
        "Q5 - Total matches won by each team",
        "Q6 - Count of players by playing role",
        "Q7 - Highest batting score per format",
        "Q8 - Series started in 2024",
        "Q9 - All-rounders with 1000+ runs & 50+ wickets",
        "Q10 - Last 20 completed matches",
        "Q11 - Compare player performance across formats",
        "Q12 - Home vs Away team performance",
        "Q13 - Partnerships scoring 100+ runs",
        "Q14 - Bowling performance by venue",
        "Q15 - Player performance in close matches",
        "Q16 - Player batting trend (since 2020)",
        "Q17 - Toss advantage analysis",
        "Q18 - Most economical bowlers in limited overs",
        "Q19 - Consistent batsmen (low run deviation)",
        "Q20 - Matches played & averages per format",
        "Q21 - Player performance ranking system",
        "Q22 - Head-to-head match analysis between teams",
        "Q23 - Recent player form & momentum",
        "Q24 - Successful batting partnerships",
        "Q25 - Player performance evolution over time"
    ]

    selected_question = st.selectbox("📜 Select a SQL Analysis Question", question_list)

    # --- Query Mapping --- #
    sql_queries = {
        "Q1 - Find all players who represent India": """
            SELECT full_name, playing_role, batting_style, bowling_style
            FROM players WHERE country = 'India';
        """,

        "Q2 - Show all matches played recently": """
            SELECT m.match_desc, t1.team_name AS team1, t2.team_name AS team2,
                   v.venue_name, v.city, m.match_date
            FROM matches m
            JOIN teams t1 ON m.team1_id = t1.team_id
            JOIN teams t2 ON m.team2_id = t2.team_id
            JOIN venues v ON m.venue_id = v.venue_id
            WHERE m.match_date >= CURDATE() - INTERVAL 7 DAY
            ORDER BY m.match_date DESC;
        """,

        "Q3 - Top 10 highest run scorers in ODI cricket": """
            SELECT p.full_name, SUM(ps.runs) AS total_runs,
                   AVG(ps.runs) AS avg_runs,
                   SUM(CASE WHEN ps.runs >= 100 THEN 1 ELSE 0 END) AS centuries
            FROM player_stats ps
            JOIN players p ON ps.player_id = p.player_id
            WHERE ps.format = 'ODI'
            GROUP BY p.full_name
            ORDER BY total_runs DESC
            LIMIT 10;
        """,

        "Q4 - Venues with more than 30,000 capacity": """
            SELECT venue_name, city, country, capacity
            FROM venues
            WHERE capacity > 30000
            ORDER BY capacity DESC;
        """,

        "Q5 - Total matches won by each team": """
            SELECT t.team_name, COUNT(m.match_id) AS total_wins
            FROM matches m
            JOIN teams t ON m.winner_team_id = t.team_id
            GROUP BY t.team_name
            ORDER BY total_wins DESC;
        """,

        "Q6 - Count of players by playing role": """
            SELECT playing_role, COUNT(player_id) AS player_count
            FROM players
            GROUP BY playing_role;
        """,

        "Q7 - Highest batting score per format": """
            SELECT format, MAX(runs) AS highest_score
            FROM player_stats
            GROUP BY format;
        """,

        "Q8 - Series started in 2024": """
            SELECT series_name, host_country, match_type, start_date, total_matches
            FROM series
            WHERE YEAR(start_date) = 2024;
        """,

        "Q9 - All-rounders with 1000+ runs & 50+ wickets": """
            SELECT p.full_name, ps.format,
                   SUM(ps.runs) AS total_runs,
                   SUM(ps.wickets) AS total_wickets
            FROM players p
            JOIN player_stats ps ON p.player_id = ps.player_id
            GROUP BY p.full_name, ps.format
            HAVING total_runs > 1000 AND total_wickets > 50;
        """,

        "Q10 - Last 20 completed matches": """
            SELECT m.match_desc, t1.team_name AS team1, t2.team_name AS team2,
                   tw.team_name AS winner, m.result_margin, m.result_type, v.venue_name
            FROM matches m
            JOIN teams t1 ON m.team1_id = t1.team_id
            JOIN teams t2 ON m.team2_id = t2.team_id
            JOIN teams tw ON m.winner_team_id = tw.team_id
            JOIN venues v ON m.venue_id = v.venue_id
            WHERE m.status = 'Completed'
            ORDER BY m.match_date DESC
            LIMIT 20;
        """,

        "Q11 - Compare player performance across formats": """
            SELECT p.full_name,
                   SUM(CASE WHEN ps.format='Test' THEN ps.runs ELSE 0 END) AS test_runs,
                   SUM(CASE WHEN ps.format='ODI' THEN ps.runs ELSE 0 END) AS odi_runs,
                   SUM(CASE WHEN ps.format='T20I' THEN ps.runs ELSE 0 END) AS t20_runs,
                   ROUND(AVG(ps.runs),2) AS overall_avg
            FROM players p
            JOIN player_stats ps ON p.player_id = ps.player_id
            GROUP BY p.full_name
            HAVING COUNT(DISTINCT ps.format) >= 2;
        """,

        "Q12 - Home vs Away team performance": """
            SELECT t.team_name,
                   SUM(CASE WHEN v.country = t.country THEN 1 ELSE 0 END) AS home_matches,
                   SUM(CASE WHEN v.country != t.country THEN 1 ELSE 0 END) AS away_matches,
                   SUM(CASE WHEN v.country = t.country AND m.winner_team_id = t.team_id THEN 1 ELSE 0 END) AS home_wins,
                   SUM(CASE WHEN v.country != t.country AND m.winner_team_id = t.team_id THEN 1 ELSE 0 END) AS away_wins
            FROM matches m
            JOIN teams t ON m.team1_id = t.team_id OR m.team2_id = t.team_id
            JOIN venues v ON m.venue_id = v.venue_id
            GROUP BY t.team_name;
        """,

        # Add the remaining 13 queries (Q13 - Q25) as needed following the same structure.
    }

    query_to_run = sql_queries.get(selected_question)

    if query_to_run:
        if st.button("🚀 Run Query"):
            try:
                conn = get_db_connection()
                df = pd.read_sql(query_to_run, conn)
                conn.close()

                if df.empty:
                    st.warning("⚠️ No records found for this query.")
                else:
                    st.success("✅ Query executed successfully!")
                    st.dataframe(df, use_container_width=True)

                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="📥 Download as CSV",
                        data=csv,
                        file_name=f"{selected_question[:20]}.csv",
                        mime="text/csv"
                    )
            except Exception as e:
                st.error(f"❌ Error: {e}")
    else:
        st.info("Select a query to view or execute.")




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


