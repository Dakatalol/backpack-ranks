# Backpack Exchange Volume Tracker

A Python tool to track and analyze Backpack exchange leaderboard volume data with automated Telegram reporting via n8n.

## Features

- **Data Collection**: Automatically fetch and store leaderboard data from Backpack API
- **Historical Tracking**: SQLite database stores all snapshots for trend analysis
- **Statistical Analysis**: Calculate averages, medians, percentiles, and rank thresholds
- **Difficulty Scoring**: Get a difficulty score comparing current vs historical volume
- **Smart Recommendations**: Receive actionable advice on whether it's a good time to farm
- **n8n Automation**: Automated Telegram reports twice daily (8 AM & 8 PM) with volume analysis

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Collect Initial Data

```bash
python main.py collect
```

Run this 2-3 times over a few days to build historical baseline.

### 3. Analyze Current Conditions

```bash
python main.py analyze
```

---

## CLI Usage

### Collect Data
```bash
python main.py collect [--max-entries N]
```
Fetches current leaderboard and stores in database.

### Analyze Conditions
```bash
python main.py analyze [--max-entries N]
```
Compares current volume against historical average and provides farming recommendation.

### View History
```bash
python main.py history
```
Shows all stored snapshots with basic stats.

### Inspect Snapshot
```bash
python main.py inspect <snapshot_id>
```
View detailed information about a specific snapshot.

---

## Automated Telegram Reports (n8n Integration)

Get automated volume reports sent to your Telegram twice daily at 8 AM and 8 PM!

### Prerequisites

- **Node.js** v18+ (for n8n)
- **Telegram account**
- **Windows** (guide is Windows-specific, but adaptable to Linux/Mac)

### Setup Guide

#### Step 1: Install n8n

```bash
npm install n8n -g
```

Verify installation:
```bash
n8n --version
```

---

#### Step 2: Create Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` and follow the prompts
3. Choose a name (e.g., "Backpack Volume Tracker")
4. Choose a username ending in 'bot' (e.g., "backpack_volume_bot")
5. **Save the bot token** - you'll need this later

Example token: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

---

#### Step 3: Get Your Chat ID

1. Search for **@userinfobot** in Telegram
2. Start a chat with it
3. It will reply with your user information
4. **Save your Chat ID** (the number shown as "Id")

Example: `987654321`

---

#### Step 4: Start n8n

```bash
n8n start
```

n8n will open at `http://localhost:5678`

---

#### Step 5: Import Workflow

1. In n8n, click **"Workflows"** → **"Import from File"**
2. Select `n8n_workflow.json` from this project
3. The workflow will be imported with all nodes

---

#### Step 6: Set Project Path

1. Click on the **"Execute Python Script"** node
2. Update the command with your actual project path:
   - **Windows**: `cd C:\Users\YourUsername\path\to\backpack-ranks && python n8n_wrapper.py`
   - **Linux/Mac**: `cd /home/username/path/to/backpack-ranks && python n8n_wrapper.py`
3. Click **"Save"**

**Tip:** To find your path:
- Windows: Open project folder in Explorer, copy path from address bar
- Linux/Mac: Run `pwd` in the project directory

---

#### Step 7: Configure Telegram Credentials

1. Click on any **"Send to Telegram"** node
2. Under **"Credentials"**, click **"Create New"**
3. Enter:
   - **Credential Name**: `Backpack Telegram Bot`
   - **Access Token**: Your bot token from @BotFather
4. Click **"Save"**

---

#### Step 8: Set Your Chat ID

You need to set your chat ID in TWO nodes:

1. Click on **"Set Chat ID"** node
2. Replace `YOUR_CHAT_ID_HERE` with your actual chat ID:
   ```javascript
   return {
     json: {
       ...items[0].json,
       chatId: '1290944468'  // Your actual chat ID here
     }
   };
   ```
3. Click on **"Set Chat ID (Error)"** node
4. Do the same replacement

---

#### Step 9: Start Your Bot

**Important:** Before testing, you must start a conversation with your bot:

1. Open Telegram
2. Search for your bot (the username you created)
3. Click on it to open the chat
4. Send `/start` (or click the "Start" button)

---

#### Step 10: Test the Workflow

1. In n8n, click **"Execute Workflow"** button (top right)
2. Wait 5-10 seconds
3. Check your Telegram - you should receive a formatted report! 📱

---

#### Step 11: Activate Automation

1. Toggle the switch at the top right to **"Active"**
2. Keep n8n running
3. You'll now receive reports automatically at 8 AM and 8 PM!

---

### Running n8n Continuously

To keep n8n running so it can send scheduled reports:

**Option 1: Keep terminal open**
```bash
n8n start
```
Keep this terminal window open.

**Option 2: Run in background (Linux/Mac)**
```bash
nohup n8n start &
```

