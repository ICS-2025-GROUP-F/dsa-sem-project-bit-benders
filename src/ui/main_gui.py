"""
Book Logger Desktop App  •  Stack  •  SQLite
Features:
 • Add Book  • View All  • Delete  • Reverse  • Clear
Author: Michelle Kases (186989)
"""

import tkinter as tk
from tkinter import messagebox
import sqlite3
from pathlib import Path
from ds.stack import Stack

# ────────────────────────────────
# 0.  GLOBALS & DB INIT
# ────────────────────────────────
stack = Stack()

DB_PATH = Path(__file__).resolve().parents[2] / "books.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS books (
        id    INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL UNIQUE
    );
    """
)
conn.commit()


# ────────────────────────────────
# 1.  HELPERS
# ────────────────────────────────
def add_book() -> None:
    title = entry.get().strip()
    if not title:
        return

    if stack.find(title) != -1:
        messagebox.showwarning("Duplicate", "That book is already in the stack.")
        return

    # Stack + DB
    logs.insert(tk.END, stack.push(title))
    cursor.execute("INSERT OR IGNORE INTO books (title) VALUES (?)", (title,))
    conn.commit()
    entry.delete(0, tk.END)


def delete_selected() -> None:
    selection = listbox_db.curselection()
    if not selection:
        return

    # remove from DB
    sel_text = listbox_db.get(selection[0])
    title = sel_text.split(". ", maxsplit=1)[1]
    cursor.execute("DELETE FROM books WHERE title = ?", (title,))
    conn.commit()

    # remove from Stack if present
    idx = stack.find(title)
    if idx != -1:
        # convert idx to true list index
        stack_index = len(stack._items) - 1 - idx
        stack._items.pop(stack_index)
        logs.insert(tk.END, f"Deleted: {title}")

    view_saved_books(refresh_only=True)


def populate_from_db() -> None:
    rows = cursor.execute("SELECT title FROM books ORDER BY id").fetchall()
    for (title,) in rows:
        if stack.find(title) == -1:
            stack.push(title)
            logs.insert(tk.END, f"Loaded: {title}")


def view_saved_books(refresh_only: bool = False) -> None:
    """Open (or refresh) popup window listing all DB titles."""
    global popup, listbox_db

    if refresh_only and popup and listbox_db:
        listbox_db.delete(0, tk.END)
    elif not refresh_only:
        popup_setup()

    rows = cursor.execute("SELECT title FROM books ORDER BY id").fetchall()
    if not rows:
        listbox_db.insert(tk.END, "No books saved yet.")
    else:
        for i, (title,) in enumerate(rows, start=1):
            listbox_db.insert(tk.END, f"{i}. {title}")


def popup_setup():
    """Create the popup UI once."""
    global popup, listbox_db
    popup = tk.Toplevel(app)
    popup.title("All Saved Books")
    popup.geometry("360x350")

    tk.Label(popup, text="Books in Database:", font=("Segoe UI", 10, "bold")).pack(pady=10)

    listbox_db = tk.Listbox(popup, width=48, height=12)
    listbox_db.pack(pady=5)

    tk.Button(popup, text="Delete Selected Book", command=delete_selected)\
        .pack(pady=6)

    tk.Button(popup, text="Refresh List", command=view_saved_books)\
        .pack()

    popup.protocol("WM_DELETE_WINDOW", popup.withdraw)


def reverse_stack() -> None:
    if stack.is_empty():
        return
    stack.reverse()
    logs.insert(tk.END, "Stack reversed")


def clear_all() -> None:
    if messagebox.askyesno("Confirm", "Delete ALL books from Stack and DB?"):
        stack.clear()
        cursor.execute("DELETE FROM books")
        conn.commit()
        logs.insert(tk.END, "Cleared Stack + DB")
        if 'listbox_db' in globals():
            listbox_db.delete(0, tk.END)
            listbox_db.insert(tk.END, "No books saved yet.")


def on_close() -> None:
    conn.close()
    app.destroy()


# ────────────────────────────────
# 2.  GUI LAYOUT
# ────────────────────────────────
app = tk.Tk()
app.title("Book Logger  •  Stack  •  SQLite")
app.geometry("460x460")

# input row
tk.Label(app, text="Enter Book Title:", font=("Segoe UI", 11)).pack(pady=(15, 4))
entry = tk.Entry(app, width=36, font=("Segoe UI", 11))
entry.pack()

tk.Button(app, text="Add Book", width=15, command=add_book).pack(pady=6)

# feature buttons
feat_frame = tk.Frame(app)
feat_frame.pack(pady=6)
tk.Button(feat_frame, text="View All Saved Books", command=view_saved_books)\
    .grid(row=0, column=0, padx=4, pady=2, sticky="ew")
tk.Button(feat_frame, text="Reverse Stack Order", command=reverse_stack)\
    .grid(row=0, column=1, padx=4, pady=2, sticky="ew")
tk.Button(feat_frame, text="Clear ALL", fg="red", command=clear_all)\
    .grid(row=0, column=2, padx=4, pady=2, sticky="ew")

# log panel
tk.Label(app, text="Operation Logs:", font=("Segoe UI", 10, "bold")).pack()
logs = tk.Listbox(app, width=60, height=12)
logs.pack(pady=(0, 14))

# load persisted records
populate_from_db()

# graceful exit
app.protocol("WM_DELETE_WINDOW", on_close)

popup = None       # will hold the popup window reference
listbox_db = None  # will hold the listbox inside popup

app.mainloop()
