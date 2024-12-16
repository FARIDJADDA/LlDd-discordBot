import discord
import random
import asyncio
from discord.ext import commands


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.questions = [
            {"question": "Dans quel Call of Duty le mode 'Zombie' a-t-il été introduit ?", "answer": "World at War"},
            {"question": "Quel Call of Duty propose une campagne où l'on combat avec le capitaine Price ?", "answer": "Modern Warfare"},
            {"question": "Quel est le nom du mode de bataille royale introduit dans Call of Duty : Modern Warfare (2019) ?", "answer": "Warzone"},
            {"question": "Dans Call of Duty : Black Ops, qui est le protagoniste principal ?", "answer": "Alex Mason"},
            {"question": "Quel est le nom du véhicule utilisé pour se déplacer rapidement dans Warzone ?", "answer": "Bertha"},
            {"question": "Dans quel GTA le personnage Trevor apparaît-il ?", "answer": "GTA V"},
            {"question": "Quel est le nom de la ville principale dans GTA : Vice City ?", "answer": "Vice City"},
            {"question": "Dans GTA : San Andreas, quel est le nom du protagoniste ?", "answer": "CJ"},
            {"question": "Quel jeu de la série GTA a introduit pour la première fois des motos ?", "answer": "GTA Vice City"},
            {"question": "Dans GTA V, combien de protagonistes jouables y a-t-il ?", "answer": "Trois"},
            {"question": "Quel joueur était sur la couverture de FIFA 21 ?", "answer": "Kylian Mbappé"},
            {"question": "Quel studio développe les jeux FIFA ?", "answer": "EA Sports"},
            {"question": "Dans FIFA, quel mode permet de gérer une équipe sur plusieurs saisons ?", "answer": "Carrière"},
            {"question": "Quelle année a vu la sortie du premier jeu FIFA ?", "answer": "1993"},
            {"question": "Dans FIFA Ultimate Team, que signifie l'abréviation 'TOTW' ?", "answer": "Team of the Week"},
            {"question": "Dans Pac-Man, quel est le nom du fantôme rouge ?", "answer": "Blinky"},
            {"question": "Quel jeu célèbre commence par la phrase 'It's dangerous to go alone! Take this.' ?", "answer": "The Legend of Zelda"},
            {"question": "Dans Super Mario Bros, quel personnage capture la princesse Peach ?", "answer": "Bowser"},
            {"question": "Dans Tetris, quel est l’objectif principal du jeu ?", "answer": "Empiler les blocs pour créer des lignes complètes"},
            {"question": "Dans quel jeu le personnage principal est un hérisson bleu ?", "answer": "Sonic the Hedgehog"},
        ]

    @commands.hybrid_command(name="quiz", description="Lance un quiz simple sur le gaming.")
    async def quiz(self, ctx: commands.Context):
        """Pose une question sur le gaming avec 3 chances pour répondre."""
        question = random.choice(self.questions)
        attempts = 3

        # Envoie de la question initiale
        await ctx.send(
            f"🎮 **Quiz Gaming** 🎮\n{question['question']}\n\nTu as **{attempts} chances** de répondre correctement !"
        )

        def check(message):
            """Vérifie que la réponse vient de l'utilisateur et du bon canal."""
            return message.channel == ctx.channel and message.author == ctx.author

        while attempts > 0:
            try:
                msg = await self.bot.wait_for("message", check=check, timeout=30.0)

                if msg.content.lower() == question["answer"].lower():
                    await ctx.send(f"✅ Bonne réponse, {msg.author.mention} ! 🎉")
                    return
                else:
                    attempts -= 1
                    if attempts > 0:
                        await ctx.send(
                            f"❌ Mauvaise réponse, {msg.author.mention}. Il te reste **{attempts} tentatives**."
                        )
            except asyncio.TimeoutError:
                await ctx.send(f"⏳ Temps écoulé ! La bonne réponse était : **{question['answer']}**.")
                return

        # Si toutes les tentatives échouent
        await ctx.send(
            f"❌ Toutes tes chances sont écoulées, {ctx.author.mention}. La bonne réponse était : **{question['answer']}**."
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Games(bot))
