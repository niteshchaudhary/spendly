import sqlite3
import os
from flask import g
from werkzeug.security import generate_password_hash

DATABASE = 'expense_tracker.db'

def get_db():
    """Get a database connection."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        # Enable foreign key constraints
        db.execute("PRAGMA foreign_keys = ON")
    return db

def init_db():
    """Initialize the database with tables."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create expenses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date DATE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')

        conn.commit()

def seed_db():
    """Seed the database with sample data."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        # Check if we already have data
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] > 0:
            return  # Already seeded

        # Insert demo user using PBKDF2 hashing method (more compatible)
        cursor.execute('''
            INSERT INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
        ''', ('Demo User', 'demo@sudly.com', generate_password_hash('demo123', method='pbkdf2:sha256')))

        # Get user ID for the demo user
        cursor.execute("SELECT id FROM users WHERE email = ?", ('demo@sudly.com',))
        user_id = cursor.fetchone()[0]

        # Insert sample expenses covering all categories
        sample_expenses = [
            # Food
            (user_id, 12.50, 'Food', '2024-01-05', 'Weekly grocery shopping'),
            (user_id, 8.75, 'Food', '2024-01-10', 'Sandwich and drink'),

            # Transport
            (user_id, 45.00, 'Transport', '2024-01-03', 'Fill up tank'),
            (user_id, 12.00, 'Transport', '2024-01-07', 'Daily commute'),

            # Bills
            (user_id, 85.00, 'Bills', '2024-01-01', 'Monthly electricity'),
            (user_id, 42.00, 'Bills', '2024-01-15', 'High-speed internet'),

            # Health
            (user_id, 25.00, 'Health', '2024-01-08', 'Prescription medication'),
            (user_id, 60.00, 'Health', '2024-01-01', 'Monthly fitness'),

            # Entertainment
            (user_id, 15.00, 'Entertainment', '2024-01-12', 'Weekend movie'),
            (user_id, 20.00, 'Entertainment', '2024-01-20', 'Live music show'),

            # Shopping
            (user_id, 35.00, 'Shopping', '2024-01-06', 'Casual clothing'),
            (user_id, 25.00, 'Shopping', '2024-01-18', 'Programming guide'),

            # Other
            (user_id, 10.00, 'Other', '2024-01-09', 'Local food bank'),
            (user_id, 5.00, 'Other', '2024-01-14', 'Downtown parking'),
        ]

        cursor.executemany('''
            INSERT INTO expenses (user_id, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?)
        ''', sample_expenses)

        conn.commit()