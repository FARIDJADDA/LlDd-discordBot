import discord
import json
import os
from discord.ext import commands
from utils.logger import logger

# Chemin vers le fichier JSON dans le dossier 'data'
CONFIG_DIR = "data"
WARNINGS_FILE = os.path.join(CONFIG_DIR, "warnings.json")


class Warnings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warnings = self.load_warnings()
        self.max_warnings = 3

    def load_warnings(self):
        """Charge les avertissements depuis un fichier JSON dans 'data'. Crée le fichier s'il est manquant."""
        # Crée le dossier 'data' s'il n'existe pas
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
            logger.info(f"📁 Dossier '{CONFIG_DIR}' créé.")

        # Crée le fichier JSON par défaut s'il n'existe pas
        if not os.path.exists(WARNINGS_FILE):
            logger.warning(f"⚠️ Fichier 'warnings.json' manquant. Création avec des valeurs par défaut.")
            with open(WARNINGS_FILE, "w") as file:
                json.dump({}, file, indent=4)
            return {}

        # Charge les avertissements existants
        try:
            with open(WARNINGS_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erreur lors de la lecture de '{WARNINGS_FILE}' : {e}")
            return {}

    def save_warnings(self):
        """Sauvegarde les avertissements dans un fichier JSON."""
        try:
            with open(WARNINGS_FILE, "w") as file:
                json.dump(self.warnings, file, indent=4)
            logger.info(f"✅ Avertissements sauvegardés dans '{WARNINGS_FILE}'.")
        except Exception as e:
            logger.error(f"❌ Erreur lors de la sauvegarde dans '{WARNINGS_FILE}' : {e}")

    @commands.hybrid_command(name="warn", help="Avertit un utilisateur.")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx: commands.Context, member: discord.Member, *, reason: str = "Aucune raison spécifiée."):
        """Avertit un utilisateur via une commande hybride."""
        if str(member.id) not in self.warnings:
            self.warnings[str(member.id)] = []
        self.warnings[str(member.id)].append(reason)
        self.save_warnings()

        total_warnings = len(self.warnings[str(member.id)])
        embed = discord.Embed(
            title="⚠️ Avertissement",
            description=(
                f"**{member.mention}** a reçu un avertissement.\n"
                f"📝 **Raison** : {reason}\n"
                f"⚠️ **Total d'avertissements** : {total_warnings}/{self.max_warnings}"
            ),
            color=discord.Color.dark_red(),
        )
        await ctx.send(embed=embed)

        # Vérification du seuil maximum
        if total_warnings >= self.max_warnings:
            await self.apply_sanction(ctx, member)

    @commands.hybrid_command(name="warnings", help="Affiche les avertissements d'un utilisateur.")
    async def show_warnings(self, ctx: commands.Context, member: discord.Member):
        """Affiche les avertissements d'un utilisateur."""
        warnings_list = self.warnings.get(str(member.id), [])
        if warnings_list:
            warning_str = "\n".join([f"{i + 1}. {reason}" for i, reason in enumerate(warnings_list)])
            embed = discord.Embed(
                title=f"📋 Avertissements pour {member.name}",
                description=warning_str,
                color=discord.Color.dark_purple(),
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=discord.Embed(
                title="✅ Aucun avertissement",
                description=f"**{member.mention}** n'a actuellement aucun avertissement.",
                color=discord.Color.green()
            ))

    @commands.hybrid_command(name="clear_warnings", help="Efface les avertissements d'un utilisateur.")
    @commands.has_permissions(manage_messages=True)
    async def clear_warnings(self, ctx: commands.Context, member: discord.Member):
        """Efface tous les avertissements d'un utilisateur."""
        if str(member.id) in self.warnings:
            del self.warnings[str(member.id)]
            self.save_warnings()
            await ctx.send(embed=discord.Embed(
                title="🧹 Avertissements effacés",
                description=f"✅ Tous les avertissements pour **{member.mention}** ont été supprimés.",
                color=discord.Color.green(),
            ))
        else:
            await ctx.send(embed=discord.Embed(
                title="✅ Aucun avertissement",
                description=f"**{member.mention}** n'a aucun avertissement à supprimer.",
                color=discord.Color.green()
            ))

    @commands.hybrid_command(name="set_max_warnings", help="Définit le nombre maximum d'avertissements avant sanction.")
    @commands.has_permissions(administrator=True)
    async def set_max_warnings(self, ctx: commands.Context, number: int):
        """Définit le nombre maximum d'avertissements avant sanction."""
        if number > 0:
            self.max_warnings = number
            await ctx.send(embed=discord.Embed(
                title="✅ Configuration mise à jour",
                description=f"⚠️ Le nombre maximum d'avertissements a été fixé à **{number}**.",
                color=discord.Color.dark_purple()
            ))
        else:
            await ctx.send(embed=discord.Embed(
                title="❌ Erreur",
                description="Le nombre maximum d'avertissements doit être supérieur à 0.",
                color=discord.Color.red()
            ))

    async def apply_sanction(self, ctx: commands.Context, member: discord.Member):
        """Applique une sanction si le seuil maximum d'avertissements est atteint."""
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False)

        await member.add_roles(muted_role, reason="Trop d'avertissements")
        await ctx.send(embed=discord.Embed(
            title="🔇 Sanction appliquée",
            description=f"**{member.mention}** a été mute automatiquement après {self.max_warnings} avertissements.",
            color=discord.Color.red(),
        ))


async def setup(bot: commands.Bot):
    """Ajoute la cog au bot."""
    await bot.add_cog(Warnings(bot))
    logger.info("✅ Cog Warnings ajouté avec succès.")
