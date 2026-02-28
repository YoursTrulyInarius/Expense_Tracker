# 💰 Personal Expense Tracker

A desktop application built with Python, Tkinter, and SQLite. Designed for high-clarity, ease of use, and professional standards.

## ✨ Features

- **✅ Full CRUD Support**: Seamlessly add, view, update, and delete expense records.
- **🔍 Live Search**: Filter expenses in real-time by typing any part of the description.
- **🗂️ Category Filter**: Narrow down records by category (Food, Transport, Utilities, etc.) with a single dropdown selection. Works alongside the search box.
- **🚫 Duplicate Validation**: Detects identical entries (same description, category, and amount) before inserting and prompts for confirmation.
- **🗑️ Multiple Delete**: Select multiple rows using `Ctrl+Click` or `Shift+Click` and delete them all at once with a single confirmation.
- **🕒 Auto Timestamp**: Automatically captures the current local date and time in a human-readable 12-hour format (e.g., *January 22, 2026, 02:08 PM*).
- **📊 CSV Export**: Save your expense data to a `.csv` file for use in Excel, Google Sheets, or for external backups.
- **🗄️ SQLite Database**: Integrated relational database for secure, local data persistence.

## 🛠️ Built With

- **Python**: Core application logic.
- **Tkinter**: Modern GUI framework with custom styling.
- **SQLite**: Reliable, serverless database engine.

## 🚀 Getting Started

### Prerequisites

- Python 3.x installed.

### How to Run

1. Clone or download the project directory.
2. Navigate to the project folder.
3. Run the application:
   ```bash
   python main.py
   ```

## 📂 Project Structure

- `main.py`: The heart of the app—handles UI and application logic.
- `database.py`: Manages SQLite connections, queries, and data validation.
- `app_styles.py`: Contains the design system, colors, and font tokens.
- `expenses.db`: Your local database file (automatically created on first run).

## 📄 Exporting Data

Click the **"Export to CSV"** button in the sidebar to save your entire expense history. The file will be pre-named with the current date for easy organization.

---
*Developed by sonjebgwapo*
