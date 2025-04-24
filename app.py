import sqlite3
import random
import time
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

# ----------------------------
# Database Helper Functions
# ----------------------------
def init_db():
    """Initialize the SQLite database and create the searches table if it doesn't exist."""
    conn = sqlite3.connect("search_results.db", check_same_thread=False)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            method TEXT,
            list_size INTEGER,
            target INTEGER,
            result_index INTEGER,
            exec_time REAL,
            timestamp TEXT
        )
    ''')
    conn.commit()
    return conn, c

def store_search_result(conn, method, list_size, target, result_index, exec_time):
    """Store search result in the database."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with conn:
        conn.execute('''
            INSERT INTO searches (method, list_size, target, result_index, exec_time, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (method, list_size, target, result_index, exec_time, timestamp))

def fetch_recent_searches(conn, limit=100):
    """Fetch the most recent search results."""
    return pd.read_sql(f"SELECT * FROM searches ORDER BY timestamp DESC LIMIT {limit}", conn)

# ----------------------------
# Search Algorithm Functions
# ----------------------------
def binary_search(arr, target):
    """Perform binary search on a sorted array."""
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid  # Target found
        elif arr[mid] > target:
            high = mid - 1
        else:
            low = mid + 1
    return -1  # Target not found

# ----------------------------
# Streamlit UI Setup
# ----------------------------
def display_sidebar():
    """Display sidebar widgets for user input."""
    st.sidebar.header("Search Parameters")
    list_size = st.sidebar.slider("Select List Size", 100, 5000, 1000, step=100)
    target = st.sidebar.number_input("Enter Target Number", value=random.randint(-3 * list_size, 3 * list_size))
    mode = st.sidebar.radio("Select Mode", ["Single Search", "Compare Multiple Searches"])
    return list_size, target, mode

def display_results(index, target, exec_time):
    """Display results after search execution."""
    if index != -1:
        st.success(f"Target {target} found at index {index}.")
    else:
        st.error(f"Target {target} not found in the list.")
    st.info(f"Execution Time: {exec_time:.6f} seconds")

def display_performance_metrics(df):
    """Display a bar chart of binary search performance metrics."""
    if not df.empty:
        fig = px.bar(
            df,
            x="timestamp",
            y="exec_time",
            color="method",
            barmode="group",
            title="Binary Search Execution Times",
            labels={"exec_time": "Execution Time (seconds)"}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No search data available. Please perform a search above.")

def display_search_history(df):
    """Display a table of the recent search history."""
    st.markdown("### Search History")
    method_filter = st.selectbox("Filter by Method", ["All", "Binary Search"])
    list_size_filter = st.slider("Filter by List Size", 100, 5000, 1000, step=100)
    filtered_df = df[
        (df["list_size"] == list_size_filter) & 
        (df["method"] == method_filter if method_filter != "All" else df["method"])
    ]
    st.dataframe(filtered_df.tail(50), use_container_width=True)
    
    # Export Button
    st.download_button(
        "Download Search History as CSV",
        filtered_df.to_csv(index=False).encode(),
        "search_history.csv",
        "text/csv"
    )

# ----------------------------
# Main App Function
# ----------------------------
def run_app():
    """Run the main Streamlit app."""
    st.set_page_config(page_title="Binary Search Performance", layout="wide")
    st.title("Binary Search with Performance Metrics")
    
    # Sidebar widgets for user input
    list_size, target, mode = display_sidebar()

    # Button to trigger search
    if st.sidebar.button("Run Search"):
        # Initialize database
        conn, _ = init_db()
        
        # Generate a sorted list of random integers
        sorted_list = sorted(random.sample(range(-3 * list_size, 3 * list_size), list_size))
        
        # Track search execution time
        start_time = time.time()
        index = binary_search(sorted_list, target)
        end_time = time.time()
        exec_time = end_time - start_time

        # Store the result in the database
        store_search_result(conn, "Binary Search", list_size, target, index, exec_time)

        # Display search result and execution time
        display_results(index, target, exec_time)

        # Close the database connection
        conn.close()

    # Fetch recent search results and display performance metrics
    with sqlite3.connect("search_results.db", check_same_thread=False) as conn:
        df = fetch_recent_searches(conn)
        display_performance_metrics(df)
        display_search_history(df)

# Run the Streamlit app
if __name__ == "__main__":
    run_app()
