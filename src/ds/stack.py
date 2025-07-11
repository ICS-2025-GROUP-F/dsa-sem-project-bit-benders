class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)
        return f"Pushed: {item}"

    def pop(self):
        if self.is_empty():
            return "Stack is empty"
        return self.items.pop()

    def peek(self):
        if self.is_empty():
            return "Stack is empty"
        return self.items[-1]

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def display(self):
        return self.items
