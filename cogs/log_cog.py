from discord.ext import commands
import discord
from utils.logger import logger  # Utilise le logger configuré dans logger.py


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def log_action(self, ctx, action, target, reason=None):
        """Logger une action de modération dans un canal spécifique et dans un fichier local"""
        log_message = f"Action: {action}, Utilisateur: {target}, Par: {ctx.author}, Raison: {reason or 'Aucune'}"

        # Log dans un fichier local
        logger.info(log_message)

        # Log dans un canal Discord
        log_channel = discord.utils.get(ctx.guild.channels, name="logs")
        if log_channel:
            try:
                embed = discord.Embed(
                    title="Action de modération",
                    description=f"**Action** : {action}\n**Utilisateur** : {target.mention}\n**Par** : {ctx.author.mention}\n**Raison** : {reason or 'Aucune'}",
                    color=discord.Color.red()
                )
                await log_channel.send(embed=embed)
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi du log Discord pour {action}: {e}")
        else:
            logger.warning(f"Le canal 'logs' est introuvable dans le serveur {ctx.guild.name}.")

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Logger les messages supprimés"""
        if message.author == self.bot.user:
            return

        log_message = f"Message supprimé : {message.content} par {message.author} dans {message.channel}"
        logger.info(log_message)

        # Log dans un canal Discord
        log_channel = discord.utils.get(message.guild.channels, name="logs")
        if log_channel:
            try:
                embed = discord.Embed(
                    title="Message supprimé",
                    description=f"**Auteur** : {message.author.mention}\n**Canal** : {message.channel.mention}\n**Contenu** : {message.content}",
                    color=discord.Color.orange()
                )
                await log_channel.send(embed=embed)
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi du log Discord pour un message supprimé : {e}")
        else:
            logger.warning("Le canal 'logs' est introuvable pour un message supprimé.")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Logger les connexions des membres"""
        log_message = f"Nouveau membre : {member} a rejoint le serveur {member.guild.name}."
        logger.info(log_message)

        # Log dans un canal Discord
        log_channel = discord.utils.get(member.guild.channels, name="logs")
        if log_channel:
            try:
                embed = discord.Embed(
                    title="Nouveau membre",
                    description=f"Bienvenue à {member.mention} sur le serveur {member.guild.name} !",
                    color=discord.Color.green()
                )
                await log_channel.send(embed=embed)
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi du log Discord pour un nouveau membre : {e}")
        else:
            logger.warning(f"Le canal 'logs' est introuvable pour un nouveau membre.")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Logger les départs des membres"""
        log_message = f"Membre : {member} a quitté le serveur {member.guild.name}."
        logger.info(log_message)

        # Log dans un canal Discord
        log_channel = discord.utils.get(member.guild.channels, name="logs")
        if log_channel:
            try:
                embed = discord.Embed(
                    title="Départ d'un membre",
                    description=f"{member.mention} a quitté le serveur {member.guild.name}.",
                    color=discord.Color.dark_red()
                )
                await log_channel.send(embed=embed)
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi du log Discord pour un départ de membre : {e}")
        else:
            logger.warning(f"Le canal 'logs' est introuvable pour un départ de membre.")


async def setup(bot):
    await bot.add_cog(Logging(bot))
