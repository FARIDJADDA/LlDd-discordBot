import discord
from discord.ext import commands
import datetime

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.datetime.utcnow()

    @commands.command()
    async def status(self, ctx):
        """Affiche le statut du bot"""
        # Calcul du temps d'activité
        uptime = datetime.datetime.utcnow() - self.start_time
        uptime_str = str(uptime).split('.')[0]  # Supprime les microsecondes

        # Création de l'embed
        embed = discord.Embed(
            title="Statut du bot",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else "")
        embed.add_field(name="Nom du bot", value=f"{self.bot.user.name}#{self.bot.user.discriminator}", inline=False)
        embed.add_field(name="Uptime", value=f"{uptime_str}", inline=False)
        embed.add_field(name="Nombre de cogs chargés", value=f"{len(self.bot.cogs)}", inline=True)
        embed.add_field(name="Nombre de serveurs", value=f"{len(self.bot.guilds)}", inline=True)
        embed.set_footer(text=f"Demandé par {ctx.author}", icon_url=ctx.author.avatar.url)

        # Envoi de l'embed
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Status(bot))
