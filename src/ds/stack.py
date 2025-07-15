"""
Stack data-structure for Book Logger
"""

class Stack:
    def __init__(self):
        self._items: list[str] = []

    # ───────── basic ops ─────────
    def push(self, item: str) -> str:
        self._items.append(item)
        return f"Pushed: {item}"

    def pop(self) -> str:
        if self.is_empty():
            return "Stack is empty"
        return f"Popped: {self._items.pop()}"

    def peek(self):
        return "Stack is empty" if self.is_empty() else self._items[-1]

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def size(self) -> int:
        return len(self._items)

    # ───────── extra ops ─────────
    def find(self, item: str) -> int:
        """
        Return 0-based index from top of stack; -1 if not found.
        Top of stack = right-most list element.
        """
        try:
            return len(self._items) - 1 - self._items[::-1].index(item)
        except ValueError:
            return -1

    def reverse(self) -> None:
        """Reverse the stack in place (O(n))."""
        self._items.reverse()

    def clear(self) -> None:
        """Remove all items."""
        self._items.clear()

    # ───────── misc ─────────
    def __iter__(self):
        """Iterate from bottom to top (for debugging/visualisation)."""
        return iter(self._items)

    def __repr__(self) -> str:
        return f"Stack({self._items})"
