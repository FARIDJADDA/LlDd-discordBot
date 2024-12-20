import discord
import random
import json
import os
import aiohttp
from discord.ext import commands
from utils.logger import logger

LEADERBOARD_FILE = "data/leaderboard.json"
TRIVIA_API_URL = "https://opentdb.com/api.php?amount=50&category=15&type=multiple"

def load_leaderboard():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "w") as file:
            json.dump({}, file)
    with open(LEADERBOARD_FILE, "r") as file:
        return json.load(file)

def save_leaderboard(leaderboard):
    with open(LEADERBOARD_FILE, "w") as file:
        json.dump(leaderboard, file, indent=4)

class Trivia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.trivia_active = {}

    async def fetch_trivia_question(self):
        """Récupère des questions Trivia depuis l'API OpenTDB."""
        async with aiohttp.ClientSession() as session:
            async with session.get(TRIVIA_API_URL) as resp:
                if resp.status == 200:
                    logger.info("✅ Questions Trivia récupérées avec succès depuis l'API.")
                    data = await resp.json()
                    if data["response_code"] == 0:
                        return data["results"]
                logger.error("❌ Impossible de récupérer les questions Trivia.")
                return None

    @commands.hybrid_command(name="trivia", help="Réponds à une question sur le gaming et gagne des points.")
    async def trivia(self, ctx):
        if ctx.author.id in self.trivia_active:
            logger.warning(f"{ctx.author} a tenté de lancer une nouvelle question sans répondre à la précédente.")
            await ctx.send("⚠️ Tu as déjà une question en cours ! Réponds-y d'abord.")
            return

        questions = await self.fetch_trivia_question()
        if not questions:
            await ctx.send("❌ Erreur : Impossible de récupérer les questions Trivia.")
            return

        question_data = random.choice(questions)
        question = discord.utils.escape_markdown(question_data["question"])
        correct_answer = question_data["correct_answer"]
        options = question_data["incorrect_answers"] + [correct_answer]
        random.shuffle(options)

        self.trivia_active[ctx.author.id] = {"answer": correct_answer.lower(), "options": options}

        embed = discord.Embed(
            title="🧠 Trivia Gaming 🧠",
            description=f"**Question** : {question}\n\n" + "\n".join(
                [f"{i+1}. {option}" for i, option in enumerate(options)]
            ),
            color=discord.Color.dark_purple()
        )
        embed.set_footer(text="Réponds avec `/answer <numéro>` dans les 30 secondes.")
        await ctx.send(embed=embed)
        logger.info(f"🎮 {ctx.author} a lancé une question Trivia : {question}")

        # Timer de 30 secondes
        def timeout_check():
            if ctx.author.id in self.trivia_active:
                del self.trivia_active[ctx.author.id]
                logger.info(f"⏳ Temps écoulé pour la question Trivia de {ctx.author}.")

        self.bot.loop.call_later(30, timeout_check)

    @commands.hybrid_command(name="answer", help="Réponds à la question Trivia en cours.")
    async def answer(self, ctx, response: int):
        if ctx.author.id not in self.trivia_active:
            await ctx.send("⚠️ Tu n'as pas de question Trivia en cours. Utilise `/trivia` pour commencer !")
            return

        game = self.trivia_active.pop(ctx.author.id)
        correct_answer = game["answer"]
        options = game["options"]

        if 1 <= response <= len(options) and options[response - 1].lower() == correct_answer:
            leaderboard = load_leaderboard()
            leaderboard[str(ctx.author.id)] = leaderboard.get(str(ctx.author.id), 0) + 1
            save_leaderboard(leaderboard)

            embed = discord.Embed(
                title="🎉 Bonne réponse ! 🎉",
                description=f"✅ La réponse était bien **{correct_answer}**.\nTu gagnes **1 point** !",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            logger.info(f"✅ {ctx.author} a répondu correctement. Nouveau score : {leaderboard[str(ctx.author.id)]}")
        else:
            embed = discord.Embed(
                title="❌ Mauvaise réponse ! ❌",
                description=f"La bonne réponse était **{correct_answer}**.",
                color=discord.Color.dark_embed()
            )
            await ctx.send(embed=embed)
            logger.info(f"❌ {ctx.author} a donné une mauvaise réponse : {options[response-1] if 1 <= response <= len(options) else 'invalide'}.")

    @commands.hybrid_command(name="my_trivia_score", help="Affiche ton score actuel dans le Trivia Gaming.")
    async def my_trivia_score(self, ctx):
        leaderboard = load_leaderboard()
        user_score = leaderboard.get(str(ctx.author.id), 0)
        embed = discord.Embed(
            title="🎮 Mon Score Trivia 🎮",
            description=f"**{ctx.author.mention}**, tu as actuellement **{user_score} point(s)** dans le Trivia Gaming !",
            color=discord.Color.dark_teal()
        )
        await ctx.send(embed=embed)
        logger.info(f"📊 {ctx.author} a demandé son score Trivia : {user_score} point(s).")

async def setup(bot):
    await bot.add_cog(Trivia(bot))
