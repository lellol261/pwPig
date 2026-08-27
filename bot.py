import os
from dotenv import load_dotenv
from nextcord.ext import commands
import nextcord

intents = nextcord.Intents.default()
intents.message_content = True
GUILD_ID = 1542288270749081621

def main():
    client = commands.Bot(command_prefix="!", intents=intents)
    load_dotenv()

    @client.event
    async def on_ready():
        print(f"{client.user.name} has connected to Discord.")

    # load all cogs
    for folder in os.listdir("modules"):
        if os.path.exists(os.path.join("modules", folder, "cog.py")):
            client.load_extension(f"modules.{folder}.cog")
            print(f"Loaded cogs.{folder}")

    client.run(os.getenv("DISCORD_TOKEN"))

if __name__ == '__main__':
    main()