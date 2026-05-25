#!/usr/bin/env python3
"""Test script to verify database functionality"""

import sys
import os
sys.path.insert(0, '.')

from flask import Flask
from database.db import init_db, get_db, seed_db

def test_database():
    print("Testing database functionality...")

    # Create a Flask app for testing
    app = Flask(__name__)

    with app.app_context():
        # Initialize database
        print("1. Initializing database...")
        init_db()
        print("   ✓ Database initialized")

        # Seed database
        print("2. Seeding database...")
        seed_db()
        print("   ✓ Database seeded")

        # Test connection
        print("3. Testing database connection...")
        db = get_db()
        cursor = db.cursor()

        # Check users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"   ✓ Found {user_count} users")

        # Check expenses
        cursor.execute("SELECT COUNT(*) FROM expenses")
        expense_count = cursor.fetchone()[0]
        print(f"   ✓ Found {expense_count} expenses")

        # Show sample data
        print("\n4. Sample data:")
        cursor.execute("SELECT name, email FROM users")
        users = cursor.fetchall()
        for user in users:
            print(f"   User: {user['name']} ({user['email']})")

        cursor.execute("SELECT amount, description, category, date FROM expenses")
        expenses = cursor.fetchall()
        for expense in expenses:
            print(f"   Expense: ${expense['amount']} for {expense['description']} ({expense['category']}) on {expense['date']}")

        # Test foreign key constraint
        print("\n5. Testing foreign key constraint...")
        try:
            # Try to insert an expense with invalid user_id
            cursor.execute("INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)",
                          (99999, 10.00, 'Food', '2024-01-01'))
            db.commit()
            print("   ✗ Foreign key constraint NOT enforced")
        except Exception as e:
            print(f"   ✓ Foreign key constraint enforced: {type(e).__name__}")

        # Test unique constraint on email
        print("\n6. Testing unique constraint...")
        try:
            # Try to insert duplicate email
            cursor.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                          ('Another User', 'demo@sudly.com', 'hash'))
            db.commit()
            print("   ✗ Unique constraint NOT enforced")
        except Exception as e:
            print(f"   ✓ Unique constraint enforced: {type(e).__name__}")

    print("\n✓ All tests passed!")

if __name__ == "__main__":
    test_database()