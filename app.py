import random
import time
import sqlite3
import streamlit as st

# Set up the SQLite database connection
def setup_database():
    conn = sqlite3.connect('search_performance.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS search_stats (
                        id INTEGER PRIMARY KEY,
                        method TEXT,
                        target INTEGER,
                        list_length INTEGER,
                        time_taken REAL)''')
    conn.commit()
    return conn, cursor

# Naive search: scans the entire list for the target
def naive_search(l, target):
    for i in range(len(l)):
        if l[i] == target:
            return i
    return -1

# Binary search: efficient search leveraging the sorted property of the list
def binary_search(l, target, low=None, high=None):
    if low is None:
        low = 0
    if high is None:
        high = len(l) - 1

    if high < low:
        return -1

    midpoint = (low + high) // 2

    if l[midpoint] == target:
        return midpoint
    elif target < l[midpoint]:
        return binary_search(l, target, low, midpoint-1)
    else:
        return binary_search(l, target, midpoint+1, high)

# Function to log search statistics to SQLite
def log_search_stats(cursor, method, target, list_length, time_taken):
    cursor.execute("INSERT INTO search_stats (method, target, list_length, time_taken) VALUES (?, ?, ?, ?)", 
                   (method, target, list_length, time_taken))
    cursor.connection.commit()

# Function to display performance statistics from the SQLite database
def display_performance_stats(cursor):
    cursor.execute("SELECT method, AVG(time_taken) as avg_time, COUNT(*) as num_searches FROM search_stats GROUP BY method")
    results = cursor.fetchall()
    st.write("### Performance Summary")
    for row in results:
        st.write(f"Method: {row[0]}, Average Time: {row[1]:.6f} seconds, Number of Searches: {row[2]}")

# Streamlit app interface
def main():
    st.title("Search Algorithm Performance: Naive vs Binary Search")
    
    # Set up database
    conn, cursor = setup_database()

    # User input for list length and target number
    length = st.slider("Choose List Length", 1000, 10000, 5000, step=1000)
    target = st.number_input("Enter Target Value", min_value=-3*length, max_value=3*length, value=100)
    
    # Generate sorted list
    sorted_list = sorted(random.sample(range(-3*length, 3*length), length))

    # Radio buttons to select the search method
    search_method = st.radio("Select Search Method", ("Naive Search", "Binary Search"))

    # Display and time the search based on selected method
    if st.button("Run Search"):
        start_time = time.time()
        if search_method == "Naive Search":
            naive_search(sorted_list, target)
        else:
            binary_search(sorted_list, target)
        end_time = time.time()
        
        time_taken = end_time - start_time
        st.write(f"Search time: {time_taken:.6f} seconds")
        
        # Log the search stats to the database
        log_search_stats(cursor, search_method, target, length, time_taken)

    # Display search performance statistics from the database
    display_performance_stats(cursor)

    # Close the SQLite connection
    conn.close()

if __name__ == "__main__":
    main()
