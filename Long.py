import json
import os
from datetime import datetime


class Expense:
    """Represents a single expense entry."""

    def __init__(self, amount: float, category: str, description: str, date: str = None):
        self.amount = float(amount)
        self.category = category.strip().title()
        self.description = description.strip()
        self.date = date if date else datetime.now().strftime("%Y-%m-%d %H:%M")

    def to_dict(self) -> dict:
        """Converts the Expense object into a dictionary for JSON serialization."""
        return {
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "date": self.date,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Creates an Expense object from a dictionary."""
        return cls(
            amount=data["amount"],
            category=data["category"],
            description=data["description"],
            date=data["date"],
        )

    def __str__(self) -> str:
        return f"[{self.date}] {self.category:<12} | ₹{self.amount:>8.2f} | {self.description}"


class ExpenseTracker:
    """Manages a collection of expenses and handles persistent storage."""

    def __init__(self, filename: str = "expenses.json"):
        self.filename = filename
        self.expenses = []
        self.load_expenses()

    def load_expenses(self):
        """Loads saved expenses from a JSON file if it exists."""
        if not os.path.exists(self.filename):
            return

        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                data = json.load(file)
                self.expenses = [Expense.from_dict(item) for item in data]
        except (json.JSONDecodeError, KeyError) as error:
            print(f"Warning: Could not read {self.filename} ({error}). Starting fresh.")
            self.expenses = []

    def save_expenses(self):
        """Saves current expenses to a JSON file."""
        with open(self.filename, "w", encoding="utf-8") as file:
            json.dump([exp.to_dict() for exp in self.expenses], file, indent=4)

    def add_expense(self, amount: float, category: str, description: str):
        """Adds a new expense and saves the updated list."""
        expense = Expense(amount, category, description)
        self.expenses.append(expense)
        self.save_expenses()
        print("Expense added successfully.")

    def delete_expense(self, index: int) -> bool:
        """Deletes an expense by its 1-based display index."""
        if 1 <= index <= len(self.expenses):
            removed = self.expenses.pop(index - 1)
            self.save_expenses()
            print(f"Deleted: {removed.description} (₹{removed.amount:.2f})")
            return True
        return False

    def view_all(self):
        """Displays all recorded expenses."""
        if not self.expenses:
            print("\nNo expenses recorded yet.")
            return

        print("\n" + "=" * 65)
        print(f"{'#':<4} {'Date':<18} {'Category':<12} | {'Amount':>9} | Description")
        print("-" * 65)
        for idx, expense in enumerate(self.expenses, start=1):
            print(f"{idx:<4} {expense}")
        print("=" * 65)

    def view_summary(self):
        """Calculates and displays total spending broken down by category."""
        if not self.expenses:
            print("\nNo expenses to summarize.")
            return

        category_totals = {}
        grand_total = 0.0

        for expense in self.expenses:
            category_totals[expense.category] = (
                category_totals.get(expense.category, 0.0) + expense.amount
            )
            grand_total += expense.amount

        print("\n--- Spending Summary by Category ---")
        for category, total in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            percentage = (total / grand_total) * 100
            print(f"{category:<15}: ₹{total:>9.2f} ({percentage:>5.1f}%)")
        print("-" * 40)
        print(f"{'Total Spending':<15}: ₹{grand_total:>9.2f}")


def get_valid_float(prompt: str) -> float:
    """Prompts the user until a valid positive number is entered."""
    while True:
        try:
            value = float(input(prompt))
            if value <= 0:
                print("Please enter an amount greater than zero.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a numeric value.")


def main():
    tracker = ExpenseTracker()

    while True:
        print("\n=== Personal Expense Tracker ===")
        print("1. Add an Expense")
        print("2. View All Expenses")
        print("3. View Category Summary")
        print("4. Delete an Expense")
        print("5. Exit")

        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            amount = get_valid_float("Enter amount (₹): ")
            category = input("Enter category (e.g., Food, Travel, Bills): ") or "General"
            description = input("Enter description: ") or "No description"
            tracker.add_expense(amount, category, description)

        elif choice == "2":
            tracker.view_all()

        elif choice == "3":
            tracker.view_summary()

        elif choice == "4":
            tracker.view_all()
            if tracker.expenses:
                try:
                    idx = int(input("\nEnter the # of the expense to delete: "))
                    if not tracker.delete_expense(idx):
                        print("Invalid item number.")
                except ValueError:
                    print("Please enter a valid number.")

        elif choice == "5":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please select a number between 1 and 5.")


if __name__ == "__main__":
    main()
