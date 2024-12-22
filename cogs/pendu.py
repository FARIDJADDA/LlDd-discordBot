import discord
from discord.ext import commands
import random
from utils.logger import logger
import asyncio

import os

class Pendu:
    def __init__(self, word):
        self.word = word
        self.lives = 6
        self.progress = "-" * len(word)
        self.remaining = len(word)
        self.misses = []
        self.status = "en cours"

    def guess(self, letter):
        if letter in self.progress:
            self.lives -= 1
        elif letter in self.word:
            for i, char in enumerate(self.word):
                if char == letter:
                    self.progress = self.progress[:i] + letter + self.progress[i + 1:]
                    self.remaining -= 1
        else:
            if letter not in self.misses:
                self.misses.append(letter)
            self.lives -= 1

        if self.lives == 0:
            self.status = "perdu"
        elif self.remaining == 0:
            self.status = "gagné"

        return {
            "status": self.status,
            "progress": self.progress,
            "misses": self.misses,
            "lives": self.lives,
        }

class PenduCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}
        self.figure = [
            " +---+\n |   |\n     |\n     |\n     |\n     |\n=========",
            " +---+\n |   |\n O   |\n     |\n     |\n     |\n=========",
            " +---+\n |   |\n O   |\n |   |\n     |\n     |\n=========",
            " +---+\n |   |\n O   |\n/|   |\n     |\n     |\n=========",
            " +---+\n |   |\n O   |\n/|\\  |\n     |\n     |\n=========",
            " +---+\n |   |\n O   |\n/|\\  |\n/    |\n     |\n=========",
            " +---+\n |   |\n O   |\n/|\\  |\n/ \\ |\n========="
        ]

    @commands.hybrid_command(name="pendu", description="Lance une partie de Pendu.")
    async def pendu(self, ctx, mode: str = "random"):
        if ctx.author.id in self.active_games:
            await ctx.send("⚠️ Vous avez déjà une partie en cours !")
            return

        word = None
        if mode == "random":
            word_list_path = os.path.join(os.path.dirname(__file__), "word_list.txt")
            try:
                with open(word_list_path, "r", encoding="utf-8") as file:
                    words = [line.strip() for line in file if line.strip()]
                    word = random.choice(words).lower()
            except FileNotFoundError:
                await ctx.send(
                    f"❌ Le fichier de mots n'a pas été trouvé à `{word_list_path}`. Veuillez vérifier sa présence.")
                return
        elif mode == "custom":
            await ctx.author.send("Veuillez entrer un mot pour le jeu du pendu :")

            def check(m):
                return m.author == ctx.author and isinstance(m.channel, discord.DMChannel)

            try:
                msg = await self.bot.wait_for("message", check=check, timeout=60)
                word = msg.content.strip().lower()
                if not word.isalpha() or len(word) < 3:
                    await ctx.author.send(
                        "❌ Le mot doit contenir au moins 3 lettres et ne doit pas contenir de caractères spéciaux.")
                    return
            except asyncio.TimeoutError:
                await ctx.author.send("⏳ Temps écoulé. Veuillez réessayer.")
                return
        else:
            await ctx.send("❌ Mode invalide. Utilisez `random` ou `custom`.")
            return

        game = Pendu(word)
        self.active_games[ctx.author.id] = game

        await self.display_game(ctx, game)

    async def display_game(self, ctx, game):
        figure_step = self.figure[6 - game.lives]
        misses = ", ".join(game.misses) if game.misses else "Aucune"
        embed = discord.Embed(
            title="Jeu du Pendu 🪑𓍯",
            description=(
                f"```\n{figure_step}\n```\n"
                f"**Mot :** {game.progress}\n"
                f"**Lettres manquées :** {misses}\n"
                f"**Vies restantes :** {game.lives} ❤️"
            ),
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.author.id not in self.active_games:
            return

        game = self.active_games[message.author.id]
        letter = message.content.lower()

        if len(letter) != 1 or not letter.isalpha():
            await message.channel.send("⚠️ Veuillez entrer une seule lettre valide.", delete_after=5)
            return

        result = game.guess(letter)

        if result["status"] == "gagné":
            await message.channel.send(
                f"🎉 Félicitations {message.author.mention}, vous avez trouvé le mot : **{game.word}** !"
            )
            del self.active_games[message.author.id]
        elif result["status"] == "perdu":
            await message.channel.send(
                f"💀 Partie terminée {message.author.mention}. Le mot était : **{game.word}**."
            )
            del self.active_games[message.author.id]
        else:
            await self.display_game(message.channel, game)

async def setup(bot):
    await bot.add_cog(PenduCog(bot))
    logger.info("☑️ Cog Pendu ajouté avec succès.")
