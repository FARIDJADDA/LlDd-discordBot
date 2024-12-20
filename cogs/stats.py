import discord
from discord.ext import commands
from utils.logger import logger
from datetime import datetime


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="server_stats", description="Affiche les statistiques du serveur.")
    async def server_stats(self, ctx: commands.Context):
        """Affiche les statistiques du serveur via une commande hybride."""
        guild = ctx.guild

        if not guild:
            await ctx.send(embed=discord.Embed(
                title="❌ Erreur",
                description="Impossible de récupérer les statistiques du serveur.",
                color=discord.Color.dark_embed()
            ))
            logger.error(f"Échec de récupération des statistiques pour {ctx.author}.")
            return

        # Calcul des statistiques
        total_members = guild.member_count
        online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        total_channels = len(guild.channels)
        total_roles = len(guild.roles)
        total_emojis = len(guild.emojis)
        created_at = guild.created_at.strftime("%d/%m/%Y à %H:%M:%S")

        # Création de l'embed avec style Demon Slayer
        embed = discord.Embed(
            title=f"📊 **Statistiques du serveur : {guild.name}**",
            color=discord.Color.dark_purple(),  # Violet foncé
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url="assets/lldd_bot_dsgn.jpg")  # Placeholder image
        file = discord.File("assets/lldd_bot_dsgn.jpg", filename="lldd_bot_dsgn.jpg")
        embed.set_thumbnail(url="attachment://lldd_bot_dsgn.jpg")
        embed.add_field(name="📅 **Créé le**", value=f"{created_at}", inline=True)
        embed.add_field(name="👥 **Membres**", value=f"Total : {total_members}\nEn ligne : {online_members}", inline=True)
        embed.add_field(name="💬 **Salons**", value=f"Textuels : {text_channels}\nVocaux : {voice_channels}\nTotal : {total_channels}", inline=True)
        embed.add_field(name="🏷️ **Rôles**", value=f"{total_roles}", inline=True)
        embed.add_field(name="😎 **Émojis**", value=f"{total_emojis}", inline=True)
        embed.add_field(name="🚀 **Boosts**", value=f"Niveau : {guild.premium_tier}\nBoosts : {guild.premium_subscription_count or 0}", inline=True)

        embed.set_footer(text=f"Demandé par {ctx.author.name}", icon_url=ctx.author.avatar.url)

        # Envoie de l'embed
        if isinstance(ctx, commands.Context):
            await ctx.send(file=file,embed=embed)
        else:
            await ctx.interaction.response.send_message(embed=embed)

        logger.info(f"Statistiques du serveur affichées pour {ctx.author}.")

    @server_stats.error
    async def handle_command_errors(self, ctx: commands.Context, error):
        """Gestion des erreurs pour la commande hybride."""
        if isinstance(error, commands.CommandError):
            await ctx.send(embed=discord.Embed(
                title="❌ Erreur",
                description="Une erreur est survenue lors de l'exécution de la commande.",
                color=discord.Color.dark_embed()
            ))
            logger.error(f"Erreur dans la commande 'server_stats' : {error}")


async def setup(bot: commands.Bot):
    """Ajoute la cog au bot."""
    await bot.add_cog(Stats(bot))
