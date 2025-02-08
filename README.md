# Skyblock Role Bot

## Overview
Skyblock Role Bot is a Discord bot that assigns roles to users based on their Skyblock level in Hypixel Skyblock. Users can register their Minecraft name using the `/form` command, and when the `/update` command is run, the bot updates roles accordingly.

## Features
- `/form`: Users submit their Minecraft username to be tracked.
- `/update`: The bot fetches the latest Skyblock level for all registered users and assigns roles based on that.
- Automatic role assignment based on Hypixel Skyblock levels.

## Usage
- Users type `/form ` to link their Discord account to their Minecraft account.
- An administrator runs `/update` to fetch data and assign roles.
- The bot assigns roles based on configured Skyblock level thresholds.

## Requirements
- Python 3.8+
- `discord.py`
- `requests`
- `asyncio`
- A Hypixel API key
- A Discord Bot Key

## Future Enhancements
- I dont know figure it out yourself
## Contributors
@SuperbMuffin - Initial development

