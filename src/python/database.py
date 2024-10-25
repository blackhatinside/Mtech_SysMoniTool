import sqlite3

class Database:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.create_tables()

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
        self.conn.commit()

    def insert_data(self, metrics):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO metrics (cpu_usage, memory_usage, disk_io, network_usage)
            VALUES (?, ?, ?, ?)
        ''', (metrics['cpu_usage'], metrics['memory_usage'], metrics['disk_io'], metrics['network_usage']))
        self.conn.commit()

    def query_data(self, start_date, end_date):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM metrics
            WHERE timestamp BETWEEN ? AND ?
        ''', (start_date, end_date))
        return cursor.fetchall()

    def __del__(self):
        self.conn.close()
