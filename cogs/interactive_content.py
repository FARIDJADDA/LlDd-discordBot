import discord
import aiohttp
import os
from discord.ext import commands
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv(dotenv_path="config")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")


class InteractiveContent(commands.Cog):
    """Cog pour les commandes interactives : Météo et Actualités Gaming."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="weather", description="Affiche la météo actuelle d'une ville.")
    async def weather(self, ctx, *, city: str):
        """Commande pour récupérer et afficher la météo d'une ville."""
        if not OPENWEATHER_API_KEY:
            await ctx.send("❌ Clé API OpenWeatherMap non configurée.")
            return

        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={OPENWEATHER_API_KEY}&lang=fr"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send("❌ Impossible de récupérer la météo. Vérifiez le nom de la ville.")
                    return
                data = await resp.json()

        weather_desc = data["weather"][0]["description"].capitalize()
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        city_name = data["name"]
        country = data["sys"]["country"]
        icon = data["weather"][0]["icon"]

        # Embed météo
        embed = discord.Embed(
            title=f"🌤️ Météo à {city_name}, {country}",
            description=f"**{weather_desc}**",
            color=discord.Color.blue()
        )
        embed.add_field(name="🌡 Température", value=f"{temp}°C", inline=True)
        embed.add_field(name="🌡 Ressenti", value=f"{feels_like}°C", inline=True)
        embed.set_thumbnail(url=f"http://openweathermap.org/img/wn/{icon}@2x.png")
        embed.set_footer(text="Données fournies par OpenWeatherMap")

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="news", description="Affiche les dernières actualités gaming.")
    async def news(self, ctx):
        """Commande pour récupérer et afficher les actualités gaming."""
        if not NEWS_API_KEY:
            await ctx.send("❌ Clé API NewsAPI non configurée.")
            return

        url = f"https://newsapi.org/v2/everything?q=gaming&language=fr&sortBy=publishedAt&pageSize=5&apiKey={NEWS_API_KEY}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send("❌ Impossible de récupérer les actualités gaming.")
                    return
                data = await resp.json()

        articles = data.get("articles", [])
        if not articles:
            await ctx.send("❌ Aucune actualité trouvée.")
            return

        embed = discord.Embed(
            title="📰 Actualités Gaming",
            description="Les dernières actualités sur les jeux vidéo 🎮",
            color=discord.Color.dark_purple()
        )
        for article in articles:
            title = article["title"]
            url = article["url"]
            embed.add_field(name=f"🔗 {title}", value=f"[Lire l'article]({url})", inline=False)

        embed.set_footer(text="Données fournies par NewsAPI")
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    """Ajoute la cog au bot."""
    await bot.add_cog(InteractiveContent(bot))
