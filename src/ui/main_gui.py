import tkinter as tk
from ds.stack import Stack

stack = Stack()

def add_book():
    book_name = entry.get()
    if book_name:
        msg = stack.push(book_name)
        logs.insert(tk.END, msg)
        entry.delete(0, tk.END)

app = tk.Tk()
app.title("Book Entry - Stack History")
app.geometry("400x300")

tk.Label(app, text="Enter Book Name:").pack(pady=5)
entry = tk.Entry(app, width=30)
entry.pack()

tk.Button(app, text="Add Book", command=add_book).pack(pady=10)

tk.Label(app, text="Operation Logs:").pack()
logs = tk.Listbox(app, width=50, height=10)
logs.pack()

app.mainloop()
