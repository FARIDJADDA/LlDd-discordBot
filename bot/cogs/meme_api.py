import discord
import aiohttp
from discord.ext import commands
from utils.logger import logger


class MemeAPI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.imgflip_url = "https://api.imgflip.com/get_memes"

    @commands.hybrid_command(name="meme", description="Affiche un meme aléatoire.")
    async def meme(self, ctx: commands.Context):
        """Récupère un meme aléatoire depuis l'API Imgflip."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.imgflip_url) as resp:
                    if resp.status != 200:
                        await ctx.send("❌ Impossible de récupérer un meme pour le moment.")
                        return

                    data = await resp.json()
                    memes = data.get("data", {}).get("memes", [])
                    if not memes:
                        await ctx.send("❌ Aucun meme trouvé.")
                        return

                    # Sélectionne un meme aléatoire
                    import random
                    meme = random.choice(memes)

                    # Création de l'embed
                    embed = discord.Embed(
                        title=meme["name"],
                        color=discord.Color.dark_purple(),
                    )
                    embed.set_image(url=meme["url"])
                    embed.set_footer(text="Meme généré depuis Imgflip")
                    await ctx.send(embed=embed)

            except Exception as e:
                await ctx.send("❌ Une erreur est survenue en récupérant un meme.")
                print(f"Erreur API Meme : {e}")


async def setup(bot: commands.Bot):
    """Ajoute la cog des memes au bot."""
    await bot.add_cog(MemeAPI(bot))
    logger.info("☑️ Cog MemeAPI ajouté avec succès.")

