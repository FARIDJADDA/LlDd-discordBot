import discord
from discord.ext import commands
import os
import sys

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def restart(self, ctx):
        """Redémarre le bot"""
        # Demande de confirmation
        await ctx.send("⏳ Redémarrage en cours...")
        try:
            # Fermer proprement
            await self.bot.close()
            # Redémarrer le script (optionnel : selon votre méthode de lancement)
            os.execv(sys.executable, ['python'] + sys.argv)
        except Exception as e:
            await ctx.send(f"⚠️ Erreur lors du redémarrage : {e}")
            print(f"Erreur lors du redémarrage : {e}")

async def setup(bot):
    await bot.add_cog(Admin(bot))
