import discord
from discord.ext import commands
import datetime


class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.datetime.utcnow()

    @commands.hybrid_command(name="status", description="Affiche le statut actuel du bot.")
    async def status(self, ctx: commands.Context):
        """Affiche le statut actuel du bot avec un embed."""
        # Calcul du temps d'activité
        uptime = datetime.datetime.utcnow() - self.start_time
        uptime_str = str(uptime).split('.')[0]  # Supprime les microsecondes

        # Création de l'embed
        embed = discord.Embed(
            title="Statut du bot",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        embed.add_field(name="Nom du bot", value=f"{self.bot.user.name}#{self.bot.user.discriminator}", inline=False)
        embed.add_field(name="Uptime", value=f"{uptime_str}", inline=False)
        embed.add_field(name="Nombre de cogs chargés", value=f"{len(self.bot.cogs)}", inline=True)
        embed.add_field(name="Nombre de serveurs", value=f"{len(self.bot.guilds)}", inline=True)
        embed.set_footer(text=f"Demandé par {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

        # Répond au contexte (commande préfixe ou slash)
        if isinstance(ctx, commands.Context):
            await ctx.send(embed=embed)
        else:
            await ctx.interaction.response.send_message(embed=embed)

    @status.error
    async def handle_command_errors(self, ctx: commands.Context, error):
        """Gestion des erreurs pour la commande hybride."""
        if isinstance(error, commands.CommandError):
            await ctx.send("❌ Une erreur est survenue lors de l'exécution de la commande.")
            print(f"Erreur dans la commande 'status': {error}")


async def setup(bot: commands.Bot):
    """Ajoute la cog au bot."""
    await bot.add_cog(Status(bot))
