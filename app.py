import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import altair as alt

# -----------------------
# File Paths and Constants
# -----------------------
DATA_DIR = "data"
TRACKING_FILE = os.path.join(DATA_DIR, "tracking_data.json")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")

# Define Bible verses for each category
BIBLE_VERSES = {
    "Love & Service": "Matthew 25:35-40",
    "Evangelism & Discipleship": "Matthew 28:19-20",
    "Faithfulness in Trials": "James 1:12",
    "Generosity & Giving": "2 Corinthians 9:7",
    "Holiness & Obedience": "1 Peter 1:15-16",
    "Use of Talents for God's Glory": "Matthew 25:14-30",
    "Heart & Motivation Check": "Matthew 6:1-4"
}

# List of Categories
CATEGORIES = list(BIBLE_VERSES.keys())

# -----------------------
# Initialization Functions
# -----------------------
def init_data_files():
    """Create the data directory and JSON files if they do not exist."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    if not os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, "w") as f:
            json.dump({"entries": []}, f, indent=4)
    
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "goals": {
                "Love & Service": "Serve at least 5 people weekly",
                "Evangelism & Discipleship": "Share the Gospel or mentor 3 people weekly",
                "Faithfulness in Trials": "Journal one instance per trial of trust in God",
                "Generosity & Giving": "Give 10% of income/time to ministry",
                "Holiness & Obedience": "Engage in daily Bible study and prayer",
                "Use of Talents for God's Glory": "Identify and use your talents weekly for ministry",
                "Heart & Motivation Check": "Complete a monthly questionnaire on your intentions"
            },
            "notification_settings": {
                "daily_reminder_time": "08:00",
                "enable_notifications": True
            }
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(default_config, f, indent=4)

def load_data():
    """Load tracking data from the JSON file."""
    with open(TRACKING_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    """Save tracking data to the JSON file."""
    with open(TRACKING_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_config():
    """Load configuration data from the JSON file."""
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    """Save configuration data to the JSON file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

# -----------------------
# App Page Functions
# -----------------------
def render_dashboard():
    st.title("Dashboard")
    st.write("Overview of your logged entries:")
    
    data = load_data()
    entries = data.get("entries", [])
    
    if not entries:
        st.info("No entries have been logged yet.")
    else:
        # Sort entries by date (descending) and display as a table
        sorted_entries = sorted(entries, key=lambda x: x["date"], reverse=True)
        st.dataframe(sorted_entries)

def render_log_entry():
    st.title("Log New Entry")
    
    # Let user choose a category
    category = st.selectbox("Select a Category", CATEGORIES)
    
    # Load default config and get the goal for this category
    config = load_config()
    goal = config.get("goals", {}).get(category, "No goal defined.")
    bible_verse = BIBLE_VERSES.get(category, "")
    
    st.markdown(f"**Goal/Reflection:** {goal}")
    st.markdown(f"**Bible Verse:** {bible_verse}")
    
    st.write("Please fill out the form below:")
    
    # Use a form to capture the log details
    with st.form(key="entry_form"):
        # Automatically use the current date (can be overridden if needed)
        entry_date = st.date_input("Date", datetime.today())
        # Metric input (number of acts, hours, etc.)
        value = st.number_input("Metric Value (e.g., number of acts, hours, etc.)", min_value=0, step=1)
        reflection = st.text_area("Reflection/Notes")
        submit_button = st.form_submit_button(label="Submit Entry")
    
    if submit_button:
        # Create a new entry dictionary
        new_entry = {
            "date": entry_date.strftime("%Y-%m-%d"),
            "category": category,
            "metric": value,
            "reflection": reflection,
            "bible_verse": bible_verse
        }
        # Load current data, append new entry, and save
        data = load_data()
        data["entries"].append(new_entry)
        save_data(data)
        st.success("Entry logged successfully!")

