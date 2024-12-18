import discord
import aiohttp
from discord.ext import commands


class FunAPI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.imgflip_url = "https://api.imgflip.com/get_memes"
        self.jokeapi_url = "https://v2.jokeapi.dev/joke/Any"

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

    @commands.hybrid_command(name="joke", description="Raconte une blague aléatoire.")
    async def joke(self, ctx: commands.Context):
        """Récupère une blague aléatoire depuis JokeAPI."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.jokeapi_url) as resp:
                    if resp.status != 200:
                        await ctx.send("❌ Impossible de récupérer une blague pour le moment.")
                        return

                    joke_data = await resp.json()
                    if joke_data["type"] == "single":
                        # Blague simple
                        joke = joke_data["joke"]
                    else:
                        # Blague avec question/réponse
                        joke = f"{joke_data['setup']}\n\n*{joke_data['delivery']}*"

                    embed = discord.Embed(
                        title="😂 Blague aléatoire",
                        description=joke,
                        color=discord.Color.green(),
                    )
                    embed.set_footer(text="Blague générée depuis JokeAPI")
                    await ctx.send(embed=embed)

            except Exception as e:
                await ctx.send("❌ Une erreur est survenue en récupérant une blague.")
                print(f"Erreur API Blague : {e}")


async def setup(bot: commands.Bot):
    """Ajoute la cog au bot."""
    await bot.add_cog(FunAPI(bot))
