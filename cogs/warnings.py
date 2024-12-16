import discord
import json
import os
from discord.ext import commands
from utils.logger import logger


class Warnings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "warnings.json"
        self.warnings = self.load_warnings()
        self.max_warnings = 3  # Nombre maximum d'avertissements avant sanction

    def load_warnings(self):
        """Charge les avertissements depuis un fichier JSON."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as file:
                    return json.load(file)
            else:
                logger.info("Fichier 'warnings.json' introuvable. Une structure vide sera utilisée.")
                return {}
        except Exception as e:
            logger.error(f"Erreur lors du chargement des avertissements : {e}")
            return {}

    def save_warnings(self):
        """Sauvegarde les avertissements dans un fichier JSON."""
        try:
            with open(self.config_file, "w") as file:
                json.dump(self.warnings, file, indent=4)
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des avertissements : {e}")

    @commands.hybrid_command(name="warn", help="Avertit un utilisateur.")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx: commands.Context, member: discord.Member, *, reason: str = "Aucune raison spécifiée."):
        """Avertit un utilisateur via une commande hybride."""
        if str(member.id) not in self.warnings:
            self.warnings[str(member.id)] = []
        self.warnings[str(member.id)].append(reason)
        self.save_warnings()

        total_warnings = len(self.warnings[str(member.id)])
        await ctx.send(f"⚠️ {member.mention} a été averti. Total d'avertissements : {total_warnings}.")
        logger.info(f"Avertissement donné à {member} par {ctx.author}. Raison : {reason}.")

        # Vérification du seuil maximum
        if total_warnings >= self.max_warnings:
            await self.apply_sanction(ctx, member)

    @commands.hybrid_command(name="warnings", help="Affiche les avertissements d'un utilisateur.")
    async def show_warnings(self, ctx: commands.Context, member: discord.Member):
        """Affiche les avertissements d'un utilisateur via une commande hybride."""
        if str(member.id) in self.warnings and self.warnings[str(member.id)]:
            warning_list = "\n".join(
                [f"{i + 1}. {reason}" for i, reason in enumerate(self.warnings[str(member.id)])]
            )
            await ctx.send(f"⚠️ Avertissements pour {member.mention} :\n{warning_list}")
        else:
            await ctx.send(f"✅ {member.mention} n'a aucun avertissement.")
        logger.info(f"Avertissements affichés pour {member} par {ctx.author}.")

    @commands.hybrid_command(name="clear_warnings", help="Efface les avertissements d'un utilisateur.")
    @commands.has_permissions(manage_messages=True)
    async def clear_warnings(self, ctx: commands.Context, member: discord.Member):
        """Efface tous les avertissements d'un utilisateur via une commande hybride."""
        if str(member.id) in self.warnings:
            del self.warnings[str(member.id)]
            self.save_warnings()
            await ctx.send(f"✅ Tous les avertissements pour {member.mention} ont été supprimés.")
            logger.info(f"Avertissements pour {member} effacés par {ctx.author}.")
        else:
            await ctx.send(f"✅ {member.mention} n'a aucun avertissement à supprimer.")

    @commands.hybrid_command(name="set_max_warnings", help="Définit le nombre maximum d'avertissements avant sanction.")
    @commands.has_permissions(administrator=True)
    async def set_max_warnings(self, ctx: commands.Context, number: int):
        """Définit le nombre maximum d'avertissements avant sanction."""
        if number > 0:
            self.max_warnings = number
            await ctx.send(f"✅ Nombre maximum d'avertissements fixé à {number}.")
            logger.info(f"Nombre maximum d'avertissements modifié à {number} par {ctx.author}.")
        else:
            await ctx.send("❌ Le nombre maximum d'avertissements doit être supérieur à 0.")
            logger.warning(f"Tentative de définir un nombre maximum invalide par {ctx.author}.")

    async def apply_sanction(self, ctx: commands.Context, member: discord.Member):
        """Applique une sanction si le seuil maximum d'avertissements est atteint."""
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            try:
                muted_role = await ctx.guild.create_role(name="Muted")
                for channel in ctx.guild.channels:
                    await channel.set_permissions(muted_role, send_messages=False)
                logger.info(f"Rôle 'Muted' créé dans le serveur {ctx.guild.name}.")
            except Exception as e:
                logger.error(f"Erreur lors de la création du rôle 'Muted' : {e}")
                return

        try:
            await member.add_roles(muted_role, reason="Trop d'avertissements")
            await ctx.send(
                f"🔇 {member.mention} a été mute automatiquement après {self.max_warnings} avertissements."
            )
            logger.info(f"Sanction appliquée : {member} mute après {self.max_warnings} avertissements.")
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du rôle 'Muted' à {member} : {e}")


async def setup(bot: commands.Bot):
    """Ajoute la cog au bot."""
    await bot.add_cog(Warnings(bot))
