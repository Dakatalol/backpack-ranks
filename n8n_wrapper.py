#!/usr/bin/env python3
"""
n8n Wrapper Script for Backpack Volume Tracker
Executes analysis and outputs structured JSON for n8n workflow consumption
"""

import sys
import json
import os
from datetime import datetime
from src.database import Database
from src.collector import BackpackCollector
from src.analyzer import BackpackAnalyzer


def main():
    """Main execution function that collects data and returns JSON output"""
    # Suppress print statements from collector by redirecting stdout temporarily
    original_stdout = sys.stdout
    devnull = None
    
    try:
        devnull = open(os.devnull, 'w')
        sys.stdout = devnull
        
        db = Database()
        collector = BackpackCollector()
        analyzer = BackpackAnalyzer(db)

        # Step 1: Collect current data
        result = collector.collect_and_summarize(max_entries=1000)

        if not result['success']:
            return {
                'status': 'error',
                'message': 'Failed to collect data from Backpack API',
                'timestamp': datetime.now().isoformat()
            }

        current_stats = result['stats']
        entries = result['entries']

        # Store in database
        snapshot_id = db.create_snapshot(current_stats['week_identifier'])
        db.insert_leaderboard_entries(snapshot_id, entries)

        # Step 2: Analyze against historical data
        snapshot_count = db.get_snapshot_count()

        # Get rank thresholds
        thresholds = analyzer.get_rank_thresholds(entries)

        # Compare with history if we have enough data
        if snapshot_count >= 2:
            comparison = analyzer.compare_with_history(current_stats)
        else:
            comparison = {
                'comparison': 'Need more historical data',
                'difficulty_score': 0,
                'recommendation': f'Snapshot {snapshot_count} collected. Need 2+ snapshots for analysis.',
                'total_volume_change': 0,
                'avg_volume_change': 0
            }

        # Step 3: Format output as JSON
        output = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'snapshot_id': snapshot_id,
            'week_identifier': current_stats['week_identifier'],
            'current_stats': {
                'total_entries': current_stats['total_entries'],
                'total_volume': round(current_stats['total_volume'], 2),
                'avg_volume': round(current_stats['avg_volume'], 2),
                'median_volume': round(current_stats['median_volume'], 2),
                'min_volume': round(current_stats['min_volume'], 2),
                'max_volume': round(current_stats['max_volume'], 2)
            },
            'rank_thresholds': {
                'top_10': round(thresholds.get('rank_10', 0), 2),
                'top_50': round(thresholds.get('rank_50', 0), 2),
                'top_100': round(thresholds.get('rank_100', 0), 2),
                'top_250': round(thresholds.get('rank_250', 0), 2),
                'top_500': round(thresholds.get('rank_500', 0), 2),
                'top_1000': round(thresholds.get('rank_1000', 0), 2)
            },
            'analysis': {
                'difficulty_score': comparison.get('difficulty_score', 0),
                'total_volume_change': comparison.get('total_volume_change', 0),
                'avg_volume_change': comparison.get('avg_volume_change', 0),
                'comparison': comparison.get('comparison', 'N/A'),
                'recommendation': comparison.get('recommendation', 'N/A')
            },
            'historical_snapshots': snapshot_count
        }

        return output

    except Exception as e:
        return {
            'status': 'error',
            'message': f'Unexpected error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }
    finally:
        # Always restore stdout
        sys.stdout = original_stdout
        if devnull:
            devnull.close()


if __name__ == '__main__':
    result = main()
    print(json.dumps(result, indent=2))
    
    # Exit with error code if failed
    if result['status'] == 'error':
        sys.exit(1)
    
    sys.exit(0)

