import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_name="expenses.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        """Initialize the database and create the table if it doesn't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Simple migration: if 'date' exists, drop and recreate for 'timestamp'
            cursor.execute("PRAGMA table_info(expenses)")
            columns = [info[1] for info in cursor.fetchall()]
            if columns and 'date' in columns:
                cursor.execute("DROP TABLE expenses")
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    item TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL
                )
            ''')
            conn.commit()

    def add_expense(self, item, category, amount):
        """Add a new expense to the database with automatic local timestamp (Philippines)."""
        local_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO expenses (timestamp, item, category, amount)
                VALUES (?, ?, ?, ?)
            ''', (local_time, item, category, amount))
            conn.commit()

    def fetch_all_expenses(self):
        """Fetch all expenses from the database, ordered by timestamp."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM expenses ORDER BY timestamp DESC')
            return cursor.fetchall()

    def update_expense(self, expense_id, item, category, amount):
        """Update an existing expense (updates timestamp to current Philippines time)."""
        local_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE expenses
                SET timestamp = ?, item = ?, category = ?, amount = ?
                WHERE id = ?
            ''', (local_time, item, category, amount, expense_id))
            conn.commit()

    def delete_expense(self, expense_id):
        """Delete an expense from the database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
            conn.commit()

    def get_total_expenses(self):
        """Calculate the total of all expenses."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT SUM(amount) FROM expenses')
            result = cursor.fetchone()
            return result[0] if result[0] else 0.0
