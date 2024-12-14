import discord
from discord.ext import commands

class MessageLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Logger les modifications de messages"""
        # Ignorer les messages du bot
        if before.author.bot:
            return

        # Vérifie si le message a réellement été modifié
        if before.content == after.content:
            return

        log_channel = discord.utils.get(before.guild.channels, name="logs")
        if log_channel:
            embed = discord.Embed(
                title="Message modifié",
                color=discord.Color.gold(),
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="Auteur", value=before.author.mention, inline=False)
            embed.add_field(name="Canal", value=before.channel.mention, inline=False)
            embed.add_field(name="Avant", value=before.content or "*(vide)*", inline=False)
            embed.add_field(name="Après", value=after.content or "*(vide)*", inline=False)
            embed.set_footer(text=f"ID : {before.id}")
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Logger les suppressions de messages"""
        # Ignorer les messages du bot
        if message.author.bot:
            return

        log_channel = discord.utils.get(message.guild.channels, name="logs")
        if log_channel:
            embed = discord.Embed(
                title="Message supprimé",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="Auteur", value=message.author.mention, inline=False)
            embed.add_field(name="Canal", value=message.channel.mention, inline=False)
            embed.add_field(name="Contenu", value=message.content or "*(vide)*", inline=False)
            embed.set_footer(text=f"ID : {message.id}")
            await log_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MessageLogs(bot))
