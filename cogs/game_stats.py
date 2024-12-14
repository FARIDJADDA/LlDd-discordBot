import discord
from discord.ext import commands
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="config")
COD_API_KEY = os.getenv("COD_API_KEY")  # Clé API Call of Duty

class GameStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def codstats(self, ctx, username, platform="battle"):
        """Récupérer des statistiques Call of Duty pour un joueur"""
        url = f"https://my.callofduty.com/api/stats/{platform}/{username}"

        headers = {
            "Authorization": f"Bearer {COD_API_KEY}",
        }

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
                        embed.set_footer(text=f"Demandé par {ctx.author}", icon_url=ctx.author.avatar.url)
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send(f"❌ Erreur lors de la récupération des stats : {resp.status}.")
            except Exception as e:
                await ctx.send(f"⚠️ Une erreur est survenue : {e}")

async def setup(bot):
    await bot.add_cog(GameStats(bot))