def render_view_entries():
    st.title("View All Entries")
    
    data = load_data()
    entries = data.get("entries", [])
    
    if not entries:
        st.info("No entries logged yet.")
    else:
        # Optionally, let user filter by category
        filter_category = st.selectbox("Filter by Category", ["All"] + CATEGORIES)
        if filter_category != "All":
            filtered_entries = [entry for entry in entries if entry["category"] == filter_category]
        else:
            filtered_entries = entries
        
        if filtered_entries:
            st.dataframe(filtered_entries)
        else:
            st.info("No entries found for the selected category.")

def render_settings():
    st.title("Settings")
    
    config = load_config()
    st.subheader("Goals for Each Category")
    goals = config.get("goals", {})
    
    for cat in CATEGORIES:
        st.markdown(f"**{cat}:** {goals.get(cat, 'No goal defined.')}")
    
    st.subheader("Notification Settings")
    notif_settings = config.get("notification_settings", {})
    st.markdown(f"**Daily Reminder Time:** {notif_settings.get('daily_reminder_time', 'Not set')}")
    st.markdown(f"**Enable Notifications:** {notif_settings.get('enable_notifications', False)}")
    
    st.info("Settings are currently read-only in this version.")

def render_reports():
    st.title("Reports & Visualizations")
    st.write("Visualize your spiritual journey over time.")

    data = load_data()
    entries = data.get("entries", [])
    if not entries:
        st.info("No entries logged yet. Please log some entries to see visualizations.")
        return
    
    # Convert entries to a pandas DataFrame
    df = pd.DataFrame(entries)
    
    # Convert 'date' column to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Allow the user to choose the time aggregation and category filter
    aggregation = st.selectbox("Select Time Aggregation", ["Weekly", "Monthly", "Yearly"])
    filter_category = st.selectbox("Filter by Category", ["All"] + CATEGORIES)
    
    # Create a "Period" column based on the selected aggregation
    if aggregation == "Weekly":
        df['Period'] = df['date'].dt.strftime('%Y-W%U')
    elif aggregation == "Monthly":
        df['Period'] = df['date'].dt.strftime('%Y-%m')
    elif aggregation == "Yearly":
        df['Period'] = df['date'].dt.strftime('%Y')
    
    # Filter by category if needed
    if filter_category != "All":
        df = df[df['category'] == filter_category]
    
    if df.empty:
        st.info("No data available for the selected filters.")
        return

    # Group the data. If all categories are selected, group by both Period and category.
    if filter_category == "All":
        agg_df = df.groupby(['Period', 'category'])['metric'].sum().reset_index()
        chart = alt.Chart(agg_df).mark_line(point=True).encode(
            x=alt.X('Period:N', sort=None, title="Period"),
            y=alt.Y('metric:Q', title="Total Metric"),
            color=alt.Color('category:N', title="Category"),
            tooltip=['Period', 'category', 'metric']
        ).properties(
            title=f"Metrics by {aggregation} Period and Category"
        )
    else:
        agg_df = df.groupby('Period')['metric'].sum().reset_index()
        chart = alt.Chart(agg_df).mark_line(point=True).encode(
            x=alt.X('Period:N', sort=None, title="Period"),
            y=alt.Y('metric:Q', title="Total Metric"),
            tooltip=['Period', 'metric']
        ).properties(
            title=f"Metrics by {aggregation} Period"
        )
    
    st.altair_chart(chart, use_container_width=True)

# -----------------------
# Main App
# -----------------------
def main():
    st.sidebar.title("Christian Personal Data Tracker")
    menu_options = ["Dashboard", "Log Entry", "View Entries", "Reports", "Settings"]
    choice = st.sidebar.radio("Navigation", menu_options)
    
    if choice == "Dashboard":
        render_dashboard()
    elif choice == "Log Entry":
        render_log_entry()
    elif choice == "View Entries":
        render_view_entries()
    elif choice == "Reports":
        render_reports()
    elif choice == "Settings":
        render_settings()
    else:
        st.error("Invalid choice. Please select a valid option from the sidebar.")

if __name__ == "__main__":
    init_data_files()
    main()
