import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import mysql.connector
from mysql.connector import Error
import datetime
import json
from collections import deque
import threading
import time

class Queue:
    """Custom Queue implementation with logging capabilities"""
    
    def __init__(self, name="Queue", max_size=None):
        self.name = name
        self.items = deque()
        self.max_size = max_size
        self.operations_log = []
        self.created_at = datetime.datetime.now()
    
    def enqueue(self, item):
        """Add item to rear of queue - O(1) time complexity"""
        if self.max_size and len(self.items) >= self.max_size:
            raise Exception(f"Queue '{self.name}' is full (max size: {self.max_size})")
        
        self.items.append(item)
        operation = {
            'type': 'enqueue',
            'item': item,
            'timestamp': datetime.datetime.now().isoformat(),
            'queue_size': len(self.items)
        }
        self.operations_log.append(operation)
        return operation
    
    def dequeue(self):
        """Remove and return item from front of queue - O(1) time complexity"""
        if self.is_empty():
            raise Exception(f"Queue '{self.name}' is empty")
        
        item = self.items.popleft()
        operation = {
            'type': 'dequeue',
            'item': item,
            'timestamp': datetime.datetime.now().isoformat(),
            'queue_size': len(self.items)
        }
        self.operations_log.append(operation)
        return item, operation
    
    def front(self):
        """Return front item without removing - O(1) time complexity"""
        if self.is_empty():
            raise Exception(f"Queue '{self.name}' is empty")
        return self.items[0]
    
    def rear(self):
        """Return rear item without removing - O(1) time complexity"""
        if self.is_empty():
            raise Exception(f"Queue '{self.name}' is empty")
        return self.items[-1]
    
    def is_empty(self):
        """Check if queue is empty - O(1) time complexity"""
        return len(self.items) == 0
    
    def size(self):
        """Return queue size - O(1) time complexity"""
        return len(self.items)
    
    def clear(self):
        """Clear all items from queue - O(1) time complexity"""
        self.items.clear()
        operation = {
            'type': 'clear',
            'timestamp': datetime.datetime.now().isoformat(),
            'queue_size': 0
        }
        self.operations_log.append(operation)
        return operation
    
    def to_list(self):
        """Convert queue to list for display - O(n) time complexity"""
        return list(self.items)
    
    def search(self, item):
        """Search for item in queue - O(n) time complexity"""
        try:
            index = list(self.items).index(item)
            return index
        except ValueError:
            return -1

