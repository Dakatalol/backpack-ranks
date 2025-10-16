# Backpack Exchange Volume Tracker

Track rank 1000 volume on Backpack Exchange to identify optimal volume farming periods. Get automated alerts when competition is low.

## Features

- **Rank 1000 Tracking**: Monitor the minimum volume needed to stay in top 1000
- **Historical Comparison**: Compare current vs historical rank 1000 volume
- **Smart Alerts**: Get notified only when conditions are favorable for farming
- **n8n Automation**: Automated Telegram alerts twice daily (8 AM & 8 PM)
- **CLI Tools**: Detailed analysis tools for manual checking

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Test the Rank 1000 Tracker

```bash
python n8n_tracker.py
```

This tracks rank 1000's volume (the minimum to stay in top 1000). Run it 2-3 times over a few days to build historical baseline.

**Sample output:**
```json
{
  "current": {
    "rank_1000_volume": 2272851.78,
    "user_at_rank_1000": "circuitously-wise-char"
  },
  "analysis": {
    "difficulty_score": 90.91,
    "volume_change_percent": -9.09,
    "recommendation": "✅ GOOD TIME TO FARM"
  }
}
```

### 3. Optional: Full CLI for Detailed Analysis

If you want detailed statistics beyond rank 1000:

```bash
python main.py collect  # Collect all 1000 entries
python main.py analyze  # Detailed statistical analysis
```

---

## What This Tool Does

Tracks rank 1000's volume to tell you if it's a good time to farm:

- ⚡ **Fast**: Tracks only rank 1000 volume
- 🎯 **Focused**: Directly tells you the minimum volume needed for top 1000
- 📊 **Clean Output**: JSON output perfect for n8n
- 💾 **Efficient**: Minimal database storage

**What it tracks:**
- Current rank 1000 volume
- Historical average of rank 1000 volume
- Difficulty score based on rank 1000 comparison
- Recommendation: Is it a good time to farm?

**Difficulty Score:**
- `< 80` = 🎯 EXCELLENT TIME (20%+ easier than average)
- `80-95` = ✅ GOOD TIME (easier than average)
- `95-105` = ➖ AVERAGE CONDITIONS
- `105-120` = ⚠️ HARDER THAN USUAL
- `> 120` = 🔴 VERY HARD (20%+ harder)

### Optional CLI Tools

For detailed analysis when needed:

```bash
python main.py collect            # Collect all 1000 entries
python main.py analyze            # Full statistical analysis
python main.py history            # View all snapshots
python main.py inspect <id>       # Inspect specific snapshot
```

---

## n8n Automation (Telegram Alerts)

Get automated alerts when it's a good time to farm! The workflow runs twice daily (8 AM & 8 PM) and only notifies you when conditions are favorable.

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
2. Set the working directory to your project path
3. The command should already be: `python n8n_tracker.py`
4. Click **"Save"**

**To find your project path:**
- **Windows**: Open project folder in Explorer, copy path from address bar
- **Linux/Mac**: Run `pwd` in the project directory

---

#### Step 7: Configure Telegram

1. Click on the **"Send Telegram Message"** node
2. In the **"Chat ID"** field, replace `YOUR_TELEGRAM_CHAT_ID` with your actual chat ID (the number from @userinfobot)
3. Under **"Credential to connect with"**, click the dropdown
4. Click **"Create New Credential"**
5. Enter your **bot token** from @BotFather (the long string like `123456789:ABCdefGHIjklMNOpqr...`)
6. Click **"Save"**

---

#### Step 8: Start Your Bot

**Important:** Before testing, you must start a conversation with your bot:

1. Open Telegram
2. Search for your bot (the username you created)
3. Click on it to open the chat
4. Send `/start` (or click the "Start" button)

---

#### Step 9: Test the Workflow

1. In n8n, click **"Execute Workflow"** button (top right)
2. Wait 5-10 seconds
3. Check your Telegram for a message! 📱

**Note:** You'll get a message every time the workflow runs. The message will show the current rank 1000 volume and difficulty score.

