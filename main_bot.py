import os

from discord.ext import commands
import discord
from dotenv import load_dotenv


intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

load_dotenv(dotenv_path="config")

class LddBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="/")

    async def on_ready(self):
        print(f"{self.user.display_name} est connecté au serveur")


@bot.command(name='del')
async def delete(ctx, number_of_messages: int):
    messages = ctx.channel.history(limit=number_of_messages + 1)

    async for each_message in messages:
        await each_message.delete()
    print(f"{number_of_messages} message(s) supprimé(s).")


@bot.event
async def on_member_join(member):
    general_channel: discord.TextChannel = bot.get_channel(1136615027101675583)
    await general_channel.send(content=f"Bienvenue sur le serveur discord {member.display_name} !")

ldd_bot = LddBot()
ldd_bot.run(os.getenv("TOKEN"))