class DatabaseManager:
    """Handle MySQL database operations"""
    
    def __init__(self, host='localhost', user='root', password='Ciela5684.', database='queue_app'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.setup_database()
    
    def connect(self):
        """Create database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return True
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to connect to database: {e}")
            return False
    
    def setup_database(self):
        """Create database and tables if they don't exist"""
        try:
            # Connect without database to create it
            temp_connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            cursor = temp_connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            cursor.close()
            temp_connection.close()
            
            # Connect to the database and create tables
            if self.connect():
                cursor = self.connection.cursor()
                
                # Create queues table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS queues (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL UNIQUE,
                        max_size INT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        items TEXT,
                        operations_log TEXT
                    )
                """)
                
                # Create queue_operations table for logging
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS queue_operations (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        queue_name VARCHAR(255) NOT NULL,
                        operation_type VARCHAR(50) NOT NULL,
                        item_value TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        queue_size INT
                    )
                """)
                
                self.connection.commit()
                cursor.close()
                
        except Error as e:
            messagebox.showerror("Database Setup Error", f"Failed to setup database: {e}")
    
    def save_queue(self, queue):
        """Save queue to database"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            items_json = json.dumps(queue.to_list())
            operations_json = json.dumps(queue.operations_log)
            
            cursor.execute("""
                INSERT INTO queues (name, max_size, items, operations_log)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                items = VALUES(items),
                operations_log = VALUES(operations_log)
            """, (queue.name, queue.max_size, items_json, operations_json))
            
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to save queue: {e}")
            return False
    
    def load_queue(self, queue_name):
        """Load queue from database"""
        if not self.connection:
            if not self.connect():
                return None
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM queues WHERE name = %s", (queue_name,))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                queue = Queue(result[1], result[2])  # name, max_size
                if result[4]:  # items
                    items = json.loads(result[4])
                    queue.items = deque(items)
                if result[5]:  # operations_log
                    queue.operations_log = json.loads(result[5])
                return queue
            return None
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load queue: {e}")
            return None
    
    def get_all_queues(self):
        """Get all queue names from database"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM queues")
            results = cursor.fetchall()
            cursor.close()
            return [result[0] for result in results]
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to get queues: {e}")
            return []
    
    def delete_queue(self, queue_name):
        """Delete queue from database"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM queues WHERE name = %s", (queue_name,))
            cursor.execute("DELETE FROM queue_operations WHERE queue_name = %s", (queue_name,))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to delete queue: {e}")
            return False
    
    def log_operation(self, queue_name, operation):
        """Log operation to database"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO queue_operations (queue_name, operation_type, item_value, queue_size)
                VALUES (%s, %s, %s, %s)
            """, (queue_name, operation['type'], 
                  operation.get('item', ''), operation.get('queue_size', 0)))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Failed to log operation: {e}")
            return False

class QueueApp:
    """Main application class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Queue Data Structure Manager")
        self.root.geometry("800x600")
        
        self.db_manager = DatabaseManager()
        self.current_queue = None
        self.queues = {}
        
        self.setup_gui()
        self.load_existing_queues()
        self.start_auto_save()
    
    def setup_gui(self):
        """Setup the GUI components"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Queue management frame
        queue_frame = ttk.LabelFrame(main_frame, text="Queue Management", padding="10")
        queue_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Queue selection
        ttk.Label(queue_frame, text="Queue:").grid(row=0, column=0, sticky=tk.W)
        self.queue_var = tk.StringVar()
        self.queue_combo = ttk.Combobox(queue_frame, textvariable=self.queue_var, width=20)
        self.queue_combo.grid(row=0, column=1, padx=(5, 10))
        self.queue_combo.bind('<<ComboboxSelected>>', self.on_queue_selected)
        
        # Create new queue
        ttk.Button(queue_frame, text="New Queue", command=self.create_new_queue).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(queue_frame, text="Delete Queue", command=self.delete_queue).grid(row=0, column=3, padx=(0, 5))
        
        # Queue operations frame
        ops_frame = ttk.LabelFrame(main_frame, text="Queue Operations", padding="10")
        ops_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Enqueue
        ttk.Label(ops_frame, text="Item:").grid(row=0, column=0, sticky=tk.W)
        self.item_var = tk.StringVar()
        ttk.Entry(ops_frame, textvariable=self.item_var, width=20).grid(row=0, column=1, padx=(5, 10))
        ttk.Button(ops_frame, text="Enqueue", command=self.enqueue_item).grid(row=0, column=2, padx=(0, 5))
        
        # Dequeue
        ttk.Button(ops_frame, text="Dequeue", command=self.dequeue_item).grid(row=1, column=0, pady=(10, 0))
        ttk.Button(ops_frame, text="Front", command=self.show_front).grid(row=1, column=1, pady=(10, 0))
        ttk.Button(ops_frame, text="Rear", command=self.show_rear).grid(row=1, column=2, pady=(10, 0))
        
        # Search
        ttk.Label(ops_frame, text="Search:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.search_var = tk.StringVar()
        ttk.Entry(ops_frame, textvariable=self.search_var, width=20).grid(row=2, column=1, padx=(5, 10), pady=(10, 0))
        ttk.Button(ops_frame, text="Search", command=self.search_item).grid(row=2, column=2, pady=(10, 0))
        
        # Clear queue
        ttk.Button(ops_frame, text="Clear Queue", command=self.clear_queue).grid(row=3, column=0, pady=(10, 0))
        
        # Queue display frame
        display_frame = ttk.LabelFrame(main_frame, text="Queue Contents", padding="10")
        display_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0), pady=(0, 10))
        
        self.queue_listbox = tk.Listbox(display_frame, height=10, width=30)
        self.queue_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.queue_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.queue_listbox.config(yscrollcommand=scrollbar.set)
        
        # Info frame
        info_frame = ttk.LabelFrame(display_frame, text="Queue Info", padding="5")
        info_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.info_label = ttk.Label(info_frame, text="No queue selected")
        self.info_label.grid(row=0, column=0, sticky=tk.W)
        
        # Logging frame
        log_frame = ttk.LabelFrame(main_frame, text="Operation Log", padding="10")
        log_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
    
    def create_new_queue(self):
        """Create a new queue"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create New Queue")
        dialog.geometry("300x150")
        dialog.grab_set()
        
        ttk.Label(dialog, text="Queue Name:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var, width=20).grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Max Size (optional):").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        size_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=size_var, width=20).grid(row=1, column=1, padx=10, pady=10)
        
        def create_queue():
            name = name_var.get().strip()
            if not name:
                messagebox.showerror("Error", "Queue name cannot be empty")
                return
            
            if name in self.queues:
                messagebox.showerror("Error", "Queue already exists")
                return
            
            max_size = None
            if size_var.get().strip():
                try:
                    max_size = int(size_var.get().strip())
                    if max_size <= 0:
                        messagebox.showerror("Error", "Max size must be positive")
                        return
                except ValueError:
                    messagebox.showerror("Error", "Max size must be a number")
                    return
            
            queue = Queue(name, max_size)
            self.queues[name] = queue
            self.update_queue_combo()
            self.queue_var.set(name)
            self.on_queue_selected(None)
            dialog.destroy()
        
        ttk.Button(dialog, text="Create", command=create_queue).grid(row=2, column=0, columnspan=2, pady=20)
    
    def delete_queue(self):
        """Delete the selected queue"""
        if not self.current_queue:
            messagebox.showwarning("Warning", "No queue selected")
            return
        
        if messagebox.askyesno("Confirm", f"Delete queue '{self.current_queue.name}'?"):
            self.db_manager.delete_queue(self.current_queue.name)
            del self.queues[self.current_queue.name]
            self.current_queue = None
            self.update_queue_combo()
            self.update_display()
    
    def on_queue_selected(self, event):
        """Handle queue selection"""
        queue_name = self.queue_var.get()
        if queue_name in self.queues:
            self.current_queue = self.queues[queue_name]
            self.update_display()
    
    def update_queue_combo(self):
        """Update the queue combobox"""
        self.queue_combo['values'] = list(self.queues.keys())
    
    def enqueue_item(self):
        """Enqueue an item"""
        if not self.current_queue:
            messagebox.showwarning("Warning", "No queue selected")
            return
        
        item = self.item_var.get().strip()
        if not item:
            messagebox.showwarning("Warning", "Item cannot be empty")
            return
        
        try:
            operation = self.current_queue.enqueue(item)
            self.db_manager.log_operation(self.current_queue.name, operation)
            self.update_display()
            self.log_operation(f"Enqueued '{item}' to {self.current_queue.name}")
            self.item_var.set("")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def dequeue_item(self):
        """Dequeue an item"""
        if not self.current_queue:
            messagebox.showwarning("Warning", "No queue selected")
            return
        
        try:
            item, operation = self.current_queue.dequeue()
            self.db_manager.log_operation(self.current_queue.name, operation)
            self.update_display()
            self.log_operation(f"Dequeued '{item}' from {self.current_queue.name}")
            messagebox.showinfo("Dequeued", f"Removed: {item}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def show_front(self):
        """Show front item"""
        if not self.current_queue:
            messagebox.showwarning("Warning", "No queue selected")
            return
        
        try:
            item = self.current_queue.front()
            messagebox.showinfo("Front Item", f"Front: {item}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def show_rear(self):
        """Show rear item"""
        if not self.current_queue:
            messagebox.showwarning("Warning", "No queue selected")
            return
        
        try:
            item = self.current_queue.rear()
            messagebox.showinfo("Rear Item", f"Rear: {item}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def search_item(self):
        """Search for an item"""
        if not self.current_queue:
            messagebox.showwarning("Warning", "No queue selected")
            return
        
        item = self.search_var.get().strip()
        if not item:
            messagebox.showwarning("Warning", "Search term cannot be empty")
            return
        
        index = self.current_queue.search(item)
        if index != -1:
            messagebox.showinfo("Search Result", f"'{item}' found at position {index}")
        else:
            messagebox.showinfo("Search Result", f"'{item}' not found in queue")
    
    def clear_queue(self):
        """Clear the queue"""
        if not self.current_queue:
            messagebox.showwarning("Warning", "No queue selected")
            return
        
        if messagebox.askyesno("Confirm", f"Clear all items from '{self.current_queue.name}'?"):
            operation = self.current_queue.clear()
            self.db_manager.log_operation(self.current_queue.name, operation)
            self.update_display()
            self.log_operation(f"Cleared queue {self.current_queue.name}")
    
    def update_display(self):
        """Update the display"""
        self.queue_listbox.delete(0, tk.END)
        
        if self.current_queue:
            items = self.current_queue.to_list()
            for i, item in enumerate(items):
                self.queue_listbox.insert(tk.END, f"{i}: {item}")
            
            info = f"Size: {self.current_queue.size()}"
            if self.current_queue.max_size:
                info += f" / {self.current_queue.max_size}"
            info += f" | Empty: {self.current_queue.is_empty()}"
            self.info_label.config(text=info)
        else:
            self.info_label.config(text="No queue selected")
    
    def log_operation(self, message):
        """Log operation to the text widget"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
    
    def load_existing_queues(self):
        """Load existing queues from database"""
        queue_names = self.db_manager.get_all_queues()
        for name in queue_names:
            queue = self.db_manager.load_queue(name)
            if queue:
                self.queues[name] = queue
        self.update_queue_combo()
    
    def start_auto_save(self):
        """Start auto-save thread"""
        def auto_save():
            while True:
                time.sleep(30)  # Save every 30 seconds
                for queue in self.queues.values():
                    self.db_manager.save_queue(queue)
        
        thread = threading.Thread(target=auto_save, daemon=True)
        thread.start()
    
    def on_closing(self):
        """Handle application closing"""
        for queue in self.queues.values():
            self.db_manager.save_queue(queue)
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = QueueApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()