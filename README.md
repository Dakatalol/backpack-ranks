# Backpack Exchange Volume Tracker

A Python tool to track and analyze Backpack exchange leaderboard volume data, helping you identify optimal periods for volume farming.

## Overview

This tool helps you make informed decisions about when to farm volume on Backpack exchange by:
- Collecting historical leaderboard data
- Analyzing volume trends over time
- Comparing current conditions against historical averages
- Providing recommendations on farming difficulty

## Features

- **Data Collection**: Automatically fetch and store leaderboard data from Backpack API
- **Historical Tracking**: SQLite database stores all snapshots for trend analysis
- **Statistical Analysis**: Calculate averages, medians, percentiles, and rank thresholds
- **Difficulty Scoring**: Get a difficulty score comparing current vs historical volume
- **Smart Recommendations**: Receive actionable advice on whether it's a good time to farm

## Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify installation**:
   ```bash
   python main.py --help
   ```

## Usage

### 1. Collect Data

Collect current leaderboard data and store it in the database:

```bash
python main.py collect
```

**Options**:
- `--max-entries N`: Number of entries to collect (default: 1000)

**Example**:
```bash
python main.py collect --max-entries 2000
```

**What it does**:
- Fetches leaderboard data from Backpack API
- Displays current week statistics
- Stores snapshot in local database

### 2. Analyze Current Conditions

Compare current leaderboard against historical data to get farming recommendations:

```bash
python main.py analyze
```

**Options**:
- `--max-entries N`: Number of entries to analyze (default: 1000)

**What it shows**:
- Current week statistics
- Rank thresholds (volume needed for top 10, 50, 100, etc.)
- Comparison with historical averages
- Difficulty score (0-100+)
- Farming recommendation

**Difficulty Score Guide**:
- **< 80**: GOOD TIME TO FARM - Volume significantly below average
- **80-95**: DECENT TIME TO FARM - Volume below average
- **95-105**: AVERAGE CONDITIONS - Volume near historical average
- **105-120**: HARDER THAN USUAL - Volume above average
- **> 120**: VERY HARD TO FARM - Volume significantly above average

### 3. View Historical Data

View all stored snapshots:

```bash
python main.py history
```

**What it shows**:
- List of all snapshots with timestamps
- Week identifier
- Entry count, total volume, and average volume for each snapshot

### 4. Inspect Specific Snapshot

View detailed information about a specific snapshot:

```bash
python main.py inspect <snapshot_id>
```

**Example**:
```bash
python main.py inspect 5
```

**What it shows**:
- Full statistics for that snapshot
- Rank thresholds at that time

## Workflow Example

### First Time Setup

1. **Collect initial data**:
   ```bash
   python main.py collect
   ```

2. **Wait a few days/weeks and collect more data**:
   ```bash
   python main.py collect
   ```

3. **Repeat step 2 regularly** (e.g., daily or every few days)

### Regular Usage

Once you have historical data (3+ snapshots recommended):

1. **Check current conditions**:
   ```bash
   python main.py analyze
   ```

2. **Review the recommendation** and decide whether to farm

3. **View trends**:
   ```bash
   python main.py history
   ```

## Understanding the Output

### Statistics Explained

- **Total Volume**: Sum of all user volumes in the snapshot
- **Average Volume**: Mean volume per user
- **Median Volume**: Middle value when all volumes are sorted
- **Percentiles**:
  - 25th: 25% of users have less volume
  - 50th: Same as median
  - 75th: 75% of users have less volume

### Rank Thresholds

Shows the minimum volume required to achieve specific ranks:
- Top 10, 50, 100, 250, 500, 1000

Use this to set volume goals based on your target rank.

### Comparison Metrics

- **Total Volume Change**: % change in total leaderboard volume vs historical average
- **Avg Volume Change**: % change in per-user volume vs historical average
- **Difficulty Score**: Combined metric (higher = harder to rank)

## Tips

1. **Collect data regularly**: The more historical data you have, the better the analysis
2. **Collect during different times**: Capture both high and low activity periods
3. **Use analyze before farming**: Check conditions before starting your farming session
4. **Monitor rank thresholds**: Track how much volume you need for your target rank
5. **Consider the trend**: Look at history to see if volume is increasing or decreasing over time

## Project Structure

```
backpack-ranks/
├── data/
│   └── backpack.db          # SQLite database (auto-created)
├── src/
│   ├── collector.py         # API fetching logic
│   ├── database.py          # Database operations
│   ├── analyzer.py          # Statistical analysis
│   └── utils.py             # Formatting utilities
├── main.py                  # CLI entry point
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## API Information

This tool uses the Backpack Exchange public API:
- Endpoint: `https://api.backpack.exchange/wapi/v1/statistics/leaderboard/volume/week`
- No authentication required
- Rate limits: Unknown (use responsibly)

## Troubleshooting

### "No historical data available"
- Run `python main.py collect` to create your first snapshot

### "Failed to collect data from API"
- Check your internet connection
- Verify the API endpoint is still valid
- Check if Backpack API is experiencing issues

### Database errors
- Ensure the `data/` directory exists and is writable
- Check that `backpack.db` is not corrupted

## Future Enhancements

Potential features to add:
- Automated scheduling (cron/Task Scheduler integration)
- Email/notification alerts when conditions are favorable
- Web dashboard for visualization
- Export data to CSV/JSON
- Multi-week trend charts

## License

This is a personal utility tool. Use at your own discretion.

## Disclaimer

This tool is for informational purposes only. Volume farming decisions should be made based on multiple factors, not just this tool's recommendations.
