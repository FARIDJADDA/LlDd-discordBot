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
        self.task = self.bot.loop.create_task(self.check_streams_task())

    def load_config(self):
        """Charge la configuration depuis un fichier JSON."""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError as e:
                    logger.error(f"Erreur de chargement du fichier {self.config_file} : {e}")
                    return {"streamers": [], "notification_channel_id": None}
        else:
            default_config = {"streamers": [], "notification_channel_id": None}
            self.save_config(default_config)
            return default_config

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
                        logger.error(f"Erreur API Twitch (Token): {resp.status} - {await resp.text()}")
            except Exception as e:
                logger.error(f"Erreur lors de l'obtention du token Twitch : {e}")

    async def check_stream_status(self, streamer):
        """Vérifie si un streamer est en live."""
        url = f"{self.twitch_api_url}streams?user_login={streamer}"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return bool(data.get("data"))
                    elif resp.status == 401:
                        logger.warning("Token Twitch expiré, régénération nécessaire.")
                        await self.fetch_twitch_token()
                        return False
                    else:
                        logger.error(f"Erreur API Twitch pour {streamer}: {resp.status} - {await resp.text()}")
            except Exception as e:
                logger.error(f"Erreur lors de la vérification du stream pour {streamer} : {e}")
                return False

    @commands.hybrid_group(name="twitch", invoke_without_command=True, description="Gère les notifications Twitch.")
    async def twitch(self, ctx: commands.Context):
        """Commandes principales pour gérer Twitch."""
        await ctx.send("Utilisez une sous-commande pour gérer les notifications Twitch.")

    @twitch.command(name="list", help="Affiche la liste des streamers suivis.")
    async def list_streamers(self, ctx: commands.Context):
        """Affiche la liste des streamers suivis."""
        streamers = self.config["streamers"]
        if streamers:
            streamers_list = ", ".join(streamers)
            await ctx.send(f"📜 **Liste des streamers suivis :** {streamers_list}")
        else:
            await ctx.send("❌ Aucun streamer n'est actuellement suivi.")

    @twitch.command(name="add", help="Ajoute un streamer à la liste.")
    async def add_streamer(self, ctx: commands.Context, streamer: str):
        """Ajoute un streamer à la liste."""
        if streamer not in self.config["streamers"]:
            self.config["streamers"].append(streamer)
            self.save_config(self.config)
            await ctx.send(f"✅ Le streamer `{streamer}` a été ajouté à la liste.")
        else:
            await ctx.send(f"❌ Le streamer `{streamer}` est déjà dans la liste.")

    @twitch.command(name="remove", help="Supprime un streamer de la liste.")
    async def remove_streamer(self, ctx: commands.Context, streamer: str):
        """Supprime un streamer de la liste."""
        if streamer in self.config["streamers"]:
            self.config["streamers"].remove(streamer)
            self.save_config(self.config)
            await ctx.send(f"✅ Le streamer `{streamer}` a été supprimé de la liste.")
        else:
            await ctx.send(f"❌ Le streamer `{streamer}` n'est pas dans la liste.")

    @twitch.command(name="set_channel", help="Définit le canal de notification Twitch.")
    async def set_twitch_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Définit le canal de notification pour les streams."""
        self.config["notification_channel_id"] = channel.id
        self.save_config(self.config)
        await ctx.send(f"✅ Les notifications Twitch seront envoyées dans {channel.mention}.")

    async def check_streams_task(self):
        """Tâche pour vérifier périodiquement les streams."""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            channel_id = self.config.get("notification_channel_id")
            if not channel_id:
                logger.warning("Aucun canal de notification configuré.")
                await asyncio.sleep(60)
                continue

            channel = self.bot.get_channel(channel_id)
            if not channel:
                logger.warning(f"Le canal avec l'ID {channel_id} est introuvable ou inaccessible.")
                await asyncio.sleep(60)
                continue

            for streamer in self.config["streamers"]:
                is_live = await self.check_stream_status(streamer)
                if is_live and not self.streamers_status[streamer]:
                    self.streamers_status[streamer] = True
                    await channel.send(f"🚨 **{streamer} est maintenant en live !**\nLien : https://twitch.tv/{streamer}")
                elif not is_live and self.streamers_status[streamer]:
                    self.streamers_status[streamer] = False
                    logger.info(f"{streamer} n'est plus en live.")

            await asyncio.sleep(120)


async def setup(bot: commands.Bot):
    """Ajoute la cog au bot."""
    await bot.add_cog(Twitch(bot))
