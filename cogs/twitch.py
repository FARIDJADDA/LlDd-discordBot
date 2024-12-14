import aiohttp
import asyncio
import json
import os
import discord  # Import nécessaire pour les types et fonctionnalités Discord
from discord.ext import commands, tasks
from utils.logger import logger
from dotenv import load_dotenv


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
        self.check_streams.start()

    def load_config(self):
        """Charge la configuration depuis un fichier JSON"""
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
        """Sauvegarde la configuration dans un fichier JSON"""
        with open(self.config_file, "w") as file:
            json.dump(data, file, indent=4)

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

    @tasks.loop(minutes=1)
    async def check_streams(self):
        """Boucle pour vérifier l'état des streams"""
        channel_id = self.config.get("notification_channel_id")
        if channel_id is None:
            logger.warning("Aucun canal de notification configuré.")
            return

        channel = self.bot.get_channel(channel_id)
        if channel is None:
            logger.warning(f"Le canal avec l'ID {channel_id} est introuvable ou inaccessible.")
            return

        for streamer in self.config["streamers"]:
            is_live = await self.check_stream_status(streamer)

            if is_live and not self.streamers_status[streamer]:
                self.streamers_status[streamer] = True
                try:
                    await channel.send(f"🚨 **{streamer} est maintenant en live !**\nLien : https://twitch.tv/{streamer}")
                    logger.info(f"Notification envoyée pour {streamer}.")
                except Exception as e:
                    logger.error(f"Erreur lors de l'envoi de la notification pour {streamer} : {e}")

            elif not is_live and self.streamers_status[streamer]:
                self.streamers_status[streamer] = False
                logger.info(f"{streamer} n'est plus en live.")

    @check_streams.before_loop
    async def before_check_streams(self):
        await self.bot.wait_until_ready()
        await self.fetch_twitch_token()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_twitch_channel(self, ctx, channel: discord.TextChannel):
        """Définit le canal de notification pour les streams"""
        self.config["notification_channel_id"] = channel.id
        self.save_config(self.config)
        await ctx.send(f"✅ Les notifications Twitch seront envoyées dans {channel.mention}.")

    @commands.command()
    async def list_streamers(self, ctx):
        """Affiche la liste des streamers suivis"""
        streamers = self.config["streamers"]
        if streamers:
            streamers_list = ", ".join(streamers)
            await ctx.send(f"📜 **Liste des streamers suivis :** {streamers_list}")
        else:
            await ctx.send("❌ Aucun streamer n'est actuellement suivi.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def add_streamer(self, ctx, streamer: str):
        """Ajoute un streamer à la liste"""
        if streamer not in self.config["streamers"]:
            self.config["streamers"].append(streamer)
            self.save_config(self.config)
            await ctx.send(f"✅ Le streamer `{streamer}` a été ajouté à la liste.")
        else:
            await ctx.send(f"❌ Le streamer `{streamer}` est déjà dans la liste.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def remove_streamer(self, ctx, streamer: str):
        """Supprime un streamer de la liste, insensible à la casse"""
        # Convertir en minuscule pour comparaison
        normalized_streamer = streamer.lower()
        streamers_normalized = [s.lower() for s in self.config["streamers"]]

        if normalized_streamer in streamers_normalized:
            # Supprimer le streamer en conservant la casse originale
            index = streamers_normalized.index(normalized_streamer)
            removed_streamer = self.config["streamers"].pop(index)

            # Sauvegarder la configuration
            self.save_config(self.config)
            await ctx.send(f"✅ Le streamer `{removed_streamer}` a été supprimé de la liste.")
        else:
            await ctx.send(f"❌ Le streamer `{streamer}` n'est pas dans la liste.")

async def setup(bot):
    await bot.add_cog(Twitch(bot))