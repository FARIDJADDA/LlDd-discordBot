import discord
import json
import os
from discord.ext import commands
from utils.logger import logger


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roles_file = "data/default_roles.json"  # Nouveau chemin
        self.default_roles = self.load_roles()

    def load_roles(self):
        """Charge les rôles par défaut depuis un fichier JSON."""
        os.makedirs("data", exist_ok=True)  # Crée le dossier data s'il n'existe pas
        if not os.path.exists(self.roles_file):
            logger.info(f"Fichier '{self.roles_file}' introuvable. Création avec une liste vide par défaut.")
            with open(self.roles_file, "w") as file:
                json.dump([], file, indent=4)  # Initialisation avec une liste vide
            return []

        try:
            with open(self.roles_file, "r") as file:
                return json.load(file)
        except Exception as e:
            logger.error(f"Erreur lors du chargement des rôles par défaut : {e}")
            return []

    def save_roles(self):
        """Sauvegarde les rôles par défaut dans un fichier JSON."""
        try:
            with open(self.roles_file, "w") as file:
                json.dump(self.default_roles, file, indent=4)
            logger.info(f"Rôles par défaut sauvegardés dans '{self.roles_file}'.")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des rôles par défaut : {e}")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Attribue automatiquement les rôles par défaut aux nouveaux membres."""
        guild = member.guild

        # Vérifie que des rôles par défaut sont configurés
        if not self.default_roles:
            logger.warning("Aucun rôle par défaut configuré.")
            return

        # Recherche des rôles existants sur le serveur
        roles_to_add = []
        for role_name in self.default_roles:
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                roles_to_add.append(role)
            else:
                logger.warning(f"Le rôle '{role_name}' est introuvable sur le serveur '{guild.name}'.")

        # Vérifie que des rôles valides existent
        if not roles_to_add:
            logger.warning(f"Aucun rôle valide trouvé pour attribuer à {member.name} dans {guild.name}.")
            return

        # Attribution des rôles
        try:
            await member.add_roles(*roles_to_add, reason="Attribution automatique à l'arrivée")
            logger.info(
                f"Rôles ajoutés à {member.name} dans {guild.name} : {', '.join([role.name for role in roles_to_add])}.")

            # Confirmation en DM au membre
            embed = discord.Embed(
                title="🎉 Bienvenue sur le serveur !",
                description=f"Salut {member.mention} !\nTu as reçu les rôles suivants :\n**{', '.join([role.name for role in roles_to_add])}**",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url="attachment://roles_icon.png")
            await member.send(embed=embed, file=discord.File("assets/roles_icon.png", filename="roles_icon.png"))

        except discord.Forbidden:
            logger.error(f"Permissions insuffisantes pour attribuer des rôles à {member.name}.")
        except Exception as e:
            logger.error(f"Erreur inattendue lors de l'attribution des rôles à {member.name} : {e}")

    @commands.hybrid_command(name="set_default_roles", description="Définit les rôles par défaut pour les nouveaux membres.")
    @commands.has_permissions(administrator=True)
    async def set_default_roles(self, ctx: commands.Context, *, roles: str):
        """Définit les rôles par défaut via une commande hybride."""
        role_names = [role.strip() for role in roles.split(",")]
        self.default_roles = role_names
        self.save_roles()

        embed = discord.Embed(
            title="✅ Rôles par défaut mis à jour",
            description=f"Les rôles suivants seront attribués automatiquement :\n**{', '.join(role_names)}**",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        logger.info(f"Rôles par défaut mis à jour par {ctx.author}: {', '.join(role_names)}.")

    @commands.hybrid_command(name="show_default_roles", description="Affiche les rôles par défaut actuels.")
    async def show_default_roles(self, ctx: commands.Context):
        """Affiche les rôles par défaut via une commande hybride."""
        if self.default_roles:
            embed = discord.Embed(
                title="📋 Rôles par défaut",
                description=f"Les rôles suivants seront attribués automatiquement :\n**{', '.join(self.default_roles)}**",
                color=discord.Color.dark_green()
            )
        else:
            embed = discord.Embed(
                title="❌ Aucun rôle par défaut défini",
                description="Aucun rôle n'est configuré pour être attribué automatiquement.",
                color=discord.Color.red()
            )
        await ctx.send(embed=embed)
        logger.info(f"Rôles par défaut affichés pour {ctx.author}.")


async def setup(bot: commands.Bot):
    """Ajoute la cog au bot."""
    await bot.add_cog(Roles(bot))
