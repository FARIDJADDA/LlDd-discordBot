import discord
import json
import os
from discord.ext import commands


class MessageLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "log_config.json"
        self.log_channel_id = self.load_config()

    def load_config(self):
        """Charge l'ID du canal de log depuis un fichier JSON."""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as file:
                try:
                    config = json.load(file)
                    return config.get("log_channel_id")
                except json.JSONDecodeError:
                    print(f"⚠️ Erreur de format dans {self.config_file}.")
                    return None
        print("⚠️ Aucun fichier de configuration trouvé. Aucune configuration par défaut n'est chargée.")
        return None

    def save_config(self, channel_id):
        """Sauvegarde l'ID du canal de log dans un fichier JSON."""
        with open(self.config_file, "w") as file:
            json.dump({"log_channel_id": channel_id}, file, indent=4)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Logger les modifications de messages."""
        if before.author.bot or before.content == after.content:
            return

        if not self.log_channel_id:
            print("⚠️ Aucun canal de log configuré. Ignorant l'événement on_message_edit.")
            return

        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            embed = discord.Embed(
                title="✏️ Message modifié",
                color=discord.Color.gold(),
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="Auteur", value=before.author.mention, inline=False)
            embed.add_field(name="Canal", value=before.channel.mention, inline=False)
            embed.add_field(name="Avant", value=before.content or "*(vide)*", inline=False)
            embed.add_field(name="Après", value=after.content or "*(vide)*", inline=False)
            embed.set_footer(text=f"Message ID : {before.id}")
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """Logger les suppressions de messages."""
        if message.author.bot:
            return

        if not self.log_channel_id:
            print("⚠️ Aucun canal de log configuré. Ignorant l'événement on_message_delete.")
            return

        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            embed = discord.Embed(
                title="🗑️ Message supprimé",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="Auteur", value=message.author.mention, inline=False)
            embed.add_field(name="Canal", value=message.channel.mention, inline=False)
            embed.add_field(name="Contenu", value=message.content or "*(vide)*", inline=False)
            embed.set_footer(text=f"Message ID : {message.id}")
            await log_channel.send(embed=embed)

    @commands.hybrid_command(name="set_log_channel", description="Configure le canal de log des messages.")
    async def set_log_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Définit dynamiquement le canal de log."""
        self.log_channel_id = channel.id
        self.save_config(channel.id)
        await ctx.send(f"✅ Canal de log configuré : {channel.mention}")

    @set_log_channel.error
    async def set_log_channel_error(self, ctx, error):
        """Gestion des erreurs pour la commande set_log_channel."""
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Veuillez spécifier un canal valide.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Argument invalide. Assurez-vous de mentionner un canal texte valide.")
        else:
            await ctx.send("❌ Une erreur inattendue s'est produite.")
            raise error


async def setup(bot: commands.Bot):
    await bot.add_cog(MessageLogs(bot))
