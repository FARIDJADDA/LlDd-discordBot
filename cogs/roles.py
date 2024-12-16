import discord
import json
import os
from discord.ext import commands
from utils.logger import logger


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roles_file = "default_roles.json"
        self.default_roles = self.load_roles()

    def load_roles(self):
        """Charge les rôles par défaut depuis un fichier JSON."""
        try:
            if os.path.exists(self.roles_file):
                with open(self.roles_file, "r") as file:
                    return json.load(file)
            else:
                logger.info("Fichier 'default_roles.json' introuvable. Une liste vide sera utilisée.")
                return []
        except Exception as e:
            logger.error(f"Erreur lors du chargement des rôles par défaut : {e}")
            return []

    def save_roles(self):
        """Sauvegarde les rôles par défaut dans un fichier JSON."""
        try:
            with open(self.roles_file, "w") as file:
                json.dump(self.default_roles, file, indent=4)
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des rôles par défaut : {e}")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Attribue automatiquement les rôles par défaut aux nouveaux membres."""
        guild = member.guild
        roles_to_add = [discord.utils.get(guild.roles, name=role_name) for role_name in self.default_roles]
        roles_to_add = [role for role in roles_to_add if role is not None]

        if not roles_to_add:
            logger.warning(f"Aucun rôle valide trouvé pour {member.name} dans {guild.name}.")
            return

        try:
            await member.add_roles(*roles_to_add, reason="Attribution automatique à l'arrivée")
            logger.info(f"Rôles ajoutés à {member.name} dans {guild.name} : {', '.join([role.name for role in roles_to_add])}")
            await member.send(
                f"🎉 Bienvenue sur **{guild.name}** ! Tu as reçu les rôles : {', '.join([role.name for role in roles_to_add])}."
            )
        except Exception as e:
            logger.error(f"Erreur lors de l'attribution des rôles pour {member.name} : {e}")

    @commands.hybrid_command(name="set_default_roles", description="Définit les rôles par défaut pour les nouveaux membres.")
    async def set_default_roles(self, ctx: commands.Context, *, roles: str):
        """Définit les rôles par défaut via une commande hybride."""
        role_names = [role.strip() for role in roles.split(",")]
        self.default_roles = role_names
        self.save_roles()
        await ctx.send(f"✅ Rôles par défaut mis à jour : {', '.join(role_names)}.")
        logger.info(f"Rôles par défaut mis à jour par {ctx.author}: {', '.join(role_names)}.")

    @commands.hybrid_command(name="show_default_roles", description="Affiche les rôles par défaut actuels.")
    async def show_default_roles(self, ctx: commands.Context):
        """Affiche les rôles par défaut via une commande hybride."""
        if self.default_roles:
            await ctx.send(f"📜 Rôles par défaut actuels : {', '.join(self.default_roles)}.")
        else:
            await ctx.send("❌ Aucun rôle par défaut défini.")
        logger.info(f"Rôles par défaut affichés pour {ctx.author}.")

    @set_default_roles.error
    @show_default_roles.error
    async def handle_command_errors(self, ctx: commands.Context, error):
        """Gestion des erreurs pour les commandes hybrides."""
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Veuillez fournir tous les arguments requis.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Argument invalide. Veuillez vérifier votre saisie.")
        else:
            await ctx.send("❌ Une erreur inattendue s'est produite.")
            logger.error(f"Erreur dans une commande hybride : {error}")


async def setup(bot: commands.Bot):
    """Ajoute la cog au bot."""
    print("🔧 Tentative d'ajout du cog 'Roles'")
    await bot.add_cog(Roles(bot))
    print("✅ Cog 'Roles' ajouté avec succès")

