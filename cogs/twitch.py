import aiohttp
import asyncio
import json
import os
import discord
from discord.ext import commands
from utils.logger import logger
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv(dotenv_path="config")
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")


class Twitch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "twitch_config.json"
        self.config = self.load_config()
        self.streamers_status = {streamer: False for streamer in self.config["streamers"]}
        self.headers = {}
        self.twitch_api_url = "https://api.twitch.tv/helix/"
        self.bot.loop.create_task(self.initialize())  # Appel au démarrage

    async def initialize(self):
        """Initialise le token et la tâche de vérification."""
        await self.fetch_twitch_token()
        self.task = self.bot.loop.create_task(self.check_streams_task())

    def load_config(self):
        """Charge la configuration depuis un fichier JSON."""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError as e:
                    logger.error(f"Erreur de chargement de la configuration Twitch : {e}")
        return {"streamers": [], "notification_channel_id": None}

    def save_config(self, data):
        """Sauvegarde la configuration dans un fichier JSON."""
        with open(self.config_file, "w") as file:
            json.dump(data, file, indent=4)

    async def fetch_twitch_token(self):
        """Obtenir un token d'accès pour l'API Twitch."""
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": TWITCH_CLIENT_ID,
            "client_secret": TWITCH_CLIENT_SECRET,
            "grant_type": "client_credentials",
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.headers = {
                            "Client-ID": TWITCH_CLIENT_ID,
                            "Authorization": f"Bearer {data['access_token']}",
                        }
                        logger.info("Token Twitch récupéré avec succès.")
                    else:
                        logger.error(f"Erreur API Twitch (Token): {resp.status}")
            except Exception as e:
                logger.error(f"Erreur lors de l'obtention du token Twitch : {e}")

    async def fetch_stream_data(self, streamer):
        """Récupère les informations sur le stream en cours et l'utilisateur."""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                stream_url = f"{self.twitch_api_url}streams?user_login={streamer}"
                async with session.get(stream_url) as stream_resp:
                    stream_data = await stream_resp.json()
                    if not stream_data.get("data"):
                        return None  # Stream offline

                user_url = f"{self.twitch_api_url}users?login={streamer}"
                async with session.get(user_url) as user_resp:
                    user_data = await user_resp.json()
                    return {**stream_data["data"][0], **user_data["data"][0]}
            except Exception as e:
                logger.error(f"Erreur lors de la récupération des données Twitch pour {streamer}: {e}")
                return None

    async def check_streams_task(self):
        """Tâche pour vérifier régulièrement si les streamers sont en live."""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            channel_id = self.config.get("notification_channel_id")
            if not channel_id:
                logger.warning("Aucun canal de notification configuré pour Twitch.")
                await asyncio.sleep(60)
                continue

            channel = self.bot.get_channel(channel_id)
            if not channel:
                logger.warning(f"Le canal avec l'ID {channel_id} est introuvable.")
                await asyncio.sleep(60)
                continue

            for streamer in self.config["streamers"]:
                stream_data = await self.fetch_stream_data(streamer)
                if stream_data and not self.streamers_status.get(streamer, False):
                    self.streamers_status[streamer] = True
                    embed = discord.Embed(
                        title=f"🔴 {streamer} est en live !",
                        description=f"**{stream_data['title']}**\n🎮 **Jeu** : {stream_data['game_name']}",
                        url=f"https://www.twitch.tv/{streamer}",
                        color=discord.Color.dark_purple(),
                    )
                    embed.set_thumbnail(url=stream_data.get("profile_image_url"))
                    embed.set_image(url=stream_data.get("thumbnail_url").replace("{width}x{height}", "1280x720"))
                    embed.set_footer(text="Rejoins le stream maintenant ! 🚀")
                    await channel.send(embed=embed)
                elif not stream_data and self.streamers_status.get(streamer, False):
                    self.streamers_status[streamer] = False
            await asyncio.sleep(120)

    @commands.hybrid_command(name="set_twitch_channel", help="Définit le salon pour les notifications Twitch.")
    async def set_twitch_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Définit le salon pour les notifications."""
        self.config["notification_channel_id"] = channel.id
        self.save_config(self.config)
        await ctx.send(f"✅ Les notifications Twitch seront envoyées dans {channel.mention}.")

    @commands.hybrid_command(name="add_twitch_streamer", help="Ajoute un streamer à la liste.")
    async def add_streamer(self, ctx: commands.Context, streamer: str):
        """Ajoute un streamer à la liste."""
        if streamer not in self.config["streamers"]:
            self.config["streamers"].append(streamer)
            self.save_config(self.config)
            await ctx.send(f"✅ **{streamer}** a été ajouté à la liste des streamers.")
        else:
            await ctx.send(f"⚠️ **{streamer}** est déjà dans la liste.")

    @commands.hybrid_command(name="list_twitch_streamers", help="Affiche la liste des streamers suivis.")
    async def list_streamers(self, ctx: commands.Context):
        """Affiche les streamers suivis."""
        streamers = self.config["streamers"]
        description = "\n".join(streamers) if streamers else "Aucun streamer suivi."
        await ctx.send(embed=discord.Embed(
            title="📜 Liste des streamers suivis",
            description=description,
            color=discord.Color.dark_purple()
        ))


async def setup(bot: commands.Bot):
    """Ajoute la cog au bot."""
    await bot.add_cog(Twitch(bot))
