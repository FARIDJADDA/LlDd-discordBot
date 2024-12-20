import discord
from discord.ext import commands
from utils.logger import logger

class Poll:
    def __init__(self, question, options):
        self.question = question
        self.options = options[:10]
        self.votes = {option: 0 for option in options}
        self.message = None
        self.ended = False

    def vote(self, option):
        if option in self.votes:
            self.votes[option] += 1

    def results(self):
        return sorted(self.votes.items(), key=lambda x: x[1], reverse=True)

class Sondage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_polls = {}

    @commands.hybrid_command(name="sondage_creer", description="Crée un nouveau sondage avec une question et des options.")
    async def create_poll(self, ctx, question: str, options: str):
        if ctx.channel.id in self.active_polls:
            await ctx.send("⚠️ Un sondage est déjà en cours dans ce salon !")
            return

        options_list = [option.strip() for option in options.split(",")]

        if len(options_list) < 2:
            await ctx.send("❌ Vous devez fournir au moins deux options pour le sondage.")
            return

        poll = Poll(question, options_list)
        self.active_polls[ctx.channel.id] = poll

        embed = discord.Embed(
            title="📊 Sondage",
            description=f"**{poll.question}**\n\n" + "\n".join([f"{chr(65 + i)} : {option}" for i, option in enumerate(poll.options)]),
            color=discord.Color.purple()
        )
        embed.set_footer(text="Votez en cliquant sur les réactions ci-dessous.")

        message = await ctx.send(embed=embed)
        poll.message = message

        for i in range(len(poll.options)):
            await message.add_reaction(chr(127462 + i))

    @commands.hybrid_command(name="sondage_resultats", description="Affiche les résultats du sondage en cours dans ce salon.")
    async def show_results(self, ctx):
        if ctx.channel.id not in self.active_polls:
            await ctx.send("❌ Aucun sondage actif dans ce salon.")
            return

        poll = self.active_polls[ctx.channel.id]
        results = poll.results()

        embed = discord.Embed(
            title="📊 Résultats du sondage",
            description=f"**{poll.question}**\n\n" + "\n".join([f"{option} : {votes} vote(s)" for option, votes in results]),
            color=discord.Color.dark_teal()
        )

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="sondage_terminer", description="Termine le sondage en cours dans ce salon et affiche les résultats.")
    async def end_poll(self, ctx):
        if ctx.channel.id not in self.active_polls:
            await ctx.send("❌ Aucun sondage actif dans ce salon.")
            return

        poll = self.active_polls.pop(ctx.channel.id)
        poll.ended = True

        results = poll.results()
        embed = discord.Embed(
            title="📊 Sondage terminé",
            description=f"**{poll.question}**\n\n" + "\n".join([f"{option} : {votes} vote(s)" for option, votes in results]),
            color=discord.Color.dark_teal()
        )

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return

        poll = next((poll for poll in self.active_polls.values() if poll.message.id == reaction.message.id), None)
        if not poll or poll.ended:
            return

        emoji_index = ord(reaction.emoji) - 127462
        if 0 <= emoji_index < len(poll.options):
            poll.vote(poll.options[emoji_index])

async def setup(bot):
    await bot.add_cog(Sondage(bot))
    logger.info("✅ Cog Sondage ajouté avec succès.")