---

#### Step 10: Activate Automation

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

You'll get alerts twice daily (8 AM & 8 PM) with the current rank 1000 status:

**Example message:**
```
✅ Backpack Volume Alert

GOOD TIME TO FARM - Rank 1000 volume is below average

📊 Current Rank 1000: $2.27M
👤 User: circuitously-wise-char
📈 Difficulty Score: 90.91/100
📉 Change: -9.09%

You need more than $2.27M in trading volume to be in the top 1000.
```

**Emoji indicators:**
- 🎯 = Score < 80 (Excellent time)
- ✅ = Score < 95 (Good time)
- ➖ = Score 95-105 (Average)
- ⚠️ = Score 105-120 (Harder)
- 🔴 = Score > 120 (Very hard)

---

### Difficulty Score Guide

The difficulty score shows how hard it is to farm compared to historical average:

- 🎯 **< 80**: EXCELLENT TIME - 20%+ easier than average
- ✅ **80-95**: GOOD TIME - Easier than average  
- ➖ **95-105**: AVERAGE CONDITIONS - Normal competition
- ⚠️ **105-120**: HARDER THAN USUAL - Above average competition
- 🔴 **> 120**: VERY HARD - 20%+ harder than average

**Lower score = less competition = better time to farm**

---

## Troubleshooting

### Telegram: "Chat not found"

**Solution:** Send `/start` to your bot in Telegram first, then test again.

### Telegram: No message received

**Check:**
1. Bot token is correct in n8n credentials
2. Chat ID is correct (should be just the number in the Telegram node)
3. You've sent `/start` to your bot
4. Workflow is "Active" in n8n
5. n8n is running

You'll get a message every time regardless of score. If you want to test immediately:
- Click "Execute Workflow" in n8n
- Or run `python n8n_tracker.py` directly to see the JSON output

### Python: "Module not found"

**Solution:**
```bash
pip install -r requirements.txt
```

### n8n: Not receiving messages

**Check:**
1. Bot credentials are configured correctly (bot token from @BotFather)
2. Chat ID is correct (numeric ID from @userinfobot)
3. You've sent `/start` to your bot in Telegram
4. Workflow is "Active" in n8n
5. n8n is running

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
│   └── backpack.db           # SQLite database
├── src/
│   ├── collector.py          # API fetching logic (used by main.py)
│   ├── database.py           # Database operations (used by main.py)
│   ├── analyzer.py           # Statistical analysis (used by main.py)
│   └── utils.py              # Formatting utilities (used by main.py)
├── main.py                   # CLI entry point (optional detailed analysis)
├── n8n_tracker.py            # Rank 1000 tracker (main script) ⭐
├── n8n_workflow.json         # n8n workflow file ⭐
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## API Information

Uses Backpack Exchange public API:
- **Endpoint**: `https://api.backpack.exchange/wapi/v1/statistics/leaderboard/volume/week`
- **Authentication**: None required
- **Rate limits**: Unknown (use responsibly)

---

## Tips & Best Practices

1. **Build history first**: Run `python n8n_tracker.py` 2-3 times over a few days before activating n8n
2. **Regular updates**: You'll get updates twice daily (8 AM & 8 PM) automatically
3. **Use CLI for deep dives**: Run `python main.py analyze` when you want detailed statistics
4. **Keep n8n running**: Ensure n8n is always running for scheduled alerts
5. **Monitor difficulty score**: Act when 🎯 (< 80) or ✅ (< 95) appears
6. **Understand the metric**: Rank 1000 volume tells you exactly how much you need to trade

---

## Quick Reference

### Main Command
```bash
python n8n_tracker.py             # Check rank 1000 volume + get recommendation
```

### Optional CLI Tools (for detailed analysis)
```bash
python main.py collect            # Collect all 1000 entries
python main.py analyze            # Detailed statistical analysis
python main.py history            # View all snapshots
python main.py inspect <id>       # Inspect specific snapshot
```

### n8n
```bash
n8n start                         # Start n8n server (keep running)
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
