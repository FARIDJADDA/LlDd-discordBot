import discord
from discord import app_commands
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="config")
COD_API_KEY = os.getenv("COD_API_KEY")  # Clé API Call of Duty


class GameStats:
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="codstats",
        description="Récupère des statistiques Call of Duty pour un joueur."
    )
    @app_commands.describe(
        username="Nom d'utilisateur Call of Duty.",
        platform="Plateforme du joueur (par défaut: battle)."
    )
    async def codstats(self, interaction: discord.Interaction, username: str, platform: str = "battle"):
        """Récupérer des statistiques Call of Duty via une Slash Command."""
        url = f"https://my.callofduty.com/api/stats/{platform}/{username}"

        headers = {
            "Authorization": f"Bearer {COD_API_KEY}",
        }

        await interaction.response.defer()  # Indiquer que le traitement prend du temps

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        stats = data.get("lifetime", {}).get("all", {}).get("properties", {})
                        embed = discord.Embed(
                            title=f"Statistiques Call of Duty pour {username}",
                            color=discord.Color.blue()
                        )
                        embed.add_field(name="Kills", value=f"{stats.get('kills', 'N/A')}", inline=True)
                        embed.add_field(name="Morts", value=f"{stats.get('deaths', 'N/A')}", inline=True)
                        embed.add_field(name="K/D Ratio", value=f"{stats.get('kdRatio', 'N/A')}", inline=True)
                        embed.set_footer(
                            text=f"Demandé par {interaction.user}",
                            icon_url=interaction.user.avatar.url if interaction.user.avatar else ""
                        )
                        await interaction.followup.send(embed=embed)
                    else:
                        await interaction.followup.send(f"❌ Erreur lors de la récupération des stats : {resp.status}.")
            except Exception as e:
                await interaction.followup.send(f"⚠️ Une erreur est survenue : {e}")

    async def setup_commands(self):
        """Ajoute la commande Slash au CommandTree."""
        self.bot.tree.add_command(self.codstats)


async def setup(bot):
    cog = GameStats(bot)
    await cog.setup_commands()
