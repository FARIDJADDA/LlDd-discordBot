import discord
from discord.ext import commands
import os
import sys
from utils.logger import logger


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="restart", description="Redémarre le bot.")
    @commands.is_owner()
    async def restart(self, ctx: commands.Context):
        """Commande hybride pour redémarrer le bot."""
        try:
            # Confirmation de redémarrage
            if isinstance(ctx, discord.Interaction):
                await ctx.response.send_message("⏳ Redémarrage en cours...", ephemeral=True)
            else:
                await ctx.send("⏳ Redémarrage en cours...")

            logger.info("Redémarrage initié par un administrateur.")

            # Fermer proprement
            await self.bot.close()

            # Redémarrer le script (si applicable, selon votre méthode de lancement)
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception as e:
            logger.error(f"Erreur lors du redémarrage : {e}")
            if isinstance(ctx, discord.Interaction):
                await ctx.followup.send(f"⚠️ Erreur lors du redémarrage : {e}")
            else:
                await ctx.send(f"⚠️ Erreur lors du redémarrage : {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
