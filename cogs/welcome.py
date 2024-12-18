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
                    return {"rules_channel_id": None, "welcome_channel_name": "welcome"}
        else:
            default_config = {"rules_channel_id": None, "welcome_channel_name": "welcome"}
            self.save_config(default_config)
            return default_config

    def save_config(self, config):
        """Sauvegarde la configuration dans un fichier JSON."""
        with open(self.config_file, "w") as file:
            json.dump(config, file, indent=4)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Envoie un message de bienvenue lorsqu'un nouveau membre rejoint le serveur."""
        guild = member.guild
        welcome_channel_name = self.config.get("welcome_channel_name", "welcome")

        # Récupérer le salon de bienvenue
        welcome_channel = None
        try:
            if welcome_channel_name.isdigit():
                welcome_channel = guild.get_channel(int(welcome_channel_name))
            else:
                welcome_channel = discord.utils.get(guild.text_channels, name=welcome_channel_name)
        except Exception as e:
            print(f"⚠️ Erreur lors de la recherche du salon : {e}")

        if not welcome_channel:
            print(f"⚠️ Salon de bienvenue '{welcome_channel_name}' introuvable dans '{guild.name}'.")
            return

        # Récupération du salon des règles
        rules_channel_id = self.config.get("rules_channel_id")
        rules_channel_mention = f"<#{rules_channel_id}>" if rules_channel_id else "le salon des règles"

        # Chemin des images locales
        banner_path = "assets/avatar_lldd_bot3.png"
        if not os.path.exists(banner_path):
            print(f"⚠️ L'image '{banner_path}' est introuvable.")
            return

        # Avatar du membre
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url

        try:
            # Préparation de l'image
            file = discord.File(banner_path, filename="avatar_lldd_bot3.png")

            # Configuration de l'embed stylisé
            embed = discord.Embed(
                title=f"**⛩️ ❟❛❟ Salut soldat ❟❛❟ ⛩️**",
                description=(
                    f"⚔️ {member.mention} Bienvenue  sur **{guild.name}**.\n\n"
                    f"🪖 *N'oublie pas de consulter {rules_channel_mention} !*\n\n"
                    f"🫡 Profite bien de ton séjour ici, jeune padawan ."
                ),
                color=discord.Color.dark_purple(),
            )

            # Ajout des visuels
            embed.set_thumbnail(url=avatar_url)
            embed.set_image(url="attachment://avatar_lldd_bot3.png")
            embed.set_footer(
                text=f"Bienvenue dans {guild.name} !",
                icon_url=guild.icon.url if guild.icon else None
            )

            # Envoi du message de bienvenue
            await welcome_channel.send(file=file, embed=embed)
            print(f"✅ Message de bienvenue envoyé dans '{welcome_channel.name}' pour {member.name}.")

        except Exception as e:
            print(f"❌ Erreur lors de l'envoi du message de bienvenue : {e}")

    @commands.hybrid_command(name="set_rules_channel", help="Définit le salon des règles.")
    @commands.has_permissions(administrator=True)
    async def set_rules_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Définit le salon des règles."""
        self.config["rules_channel_id"] = str(channel.id)
        self.save_config(self.config)
        await ctx.send(embed=discord.Embed(
            title="✅ Configuration mise à jour",
            description=f"Le salon des règles a été configuré sur {channel.mention}.",
            color=discord.Color.green()
        ))

    @commands.hybrid_command(name="set_welcome_channel", help="Définit le nom ou l'ID du salon de bienvenue.")
    @commands.has_permissions(administrator=True)
    async def set_welcome_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Définit le nom ou l'ID du salon de bienvenue."""
        self.config["welcome_channel_name"] = str(channel.id)
        self.save_config(self.config)
        await ctx.send(embed=discord.Embed(
            title="✅ Configuration mise à jour",
            description=f"Le salon de bienvenue a été configuré sur {channel.mention}.",
            color=discord.Color.green()
        ))

    @commands.hybrid_command(name="show_welcome_config", help="Affiche la configuration actuelle des messages de bienvenue.")
    async def show_welcome_config(self, ctx: commands.Context):
        """Affiche la configuration actuelle."""
        rules_channel_id = self.config.get("rules_channel_id")
        welcome_channel_name = self.config.get("welcome_channel_name")

        rules_channel_mention = f"<#{rules_channel_id}>" if rules_channel_id else "Non défini"
        welcome_channel_mention = f"<#{welcome_channel_name}>" if welcome_channel_name else "Non défini"

        await ctx.send(embed=discord.Embed(
            title="📜 Configuration actuelle des messages de bienvenue",
            description=(
                f"- **Salon de bienvenue** : {welcome_channel_mention}\n"
                f"- **Salon des règles** : {rules_channel_mention}"
            ),
            color=discord.Color.dark_purple()
        ))


async def setup(bot: commands.Bot):
    """Ajoute la cog au bot."""
    await bot.add_cog(Welcome(bot))
