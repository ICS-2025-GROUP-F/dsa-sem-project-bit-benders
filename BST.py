class BSTNode:
    def __init__(self, key, value):
        self.key = key   # e.g., contact name
        self.value = value  # e.g., contact details (dict)
        self.left = None
        self.right = None

class BST:
    def __init__(self):
        self.root = None

    def insert(self, key, value):
        def _insert(node, key, value):
            if node is None:
                return BSTNode(key, value)
            if key < node.key:
                node.left = _insert(node.left, key, value)
            elif key > node.key:
                node.right = _insert(node.right, key, value)
            else:
                node.value = value  # update if key exists
            return node
        self.root = _insert(self.root, key, value)

    def search(self, key):
        def _search(node, key):
            if node is None:
                return None
            if key == node.key:
                return node.value
            elif key < node.key:
                return _search(node.left, key)
            else:
                return _search(node.right, key)
        return _search(self.root, key)

    def inorder(self):
        result = []
        def _inorder(node):
            if node:
                _inorder(node.left)
                result.append((node.key, node.value))
                _inorder(node.right)
        _inorder(self.root)
        return result

import tkinter as tk
from tkinter import messagebox

class ContactManagerApp:
    def __init__(self, master):
        self.master = master
        master.title("Contact Manager with BST")

        self.bst = BST()

        # Labels & entries
        tk.Label(master, text="Contact Name:").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(master, text="Phone Number:").grid(row=1, column=0, padx=5, pady=5)

        self.name_entry = tk.Entry(master)
        self.phone_entry = tk.Entry(master)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.phone_entry.grid(row=1, column=1, padx=5, pady=5)

        # Buttons
        tk.Button(master, text="Add Contact", command=self.add_contact).grid(row=2, column=0, pady=5)
        tk.Button(master, text="Search Contact", command=self.search_contact).grid(row=2, column=1, pady=5)
        tk.Button(master, text="Show All Contacts", command=self.show_all_contacts).grid(row=3, column=0, columnspan=2, pady=5)

        # Listbox to display contacts
        self.listbox = tk.Listbox(master, width=40)
        self.listbox.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    def add_contact(self):
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        if name and phone:
            self.bst.insert(name, {"phone": phone})
            messagebox.showinfo("Success", f"Contact '{name}' added!")
            self.name_entry.delete(0, tk.END)
            self.phone_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Input Error", "Please fill both fields.")

    def search_contact(self):
        name = self.name_entry.get().strip()
        if name:
            result = self.bst.search(name)
            if result:
                messagebox.showinfo("Contact Found", f"Name: {name}\nPhone: {result['phone']}")
            else:
                messagebox.showinfo("Not Found", f"Contact '{name}' not found.")
        else:
            messagebox.showwarning("Input Error", "Enter a name to search.")

    def show_all_contacts(self):
        contacts = self.bst.inorder()
        self.listbox.delete(0, tk.END)
        for name, data in contacts:
            self.listbox.insert(tk.END, f"{name} - {data['phone']}")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = ContactManagerApp(root)
    root.mainloop()