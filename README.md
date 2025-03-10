# Discord Server Manager CLI

A powerful command-line interface tool for managing Discord servers. Developed by Sk Bindas.

© 2025 Sk Bindas. All rights reserved.

## Features

- View all joined Discord servers
- Leave multiple servers at once using Server ID (recommended method)
- Auto-refresh server list
- Rate limit handling
- Progress tracking for server operations

## Important Notice for Users (Zaruri Soochna)

🔴 **Server Leave Karne ke Liye Best Method**:
- Server ID method (Option 2) ka use karein, yeh 100% reliable hai
- Select Servers option (Option 1) mein kuch technical issues hain, isliye avoid karein
- Server ID aap server list se copy kar sakte hain

### Server ID Kaise Prapt Karein?
1. Bot ko run karein (`python bot.py`)
2. Main menu mein Option 1 (Select Servers) chunein
3. Server list display hogi, jisme har server ke liye:
   - Server ka naam
   - Server ID (green color mein)
4. Aap in Server IDs ko copy karke Option 2 mein use kar sakte hain

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

## Configuration (Discord Token Kaise Prapt Karein)

1. Create a `.env` file in the project directory
2. Discord token prapt karne ke liye:
   a. Discord web ya app mein login karein
   b. Browser ke Developer Tools ko kholein (F12 ya Ctrl+Shift+I)
   c. Network tab par click karein
   d. Kisi bhi Discord channel ya message par click karein
   e. Network tab mein requests dikhenge
   f. Kisi bhi Discord request par click karein
   g. Headers section mein scroll karke 'Authentication' dhoondhein
   h. Wahan jo token dikhega, wahi aapka Discord token hai
3. Token ko `.env` file mein add karein:
   ```
   DISCORD_TOKEN=your_token_here
   ```

⚠️ **IMPORTANT SECURITY WARNING**
- Token leak hone par aapka Discord account hack ho sakta hai
- Token ko KABHI bhi public ya share na karein
- Agar galti se token leak ho jaye, turant Discord password change karein

## Usage Guide (Upyog Kaise Karein)

1. Run the bot:
   ```
   python bot.py
   ```
2. Main Menu se Option 2 (Leave Server by ID) chunein
3. Server ID comma se separate karke daalen (e.g., 123456789,987654321)
4. Confirmation ke baad servers leave ho jayenge

## Security Note (Suraksha Sujhav)

- Apna Discord token kabhi kisi ke saath share na karein
- Token ko secure aur private rakhein
- Kisi bhi suspicious activity ke liye token immediately reset karein

## Support

For support and updates, connect with me:
- GitHub: [Skbindas](https://github.com/Skbindas)
- Telegram: [AirdropGuru47](https://t.me/AirdropGuru47)