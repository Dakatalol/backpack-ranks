#!/usr/bin/env python3
"""
Backpack Exchange Volume Tracker
Track and analyze Backpack exchange leaderboard volume to identify optimal farming periods
"""

import sys
import argparse
from src.database import Database
from src.collector import BackpackCollector
from src.analyzer import BackpackAnalyzer
from src.utils import (
    print_section_header,
    print_stats_table,
    print_comparison_table,
    print_rank_thresholds,
    print_history_table,
    print_success_message,
    print_error_message
)

def cmd_collect(args):
    """Collect current leaderboard data and store in database"""
    db = Database()
    collector = BackpackCollector()

    print_section_header("COLLECTING LEADERBOARD DATA")

    # Fetch data
    result = collector.collect_and_summarize(max_entries=args.max_entries)

    if not result['success']:
        print_error_message("Failed to collect data from API")
        return 1

    entries = result['entries']
    stats = result['stats']

    # Display current stats
    print("\nCurrent Week Statistics:")
    print_stats_table(stats)

    # Store in database
    print(f"\nStoring data in database (week: {stats['week_identifier']})...")
    snapshot_id = db.create_snapshot(stats['week_identifier'])
    db.insert_leaderboard_entries(snapshot_id, entries)

    print_success_message(f"Successfully stored {len(entries)} entries (Snapshot ID: {snapshot_id})")

    return 0

def cmd_analyze(args):
    """Analyze current data against historical trends"""
    db = Database()
    collector = BackpackCollector()
    analyzer = BackpackAnalyzer(db)

    print_section_header("ANALYZING CURRENT CONDITIONS")

    # Check if we have historical data
    snapshot_count = db.get_snapshot_count()

    if snapshot_count == 0:
        print_error_message("No historical data available. Run 'collect' first.")
        return 1

    # Fetch current data
    print("\nFetching current leaderboard data...")
    result = collector.collect_and_summarize(max_entries=args.max_entries)

    if not result['success']:
        print_error_message("Failed to collect data from API")
        return 1

    current_stats = result['stats']
    entries = result['entries']

    # Display current stats
    print_section_header("CURRENT WEEK STATISTICS")
    print_stats_table(current_stats)

    # Show rank thresholds
    thresholds = analyzer.get_rank_thresholds(entries)
    if thresholds:
        print()
        print_rank_thresholds(thresholds)

    # Compare with history
    if snapshot_count > 0:
        comparison = analyzer.compare_with_history(current_stats)
        print()
        print_comparison_table(comparison)

    return 0

def cmd_history(args):
    """View historical snapshot data"""
    db = Database()

    print_section_header("HISTORICAL SNAPSHOTS")

    snapshots = db.get_all_snapshots()

    if not snapshots:
        print("\nNo historical data available yet.")
        print("Run 'python main.py collect' to start collecting data.\n")
        return 0

    print(f"\nTotal snapshots: {len(snapshots)}\n")
    print_history_table(snapshots)
    print()

    return 0

def cmd_inspect(args):
    """Inspect a specific snapshot"""
    db = Database()
    analyzer = BackpackAnalyzer(db)

    snapshot_id = args.snapshot_id

    print_section_header(f"SNAPSHOT #{snapshot_id} DETAILS")

    analysis = analyzer.analyze_snapshot(snapshot_id)

    if not analysis:
        print_error_message(f"Snapshot #{snapshot_id} not found")
        return 1

    print("\nStatistics:")
    print_stats_table(analysis['stats'])

    if analysis['rank_thresholds']:
        print()
        print_rank_thresholds(analysis['rank_thresholds'])

    print()
    return 0

def main():
    parser = argparse.ArgumentParser(
        description="Backpack Exchange Volume Tracker - Track and analyze farming conditions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py collect                  # Collect current data
  python main.py analyze                  # Analyze current vs historical
  python main.py history                  # View all snapshots
  python main.py inspect 5                # Inspect snapshot #5
  python main.py collect --max-entries 2000  # Collect up to 2000 entries
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Collect command
    parser_collect = subparsers.add_parser('collect', help='Collect current leaderboard data')
    parser_collect.add_argument(
        '--max-entries',
        type=int,
        default=1000,
        help='Maximum number of entries to collect (default: 1000)'
    )

    # Analyze command
    parser_analyze = subparsers.add_parser('analyze', help='Analyze current conditions vs history')
    parser_analyze.add_argument(
        '--max-entries',
        type=int,
        default=1000,
        help='Maximum number of entries to analyze (default: 1000)'
    )

    # History command
    subparsers.add_parser('history', help='View historical snapshots')

    # Inspect command
    parser_inspect = subparsers.add_parser('inspect', help='Inspect a specific snapshot')
    parser_inspect.add_argument('snapshot_id', type=int, help='Snapshot ID to inspect')

    # Parse arguments
    args = parser.parse_args()

    # Execute command
    if args.command == 'collect':
        return cmd_collect(args)
    elif args.command == 'analyze':
        return cmd_analyze(args)
    elif args.command == 'history':
        return cmd_history(args)
    elif args.command == 'inspect':
        return cmd_inspect(args)
    else:
        parser.print_help()
        return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error_message(f"Unexpected error: {e}")
        sys.exit(1)
