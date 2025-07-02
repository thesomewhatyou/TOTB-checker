
# Dandy's World Twisted Oracle Bot 🔮

Ever missed out on knowing the Daily Twisted character in Dandy's World? This friendly Discord bot is here to help! It keeps an eye on the [Dandy's World Wiki's Daily Twisted Board](https://dandys-world-robloxhorror.fandom.com/wiki/Daily_Twisted_Board) and automatically tells your Discord server when the character changes. It even shows you a picture of the character!

## ✨ Cool Features

- **Always Watching**: Checks the Twisted Board every hour, right on time.
- **Smart Alerts**: Only pings you when the character actually changes or when the board's timer resets. No spam!
- **Picture Perfect**: Grabs character images straight from the wiki to show you who's Twisted.
- **Timed Just Right**: Has a special delay for the midnight UTC (often 8 PM EST) update to make sure it gets the freshest info.
- **Ping Who You Want**: You can set it up to ping a specific role or even individual friends when there's news.
- **Keeps on Chugging**: If something goes a bit wrong (like the wiki being down), it tries its best to recover and keeps a log of what happened.

## 🌐 Check Out Our Website!

Want a prettier way to see what this bot is all about? Head over to our GitHub Pages site:

**[https://thesomewhatyou.github.io/TOTB-checker/](https://thesomewhatyou.github.io/TOTB-checker/)**

It's got all this info, but with a nicer layout!

## 🚀 Getting Started (Easy Mode!)

Want to run this bot yourself? Here’s how!

### What You'll Need:

1.  **A Computer**: This bot runs using Python, a common programming language. Most computers can run Python. If you don't have it, you can get it from [python.org](https://www.python.org/downloads/). You'll want version 3.8 or newer.
2.  **A Discord Bot Token**: This is like a password for your bot. You get it from Discord. (More on this below!)
3.  **A Discord Channel ID**: This tells the bot which channel in your server to send messages to.

*(Optional: You can also tell it a Role ID to ping or specific User IDs if you want to notify certain people.)*

### Setting it Up:

1.  **Get the Bot's Files:**
    *   **Easy way:** Go to the [GitHub page for this bot](https://github.com/thesomewhatyou/TOTB-checker) (Hint: you might be there right now!). Click the green "Code" button, then "Download ZIP". Unzip this file somewhere on your computer.
    *   **Slightly fancier way (if you know Git):**
        ```bash
        git clone https://github.com/thesomewhatyou/TOTB-checker.git
        cd TOTB-checker
        ```
        *(This `TOTB-checker` name might be `dandys-world-bot` or similar if you cloned an older version or a fork).*

2.  **Install the Bot's Tools (Dependencies):**
    *   Open a command prompt or terminal window in the folder where you put the bot's files.
    *   Type this command and press Enter:
        ```bash
        pip install -r requirements.txt
        ```
        *(If you want to be extra neat and know about Python virtual environments, feel free to set one up first!)*

3.  **Create Your Bot's Settings File (`.env`):**
    *   In the bot's folder, find the file named `.env.example`.
    *   Make a copy of it and rename the copy to just `.env` (yes, starting with a dot!).
    *   Open this new `.env` file with a simple text editor (like Notepad or TextEdit).
    *   Fill in your details:
        ```env
        DISCORD_BOT_TOKEN=your_bot_token_here  # Paste your Bot Token here
        DISCORD_CHANNEL_ID=your_channel_id_here # Paste the ID of the channel for announcements

        # Optional stuff - delete the # and fill these in if you want them:
        # PING_ROLE_ID=your_role_id_here
        # PING_USER_IDS=user1_id,user2_id,user3_id

        # You can usually leave this as INFO:
        LOG_LEVEL=INFO
        ```
    *   **Important**: `DISCORD_BOT_TOKEN` and `DISCORD_CHANNEL_ID` are REQUIRED!

4.  **Run the Bot!**
    *   In your command prompt/terminal (still in the bot's folder), type this and press Enter:
        ```bash
        python bot.py
        ```
    *   If everything is set up right, your bot should log in to Discord and start watching the wiki!

## ⚙️ Making Your Bot on Discord (The Important Bits!)

To get your `DISCORD_BOT_TOKEN` and invite the bot to your server, you need to tell Discord you're making a new bot.

1.  **Go to the Discord Developer Portal:** Open [https://discord.com/developers/applications](https://discord.com/developers/applications) in your web browser.
2.  **Create a New Application:**
    *   Click "New Application" (usually top right).
    *   Give your bot a cool name (like "Dandy Twisted Oracle") and click "Create".
3.  **Go to the "Bot" Section:** On the left side menu, click "Bot".
4.  **Add a Bot:** Click the "Add Bot" button, then "Yes, do it!".
5.  **Get Your Token:** Under the bot's username, you'll see "TOKEN". Click "Copy". **This is your `DISCORD_BOT_TOKEN`! Keep it secret, keep it safe!**
6.  **Bot Permissions:** Your bot needs permission to do things in your server. When you invite it, you'll set these. The key ones it needs are:
    *   Send Messages
    *   Embed Links (to make the messages look nice)
    *   Attach Files (for images, though this bot links them)
    *   Read Message History (sometimes needed)
7.  **Invite Your Bot to Your Server:**
    *   Go back to the "General Information" page for your application (left menu). Find your "APPLICATION ID". Copy it.
    *   Use this link, replacing `YOUR_BOT_APPLICATION_ID` with the ID you just copied:
        ```
        https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_APPLICATION_ID&permissions=52224&scope=bot
        ```
        *(The `permissions=52224` number includes the basic permissions listed above. You can also use the "OAuth2 URL Generator" in the Developer Portal to create this link if you prefer.)*
    *   Open that link in your browser. Choose the server you want to add the bot to, click "Continue", review the permissions, and click "Authorize".

Phew! That's the trickiest part. Once the bot is on your server and you've set up your `.env` file, you're ready to run `python bot.py`.

## 📋 How It Knows What's Happening

*   **Checks the Clock**: Every hour, like clockwork, it peeks at the [Dandy's World Wiki](https://dandys-world-robloxhorror.fandom.com/wiki/Daily_Twisted_Board).
*   **Special Timing**: It knows the midnight UTC update (often 8 PM for Eastern Time folks in the US) is a big one, so it waits an extra minute to catch the freshest info.
*   **Smarty Pants**: It only tells you if the Twisted character is new or if the timer on the board has reset.
*   **Picture This**: It grabs the character's name, their image, and any timer info from the wiki.
*   **Pretty Messages**: It then sends a neat-looking message to your Discord channel with all these details. If you set up pings, it'll ping your chosen role or friends too!

## 🚨 Uh Oh! Troubleshooting Tips

Having a spot of bother? Here are some common fixes:

*   **Bot Won't Start?**
    *   Did you put your super-secret `DISCORD_BOT_TOKEN` in the `.env` file?
    *   Did you tell it which `DISCORD_CHANNEL_ID` to post in?
    *   Did you install the tools with `pip install -r requirements.txt`?
    *   Make sure your bot has permission to send messages in your chosen channel on Discord.
*   **No Announcements?**
    *   Is the `DISCORD_CHANNEL_ID` definitely correct in your `.env` file?
    *   Double-check the bot is actually a member of your Discord server and has "Send Messages" and "Embed Links" permissions in the announcement channel.
    *   Sometimes the wiki changes things, which can confuse the bot. If you're tech-savvy, you can check the `logs/` folder for error messages.
*   **Images Not Showing Up?**
    *   The wiki might be having a hiccup, or the image might be missing there.
    *   Check your computer's internet connection.
*   **Want More Details for Debugging? (Advanced)**
    *   If you're comfortable, you can change `LOG_LEVEL=INFO` to `LOG_LEVEL=DEBUG` in your `.env` file. This will make the bot write a LOT more information into its `logs/dandys_world_bot.log` file, which can help figure out tricky problems.

## 🧑‍💻 For the Tech-Savvy (Developers)

If you're interested in the nitty-gritty or want to contribute:

*   **Project Files**: The bot is made of several Python files (`bot.py`, `scraper.py`, `config.py`, `utils.py`). There's also `test_image.py` for checking the image-grabbing part.
*   **Want to Help?**: Cool! Check out the [main GitHub page](https://github.com/thesomewhatyou/TOTB-checker). You can "fork" the project, make your awesome changes, and then suggest them back as a "pull request."
*   **Logs**: The bot keeps detailed logs in a `logs` folder (it makes this folder itself). These are super helpful if something goes wrong.

## 📜 License

This bot is super free! It uses the Unlicense, meaning you can do almost anything you want with it. See the `LICENSE` file for the exciting legal details.

## 🙏 Thank You!

*   To the awesome Dandy's World game community!
*   To the clever folks behind the [Discord.py](https://discordpy.readthedocs.io/) library that helps this bot talk to Discord.
*   To everyone who helps keep the Dandy's World Fandom Wiki up-to-date!

## 📞 Got Questions or Ideas?

If you need help, have a cool idea, or (oops!) found a bug:

*   The best place is to open an "Issue" on the [GitHub repository page](https://github.com/thesomewhatyou/TOTB-checker/issues).
*   You can also try reaching out to `thesomewhatyou` (the original creator).

---

**In Simple Terms (TL;DR):**

This bot checks the Dandy's World wiki for the Daily Twisted character every hour. If it changes, the bot posts a message with the character's name and picture in your Discord server.

To use it:
1.  Download the files.
2.  Install some tools (`pip install -r requirements.txt`).
3.  Create a bot on Discord, get its Token.
4.  Copy `.env.example` to `.env` and fill in your Bot Token and Channel ID.
5.  Run `python bot.py`.
Enjoy knowing who's Twisted!

*This bot is an open-source fan project and is not officially affiliated with Dandy's World or its creators.*
*Bot created with help from Jules from Google.*
*Last updated: July 2, 2025*
