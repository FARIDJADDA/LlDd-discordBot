import aiohttp
import asyncio
from discord.ext import commands, tasks
from utils.logger import logger  # Utilisation du logger global
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="config")
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", 1316854770790699110))  # ID par défaut

class Twitch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.streamers = ["dr_ninety", "Lefa_LLDD", "SmileNooby"]
        self.streamers_status = {streamer: False for streamer in self.streamers}
        self.headers = {}
        self.twitch_api_url = "https://api.twitch.tv/helix/"
        self.check_streams.start()

    async def fetch_twitch_token(self):
        """Obtenir un token d'accès pour l'API Twitch"""
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
        """Vérifie si un streamer est en live"""
        url = f"{self.twitch_api_url}streams?user_login={streamer}"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return bool(data.get("data"))  # Retourne True si en live
                    elif resp.status == 401:
                        logger.warning("Token Twitch expiré, régénération nécessaire.")
                        await self.fetch_twitch_token()
                        return False
                    else:
                        logger.error(f"Erreur API Twitch pour {streamer}: {resp.status} - {await resp.text()}")
            except Exception as e:
                logger.error(f"Erreur lors de la vérification du stream pour {streamer} : {e}")
                return False

    @tasks.loop(minutes=1)
    async def check_streams(self):
        """Boucle pour vérifier l'état des streams"""
        channel = self.bot.get_channel(DISCORD_CHANNEL_ID)

        # Vérification que le canal existe
        if channel is None:
            logger.warning(f"Le canal avec l'ID {DISCORD_CHANNEL_ID} est introuvable ou inaccessible.")
            return

        for streamer in self.streamers:
            is_live = await self.check_stream_status(streamer)

            if is_live and not self.streamers_status[streamer]:
                self.streamers_status[streamer] = True
                try:
                    await channel.send(f"🚨 **{streamer} est maintenant en live !**\nLien : https://twitch.tv/{streamer}")
                    logger.info(f"Notification envoyée pour {streamer}.")
                except Exception as e:
                    logger.error(f"Erreur lors de l'envoi de la notification pour {streamer} : {e}")

            elif not is_live and self.streamers_status[streamer]:
                # Streamer a arrêté le live
                self.streamers_status[streamer] = False
                logger.info(f"{streamer} n'est plus en live.")

    @check_streams.before_loop
    async def before_check_streams(self):
        await self.bot.wait_until_ready()
        await self.fetch_twitch_token()

async def setup(bot):
    await bot.add_cog(Twitch(bot))