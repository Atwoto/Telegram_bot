# File: database.py
from datetime import datetime
import sqlite3
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_name="mpesa_payments.db"):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        """Initialize database with required tables"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    amount REAL NOT NULL,
                    phone_number TEXT NOT NULL,
                    transaction_id TEXT,
                    status TEXT DEFAULT 'pending',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    group_id INTEGER
                )
                ''')
                conn.commit()
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")

    def add_payment(self, user_id, username, amount, phone_number, group_id=None):
        """Add a new payment record"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                INSERT INTO payments (user_id, username, amount, phone_number, group_id)
                VALUES (?, ?, ?, ?, ?)
                ''', (user_id, username, amount, phone_number, group_id))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error adding payment: {str(e)}")
            return None

    def update_payment_status(self, transaction_id, status):
        """Update payment status after M-Pesa confirmation"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                UPDATE payments 
                SET status = ?, transaction_id = ?
                WHERE id = (
                    SELECT id FROM payments 
                    WHERE status = 'pending' 
                    ORDER BY timestamp DESC LIMIT 1
                )
                ''', (status, transaction_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating payment status: {str(e)}")
            return False

    def get_total_contributions(self, group_id=None):
        """Get total contributions, optionally filtered by group"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                if group_id:
                    cursor.execute('''
                    SELECT COALESCE(SUM(amount), 0) as total,
                           COUNT(DISTINCT user_id) as contributors
                    FROM payments 
                    WHERE status = 'completed' AND group_id = ?
                    ''', (group_id,))
                else:
                    cursor.execute('''
                    SELECT COALESCE(SUM(amount), 0) as total,
                           COUNT(DISTINCT user_id) as contributors
                    FROM payments 
                    WHERE status = 'completed'
                    ''')
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting total contributions: {str(e)}")
            return (0, 0)