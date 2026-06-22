import os
import json
import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

PROFILE_FILE = "user_profile.json"

# --- PROFILE & STREAK MANAGEMENT ---

def load_profile():
    """Loads the user profile containing streak info and meal log history."""
    default_profile = {
        "streak": 0,
        "longest_streak": 0,
        "last_log_date": None,
        "total_days_logged": 0,
        "daily_calorie_limit": 2000,
        "history": {}  # Format: {"YYYY-MM-DD": [{"food": "Pizza", "carbs": 30, "protein": 11, "fat": 10, "fiber": 2, "calories": 250, "grams": 100}]}
    }
    
    if not os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "w") as f:
            json.dump(default_profile, f, indent=4)
        return default_profile
        
    try:
        with open(PROFILE_FILE, "r") as f:
            profile = json.load(f)
            
        # Ensure all default keys exist (handles schema upgrades)
        for key, val in default_profile.items():
            if key not in profile:
                profile[key] = val
        return profile
    except Exception as e:
        st.error(f"Error loading profile: {e}. Resetting to default.")
        return default_profile

def save_profile(profile):
    """Saves the user profile to JSON."""
    try:
        with open(PROFILE_FILE, "w") as f:
            json.dump(profile, f, indent=4)
    except Exception as e:
        st.error(f"Error saving profile: {e}")

def check_and_update_streak(profile):
    """
    Checks if the streak is maintained or broken on app load.
    Does NOT increment streak unless a log is submitted, but resets it to 0 if a day was missed.
    """
    if not profile["last_log_date"]:
        return profile
        
    today = datetime.date.today()
    last_log = datetime.datetime.strptime(profile["last_log_date"], "%Y-%m-%d").date()
    delta = (today - last_log).days
    
    # If more than 1 day has passed since the last log, streak is broken
    if delta > 1:
        profile["streak"] = 0
        save_profile(profile)
        
    return profile

def log_meal_and_update_streak(date_str, meal_entry, profile):
    """
    Logs a meal for a specific date and updates the streak if applicable.
    """
    # 1. Add meal to history
    if date_str not in profile["history"]:
        profile["history"][date_str] = []
        
    profile["history"][date_str].append(meal_entry)
    
    # 2. Update Streak
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    
    # We only update streak if logging for today or yesterday (to allow back-filling without cheating streaks)
    if date_str == today_str:
        if profile["last_log_date"] is None:
            # First log ever
            profile["streak"] = 1
            profile["total_days_logged"] = 1
        else:
            last_log = datetime.datetime.strptime(profile["last_log_date"], "%Y-%m-%d").date()
            today = datetime.date.today()
            delta = (today - last_log).days
            
            if delta == 1:
                # Logged yesterday, increment streak
                profile["streak"] += 1
            elif delta > 1:
                # Broke streak, start fresh
                profile["streak"] = 1
            elif delta == 0:
                # Already logged today, streak remains same
                pass
                
        profile["last_log_date"] = today_str
        profile["longest_streak"] = max(profile["streak"], profile["longest_streak"])
        
    # Re-calculate total unique days logged
    profile["total_days_logged"] = len(profile["history"])
    
    save_profile(profile)
    return profile

def delete_meal_entry(date_str, index, profile):
    """Deletes a logged meal entry."""
    if date_str in profile["history"] and 0 <= index < len(profile["history"][date_str]):
        profile["history"][date_str].pop(index)
        # If no items left for that date, clean up the date key
        if not profile["history"][date_str]:
            del profile["history"][date_str]
            # If the user deleted the last meal of the day and it was today, we might want to check streak,
            # but we keep last_log_date for safety unless they delete all logs from that date.
            # If they deleted the last log for the last log date, update last log date
            if profile["last_log_date"] == date_str:
                dates = sorted([d for d in profile["history"].keys()])
                profile["last_log_date"] = dates[-1] if dates else None
                # If they delete today's entire log, the streak decreases or resets
                if date_str == datetime.date.today().strftime("%Y-%m-%d"):
                    # Decrement streak or reset to previous state
                    profile["streak"] = max(0, profile["streak"] - 1)
        
        profile["total_days_logged"] = len(profile["history"])
        save_profile(profile)
    return profile

# --- CUSTOM CSS & AESTHETICS ---

