import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional

class Database:
    def __init__(self, db_path: str = "data/backpack.db"):
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_db()

    def _ensure_db_directory(self):
        """Create data directory if it doesn't exist"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create snapshots table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    week_identifier TEXT NOT NULL
                )
            ''')

            # Create leaderboard_entries table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS leaderboard_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    snapshot_id INTEGER NOT NULL,
                    rank INTEGER NOT NULL,
                    user_alias TEXT NOT NULL,
                    volume REAL NOT NULL,
                    quote_symbol TEXT NOT NULL,
                    FOREIGN KEY (snapshot_id) REFERENCES snapshots (id)
                )
            ''')

            # Create indexes for better query performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_snapshot_week
                ON snapshots(week_identifier)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_entries_snapshot
                ON leaderboard_entries(snapshot_id)
            ''')

            conn.commit()

    def create_snapshot(self, week_identifier: str) -> int:
        """Create a new snapshot and return its ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            timestamp = datetime.now().isoformat()

            cursor.execute('''
                INSERT INTO snapshots (timestamp, week_identifier)
                VALUES (?, ?)
            ''', (timestamp, week_identifier))

            conn.commit()
            return cursor.lastrowid

    def insert_leaderboard_entries(self, snapshot_id: int, entries: List[Dict]):
        """Insert multiple leaderboard entries for a snapshot"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            data = [
                (
                    snapshot_id,
                    entry['rank'],
                    entry['user_alias'],
                    float(entry['volume']),
                    entry['quote_symbol']
                )
                for entry in entries
            ]

            cursor.executemany('''
                INSERT INTO leaderboard_entries
                (snapshot_id, rank, user_alias, volume, quote_symbol)
                VALUES (?, ?, ?, ?, ?)
            ''', data)

            conn.commit()

    def get_latest_snapshot(self) -> Optional[Tuple[int, str, str]]:
        """Get the latest snapshot (id, timestamp, week_identifier)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, timestamp, week_identifier
                FROM snapshots
                ORDER BY id DESC
                LIMIT 1
            ''')
            return cursor.fetchone()

    def get_snapshot_data(self, snapshot_id: int) -> List[Dict]:
        """Get all leaderboard entries for a specific snapshot"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT rank, user_alias, volume, quote_symbol
                FROM leaderboard_entries
                WHERE snapshot_id = ?
                ORDER BY rank ASC
            ''', (snapshot_id,))

            return [
                {
                    'rank': row[0],
                    'user_alias': row[1],
                    'volume': row[2],
                    'quote_symbol': row[3]
                }
                for row in cursor.fetchall()
            ]

    def get_all_snapshots(self) -> List[Dict]:
        """Get all snapshots with basic stats"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT
                    s.id,
                    s.timestamp,
                    s.week_identifier,
                    COUNT(l.id) as entry_count,
                    SUM(l.volume) as total_volume,
                    AVG(l.volume) as avg_volume
                FROM snapshots s
                LEFT JOIN leaderboard_entries l ON s.id = l.snapshot_id
                GROUP BY s.id
                ORDER BY s.id DESC
            ''')

            return [
                {
                    'id': row[0],
                    'timestamp': row[1],
                    'week_identifier': row[2],
                    'entry_count': row[3],
                    'total_volume': row[4] or 0,
                    'avg_volume': row[5] or 0
                }
                for row in cursor.fetchall()
            ]

    def get_snapshot_count(self) -> int:
        """Get total number of snapshots"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM snapshots')
            return cursor.fetchone()[0]
