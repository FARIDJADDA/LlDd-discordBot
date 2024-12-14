from discord.ext import commands
import discord
import json
import os


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "welcome_config.json"
        self.config = self.load_config()

    def load_config(self):
        """Charge la configuration du salon des règles depuis un fichier JSON"""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as file:
                return json.load(file)
        else:
            # Configuration par défaut
            default_config = {
                "rules_channel_id": None,  # ID du salon des règles par défaut
                "welcome_channel_name": "welcome",  # Nom du salon d'accueil
            }
            self.save_config(default_config)
            return default_config

    def save_config(self, config):
        """Sauvegarde la configuration dans un fichier JSON"""
        with open(self.config_file, "w") as file:
            json.dump(config, file, indent=4)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Message de bienvenue pour les nouveaux membres"""
        # Recherche du canal d'accueil
        welcome_channel = discord.utils.get(member.guild.channels, name=self.config["welcome_channel_name"])

        # Recherche du salon des règles
        rules_channel_id = self.config["rules_channel_id"]
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

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_rules_channel(self, ctx, channel: discord.TextChannel):
        """Définit le salon des règles"""
        self.config["rules_channel_id"] = channel.id
        self.save_config(self.config)
        await ctx.send(f"✅ Le salon des règles a été configuré sur {channel.mention}.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_welcome_channel(self, ctx, channel_name: str):
        """Définit le nom du salon de bienvenue"""
        self.config["welcome_channel_name"] = channel_name
        self.save_config(self.config)
        await ctx.send(f"✅ Le salon de bienvenue a été configuré sur `{channel_name}`.")


async def setup(bot):
    print("Chargement du cog Welcome")
    await bot.add_cog(Welcome(bot))
