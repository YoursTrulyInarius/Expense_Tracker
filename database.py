import sqlite3
import os
import sys
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

    def check_duplicate(self, item, category, amount):
        """Check if an identical expense (same description, category, amount) already exists."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT COUNT(*) FROM expenses WHERE item = ? AND category = ? AND amount = ?',
                    (item.strip(), category.strip(), amount)
                )
                count = cursor.fetchone()[0]
                return count > 0
        except sqlite3.Error as e:
            print(f"Database error in check_duplicate: {e}", file=sys.stderr)
            return False

    def add_expense(self, item, category, amount):
        """Add a new expense to the database with automatic local timestamp (Philippines)."""
        # Basic secondary validation
        if not item or not item.strip():
            raise ValueError("Item description cannot be empty or blank.")
        if not category or not category.strip():
            raise ValueError("Category cannot be empty or blank.")
        if amount <= 0:
            raise ValueError("Amount must be a positive number.")

        local_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO expenses (timestamp, item, category, amount)
                    VALUES (?, ?, ?, ?)
                ''', (local_time, item.strip(), category.strip(), amount))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database error in add_expense: {e}", file=sys.stderr)
            raise

    def fetch_all_expenses(self):
        """Fetch all expenses from the database, ordered by timestamp."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM expenses ORDER BY timestamp DESC')
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error in fetch_all_expenses: {e}", file=sys.stderr)
            return []

    def fetch_filtered_expenses(self, category=None, search=None):
        """Fetch expenses filtered by category and/or description keyword."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                query = 'SELECT * FROM expenses WHERE 1=1'
                params = []

                if category and category != "All":
                    query += ' AND category = ?'
                    params.append(category)

                if search and search.strip():
                    query += ' AND item LIKE ?'
                    params.append(f'%{search.strip()}%')

                query += ' ORDER BY timestamp DESC'
                cursor.execute(query, params)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error in fetch_filtered_expenses: {e}", file=sys.stderr)
            return []

    def update_expense(self, expense_id, item, category, amount):
        """Update an existing expense (updates timestamp to current Philippines time)."""
        # Basic secondary validation
        if not item or not item.strip():
            raise ValueError("Item description cannot be empty or blank.")
        if not category or not category.strip():
            raise ValueError("Category cannot be empty or blank.")
        if amount <= 0:
            raise ValueError("Amount must be a positive number.")

        local_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE expenses
                    SET timestamp = ?, item = ?, category = ?, amount = ?
                    WHERE id = ?
                ''', (local_time, item.strip(), category.strip(), amount, expense_id))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database error in update_expense: {e}", file=sys.stderr)
            raise

    def delete_expense(self, expense_id):
        """Delete a single expense from the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database error in delete_expense: {e}", file=sys.stderr)
            raise

    def delete_multiple_expenses(self, ids):
        """Delete multiple expenses by a list of IDs."""
        if not ids:
            return
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                placeholders = ','.join('?' for _ in ids)
                cursor.execute(f'DELETE FROM expenses WHERE id IN ({placeholders})', ids)
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database error in delete_multiple_expenses: {e}", file=sys.stderr)
            raise

    def get_total_expenses(self, category=None, search=None):
        """Calculate the total of filtered expenses."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                query = 'SELECT SUM(amount) FROM expenses WHERE 1=1'
                params = []

                if category and category != "All":
                    query += ' AND category = ?'
                    params.append(category)

                if search and search.strip():
                    query += ' AND item LIKE ?'
                    params.append(f'%{search.strip()}%')

                cursor.execute(query, params)
                result = cursor.fetchone()
                return result[0] if result and result[0] else 0.0
        except sqlite3.Error as e:
            print(f"Database error in get_total_expenses: {e}", file=sys.stderr)
            return 0.0
