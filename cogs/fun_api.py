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

    @commands.hybrid_command(name="joke", description="Get a random joke.")
    async def joke(self, ctx: commands.Context):
        """Fetch a random joke from JokeAPI while excluding inappropriate categories."""
        self.jokeapi_url = "https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,racist,sexist,explicit"
        # The blacklistFlags parameter excludes jokes with inappropriate content

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.jokeapi_url) as resp:
                    if resp.status != 200:
                        await ctx.send("❌ Unable to fetch a joke at the moment.")
                        return

                    joke_data = await resp.json()
                    if joke_data["type"] == "single":
                        # Single-line joke
                        joke = joke_data["joke"]
                    else:
                        # Joke with setup and delivery
                        joke = f"{joke_data['setup']}\n\n*{joke_data['delivery']}*"

                    embed = discord.Embed(
                        title="😂 Random Joke",
                        description=joke,
                        color=discord.Color.dark_purple(),
                    )
                    embed.set_footer(text="Joke generated from JokeAPI")
                    await ctx.send(embed=embed)

            except Exception as e:
                await ctx.send("❌ An error occurred while fetching a joke.")
                print(f"Joke API Error: {e}")


async def setup(bot: commands.Bot):
    """Ajoute la cog au bot."""
    await bot.add_cog(FunAPI(bot))
