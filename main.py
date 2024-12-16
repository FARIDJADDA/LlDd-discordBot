import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv


load_dotenv(dotenv_path="config")
TOKEN = os.getenv("DISCORD_TOKEN")

# Initialisation du bot avec un préfixe pour les commandes classiques
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    """Synchronise les commandes hybrides au démarrage et affiche le statut du bot."""
    await bot.tree.sync()  # Synchronisation des commandes Slash avec Discord
    print(f"✅ Commandes Slash synchronisées.")
    print(f"✅ Bot connecté en tant que {bot.user.name} ({bot.user.id})")


async def load_cogs():
    """Décharge tout avant de charger les cogs."""
    await unload_all_cogs()
    # Charger les cogs ensuite
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("__"):
            try:
                module_name = f"cogs.{filename[:-3]}"
                await bot.load_extension(module_name)
                print(f"✅ Cog chargé : {filename}")
            except Exception as e:
                print(f"⚠️ Erreur lors du chargement du cog {filename} : {e}")


async def reload_cog(cog_name):
    """Recharge dynamiquement un Cog."""
    try:
        if cog_name in bot.extensions:
            print(f"🔄 Déchargement du cog : {cog_name}")
            await bot.unload_extension(cog_name)
        print(f"🔄 Chargement du cog : {cog_name}")
        await bot.load_extension(cog_name)
        print(f"✅ Cog rechargé : {cog_name}")
    except Exception as e:
        print(f"⚠️ Erreur lors du rechargement du Cog {cog_name} : {e}")



async def unload_all_cogs():
    """Décharge tous les Cogs avant de recharger."""
    for extension in list(bot.extensions.keys()):
        try:
            print(f"🔄 Déchargement du cog : {extension}")
            await bot.unload_extension(extension)
        except Exception as e:
            print(f"⚠️ Erreur lors du déchargement de {extension} : {e}")


async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
