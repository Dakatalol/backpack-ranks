from typing import Dict, List
from tabulate import tabulate
from datetime import datetime

def format_number(num: float, decimals: int = 2) -> str:
    """Format number with thousands separator"""
    return f"{num:,.{decimals}f}"

def format_volume(volume: float) -> str:
    """Format volume in a readable way"""
    if volume >= 1_000_000:
        return f"${volume / 1_000_000:.2f}M"
    elif volume >= 1_000:
        return f"${volume / 1_000:.2f}K"
    else:
        return f"${volume:.2f}"

def format_percentage(value: float) -> str:
    """Format percentage with + or - sign"""
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}%"

def print_section_header(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_stats_table(stats: Dict):
    """Print statistics in a formatted table"""
    data = [
        ["Total Entries", format_number(stats['total_entries'], 0)],
        ["Total Volume", format_volume(stats['total_volume'])],
        ["Average Volume", format_volume(stats['avg_volume'])],
        ["Median Volume", format_volume(stats['median_volume'])],
        ["Min Volume", format_volume(stats['min_volume'])],
        ["Max Volume", format_volume(stats['max_volume'])],
    ]

    # Add percentiles if available
    if 'percentile_25' in stats:
        data.extend([
            ["25th Percentile", format_volume(stats['percentile_25'])],
            ["50th Percentile", format_volume(stats['percentile_50'])],
            ["75th Percentile", format_volume(stats['percentile_75'])],
        ])

    print(tabulate(data, headers=["Metric", "Value"], tablefmt="simple"))

def print_comparison_table(comparison: Dict):
    """Print comparison analysis in a formatted table"""
    print_section_header("COMPARISON WITH HISTORICAL DATA")

    # Check if we have enough historical data for comparison
    if 'historical' not in comparison:
        print(f"\n{comparison['recommendation']}\n")
        return

    # Historical averages
    print("\nHistorical Averages:")
    historical = comparison['historical']
    hist_data = [
        ["Snapshots Analyzed", format_number(historical['snapshot_count'], 0)],
        ["Avg Total Volume", format_volume(historical['avg_total_volume'])],
        ["Avg User Volume", format_volume(historical['avg_avg_volume'])],
    ]
    print(tabulate(hist_data, headers=["Metric", "Value"], tablefmt="simple"))

    # Current vs Historical
    print("\nCurrent vs Historical:")
    comp_data = [
        ["Total Volume Change", format_percentage(comparison['total_volume_change'])],
        ["Avg Volume Change", format_percentage(comparison['avg_volume_change'])],
        ["Difficulty Score", f"{comparison['difficulty_score']}/100"],
    ]
    print(tabulate(comp_data, headers=["Metric", "Value"], tablefmt="simple"))

    # Recommendation
    print_section_header("RECOMMENDATION")
    print(f"\n{comparison['recommendation']}\n")

def print_rank_thresholds(thresholds: Dict):
    """Print rank thresholds in a formatted table"""
    print_section_header("RANK THRESHOLDS")

    data = []
    for rank_key, volume in sorted(thresholds.items()):
        rank = rank_key.replace('rank_', '')
        data.append([f"Top {rank}", format_volume(volume)])

    print(tabulate(data, headers=["Rank", "Min Volume Required"], tablefmt="simple"))

def print_history_table(snapshots: List[Dict]):
    """Print historical snapshots in a formatted table"""
    if not snapshots:
        print("No historical data available")
        return

    data = []
    for snapshot in snapshots:
        timestamp = datetime.fromisoformat(snapshot['timestamp'])
        formatted_time = timestamp.strftime("%Y-%m-%d %H:%M")

        data.append([
            snapshot['id'],
            snapshot['week_identifier'],
            formatted_time,
            format_number(snapshot['entry_count'], 0),
            format_volume(snapshot['total_volume']),
            format_volume(snapshot['avg_volume']),
        ])

    print(tabulate(
        data,
        headers=["ID", "Week", "Timestamp", "Entries", "Total Volume", "Avg Volume"],
        tablefmt="simple"
    ))

def print_success_message(message: str):
    """Print a success message"""
    print(f"\n✓ {message}\n")

def print_error_message(message: str):
    """Print an error message"""
    print(f"\n✗ Error: {message}\n")
