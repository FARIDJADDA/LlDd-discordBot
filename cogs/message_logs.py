import discord
import json
import os
from discord.ext import commands
from utils.logger import logger

# Chemin vers le fichier JSON dans le dossier 'data'
CONFIG_DIR = "data"
LOG_CONFIG_FILE = os.path.join(CONFIG_DIR, "log_config.json")


class MessageLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = self.load_config()

    def load_config(self):
        """Charge et valide la configuration des logs."""
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
            logger.info(f"📁 Dossier '{CONFIG_DIR}' créé.")

        if not os.path.exists(LOG_CONFIG_FILE):
            logger.warning(f"⚠️ Fichier '{LOG_CONFIG_FILE}' manquant. Création avec des valeurs par défaut.")
            return self.reset_config()

        try:
            with open(LOG_CONFIG_FILE, "r") as file:
                config = json.load(file)
                # Vérifie si log_channel_id est présent et valide
                if "log_channel_id" not in config or not isinstance(config["log_channel_id"], (int, type(None))):
                    logger.warning("⚠️ Configuration invalide détectée. Réinitialisation en cours.")
                    return self.reset_config()
                return config["log_channel_id"]
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"❌ Erreur de lecture dans '{LOG_CONFIG_FILE}': {e}")
            return self.reset_config()

    def reset_config(self):
        """Réinitialise la configuration avec des valeurs par défaut."""
        default_config = {"log_channel_id": None}
        with open(LOG_CONFIG_FILE, "w") as file:
            json.dump(default_config, file, indent=4)
        logger.info(f"✅ Fichier '{LOG_CONFIG_FILE}' réinitialisé.")
        return default_config["log_channel_id"]

    def save_config(self, channel_id):
        """Sauvegarde l'ID du canal de log dans un fichier JSON."""
        try:
            with open(LOG_CONFIG_FILE, "w") as file:
                json.dump({"log_channel_id": channel_id}, file, indent=4)
            logger.info(f"✅ Configuration de log sauvegardée : Canal ID {channel_id}")
        except Exception as e:
            logger.error(f"❌ Erreur lors de la sauvegarde de '{LOG_CONFIG_FILE}' : {e}")


    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Logger les modifications de messages."""
        if before.author.bot or before.content == after.content:
            return

        if not self.log_channel_id:
            logger.warning("⚠️ Aucun canal de log configuré. Ignorant l'événement on_message_edit.")
            return

        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            # Vérification des permissions avant d'envoyer le message
            if not log_channel.permissions_for(log_channel.guild.me).send_messages:
                logger.warning(f"⚠️ Permissions insuffisantes pour envoyer des messages dans '{log_channel.name}'.")
                return

            try:
                embed = discord.Embed(
                    title="✏️ Message modifié",
                    color=discord.Color.dark_purple(),
                    timestamp=discord.utils.utcnow()
                )
                embed.add_field(name="Auteur", value=before.author.mention, inline=False)
                embed.add_field(name="Canal", value=before.channel.mention, inline=False)
                embed.add_field(name="Avant", value=before.content or "*(vide)*", inline=False)
                embed.add_field(name="Après", value=after.content or "*(vide)*", inline=False)
                embed.set_thumbnail(url="attachment://message_edit_icon.png")
                embed.set_footer(text=f"Message ID : {before.id}")

                # Envoi avec l'icône jointe
                file = discord.File("assets/message_edit_icon.png", filename="message_edit_icon.png")
                await log_channel.send(file=file, embed=embed)
                logger.info(f"✏️ Modification de message loggée dans '{log_channel.name}'.")

            except Exception as e:
                logger.error(f"❌ Erreur lors de l'envoi du log dans '{log_channel.name}': {e}")


    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """Logger les suppressions de messages."""
        if message.author.bot:
            return

        if not self.log_channel_id:
            logger.warning("⚠️ Aucun canal de log configuré. Ignorant l'événement on_message_delete.")
            return

        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            # Vérification des permissions avant d'envoyer le message
            if not log_channel.permissions_for(log_channel.guild.me).send_messages:
                logger.warning(f"⚠️ Permissions insuffisantes pour envoyer des messages dans '{log_channel.name}'.")
                return

            try:
                embed = discord.Embed(
                    title="🗑️ Message supprimé",
                    color=discord.Color.dark_red(),
                    timestamp=discord.utils.utcnow()
                )
                embed.add_field(name="Auteur", value=message.author.mention, inline=False)
                embed.add_field(name="Canal", value=message.channel.mention, inline=False)
                embed.add_field(name="Contenu", value=message.content or "*(vide)*", inline=False)
                embed.set_thumbnail(url="attachment://message_delete_icon.png")
                embed.set_footer(text=f"Message ID : {message.id}")

                # Envoi avec l'icône jointe
                file = discord.File("assets/message_delete_icon.png", filename="message_delete_icon.png")
                await log_channel.send(file=file, embed=embed)
                logger.info(f"🗑️ Suppression de message loggée dans '{log_channel.name}'.")

            except Exception as e:
                logger.error(f"❌ Erreur lors de l'envoi du log dans '{log_channel.name}': {e}")


    @commands.hybrid_command(name="set_log_channel", description="Configure le canal de log des messages.")
    async def set_log_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Définit dynamiquement le canal de log."""
        self.log_channel_id = channel.id
        self.save_config(channel.id)
        await ctx.send(embed=discord.Embed(
            title="✅ Canal de log configuré",
            description=f"Les logs seront envoyés dans {channel.mention}.",
            color=discord.Color.green()
        ))
        logger.info(f"✅ Canal de log configuré par {ctx.author.name} : {channel.name} (ID: {channel.id})")


    @commands.hybrid_command(name="reset_log_config", help="Réinitialise la configuration de log.")
    @commands.has_permissions(administrator=True)
    async def reset_log_config(self, ctx: commands.Context):
        """Réinitialise la configuration de log."""
        self.log_channel_id = self.reset_config()
        await ctx.send(embed=discord.Embed(
            title="🔄 Configuration réinitialisée",
            description="Le fichier de configuration des logs a été réinitialisé avec succès.",
            color=discord.Color.orange()
        ))
        logger.info(f"🔄 Configuration de log réinitialisée par {ctx.author.name}.")


async def setup(bot: commands.Bot):
    """Ajoute la cog au bot."""
    await bot.add_cog(MessageLogs(bot))
    logger.info("✅ Cog MessageLogs ajouté avec succès.")
