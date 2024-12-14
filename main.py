import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

# Charger les variables d'environnement
load_dotenv(dotenv_path="config")
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = '!'

# Initialisation du bot
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)


async def load_cogs():
    print("Dossier des cogs détecté.")
    for filename in os.listdir('./cogs'):
        print(f"Fichier détecté : {filename}")  # Log chaque fichier détecté
        if filename.endswith('.py') and not filename.startswith('__'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')  # Utiliser await
                print(f"Cog chargé : {filename}")
            except Exception as e:
                print(f"⚠️ Erreur lors du chargement du cog {filename} : {e}")

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user.name} ({bot.user.id})")
    print(f"✅ Cogs chargés : {[cog for cog in bot.cogs.keys()]}")


async def main():
    async with bot:
        await load_cogs()  # Charger tous les cogs
        await bot.start(TOKEN)  # Démarrer le bot


if __name__ == "__main__":
    asyncio.run(main())