from discord.ext import commands
import discord
import json
import os
from utils.logger import logger  # Utilisation du logger global


class Warnings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warnings = self.load_warnings()
        self.max_warnings = 3  # Nombre maximum d'avertissements avant sanction

    def load_warnings(self):
        """Charger les avertissements depuis un fichier JSON"""
        try:
            with open("warnings.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            logger.warning("Fichier 'warnings.json' introuvable. Création d'une nouvelle base.")
            return {}
        except Exception as e:
            logger.error(f"Erreur lors du chargement des avertissements : {e}")
            return {}

    def save_warnings(self):
        """Sauvegarder les avertissements dans un fichier JSON"""
        try:
            with open("warnings.json", "w") as file:
                json.dump(self.warnings, file, indent=4)
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des avertissements : {e}")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason=None):
        """Avertir un utilisateur"""
        if str(member.id) not in self.warnings:
            self.warnings[str(member.id)] = []
        self.warnings[str(member.id)].append(reason or "Aucune raison spécifiée.")
        self.save_warnings()

        total_warnings = len(self.warnings[str(member.id)])
        await ctx.send(f"⚠️ {member.mention} a été averti. Total d'avertissements : {total_warnings}")
        logger.info(f"Avertissement donné à {member} par {ctx.author}. Raison : {reason or 'Non spécifiée'}.")

        # Log dans le canal 'logs'
        log_channel = discord.utils.get(ctx.guild.channels, name="logs")
        if log_channel:
            embed = discord.Embed(
                title="Avertissement",
                description=f"**Utilisateur** : {member.mention}\n**Par** : {ctx.author.mention}\n"
                            f"**Raison** : {reason or 'Non spécifiée'}\n**Total** : {total_warnings} avertissement(s).",
                color=discord.Color.orange(),
            )
            await log_channel.send(embed=embed)

        # Vérifie si l'utilisateur atteint le seuil maximum d'avertissements
        if total_warnings >= self.max_warnings:
            await self.apply_sanction(ctx, member)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warnings(self, ctx, member: discord.Member):
        """Afficher les avertissements pour un utilisateur"""
        if str(member.id) in self.warnings and self.warnings[str(member.id)]:
            warning_list = "\n".join(
                [f"{i + 1}. {reason}" for i, reason in enumerate(self.warnings[str(member.id)])]
            )
            await ctx.send(f"⚠️ Avertissements pour {member.mention} :\n{warning_list}")
        else:
            await ctx.send(f"✅ {member.mention} n'a aucun avertissement.")
        logger.info(f"Affichage des avertissements pour {member} par {ctx.author}.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear_warnings(self, ctx, member: discord.Member):
        """Supprimer tous les avertissements pour un utilisateur"""
        if str(member.id) in self.warnings:
            del self.warnings[str(member.id)]
            self.save_warnings()
            await ctx.send(f"✅ Tous les avertissements pour {member.mention} ont été supprimés.")
            logger.info(f"Avertissements pour {member} supprimés par {ctx.author}.")
        else:
            await ctx.send(f"✅ {member.mention} n'a aucun avertissement à supprimer.")

    async def apply_sanction(self, ctx, member):
        """Appliquer une sanction si le seuil maximum d'avertissements est atteint"""
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
            await ctx.send(f"🔇 {member.mention} a été mute automatiquement après {self.max_warnings} avertissements.")
            logger.info(f"Sanction appliquée : {member} mute après {self.max_warnings} avertissements.")
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du rôle 'Muted' à {member} : {e}")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def set_max_warnings(self, ctx, number: int):
        """Définir le nombre maximum d'avertissements avant sanction"""
        if number > 0:
            self.max_warnings = number
            await ctx.send(f"✅ Nombre maximum d'avertissements fixé à {number}.")
            logger.info(f"Nombre maximum d'avertissements modifié à {number} par {ctx.author}.")
        else:
            await ctx.send("❌ Le nombre maximum d'avertissements doit être supérieur à 0.")
            logger.warning(f"Tentative de définir un nombre maximum invalide par {ctx.author}.")


async def setup(bot):
    await bot.add_cog(Warnings(bot))