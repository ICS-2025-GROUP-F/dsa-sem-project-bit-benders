import tkinter as tk
from tkinter import messagebox
import sqlite3



class BookNode:
    def _init_(self, book_id, title, author, year, isbn):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.year = year
        self.isbn = isbn
        self.next = None

class BookLinkedList:
    def _init_(self):
        self.head = None

    def append(self, book_id, title, author, year, isbn):
        new_node = BookNode(book_id, title, author, year, isbn)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

    def to_list(self):
        books = []
        current = self.head
        while current:
            books.append((current.book_id, current.title, current.author, current.year, current.isbn))
            current = current.next
        return books

    def clear(self):
        self.head = None



class BookApp:
    def _init_(self, root):
        self.root = root
        self.root.title("Linked List Book App")
        self.book_list = BookLinkedList()

        self.db_connection = sqlite3.connect("books.db")
        self.db_cursor = self.db_connection.cursor()
        self.create_table()

        
        self.listbox = tk.Listbox(root, width=80)
        self.listbox.pack(pady=10)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)

        
        self.title_entry = tk.Entry(root)
        self.title_entry.pack()
        self.title_entry.insert(0, "Title")

        self.author_entry = tk.Entry(root)
        self.author_entry.pack()
        self.author_entry.insert(0, "Author")

        self.year_entry = tk.Entry(root)
        self.year_entry.pack()
        self.year_entry.insert(0, "Year")

        self.isbn_entry = tk.Entry(root)
        self.isbn_entry.pack()
        self.isbn_entry.insert(0, "ISBN")

        
        self.add_button = tk.Button(root, text="Add Book", command=self.add_book)
        self.add_button.pack(pady=5)

        self.update_button = tk.Button(root, text="Update Selected Book", command=self.update_book)
        self.update_button.pack(pady=5)

        self.delete_button = tk.Button(root, text="Delete Selected Book", command=self.delete_book)
        self.delete_button.pack(pady=5)

        self.selected_book_id = None

        self.load_books()

    def create_table(self):
        self.db_cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                year TEXT,
                isbn TEXT
            )
        ''')
        self.db_connection.commit()

    def load_books(self):
        self.book_list.clear()
        self.db_cursor.execute("SELECT * FROM books")
        rows = self.db_cursor.fetchall()

        for book in rows:
            book_id, title, author, year, isbn = book
            self.book_list.append(book_id, title, author, year, isbn)

        self.refresh_listbox()

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for book in self.book_list.to_list():
            self.listbox.insert(tk.END, f"{book[1]} by {book[2]} ({book[3]}, ISBN: {book[4]})")

    def add_book(self):
        title = self.title_entry.get()
        author = self.author_entry.get()
        year = self.year_entry.get()
        isbn = self.isbn_entry.get()

        if not title or not author:
            messagebox.showwarning("Missing Fields", "Title and Author are required.")
            return

        self.db_cursor.execute("INSERT INTO books (title, author, year, isbn) VALUES (?, ?, ?, ?)",
                               (title, author, year, isbn))
        self.db_connection.commit()

        new_id = self.db_cursor.lastrowid
        self.book_list.append(new_id, title, author, year, isbn)
        self.refresh_listbox()

        self.clear_entries()

    def on_select(self, event):
        selected_index = self.listbox.curselection()
        if not selected_index:
            return

        book = self.book_list.to_list()[selected_index[0]]
        self.selected_book_id = book[0]

        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, book[1])

        self.author_entry.delete(0, tk.END)
        self.author_entry.insert(0, book[2])

        self.year_entry.delete(0, tk.END)
        self.year_entry.insert(0, book[3])

        self.isbn_entry.delete(0, tk.END)
        self.isbn_entry.insert(0, book[4])

    def update_book(self):
        if self.selected_book_id is None:
            messagebox.showwarning("No selection", "Please select a book to update.")
            return

        title = self.title_entry.get()
        author = self.author_entry.get()
        year = self.year_entry.get()
        isbn = self.isbn_entry.get()

        self.db_cursor.execute("""
            UPDATE books 
            SET title = ?, author = ?, year = ?, isbn = ?
            WHERE id = ?
        """, (title, author, year, isbn, self.selected_book_id))
        self.db_connection.commit()

        self.load_books()
        self.clear_entries()

    def delete_book(self):
        if self.selected_book_id is None:
            messagebox.showwarning("No selection", "Please select a book to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this book?")
        if confirm:
            self.db_cursor.execute("DELETE FROM books WHERE id = ?", (self.selected_book_id,))
            self.db_connection.commit()

            self.load_books()
            self.clear_entries()

    def clear_entries(self):
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.year_entry.delete(0, tk.END)
        self.isbn_entry.delete(0, tk.END)
        self.selected_book_id = None



if _name_ == "_main_":
    root = tk.Tk()
    app = BookApp(root)
    root.mainloop()