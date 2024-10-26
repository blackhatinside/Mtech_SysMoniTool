# SysMoniTool/src/python/database.py
import sqlite3
import logging
from datetime import datetime

class Database:
    def __init__(self, db_file):
        try:
            self.conn = sqlite3.connect(db_file)
            self.create_tables()
        except Exception as e:
            logging.error(f"Database initialization error: {e}")
            raise

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cpu_usage REAL,
                memory_usage REAL,
                disk_io REAL,
                network_usage REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS thresholds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                value REAL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def insert_data(self, metrics):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO metrics (timestamp, cpu_usage, memory_usage, disk_io, network_usage)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            metrics['timestamp'],
            metrics['cpu_usage'],
            metrics['memory_usage'],
            metrics['disk_io'],
            metrics['network_usage']
        ))
        self.conn.commit()

    def query_data(self, start_date, end_date):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM metrics
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
        ''', (start_date, end_date))
        return cursor.fetchall()

    def get_latest_metrics(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM metrics
            ORDER BY timestamp DESC
            LIMIT 1
        ''')
        return cursor.fetchone()
    
    def update_threshold(self, name, value):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO thresholds (name, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (name, value))
        self.conn.commit()
    
    def get_thresholds(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT name, value FROM thresholds')
        return dict(cursor.fetchall())

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()


