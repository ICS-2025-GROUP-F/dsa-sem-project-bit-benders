"""
Book Logger Desktop App
Stack + SQLite + View-All
Author: Michelle Kases (186989)
"""

import tkinter as tk
import sqlite3
from pathlib import Path
from ds.stack import Stack

# ────────────────────────────────
# 0.  GLOBALS
# ────────────────────────────────
stack = Stack()

# DB file lives in repo root (one level above src/)
DB_PATH = Path(__file__).resolve().parents[2] / "books.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS books (
        id    INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL
    );
    """
)
conn.commit()


# ────────────────────────────────
# 1.  HELPERS
# ────────────────────────────────
def add_book() -> None:
    """Push title to stack + insert row into DB + update log panel."""
    title = entry.get().strip()
    if not title:
        return

    # stack
    logs.insert(tk.END, stack.push(title))

    # database
    cursor.execute("INSERT INTO books (title) VALUES (?)", (title,))
    conn.commit()

    entry.delete(0, tk.END)


def populate_from_db() -> None:
    """Load existing DB rows on startup."""
    rows = cursor.execute("SELECT title FROM books ORDER BY id").fetchall()
    for (title,) in rows:
        stack.push(title)
        logs.insert(tk.END, f"Loaded: {title}")


def view_saved_books() -> None:
    """Popup window listing every title in DB."""
    popup = tk.Toplevel(app)
    popup.title("All Saved Books")
    popup.geometry("340x320")

    tk.Label(popup, text="Books in Database:", font=("Segoe UI", 10, "bold")).pack(pady=10)
    listbox = tk.Listbox(popup, width=45, height=12)
    listbox.pack(pady=5)

    rows = cursor.execute("SELECT title FROM books ORDER BY id").fetchall()
    if not rows:
        listbox.insert(tk.END, "No books saved yet.")
    else:
        for i, (title,) in enumerate(rows, start=1):
            listbox.insert(tk.END, f"{i}. {title}")


def on_close() -> None:
    """Make sure DB connection closes cleanly."""
    conn.close()
    app.destroy()


# ────────────────────────────────
# 2.  GUI LAYOUT
# ────────────────────────────────
app = tk.Tk()
app.title("Book Logger  •  Stack  •  SQLite")
app.geometry("430x380")

# Input row
tk.Label(app, text="Enter Book Title:", font=("Segoe UI", 11)).pack(pady=(15, 4))
entry = tk.Entry(app, width=34, font=("Segoe UI", 11))
entry.pack()

tk.Button(app, text="Add Book", width=15, command=add_book).pack(pady=8)
tk.Button(app, text="View All Saved Books", command=view_saved_books).pack(pady=4)

# Log panel
tk.Label(app, text="Operation Logs:", font=("Segoe UI", 10, "bold")).pack()
logs = tk.Listbox(app, width=55, height=10)
logs.pack(pady=(0, 12))

# Load persisted data
populate_from_db()

# Handle window close
app.protocol("WM_DELETE_WINDOW", on_close)

app.mainloop()
