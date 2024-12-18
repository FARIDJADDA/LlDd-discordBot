import discord
import random
import json
import os
import aiohttp
from discord.ext import commands

LEADERBOARD_FILE = "leaderboard.json"
TRIVIA_API_URL = "https://opentdb.com/api.php?amount=50&category=15&type=multiple"


# Gestion du leaderboard
def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "w") as file:
            json.dump({}, file)
    with open(LEADERBOARD_FILE, "r") as file:
        return json.load(file)

def save_leaderboard(leaderboard):
    with open(LEADERBOARD_FILE, "w") as file:
        json.dump(leaderboard, file, indent=4)


class GamesExtended(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.trivia_active = {}

    async def fetch_trivia_question(self):
        """Récupère des questions Trivia depuis l'API OpenTDB."""
        async with aiohttp.ClientSession() as session:
            async with session.get(TRIVIA_API_URL) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data["response_code"] == 0:
                        return data["results"]
                return None

    @commands.hybrid_command(name="trivia", help="Réponds à une question sur le gaming et gagne des points.")
    async def trivia(self, ctx):
        """Pose une question Trivia via l'API OpenTDB."""
        if ctx.author.id in self.trivia_active:
            await ctx.send("⚠️ Tu as déjà une question en cours ! Réponds-y d'abord.")
            return

        questions = await self.fetch_trivia_question()
        if not questions:
            await ctx.send("❌ Erreur : Impossible de récupérer les questions Trivia. Réessaie plus tard.")
            return

        # Sélectionne une question au hasard
        question_data = random.choice(questions)
        question = discord.utils.escape_markdown(question_data["question"])
        correct_answer = question_data["correct_answer"]
        options = question_data["incorrect_answers"]
        options.append(correct_answer)
        random.shuffle(options)

        # Stocke la question active
        self.trivia_active[ctx.author.id] = {"answer": correct_answer.lower(), "options": options}

        # Envoi de l'embed avec les options
        embed = discord.Embed(
            title="🧠 Trivia Gaming 🧠",
            description=f"**Question** : {question}\n\n"
                        + "\n".join([f"{i+1}. {option}" for i, option in enumerate(options)]),
            color=discord.Color.dark_purple()
        )
        embed.set_footer(text="Réponds avec `/answer <numéro>` dans les 30 secondes.")
        await ctx.send(embed=embed)

        # Minuterie de 30 secondes
        def timeout_check():
            if ctx.author.id in self.trivia_active:
                del self.trivia_active[ctx.author.id]

        self.bot.loop.call_later(30, timeout_check)

    @commands.hybrid_command(name="answer", help="Réponds à la question Trivia en cours.")
    async def answer(self, ctx, response: int):
        """Vérifie la réponse à la question Trivia."""
        if ctx.author.id not in self.trivia_active:
            await ctx.send("⚠️ Tu n'as pas de question Trivia en cours. Utilise `/trivia` pour commencer !")
            return

        game = self.trivia_active[ctx.author.id]
        correct_answer = game["answer"]
        options = game["options"]
        del self.trivia_active[ctx.author.id]  # Retire la question active

        if 1 <= response <= len(options) and options[response - 1].lower() == correct_answer:
            # Mise à jour du leaderboard
            leaderboard = load_leaderboard()
            leaderboard[str(ctx.author.id)] = leaderboard.get(str(ctx.author.id), 0) + 1
            save_leaderboard(leaderboard)

            embed = discord.Embed(
                title="🎉 Bonne réponse ! 🎉",
                description=f"✅ La réponse était bien **{correct_answer}**.\nTu gagnes **1 point** !",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Score actuel : {leaderboard[str(ctx.author.id)]} points.")
        else:
            embed = discord.Embed(
                title="❌ Mauvaise réponse ! ❌",
                description=f"La bonne réponse était **{correct_answer}**.",
                color=discord.Color.red()
            )

        await ctx.send(embed=embed)

    # Commande pour afficher le classement
    @commands.hybrid_command(name="leaderboard", help="Affiche le classement des joueurs.")
    async def leaderboard(self, ctx):
        """Affiche le classement des joueurs."""
        leaderboard = load_leaderboard()
        sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)

        if not sorted_leaderboard:
            await ctx.send("🏆 Personne n'a encore marqué de points. Sois le premier !")
            return

        description = "\n".join(
            [f"<@{user_id}> : **{score} points**" for user_id, score in sorted_leaderboard[:10]]
        )
        embed = discord.Embed(
            title="🏆 Leaderboard - Trivia Gaming 🏆",
            description=description,
            color=discord.Color.dark_purple()
        )
        await ctx.send(embed=embed)

    # Commande pour le jeu du pendu
    @commands.hybrid_command(name="hangman", help="Joue au jeu du pendu.")
    async def hangman(self, ctx):
        """Débute une partie du pendu."""
        words = ["discord", "gaming", "python", "bot", "demon"]
        word = random.choice(words).upper()
        self.hangman_games[ctx.author.id] = {"word": word, "guesses": [], "attempts": 6}

        embed = discord.Embed(
            title="🎮 Jeu du pendu 🎮",
            description=f"Devine le mot lettre par lettre. Tu as **6 tentatives**.\n\nMot : {' '.join('_' for _ in word)}",
            color=discord.Color.dark_purple()
        )
        embed.set_footer(text="Utilise /guess <lettre> pour deviner une lettre.")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="guess", help="Devine une lettre pour le pendu.")
    async def guess(self, ctx, letter: str):
        """Permet de deviner une lettre pour le jeu du pendu."""
        game = self.hangman_games.get(ctx.author.id)
        if not game:
            await ctx.send("⚠️ Tu n'as pas de partie en cours. Utilise `/hangman` pour commencer une partie.")
            return

        if len(letter) != 1 or not letter.isalpha():
            await ctx.send("⚠️ Merci de deviner **une seule lettre** à la fois.")
            return

        letter = letter.upper()
        word = game["word"]

        if letter in game["guesses"]:
            await ctx.send(f"⚠️ Tu as déjà deviné la lettre **{letter}**.")
            return

        game["guesses"].append(letter)
        if letter not in word:
            game["attempts"] -= 1

        display_word = " ".join([l if l in game["guesses"] else "_" for l in word])
        if "_" not in display_word:
            await ctx.send(f"🎉 Bravo {ctx.author.mention}, tu as trouvé le mot **{word}** !")
            del self.hangman_games[ctx.author.id]
            return

        if game["attempts"] == 0:
            await ctx.send(f"💀 Game over {ctx.author.mention} ! Le mot était **{word}**.")
            del self.hangman_games[ctx.author.id]
            return

        embed = discord.Embed(
            title="🎮 Jeu du pendu 🎮",
            description=f"Mot : {display_word}\n\nTentatives restantes : **{game['attempts']}**",
            color=discord.Color.dark_purple()
        )
        await ctx.send(embed=embed)

    # Commande pour pierre, papier, ciseaux
    @commands.hybrid_command(name="rps", help="Joue à pierre, papier, ciseaux contre le bot.")
    async def rps(self, ctx, choice: str):
        """Pierre, papier, ciseaux"""
        options = ["pierre", "papier", "ciseaux"]
        bot_choice = random.choice(options)

        if choice.lower() not in options:
            await ctx.send("⚠️ Choix invalide. Utilise `pierre`, `papier` ou `ciseaux`.")
            return

        result = ""
        if choice == bot_choice:
            result = "Égalité ! 🤝"
        elif (choice == "pierre" and bot_choice == "ciseaux") or \
             (choice == "papier" and bot_choice == "pierre") or \
             (choice == "ciseaux" and bot_choice == "papier"):
            result = "🎉 Tu as gagné !"
        else:
            result = "💀 Tu as perdu !"

        embed = discord.Embed(
            title="🪨 Pierre, Papier, Ciseaux ✂️",
            description=f"**Ton choix** : {choice.capitalize()}\n**Choix du bot** : {bot_choice.capitalize()}\n\n{result}",
            color=discord.Color.dark_purple()
        )
        await ctx.send(embed=embed)




async def setup(bot: commands.Bot):
    """Ajoute la cog des mini-jeux au bot."""
    await bot.add_cog(GamesExtended(bot))
