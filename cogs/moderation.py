from discord.ext import commands
import discord
import asyncio
from utils.logger import logger  # Utilisation du logger global


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def log_action(self, ctx, action, member, reason=None):
        """Logger une action de modération dans un canal spécifique et dans un fichier local"""
        log_message = f"Action: {action}, Utilisateur: {member}, Par: {ctx.author}, Raison: {reason or 'Aucune'}"
        logger.info(log_message)  # Log local

        # Log dans un canal Discord
        log_channel = discord.utils.get(ctx.guild.channels, name="logs")
        if log_channel:
            embed = discord.Embed(
                title="Action de modération",
                description=f"**Action** : {action}\n**Utilisateur** : {member.mention}\n**Par** : {ctx.author.mention}\n**Raison** : {reason or 'Aucune'}",
                color=discord.Color.orange(),
            )
            try:
                await log_channel.send(embed=embed)
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi du log Discord pour {action}: {e}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Bannir un utilisateur avec confirmation"""
        if ctx.guild.me.top_role <= member.top_role:
            await ctx.send(f"⚠️ Je ne peux pas bannir {member.mention}, il a un rôle supérieur ou égal au mien.")
            return

        if member == ctx.author:
            await ctx.send("❌ Tu ne peux pas te bannir toi-même.")
            return

        if member == self.bot.user:
            await ctx.send("❌ Tu ne peux pas bannir le bot.")
            return

        confirmation_message = await ctx.send(f"❓ Es-tu sûr de vouloir bannir {member.mention} ? Réponds par `oui` ou `non`.")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["oui", "non"]

        try:
            reply = await self.bot.wait_for("message", check=check, timeout=30.0)
            if reply.content.lower() == "oui":
                await member.ban(reason=reason)
                await ctx.send(f"🚫 {member.mention} a été banni. Raison : {reason or 'Aucune raison spécifiée.'}")
                await self.log_action(ctx, "Ban", member, reason)
            else:
                await ctx.send("🚫 Bannissement annulé.")
        except asyncio.TimeoutError:
            await ctx.send("⏳ Temps écoulé. Bannissement annulé.")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Expulser un utilisateur"""
        if ctx.guild.me.top_role <= member.top_role:
            await ctx.send(f"⚠️ Je ne peux pas expulser {member.mention}, il a un rôle supérieur ou égal au mien.")
            return
        try:
            await member.kick(reason=reason)
            await ctx.send(f"👢 {member.mention} a été expulsé. Raison : {reason or 'Aucune raison spécifiée.'}")
            await self.log_action(ctx, "Kick", member, reason)
        except Exception as e:
            await ctx.send("Je n'ai pas pu expulser cet utilisateur.")
            logger.error(f"Erreur lors de l'expulsion de {member}: {e}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def banned_list(self, ctx):
        """Lister les utilisateurs bannis"""
        bans = await ctx.guild.bans()
        if bans:
            banned_users = "\n".join([f"**{ban.user}** (Raison : {ban.reason or 'Non spécifiée'})" for ban in bans[:10]])
            await ctx.send(f"🚫 Utilisateurs bannis :\n{banned_users}")
            if len(bans) > 10:
                await ctx.send(f"⚠️ Et {len(bans) - 10} autres...")
            logger.info(f"Liste des bannis envoyée : {len(bans)} utilisateurs.")
        else:
            await ctx.send("✅ Aucun utilisateur banni.")
            logger.info("Aucun utilisateur banni trouvé.")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Gérer les erreurs de commande"""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Tu n'as pas les permissions nécessaires pour exécuter cette commande.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ Utilisateur introuvable.")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send("❌ Une erreur est survenue lors de l'exécution de la commande.")
            logger.error(f"Erreur lors de l'exécution de la commande : {error}")
        else:
            await ctx.send("❌ Une erreur inattendue est survenue.")
            logger.error(f"Erreur inconnue : {error}")


async def setup(bot):
    await bot.add_cog(Moderation(bot))