#!/usr/bin/env python3
"""
Simplified n8n Wrapper for Backpack Volume Tracker
Only tracks rank 1000 volume (minimum volume to be in top 1000)
"""

import sys
import json
import sqlite3
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List


class SimpleVolumeTracker:
    """Simplified tracker that only monitors rank 1000 volume"""
    
    API_URL = "https://api.backpack.exchange/wapi/v1/statistics/leaderboard/volume/week"
    DB_PATH = "data/backpack.db"
    
    def __init__(self):
        self._ensure_db()
    
    def _ensure_db(self):
        """Create database and table if not exists"""
        Path(self.DB_PATH).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rank_1000_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    date_identifier TEXT NOT NULL,
                    rank_1000_volume REAL NOT NULL,
                    user_alias TEXT,
                    week_identifier TEXT
                )
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_date 
                ON rank_1000_snapshots(date_identifier)
            ''')
            conn.commit()
    
    def fetch_rank_1000_volume(self) -> Optional[Dict]:
        """Fetch only the rank 1000 user's volume from API"""
        try:
            # Fetch in batches to get to rank 1000
            # Most efficient: fetch 100 entries starting at offset 900
            all_entries = []
            
            for offset in range(0, 1000, 100):
                params = {'limit': 100, 'offset': offset}
                response = requests.get(self.API_URL, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                if not data:
                    break
                
                # Normalize and add rank
                for idx, entry in enumerate(data):
                    rank = offset + idx + 1
                    all_entries.append({
                        'rank': rank,
                        'volume': float(entry.get('volume', '0')),
                        'user_alias': entry.get('userAlias', entry.get('user_alias', 'unknown'))
                    })
                
                # If we've reached rank 1000, we can stop
                if len(all_entries) >= 1000:
                    break
                
                # If we got fewer entries than requested, we've reached the end
                if len(data) < 100:
                    break
            
            # Find rank 1000 (or closest to it)
            if not all_entries:
                return None
            
            # Try to find exact rank 1000
            for entry in all_entries:
                if entry['rank'] == 1000:
                    return entry
            
            # If not found, return the entry closest to 1000 or the last entry
            if len(all_entries) >= 1000:
                return all_entries[999]  # 0-indexed, so 999 is rank 1000
            else:
                # Return last available entry
                return all_entries[-1]
            
        except Exception as e:
            print(f"Error fetching rank 1000: {e}", file=sys.stderr)
            return None
    
    def store_snapshot(self, volume: float, user_alias: str) -> int:
        """Store rank 1000 snapshot in database"""
        with sqlite3.connect(self.DB_PATH) as conn:
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            date_id = datetime.now().strftime("%Y-%m-%d")
            week_id = datetime.now().strftime("%Y-W%W")
            
            cursor.execute('''
                INSERT INTO rank_1000_snapshots 
                (timestamp, date_identifier, rank_1000_volume, user_alias, week_identifier)
                VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, date_id, volume, user_alias, week_id))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_historical_average(self) -> Optional[Dict]:
        """Calculate average rank 1000 volume from historical data"""
        with sqlite3.connect(self.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    COUNT(*) as snapshot_count,
                    AVG(rank_1000_volume) as avg_volume,
                    MIN(rank_1000_volume) as min_volume,
                    MAX(rank_1000_volume) as max_volume
                FROM rank_1000_snapshots
            ''')
            
            row = cursor.fetchone()
            
            if not row or row[0] == 0:
                return None
            
            return {
                'snapshot_count': row[0],
                'avg_volume': row[1],
                'min_volume': row[2],
                'max_volume': row[3]
            }
    
    def get_recent_snapshots(self, limit: int = 10) -> List[Dict]:
        """Get recent snapshots for trend analysis"""
        with sqlite3.connect(self.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    timestamp,
                    date_identifier,
                    rank_1000_volume,
                    user_alias
                FROM rank_1000_snapshots
                ORDER BY id DESC
                LIMIT ?
            ''', (limit,))
            
            return [
                {
                    'timestamp': row[0],
                    'date': row[1],
                    'volume': row[2],
                    'user': row[3]
                }
                for row in cursor.fetchall()
            ]
    
    def analyze(self, current_volume: float, historical: Dict) -> Dict:
        """Analyze current volume vs historical average"""
        if not historical or historical['snapshot_count'] < 2:
            return {
                'difficulty_score': 0,
                'comparison': 'Need more historical data',
                'recommendation': f'Collected {historical["snapshot_count"] if historical else 0} snapshots. Need 2+ for analysis.'
            }
        
        avg_volume = historical['avg_volume']
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        difficulty_score = volume_ratio * 100
        
        # Lower volume at rank 1000 = easier to farm (less competition)
        # Higher volume at rank 1000 = harder to farm (more competition)
        
        if difficulty_score < 80:
            recommendation = "🎯 EXCELLENT TIME TO FARM - Rank 1000 volume is 20%+ below average"
            comparison = "Much LOWER competition than usual"
        elif difficulty_score < 95:
            recommendation = "✅ GOOD TIME TO FARM - Rank 1000 volume is below average"
            comparison = "LOWER competition than usual"
        elif difficulty_score < 105:
            recommendation = "➖ AVERAGE CONDITIONS - Rank 1000 volume is near historical average"
            comparison = "NORMAL competition"
        elif difficulty_score < 120:
            recommendation = "⚠️ HARDER THAN USUAL - Rank 1000 volume is above average"
            comparison = "HIGHER competition than usual"
        else:
            recommendation = "🔴 VERY HARD TO FARM - Rank 1000 volume is 20%+ above average"
            comparison = "Much HIGHER competition than usual"
        
        return {
            'difficulty_score': round(difficulty_score, 2),
            'volume_change_percent': round((volume_ratio - 1) * 100, 2),
            'comparison': comparison,
            'recommendation': recommendation
        }


def main():
    """Main execution function"""
    try:
        tracker = SimpleVolumeTracker()
        
        # Step 1: Fetch current rank 1000 volume
        current_data = tracker.fetch_rank_1000_volume()
        
        if not current_data:
            return {
                'status': 'error',
                'message': 'Failed to fetch rank 1000 data from Backpack API',
                'timestamp': datetime.now().isoformat()
            }
        
        current_volume = current_data['volume']
        user_alias = current_data['user_alias']
        
        # Step 2: Store snapshot
        snapshot_id = tracker.store_snapshot(current_volume, user_alias)
        
        # Step 3: Get historical data
        historical = tracker.get_historical_average()
        recent_snapshots = tracker.get_recent_snapshots(5)
        
        # Step 4: Analyze
        analysis = tracker.analyze(current_volume, historical)
        
        # Step 5: Build output
        output = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'snapshot_id': snapshot_id,
            'current': {
                'rank_1000_volume': round(current_volume, 2),
                'user_at_rank_1000': user_alias
            },
            'historical': {
                'snapshot_count': historical['snapshot_count'] if historical else 0,
                'avg_rank_1000_volume': round(historical['avg_volume'], 2) if historical else 0,
                'min_rank_1000_volume': round(historical['min_volume'], 2) if historical else 0,
                'max_rank_1000_volume': round(historical['max_volume'], 2) if historical else 0
            },
            'analysis': analysis,
            'recent_snapshots': [
                {
                    'date': s['date'],
                    'volume': round(s['volume'], 2),
                    'user': s['user']
                }
                for s in recent_snapshots
            ]
        }
        
        return output
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Unexpected error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }


if __name__ == '__main__':
    result = main()
    print(json.dumps(result, indent=2))
    
    # Exit with error code if failed
    if result['status'] == 'error':
        sys.exit(1)
    
    sys.exit(0)

