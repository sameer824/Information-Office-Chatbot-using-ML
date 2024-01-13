import sqlite3

# Define table names as constants
CHAT_HISTORY_TABLE = "chat_history"
ADMINS_TABLE = "admins"
CHATBOT_REPORTS_TABLE = "chatbot_reports"

# Create or connect to the SQLite database using a context manager
with sqlite3.connect("chatbot_database.db") as conn:
    cursor = conn.cursor()

    # Create a table to store chat history
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {CHAT_HISTORY_TABLE} (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            input_message TEXT NOT NULL,
            output_message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Create a table to store admin accounts
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {ADMINS_TABLE} (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    # Create a table to store chatbot reports
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {CHATBOT_REPORTS_TABLE} (
            id INTEGER PRIMARY KEY,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            report TEXT NOT NULL
        )
    ''')

# Function to insert a chat message into the chat_history table
def insert_chat_message(user_id, input_message, output_message):
    with sqlite3.connect("chatbot_database.db") as conn:
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO {CHAT_HISTORY_TABLE} (user_id, input_message, output_message) VALUES (?, ?, ?)", (user_id, input_message, output_message))

# Function to verify admin credentials
def verify_admin_credentials(username, password):
    with sqlite3.connect("chatbot_database.db") as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT id FROM {ADMINS_TABLE} WHERE username = ? AND password = ?", (username, password))
        return cursor.fetchone()

# Function to insert a chatbot report into the chatbot_reports table
def insert_chatbot_report(month, year, report):
    with sqlite3.connect("chatbot_database.db") as conn:
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO {CHATBOT_REPORTS_TABLE} (month, year, report) VALUES (?, ?, ?)", (month, year, report))
def close_connection():
    conn.close()