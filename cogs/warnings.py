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
        self.max_warnings = 3

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
        embed = discord.Embed(
            title="⚠️ Avertissement",
            description=(
                f"**{member.mention}** a reçu un avertissement.\n"
                f"📝 **Raison** : {reason}\n"
                f"⚠️ **Total d'avertissements** : {total_warnings}/{self.max_warnings}"
            ),
            color=discord.Color.dark_red(),
        )
        embed.set_thumbnail(url="attachment://demon_warning_icon.png")
        embed.set_footer(text=f"Averti par {ctx.author.name}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

        # Vérification du seuil maximum
        if total_warnings >= self.max_warnings:
            await self.apply_sanction(ctx, member)

    @commands.hybrid_command(name="warnings", help="Affiche les avertissements d'un utilisateur.")
    async def show_warnings(self, ctx: commands.Context, member: discord.Member):
        """Affiche les avertissements d'un utilisateur via une commande hybride."""
        warnings_list = self.warnings.get(str(member.id), [])
        if warnings_list:
            warning_str = "\n".join([f"{i + 1}. {reason}" for i, reason in enumerate(warnings_list)])
            embed = discord.Embed(
                title=f"📋 Avertissements pour {member.name}",
                description=warning_str,
                color=discord.Color.dark_purple(),
            )
            embed.set_footer(text=f"Demandé par {ctx.author.name}", icon_url=ctx.author.avatar.url)
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
        """Efface tous les avertissements d'un utilisateur via une commande hybride."""
        if str(member.id) in self.warnings:
            del self.warnings[str(member.id)]
            self.save_warnings()
            embed = discord.Embed(
                title="🧹 Avertissements effacés",
                description=f"✅ Tous les avertissements pour **{member.mention}** ont été supprimés.",
                color=discord.Color.green(),
            )
            await ctx.send(embed=embed)
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
