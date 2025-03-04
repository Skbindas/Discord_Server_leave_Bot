# Discord Server Manager CLI

A powerful command-line interface tool for managing Discord servers. Developed by Sk Bindas.

© 2025 Sk Bindas. All rights reserved.

## Features

- View all joined Discord servers
- Select and leave multiple servers at once
- Auto-refresh server list
- Rate limit handling
- Progress tracking for server operations

## Requirements

- Python 3.6+
- Required packages (install via pip):
  - requests
  - python-dotenv
  - rich

## Installation

1. Clone this repository
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Configuration

1. Create a `.env` file in the project directory
2. Add your Discord token:
   ```
   DISCORD_TOKEN=
   ```

## Usage

1. Run the bot:
   ```
   python bot.py
   ```
2. Use the interactive menu to manage your Discord servers

## Security Note

Never share your Discord token with anyone. Keep it secure and private.