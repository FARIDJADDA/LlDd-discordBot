import discord
import aiohttp
from discord.ext import commands
from utils.logger import logger


class JokeAPI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.jokeapi_url = "https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,racist,sexist,explicit"

    @commands.hybrid_command(name="joke", description="Get a random joke.")
    async def joke(self, ctx: commands.Context):
        """Fetch a random joke from JokeAPI while excluding inappropriate categories."""
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
    """Ajoute la cog des blagues au bot."""
    await bot.add_cog(JokeAPI(bot))
    logger.info("☑️ Cog JokeAPI ajouté avec succès.")
