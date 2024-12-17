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

        # Essaye de trouver le salon par ID (si c'est un ID)
        welcome_channel = None
        try:
            # Si le nom est un ID numérique valide, recherche par ID
            if welcome_channel_name.isdigit():
                welcome_channel = guild.get_channel(int(welcome_channel_name))
            # Sinon, recherche par nom
            else:
                welcome_channel = discord.utils.get(guild.text_channels, name=welcome_channel_name)
        except ValueError:
            print(f"⚠️ Nom ou ID invalide : {welcome_channel_name}")

        # Vérifie si le salon est trouvé
        if not welcome_channel:
            print(f"⚠️ Salon de bienvenue '{welcome_channel_name}' introuvable dans le serveur '{guild.name}'.")
            return

        # Vérifie si le bot a la permission d'envoyer des messages dans le salon
        if not welcome_channel.permissions_for(guild.me).send_messages:
            print(f"⚠️ Le bot n'a pas la permission d'envoyer des messages dans '{welcome_channel_name}'.")
            return

        # Chemin de l'image locale
        image_path = "assets/lldd_bot_dsgn.jpg"
        if not os.path.exists(image_path):
            print(f"⚠️ L'image '{image_path}' est introuvable.")
            return

        try:
            # Préparation de l'image locale
            file = discord.File(image_path, filename="lldd_bot_dsgn.jpg")

            # Récupération du salon des règles configuré
            rules_channel_id = self.config.get("rules_channel_id")
            rules_channel_mention = f"<#{rules_channel_id}>" if rules_channel_id else "le salon des règles"

            # Création de l'embed de bienvenue
            embed = discord.Embed(
                title="🪖 Bienvenue sur le serveur jeune padawane 🫡!",
                description=(
                    f"Salut {member.mention} !\n"
                    f"Nous sommes ravis de t'accueillir sur **{guild.name}**.\n\n"
                    f"👉 N'oublie pas de consulter {rules_channel_mention} pour connaître les règles du serveur !\n\n"
                    "Amuse-toi bien et profite de ton séjour ici ! 🚀"
                ),
                color=discord.Color.green(),
            )
            embed.set_thumbnail(url="attachment://lldd_bot_dsgn.jpg")
            embed.set_footer(text=f"Bienvenue dans {guild.name} !", icon_url=guild.icon.url if guild.icon else None)

            # Envoie le message de bienvenue dans le salon configuré
            await welcome_channel.send(file=file, embed=embed)
            print(f"✅ Message de bienvenue envoyé dans '{welcome_channel.name}' pour {member.name}.")

        except Exception as e:
            print(f"❌ Erreur lors de l'envoi du message de bienvenue : {e}")

    @commands.hybrid_command(name="set_rules_channel", help="Définit le salon des règles.")
    @commands.has_permissions(administrator=True)
    async def set_rules_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Définit le salon des règles."""
        self.config["rules_channel_id"] = channel.id
        self.save_config(self.config)
        await ctx.send(embed=discord.Embed(
            title="✅ Configuration mise à jour",
            description=f"Le salon des règles a été configuré sur {channel.mention}.",
            color=discord.Color.green()
        ))

    @commands.hybrid_command(name="set_welcome_channel", help="Définit le nom du salon de bienvenue.")
    @commands.has_permissions(administrator=True)
    async def set_welcome_channel(self, ctx: commands.Context, channel_name: str):
        """Définit le nom du salon de bienvenue."""
        self.config["welcome_channel_name"] = channel_name
        self.save_config(self.config)
        await ctx.send(embed=discord.Embed(
            title="✅ Configuration mise à jour",
            description=f"Le salon de bienvenue a été configuré sur `{channel_name}`.",
            color=discord.Color.green()
        ))

    @commands.hybrid_command(name="show_welcome_config", help="Affiche la configuration actuelle des messages de bienvenue.")
    async def show_welcome_config(self, ctx: commands.Context):
        """Affiche la configuration actuelle."""
        rules_channel_id = self.config.get("rules_channel_id")
        welcome_channel_name = self.config.get("welcome_channel_name")
        rules_channel_mention = f"<#{rules_channel_id}>" if rules_channel_id else "Non défini"
        await ctx.send(embed=discord.Embed(
            title="📜 Configuration actuelle des messages de bienvenue",
            description=(
                f"- **Salon de bienvenue** : `{welcome_channel_name}`\n"
                f"- **Salon des règles** : {rules_channel_mention}"
            ),
            color=discord.Color.dark_purple()
        ))


async def setup(bot: commands.Bot):
    """Ajoute la cog au bot."""
    await bot.add_cog(Welcome(bot))
