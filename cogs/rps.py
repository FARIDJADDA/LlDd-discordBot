import discord
from discord.ext import commands
import random
from utils.logger import logger

class RPS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="rps", description="Jouez à Pierre-Feuille-Ciseaux.")
    async def rps(self, ctx: commands.Context, adversaire: discord.Member = None, difficulte: str = "Normal"):
        """
        Jouez à Pierre-Feuille-Ciseaux.
        :param adversaire: L'adversaire contre qui jouer. Si None, vous jouez contre le bot.
        :param difficulte: Le niveau de difficulté (Facile, Normal, Difficile) contre le bot.
        """
        difficulte = difficulte.capitalize()
        if difficulte not in ["Facile", "Normal", "Difficile"]:
            await ctx.send("❌ Difficulté invalide. Choisissez entre Facile, Normal ou Difficile.")
            return

        if adversaire:
            if adversaire.bot:
                await ctx.send("🤖 Vous ne pouvez pas jouer contre un autre bot.")
                return
            await self.start_multiplayer_game(ctx, adversaire)
        else:
            await self.start_bot_game(ctx, difficulte)

    async def start_bot_game(self, ctx: commands.Context, difficulte: str):
        """Gère la logique pour un jeu en solo contre le bot."""
        choix = {"Pierre": "🪨", "Feuille": "🍁", "Ciseaux": "✂️"}

        while True:
            choix_bot = self.get_bot_choice(difficulte, list(choix.keys()))

            def check(m):
                return m.author == ctx.author and m.content.capitalize() in choix

            await ctx.send("🎮 Pierre-Feuille-Ciseaux ! Tapez votre choix (Pierre 🪨, Feuille 🍁, Ciseaux ✂️) :")

            try:
                user_msg = await self.bot.wait_for("message", check=check, timeout=30.0)
                choix_joueur = user_msg.content.capitalize()
                resultat = self.determine_winner(choix_joueur, choix_bot)

                embed = discord.Embed(
                    title="🤖 Chifoumi - Résultat du Jeu",
                    description=f"**Votre choix :** {choix[choix_joueur]} {choix_joueur}\n**Choix du bot :** {choix[choix_bot]} {choix_bot}\n\n{resultat}",
                    color=discord.Color.purple()
                )
                await ctx.send(embed=embed)

                if "Match nul" not in resultat:
                    break
            except TimeoutError:
                await ctx.send("⏰ Vous avez pris trop de temps pour répondre. Partie terminée !")
                break

    async def start_multiplayer_game(self, ctx: commands.Context, adversaire: discord.Member):
        """Gère la logique pour un jeu multijoueur."""
        choix = {"Pierre": "🪨", "Feuille": "🍁", "Ciseaux": "✂️"}

        while True:
            def check(auteur):
                return lambda m: m.author == auteur and m.content.capitalize() in choix

            await ctx.send(f"🎮 Pierre-Feuille-Ciseaux ! {ctx.author.mention} vs {adversaire.mention}.\n\nLes deux joueurs, envoyez-moi vos choix en DM !")

            try:
                await ctx.author.send("Tapez votre choix (Pierre, Feuille, Ciseaux) :")
                choix_joueur_task = self.bot.wait_for("message", check=check(ctx.author), timeout=30.0)

                await adversaire.send("Tapez votre choix (Pierre, Feuille, Ciseaux) :")
                choix_adversaire_task = self.bot.wait_for("message", check=check(adversaire), timeout=30.0)

                choix_joueur, choix_adversaire = await discord.utils.gather(choix_joueur_task, choix_adversaire_task)
                choix_joueur, choix_adversaire = choix_joueur.content.capitalize(), choix_adversaire.content.capitalize()

                resultat = self.determine_winner(choix_joueur, choix_adversaire)

                embed = discord.Embed(
                    title="👥 Chifoumi - Résultat du Jeu",
                    description=f"**Choix de {ctx.author.display_name} :** {choix[choix_joueur]} {choix_joueur}\n**Choix de {adversaire.display_name} :** {choix[choix_adversaire]} {choix_adversaire}\n\n{resultat}",
                    color=discord.Color.dark_teal()
                )
                await ctx.send(embed=embed)

                if "Match nul" not in resultat:
                    break
            except TimeoutError:
                await ctx.send("⏰ Un des joueurs a pris trop de temps pour répondre. Partie terminée !")
                break

    def get_bot_choice(self, difficulte, choix):
        """Détermine le choix du bot en fonction de la difficulté."""
        if difficulte == "Facile":
            return random.choices(choix, weights=[0.7, 0.2, 0.1], k=1)[0]
        elif difficulte == "Difficile":
            return random.choices(choix, weights=[0.1, 0.2, 0.7], k=1)[0]
        return random.choice(choix)

    def determine_winner(self, choix1, choix2):
        """Détermine le gagnant en fonction des choix."""
        if choix1 == choix2:
            return "🤝 Match nul !"

        gagne = {"Pierre": "Ciseaux", "Ciseaux": "Feuille", "Feuille": "Pierre"}
        if gagne[choix1] == choix2:
            return "🏆 Vous avez gagné !"
        return "💀 Vous avez perdu !"

async def setup(bot: commands.Bot):
    await bot.add_cog(RPS(bot))
    logger.info("✅ Cog RPS ajouté avec succès.")
