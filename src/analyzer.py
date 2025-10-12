from typing import List, Dict, Optional
from datetime import datetime
import statistics

class BackpackAnalyzer:
    def __init__(self, database):
        self.db = database

    def calculate_stats(self, entries: List[Dict]) -> Dict:
        """Calculate statistics for a set of leaderboard entries"""
        if not entries:
            return {
                'total_entries': 0,
                'total_volume': 0,
                'avg_volume': 0,
                'median_volume': 0,
                'min_volume': 0,
                'max_volume': 0,
                'percentile_25': 0,
                'percentile_50': 0,
                'percentile_75': 0,
            }

        volumes = [entry['volume'] for entry in entries]

        return {
            'total_entries': len(entries),
            'total_volume': sum(volumes),
            'avg_volume': statistics.mean(volumes),
            'median_volume': statistics.median(volumes),
            'min_volume': min(volumes),
            'max_volume': max(volumes),
            'percentile_25': self._percentile(volumes, 25),
            'percentile_50': self._percentile(volumes, 50),
            'percentile_75': self._percentile(volumes, 75),
        }

    @staticmethod
    def _percentile(values: List[float], percentile: int) -> float:
        """Calculate the nth percentile of a list of values"""
        if not values:
            return 0

        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)

        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower = sorted_values[int(index)]
            upper = sorted_values[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))

    def get_historical_average(self) -> Dict:
        """Calculate average statistics across all historical snapshots"""
        snapshots = self.db.get_all_snapshots()

        # Filter out empty/corrupted snapshots (ones with 0 entries)
        valid_snapshots = [s for s in snapshots if s['entry_count'] > 0]

        if not valid_snapshots:
            return {
                'snapshot_count': 0,
                'avg_total_volume': 0,
                'avg_avg_volume': 0,
                'avg_entry_count': 0
            }

        return {
            'snapshot_count': len(valid_snapshots),
            'avg_total_volume': statistics.mean([s['total_volume'] for s in valid_snapshots]),
            'avg_avg_volume': statistics.mean([s['avg_volume'] for s in valid_snapshots]),
            'avg_entry_count': statistics.mean([s['entry_count'] for s in valid_snapshots])
        }

    def compare_with_history(self, current_stats: Dict) -> Dict:
        """Compare current statistics with historical average"""
        historical = self.get_historical_average()

        if historical['snapshot_count'] == 0:
            return {
                'comparison': 'No historical data available',
                'difficulty_score': 0,
                'recommendation': 'First snapshot - no comparison available'
            }

        # Need at least 2 snapshots for meaningful comparison
        if historical['snapshot_count'] < 2:
            return {
                'comparison': 'Need more historical data',
                'difficulty_score': 0,
                'recommendation': 'Collect more snapshots over time for historical comparison (need 2+ snapshots)'
            }

        # Calculate difficulty score (higher = harder to farm)
        # Based on total volume and average volume
        total_volume_ratio = current_stats['total_volume'] / historical['avg_total_volume'] if historical['avg_total_volume'] > 0 else 1
        avg_volume_ratio = current_stats['avg_volume'] / historical['avg_avg_volume'] if historical['avg_avg_volume'] > 0 else 1

        difficulty_score = (total_volume_ratio + avg_volume_ratio) / 2 * 100

        # Generate recommendation
        if difficulty_score < 80:
            recommendation = "GOOD TIME TO FARM - Volume is significantly below average"
            comparison = "Current volume is LOW compared to historical average"
        elif difficulty_score < 95:
            recommendation = "DECENT TIME TO FARM - Volume is below average"
            comparison = "Current volume is SLIGHTLY LOW compared to historical average"
        elif difficulty_score < 105:
            recommendation = "AVERAGE CONDITIONS - Volume is near historical average"
            comparison = "Current volume is SIMILAR to historical average"
        elif difficulty_score < 120:
            recommendation = "HARDER THAN USUAL - Volume is above average"
            comparison = "Current volume is SLIGHTLY HIGH compared to historical average"
        else:
            recommendation = "VERY HARD TO FARM - Volume is significantly above average"
            comparison = "Current volume is HIGH compared to historical average"

        return {
            'comparison': comparison,
            'difficulty_score': round(difficulty_score, 2),
            'total_volume_change': round((total_volume_ratio - 1) * 100, 2),
            'avg_volume_change': round((avg_volume_ratio - 1) * 100, 2),
            'recommendation': recommendation,
            'historical': historical,
            'current': current_stats
        }

    def get_rank_thresholds(self, entries: List[Dict]) -> Dict:
        """Get volume thresholds for specific ranks"""
        if not entries:
            return {}

        # Sort entries by rank to ensure correct indexing
        sorted_entries = sorted(entries, key=lambda x: x['rank'])

        thresholds = {}

        # Define target ranks
        target_ranks = [10, 50, 100, 250, 500, 1000]

        for rank in target_ranks:
            # Find the entry at or near this rank
            matching_entries = [e for e in sorted_entries if e['rank'] == rank]

            if matching_entries:
                thresholds[f'rank_{rank}'] = matching_entries[0]['volume']
            elif len(sorted_entries) >= rank:
                # If exact rank not found but we have enough entries
                # Use the entry at the rank position (rank-1 for 0-indexed)
                thresholds[f'rank_{rank}'] = sorted_entries[rank - 1]['volume']

        return thresholds

    def analyze_snapshot(self, snapshot_id: int) -> Optional[Dict]:
        """Analyze a specific snapshot"""
        entries = self.db.get_snapshot_data(snapshot_id)

        if not entries:
            return None

        stats = self.calculate_stats(entries)
        thresholds = self.get_rank_thresholds(entries)

        return {
            'snapshot_id': snapshot_id,
            'stats': stats,
            'rank_thresholds': thresholds
        }

    def get_trending_data(self, limit: int = 10) -> List[Dict]:
        """Get trending data from recent snapshots"""
        snapshots = self.db.get_all_snapshots()

        if not snapshots:
            return []

        # Return most recent snapshots
        return snapshots[:limit]