def inject_custom_css():
    """Injects high-fidelity, premium custom CSS styling into Streamlit."""
    st.markdown("""
        <style>
        /* Modern Fonts and Background Styles */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
        }
        
        /* Main Container Customizations */
        .main {
            background: radial-gradient(circle at 10% 20%, rgba(20, 20, 35, 1) 0%, rgba(10, 10, 20, 1) 90.2%);
            color: #f0f2f6;
        }
        
        /* Glassmorphic Cards styled via native Streamlit containers */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(255, 255, 255, 0.03) !important;
            border-radius: 16px !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            padding: 24px !important;
            margin-bottom: 20px !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
            transition: all 0.3s ease-in-out !important;
        }
        
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5) !important;
            transform: translateY(-2px) !important;
        }
        
        /* Glowing Headers */
        .glow-text {
            color: #fff;
            text-shadow: 0 0 10px rgba(0, 255, 200, 0.5), 0 0 20px rgba(0, 255, 200, 0.3);
            font-weight: 700;
        }
        
        .glow-text-orange {
            color: #fff;
            text-shadow: 0 0 10px rgba(255, 120, 0, 0.5), 0 0 20px rgba(255, 120, 0, 0.3);
            font-weight: 700;
        }

        .glow-text-pink {
            color: #fff;
            text-shadow: 0 0 10px rgba(255, 0, 128, 0.5), 0 0 20px rgba(255, 0, 128, 0.3);
            font-weight: 700;
        }
        
        /* Custom Metrics */
        .metric-container {
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            margin: 15px 0;
        }
        
        .metric-box {
            background: rgba(255, 255, 255, 0.02);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 15px 25px;
            text-align: center;
            min-width: 140px;
            margin: 5px;
            transition: background 0.3s;
        }
        
        .metric-box:hover {
            background: rgba(255, 255, 255, 0.05);
        }
        
        .metric-value {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 5px;
        }
        
        .metric-label {
            font-size: 12px;
            color: #8a99ad;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Streak Fire Badge animation */
        .streak-badge {
            display: inline-block;
            background: linear-gradient(135deg, #ff5e36 0%, #ff9500 100%);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 16px;
            box-shadow: 0 4px 15px rgba(255, 94, 54, 0.4);
            animation: pulse 1.8s infinite alternate;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            100% { transform: scale(1.05); box-shadow: 0 4px 25px rgba(255, 94, 54, 0.6); }
        }
        
        /* Table Customizations */
        .dataframe {
            background-color: transparent !important;
            border-collapse: collapse;
            width: 100%;
        }
        
        .dataframe th {
            background-color: rgba(255, 255, 255, 0.05) !important;
            color: #00ffc8 !important;
            font-weight: 600;
            text-align: left;
            padding: 10px;
            border-bottom: 2px solid rgba(255, 255, 255, 0.1);
        }
        
        .dataframe td {
            padding: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        /* Hide default Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

# --- PLOTLY DATA VISUALIZATIONS ---

def create_calorie_gauge(current, limit):
    """Creates a beautiful dark-themed gauge chart for daily calorie progress."""
    percent = (current / limit) * 100
    color = "#00ffc8" # Cyan
    if percent > 100:
        color = "#ff3b30" # Red (Exceeded)
    elif percent > 85:
        color = "#ff9500" # Orange (Close)

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = current,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Daily Calories", 'font': {'size': 20, 'color': '#ffffff', 'family': 'Outfit'}},
        number = {'suffix': " kcal", 'font': {'color': '#ffffff', 'size': 32, 'family': 'Outfit'}},
        gauge = {
            'axis': {'range': [None, max(limit, current + 500)], 'tickwidth': 1, 'tickcolor': "#8a99ad"},
            'bar': {'color': color},
            'bgcolor': "rgba(255, 255, 255, 0.05)",
            'borderwidth': 1,
            'bordercolor': "rgba(255, 255, 255, 0.1)",
            'threshold': {
                'line': {'color': "#ff3b30", 'width': 3},
                'thickness': 0.75,
                'value': limit
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=30, b=10),
        height=200,
    )
    return fig

def create_macro_pie_chart(carbs, protein, fat):
    """Creates an interactive doughnut chart showing the macronutrient ratio."""
    # Convert to calories to show energy contribution
    carb_cal = carbs * 4
    prot_cal = protein * 4
    fat_cal = fat * 9
    total_cal = carb_cal + prot_cal + fat_cal
    
    if total_cal == 0:
        # Return empty/placeholder chart data
        labels = ["Carbohydrates", "Protein", "Fat"]
        values = [1, 1, 1]
        colors = ["rgba(255,255,255,0.1)", "rgba(255,255,255,0.1)", "rgba(255,255,255,0.1)"]
        textinfo = "none"
        hoverinfo = "none"
    else:
        labels = ["Carbohydrates", "Protein", "Fat"]
        values = [carb_cal, prot_cal, fat_cal]
        colors = ["#ff5e36", "#00ffc8", "#ffcc00"]
        textinfo = "percent"
        hoverinfo = "label+value"

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.5,
        marker=dict(colors=colors, line=dict(color='rgba(10, 10, 20, 1)', width=2)),
        textinfo=textinfo,
        textposition="inside" if total_cal > 0 else "none",
        hoverinfo=hoverinfo,
        hovertemplate="<b>%{label}</b><br>%{value:.1f} kcal contribution<br>%{percent}<extra></extra>" if total_cal > 0 else None
    )])
    
    fig.update_layout(
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=30, b=10),
        height=200,
    )
    return fig

def create_calorie_history_chart(profile):
    """Creates a line/bar chart displaying daily calorie intake history over time."""
    history = profile.get("history", {})
    if not history:
        return None
        
    sorted_dates = sorted(history.keys())
    # Take last 7 days
    recent_dates = sorted_dates[-7:]
    
    daily_totals = []
    for d in recent_dates:
        day_total = sum([item["calories"] for item in history[d]])
        daily_totals.append(day_total)
        
    df_history = pd.DataFrame({
        "Date": [datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%b %d") for d in recent_dates],
        "Calories": daily_totals
    })
    
    fig = px.bar(
        df_history, 
        x="Date", 
        y="Calories", 
        text="Calories",
        color="Calories",
        color_continuous_scale=["#00ffc8", "#ff9500", "#ff3b30"]
    )
    
    fig.update_traces(
        textposition="outside",
        marker_line_color='rgba(0,0,0,0)',
        marker_line_width=1.5,
        opacity=0.85
    )
    
    # Add target line
    limit = profile.get("daily_calorie_limit", 2000)
    fig.add_shape(
        type="line",
        x0=-0.5,
        y0=limit,
        x1=len(recent_dates)-0.5,
        y1=limit,
        line=dict(color="#ff3b30", width=2, dash="dash"),
        name="Target Limit"
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=20),
        height=280,
        coloraxis_showscale=False,
        xaxis=dict(
            showgrid=False,
            tickfont=dict(color="#8a99ad")
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.05)",
            tickfont=dict(color="#8a99ad"),
            title="Calories (kcal)"
        ),
        title=dict(
            text="Calorie Intake (Last 7 Logged Days)",
            font=dict(size=16, color="#ffffff"),
            x=0.05
        )
    )
    return fig