**Option 3: Windows Task Scheduler**
1. Open Task Scheduler
2. Create Basic Task
3. Name: `n8n Backpack Tracker`
4. Trigger: **"When I log on"**
5. Action: **"Start a program"**
   - Program: `cmd.exe`
   - Arguments: `/c n8n start`

---

### What You'll Receive

Each Telegram report includes:

```
📊 Backpack Volume Tracker Report
━━━━━━━━━━━━━━━━━━━━

📈 Current Volume Statistics
Week: 2025-W41
Total Volume: $19.24M
Average Volume: $19.24K
Median Volume: $7.47K
Traders Tracked: 1000

🏆 Rank Thresholds (Volume Needed)
Top 10: $186.25K
Top 50: $74.68K
Top 100: $47.90K
Top 250: $17.24K
Top 500: $7.47K
Top 1000: $2.74K

📊 Historical Comparison
Total Volume Change: -1.71%
Avg Volume Change: -1.71%
Historical Snapshots: 6

🟠 Difficulty Score: 98.3
AVERAGE CONDITIONS

💡 Recommendation
AVERAGE CONDITIONS - Volume is near historical average

━━━━━━━━━━━━━━━━━━━━
🕐 10/12/2025, 9:00:00 PM
Snapshot ID: 6
```

---

### Difficulty Score Guide

- 🟢 **< 80**: GOOD TIME TO FARM - Volume significantly below average
- 🟡 **80-95**: DECENT TIME TO FARM - Volume below average  
- 🟠 **95-105**: AVERAGE CONDITIONS - Volume near historical average
- 🔴 **105-120**: HARDER THAN USUAL - Volume above average
- ⛔ **> 120**: VERY HARD TO FARM - Volume significantly above average

---

## Troubleshooting

### Telegram: "Chat not found"

**Solution:** Send `/start` to your bot in Telegram first, then test again.

### Telegram: No message received

**Check:**
1. Bot token is correct in n8n credentials
2. Chat ID is correct (numeric, no quotes)
3. You've sent `/start` to your bot
4. Workflow is "Active" in n8n
5. n8n is running

**Test manually:** Click "Execute Workflow" in n8n to test immediately.

### Python: "Module not found"

**Solution:**
```bash
pip install -r requirements.txt
```

### n8n: "Format Telegram Message" node error

**Cause:** Python script outputs progress messages before JSON.

**Solution:** The `n8n_wrapper.py` script already suppresses these messages. If you still see this error, make sure you're using the latest version of `n8n_wrapper.py` from this repository.

### Schedule not triggering

**Check:**
1. Workflow is **Active** (green toggle)
2. n8n is running
3. Computer is on at scheduled times
4. Check n8n "Executions" tab for history

---

## Understanding the Metrics

### Difficulty Score
- Based on total and average volume compared to historical baseline
- Lower score = easier to farm (less competition)
- Higher score = harder to farm (more competition)

### Rank Thresholds
- Shows exact volume needed to achieve specific ranks
- Use this to set realistic farming goals
- Updated twice daily with current data

### Volume Change %
- Positive % = higher than average (harder to farm)
- Negative % = lower than average (easier to farm)

---

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
├── n8n_wrapper.py          # n8n integration script
├── n8n_workflow.json       # n8n workflow (import this)
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

---

## API Information

Uses Backpack Exchange public API:
- **Endpoint**: `https://api.backpack.exchange/wapi/v1/statistics/leaderboard/volume/week`
- **Authentication**: None required
- **Rate limits**: Unknown (use responsibly)

---

## Tips

1. **Build history first**: Collect data 2-3 times before activating automation for better analysis
2. **Monitor first week**: Check that reports arrive as expected at 8 AM and 8 PM
3. **Watch difficulty score**: Act when 🟢 (< 80) appears
4. **Use rank thresholds**: Plan volume goals based on desired rank
5. **Keep n8n running**: Ensure n8n is always running for scheduled reports

---

## Quick Reference

### Start n8n
```bash
n8n start
```

### Test Python Script
```bash
python n8n_wrapper.py
```

### Collect Data Manually
```bash
python main.py collect
```

### View Historical Data
```bash
python main.py history
```

### Check Analysis
```bash
python main.py analyze
```

---

## License

This is a personal utility tool. Use at your own discretion.

## Disclaimer

This tool is for informational purposes only. Volume farming decisions should be made based on multiple factors, not just this tool's recommendations.

---

## Support

For issues:
- **Python/CLI**: Check error messages and ensure dependencies are installed
- **n8n**: Check the Executions tab in n8n for detailed logs
- **Telegram**: Ensure bot token and chat ID are correct, and you've started the bot
- **API**: Verify Backpack API is accessible: https://api.backpack.exchange/wapi/v1/statistics/leaderboard/volume/week

Happy farming! 🚀
