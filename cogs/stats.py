import discord
from discord.ext import commands
from datetime import datetime


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_count = 0  # Compteur global des messages

    @commands.Cog.listener()
    async def on_message(self, message):
        """Compter les messages pour les statistiques"""
        if not message.author.bot:
            self.message_count += 1

    @commands.command()
    async def stats(self, ctx):
        """Afficher les statistiques du serveur"""
        guild = ctx.guild

        # Calculer le nombre de membres en ligne
        online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)

        # Création de l'embed
        embed = discord.Embed(
            title=f"Statistiques pour {guild.name}",
            color=discord.Color.blurple(),
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else "")
        embed.add_field(name="👥 Nombre total de membres", value=f"{guild.member_count}", inline=True)
        embed.add_field(name="🟢 Membres en ligne", value=f"{online_members}", inline=True)
        embed.add_field(name="📜 Nombre de rôles", value=f"{len(guild.roles)}", inline=True)
        embed.add_field(name="💬 Canaux textuels", value=f"{len(guild.text_channels)}", inline=True)
        embed.add_field(name="🔊 Canaux vocaux", value=f"{len(guild.voice_channels)}", inline=True)
        embed.add_field(name="✉️ Messages envoyés (depuis démarrage)", value=f"{self.message_count}", inline=True)
        embed.set_footer(text=f"Demandé par {ctx.author}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Stats(bot))
