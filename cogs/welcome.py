from discord.ext import commands
import discord
from utils.logger import logger  # Utilisation du logger global


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Événement déclenché lorsqu'un membre rejoint le serveur"""
        logger.info(f"Nouvel utilisateur détecté : {member.name} a rejoint {member.guild.name}")

        # Recherche du canal 'welcome'
        channel = discord.utils.get(member.guild.channels, name='welcome')

        if channel is None:
            logger.warning(f"Le canal 'welcome' est introuvable dans le serveur {member.guild.name}.")
            return

        # Envoi du message de bienvenue
        try:
            await channel.send(
                f"🎉 Bienvenue {member.mention} sur le serveur **{member.guild.name}** !\n"
                "Nous sommes ravis de t'accueillir parmi nous SOLDAT 🫡. \n"
                "👉 N'oublie pas de consulter <#1316869470446157824> pour connaître les règles du serveur.\n"
                "Amuse-toi bien et profite de ton séjour ici ! 🚀"
            )
            logger.info(f"Message de bienvenue envoyé à {member.name} dans {channel.name}.")
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du message de bienvenue pour {member.name} : {e}")

        # Log dans le canal 'logs'
        log_channel = discord.utils.get(member.guild.channels, name='logs')
        if log_channel:
            try:
                embed = discord.Embed(
                    title="Nouveau membre",
                    description=f"{member.mention} a rejoint le serveur **{member.guild.name}**.",
                    color=discord.Color.green(),
                )
                await log_channel.send(embed=embed)
                logger.info(f"Log d'arrivée envoyé dans {log_channel.name} pour {member.name}.")
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi du log Discord pour {member.name} : {e}")


async def setup(bot):
    logger.info("Chargement du cog Welcome")
    await bot.add_cog(Welcome(bot))