import discord
from discord.ext import commands
import json
import os

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roles_file = "default_roles.json"
        self.default_roles = self.load_roles()

    def load_roles(self):
        """Charger les rôles par défaut depuis un fichier JSON"""
        if os.path.exists(self.roles_file):
            with open(self.roles_file, "r") as file:
                return json.load(file)
        else:
            return []

    def save_roles(self):
        """Sauvegarder les rôles par défaut dans un fichier JSON"""
        with open(self.roles_file, "w") as file:
            json.dump(self.default_roles, file, indent=4)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Attribution automatique de rôles à l'arrivée d'un membre"""
        guild = member.guild
        roles_to_add = [discord.utils.get(guild.roles, name=role_name) for role_name in self.default_roles]
        roles_to_add = [role for role in roles_to_add if role is not None]

        if not roles_to_add:
            print(f"Aucun rôle valide trouvé pour {member.name}.")
            return

        try:
            await member.add_roles(*roles_to_add, reason="Attribution automatique à l'arrivée")
            await member.send(f"🎉 Bienvenue sur **{guild.name}** ! Tu as reçu les rôles : {', '.join([role.name for role in roles_to_add])}.")
            print(f"Rôles ajoutés à {member.name} : {', '.join([role.name for role in roles_to_add])}")
        except Exception as e:
            print(f"Erreur lors de l'attribution des rôles pour {member.name} : {e}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_default_roles(self, ctx, *, roles):
        """Définir les rôles par défaut pour les nouveaux membres"""
        role_names = [role.strip() for role in roles.split(",")]
        self.default_roles = role_names
        self.save_roles()
        await ctx.send(f"✅ Rôles par défaut mis à jour : {', '.join(role_names)}.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def show_default_roles(self, ctx):
        """Afficher les rôles par défaut actuels"""
        if self.default_roles:
            await ctx.send(f"📜 Rôles par défaut actuels : {', '.join(self.default_roles)}.")
        else:
            await ctx.send("❌ Aucun rôle par défaut défini.")

async def setup(bot):
    await bot.add_cog(Roles(bot))
