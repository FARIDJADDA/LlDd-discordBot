import discord
import os
import sys
from discord.ext import commands
from utils.logger import logger


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="restart", description="Redémarre le bot.")
    @commands.is_owner()
    async def restart(self, ctx: commands.Context):
        """Commande hybride pour redémarrer le bot."""
        try:
            # Embed de confirmation avant le redémarrage
            embed_confirm = discord.Embed(
                title="🔄 Redémarrage en cours...",
                description="Le bot est en train de redémarrer. Cela prendra quelques secondes.",
                color=discord.Color.dark_red(),
            )
            embed_confirm.set_thumbnail(url="attachment://restart_icon.png")
            embed_confirm.set_footer(text=f"Demandé par {ctx.author}", icon_url=ctx.author.avatar.url)

            # Chargement de l'image locale
            image_path = "assets/restart_icon.png"
            file = discord.File(image_path, filename="restart_icon.png")

            # Envoi du message de redémarrage
            if isinstance(ctx, discord.Interaction):
                await ctx.response.send_message(file=file, embed=embed_confirm, ephemeral=True)
            else:
                await ctx.send(file=file, embed=embed_confirm)

            logger.info("Redémarrage initié par un administrateur.")

            # Fermeture proprement
            await self.bot.close()

            # Redémarrage de l'exécution
            os.execv(sys.executable, [sys.executable] + sys.argv)

        except Exception as e:
            logger.error(f"Erreur lors du redémarrage : {e}")
            await ctx.send(embed=discord.Embed(
                title="❌ Erreur",
                description=f"Une erreur est survenue lors du redémarrage : `{e}`",
                color=discord.Color.red(),
            ))

    @commands.hybrid_command(name="reload", description="Recharge un cog spécifique.")
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, cog: str):
        """Recharge un cog spécifique."""
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            await self.bot.load_extension(f"cogs.{cog}")
            await ctx.send(f"✅ Cog **{cog}** rechargé avec succès.")
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du rechargement du cog **{cog}** : {e}")


async def setup(bot: commands.Bot):
    """Ajoute la cog au bot."""
    await bot.add_cog(Admin(bot))
