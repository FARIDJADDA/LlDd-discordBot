import discord
from discord.ext import commands
from utils.logger import logger


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ban", description="Bannit un utilisateur avec une raison facultative.")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = "Aucune raison spécifiée."):
        """Bannit un utilisateur avec une raison."""
        try:
            await member.ban(reason=reason)
            embed = discord.Embed(
                title="🔨 Utilisateur banni",
                description=f"✅ **{member}** a été banni.\n📝 Raison : {reason}",
                color=discord.Color.dark_red()
            )
            embed.set_footer(text=f"Action effectuée par {ctx.author.name}", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
            logger.info(f"{member} a été banni par {ctx.author} pour : {reason}")
        except Exception as e:
            await ctx.send(embed=discord.Embed(
                title="❌ Erreur",
                description=f"Impossible de bannir {member}.",
                color=discord.Color.red()
            ))
            logger.error(f"Erreur lors du bannissement de {member} : {e}")

    @commands.hybrid_command(name="kick", description="Expulse un utilisateur avec une raison facultative.")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str = "Aucune raison spécifiée."):
        """Expulse un utilisateur avec une raison."""
        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                title="🚪 Utilisateur expulsé",
                description=f"✅ **{member}** a été expulsé.\n📝 Raison : {reason}",
                color=discord.Color.dark_orange()
            )
            embed.set_footer(text=f"Action effectuée par {ctx.author.name}", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
            logger.info(f"{member} a été expulsé par {ctx.author} pour : {reason}")
        except Exception as e:
            await ctx.send(embed=discord.Embed(
                title="❌ Erreur",
                description=f"Impossible d'expulser {member}.",
                color=discord.Color.red()
            ))
            logger.error(f"Erreur lors de l'expulsion de {member} : {e}")

    @commands.hybrid_command(name="banned_list", description="Affiche la liste des utilisateurs bannis du serveur.")
    @commands.has_permissions(ban_members=True)
    async def banned_list(self, ctx: commands.Context):
        """Liste les utilisateurs bannis du serveur."""
        try:
            # Vérifie que le bot a la permission "ban_members"
            if not ctx.guild.me.guild_permissions.ban_members:
                await ctx.send(embed=discord.Embed(
                    title="❌ Permission insuffisante",
                    description="Je n'ai pas la permission `ban_members` pour récupérer la liste des bannis.",
                    color=discord.Color.red()
                ))
                return

            # Récupère la liste des bannis via une boucle asynchrone
            banned_users = [entry async for entry in ctx.guild.bans()]

            if not banned_users:
                await ctx.send(embed=discord.Embed(
                    title="🔍 Liste des bannis",
                    description="✅ Aucun utilisateur n'est actuellement banni sur ce serveur.",
                    color=discord.Color.green()
                ))
                return

            # Crée l'affichage de la liste des bannis
            banned_list = "\n".join([
                f"**{ban.user}** - 📝 {ban.reason or 'Aucune raison spécifiée'}"
                for ban in banned_users
            ])

            # Envoie l'embed avec les bannis
            embed = discord.Embed(
                title="🔍 Liste des utilisateurs bannis",
                description=banned_list,
                color=discord.Color.dark_red()
            )
            embed.set_footer(text=f"Demandé par {ctx.author.name}", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send(embed=discord.Embed(
                title="❌ Permission insuffisante",
                description="Je n'ai pas les permissions nécessaires pour récupérer la liste des bannis.",
                color=discord.Color.red()
            ))
        except Exception as e:
            await ctx.send(embed=discord.Embed(
                title="❌ Erreur",
                description=f"Une erreur inattendue est survenue : `{str(e)}`",
                color=discord.Color.red()
            ))
            logger.error(f"Erreur lors de la récupération de la liste des bannis : {e}")


async def setup(bot: commands.Bot):
    """Ajoute la cog au bot."""
    await bot.add_cog(Moderation(bot))
