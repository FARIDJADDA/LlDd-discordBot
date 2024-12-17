import discord
import platform
import datetime
from discord.ext import commands
import os


class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.datetime.utcnow()

    @commands.hybrid_command(name="status", description="Affiche le statut actuel du bot.")
    async def status(self, ctx: commands.Context):
        """Affiche le statut actuel du bot avec un embed enrichi."""

        # Calcul du temps d'activité
        uptime = datetime.datetime.utcnow() - self.start_time
        uptime_str = str(uptime).split('.')[0]  # Supprime les microsecondes

        # Nombre total d'utilisateurs sur tous les serveurs
        total_members = sum(guild.member_count for guild in self.bot.guilds)

        # Création de l'embed avec le style Demon Slayer
        embed = discord.Embed(
            title="⚙️ Statut du bot",
            color=discord.Color.dark_purple(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_thumbnail(url="attachment://status_icon.png")
        embed.add_field(name="🔹 Nom du bot", value=f"{self.bot.user.name}#{self.bot.user.discriminator}", inline=True)
        embed.add_field(name="🔹 Uptime", value=f"{uptime_str}", inline=True)
        embed.add_field(name="🔹 Cogs chargés", value=f"{len(self.bot.cogs)}", inline=True)
        embed.add_field(name="🔹 Serveurs", value=f"{len(self.bot.guilds)}", inline=True)
        embed.add_field(name="🔹 Membres total", value=f"{total_members}", inline=True)
        embed.add_field(name="🔹 Version Discord.py", value=f"{discord.__version__}", inline=True)
        embed.set_footer(text=f"Demandé par {ctx.author}", icon_url=ctx.author.avatar.url)

        # Ajout de l'image locale pour le thumbnail
        image_path = "assets/status_icon.png"
        if not os.path.exists(image_path):
            file = None
            print("⚠️ L'image 'status_icon.png' est introuvable.")
        else:
            file = discord.File(image_path, filename="status_icon.png")

        # Envoi de l'embed avec l'image jointe
        if isinstance(ctx, commands.Context):
            await ctx.send(file=file, embed=embed)
        else:
            await ctx.interaction.response.send_message(file=file, embed=embed)

    @status.error
    async def handle_command_errors(self, ctx: commands.Context, error):
        """Gestion des erreurs pour la commande hybride."""
        if isinstance(error, commands.CommandError):
            await ctx.send(embed=discord.Embed(
                title="❌ Erreur",
                description="Une erreur est survenue lors de l'exécution de la commande.",
                color=discord.Color.red(),
            ))
            print(f"Erreur dans la commande 'status': {error}")


async def setup(bot: commands.Bot):
    """Ajoute la cog au bot."""
    await bot.add_cog(Status(bot))
