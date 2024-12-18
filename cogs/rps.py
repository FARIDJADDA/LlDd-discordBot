import discord
import random
from discord.ext import commands
from utils.logger import logger  # Import du logger configuré

class RockPaperScissors(commands.Cog):
    """Cog pour le jeu Pierre-Papier-Ciseaux."""

    def __init__(self, bot):
        self.bot = bot
        self.options = ["pierre", "papier", "ciseaux"]

    @commands.hybrid_command(name="rps", help="Joue à pierre, papier, ciseaux contre le bot.")
    async def rps(self, ctx, choice: str):
        """Joue au jeu Pierre-Papier-Ciseaux contre le bot."""
        user_choice = choice.lower()

        if user_choice not in self.options:
            logger.warning(f"❌ {ctx.author} a entré un choix invalide : {choice}")
            await ctx.send("⚠️ Choix invalide. Utilise `pierre`, `papier` ou `ciseaux`.")
            return

        bot_choice = random.choice(self.options)
        logger.info(f"🎮 {ctx.author} a joué {user_choice}. Le bot a joué {bot_choice}.")

        # Détermination du résultat
        if user_choice == bot_choice:
            result = "Égalité ! 🤝"
            color = discord.Color.orange()
            logger.info(f"🤝 Égalité entre {ctx.author} et le bot.")
        elif (user_choice == "pierre" and bot_choice == "ciseaux") or \
             (user_choice == "papier" and bot_choice == "pierre") or \
             (user_choice == "ciseaux" and bot_choice == "papier"):
            result = "🎉 Tu as gagné !"
            color = discord.Color.green()
            logger.info(f"✅ {ctx.author} a gagné contre le bot.")
        else:
            result = "💀 Tu as perdu !"
            color = discord.Color.red()
            logger.info(f"❌ {ctx.author} a perdu contre le bot.")

        # Création de l'embed pour afficher le résultat
        embed = discord.Embed(
            title="🪨 Pierre, Papier, Ciseaux ✂️",
            description=(
                f"**Ton choix** : {user_choice.capitalize()}\n"
                f"**Choix du bot** : {bot_choice.capitalize()}\n\n"
                f"{result}"
            ),
            color=color
        )
        embed.set_footer(text="Merci d'avoir joué ! 🎮")

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="rps_help", help="Affiche les règles de Pierre-Papier-Ciseaux.")
    async def rps_help(self, ctx):
        """Affiche les règles du jeu Pierre-Papier-Ciseaux."""
        embed = discord.Embed(
            title="📜 Règles de Pierre-Papier-Ciseaux",
            description=(
                "**Pierre** bat **Ciseaux**.\n"
                "**Ciseaux** bat **Papier**.\n"
                "**Papier** bat **Pierre**.\n\n"
                "Utilise `/rps <pierre|papier|ciseaux>` pour jouer contre le bot !"
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="Amuse-toi bien ! 🎉")
        await ctx.send(embed=embed)
        logger.info(f"ℹ️ {ctx.author} a demandé les règles de RPS.")

async def setup(bot: commands.Bot):
    """Ajoute la cog RPS au bot."""
    await bot.add_cog(RockPaperScissors(bot))
    logger.info("✅ Cog RockPaperScissors ajouté avec succès.")
