import discord
import json
import os
from discord.ext import commands


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "welcome_config.json"
        self.config = self.load_config()

    def load_config(self):
        """Charge la configuration des salons depuis un fichier JSON."""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    print("⚠️ Erreur de lecture dans le fichier de configuration.")
                    return {
                        "rules_channel_id": None,
                        "welcome_channel_name": "welcome",
                    }
        else:
            default_config = {
                "rules_channel_id": None,
                "welcome_channel_name": "welcome",
            }
            self.save_config(default_config)
            return default_config

    def save_config(self, config):
        """Sauvegarde la configuration dans un fichier JSON."""
        with open(self.config_file, "w") as file:
            json.dump(config, file, indent=4)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Envoie un message de bienvenue lorsqu'un nouveau membre rejoint le serveur."""
        welcome_channel = discord.utils.get(member.guild.text_channels, name=self.config["welcome_channel_name"])
        rules_channel_id = self.config.get("rules_channel_id")
        rules_channel_mention = f"<#{rules_channel_id}>" if rules_channel_id else "le salon des règles"

        if welcome_channel:
            try:
                await welcome_channel.send(
                    f"🎉 Bienvenue {member.mention} sur le serveur **{member.guild.name}** !\n"
                    f"👉 N'oublie pas de consulter {rules_channel_mention} pour connaître les règles du serveur.\n"
                    "Amuse-toi bien et profite de ton séjour ici ! 🚀"
                )
            except Exception as e:
                print(f"Erreur lors de l'envoi du message de bienvenue : {e}")

    @commands.hybrid_command(name="set_rules_channel", help="Définit le salon des règles.")
    @commands.has_permissions(administrator=True)
    async def set_rules_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Définit le salon des règles."""
        self.config["rules_channel_id"] = channel.id
        self.save_config(self.config)
        await ctx.send(f"✅ Le salon des règles a été configuré sur {channel.mention}.")

    @commands.hybrid_command(name="set_welcome_channel", help="Définit le nom du salon de bienvenue.")
    @commands.has_permissions(administrator=True)
    async def set_welcome_channel(self, ctx: commands.Context, channel_name: str):
        """Définit le nom du salon de bienvenue."""
        self.config["welcome_channel_name"] = channel_name
        self.save_config(self.config)
        await ctx.send(f"✅ Le salon de bienvenue a été configuré sur `{channel_name}`.")

    @commands.hybrid_command(name="show_welcome_config", help="Affiche la configuration actuelle des messages de bienvenue.")
    async def show_welcome_config(self, ctx: commands.Context):
        """Affiche la configuration actuelle."""
        rules_channel_id = self.config.get("rules_channel_id")
        welcome_channel_name = self.config.get("welcome_channel_name")
        rules_channel_mention = f"<#{rules_channel_id}>" if rules_channel_id else "Non défini"
        await ctx.send(
            f"📜 **Configuration actuelle des messages de bienvenue :**\n"
            f"- Salon de bienvenue : `{welcome_channel_name}`\n"
            f"- Salon des règles : {rules_channel_mention}"
        )


async def setup(bot: commands.Bot):
    """Ajoute la cog au bot."""
    await bot.add_cog(Welcome(bot))
