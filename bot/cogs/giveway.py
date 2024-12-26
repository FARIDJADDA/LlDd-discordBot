import discord
from discord.ext import commands, tasks
from utils.logger import logger
import random
from datetime import datetime, timedelta
import pytz

LOCAL_TZ = pytz.timezone("Europe/Paris")

class Giveaway:
    def __init__(self, name, prize, winners, duration, channel):
        self.name = name
        self.prize = prize
        self.winners = winners
        self.end_time = datetime.now(LOCAL_TZ) + timedelta(seconds=duration)  # Utiliser datetime.now(LOCAL_TZ)
        self.channel = channel
        self.participants = set()
        self.message = None
        self.ended = False

    def add_participant(self, user):
        self.participants.add(user)

    def get_winners(self):
        if len(self.participants) < self.winners:
            return list(self.participants)
        return random.sample(self.participants, self.winners)

class GiveawayView(discord.ui.View):
    def __init__(self, giveaway, bot):
        super().__init__(timeout=None)
        self.giveaway = giveaway
        self.bot = bot

    @discord.ui.button(label="✨ Participer !", style=discord.ButtonStyle.blurple)
    async def participate_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        if user.bot:
            await interaction.response.send_message("Les bots ne peuvent pas participer !", ephemeral=True)
            return

        if user in self.giveaway.participants:
            await interaction.response.send_message("⚠️ Vous êtes déjà inscrit à ce concours.", ephemeral=True)
        else:
            self.giveaway.add_participant(user)
            await interaction.response.send_message("✨ Vous avez rejoint le concours !", ephemeral=True)

            # Mettre à jour l'embed avec le nombre de participants
            embed = interaction.message.embeds[0]
            embed.description = (f"Récompense : **{self.giveaway.prize}**\n"
                                 f"Nombre de gagnants : **{self.giveaway.winners}**\n"
                                 f"Participants : **{len(self.giveaway.participants)}**\n\n"
                                 "Cliquez sur ✨ pour participer !")
            await interaction.message.edit(embed=embed, view=self)

class Concours(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_giveaways = {}

    @commands.hybrid_command(name="concours_creer",
                             description="Crée un nouveau concours avec une récompense spécifique.")
    async def create_giveaway(self, ctx, type: str, name: str, winners: int, duration: int, *, prize: str):
        current_time = datetime.now(LOCAL_TZ)
        end_time = current_time + timedelta(seconds=duration)

        logger.info(
            f"[CREATE] Attempting to create giveaway '{name}' in channel {ctx.channel.id} with duration {duration} seconds.")
        logger.info(f"[CREATE] Current time: {current_time}, Scheduled end time: {end_time}")

        if ctx.channel.id in self.active_giveaways:
            logger.warning(
                f"[CREATE] Giveaway creation aborted: already an active giveaway in channel {ctx.channel.id}.")
            await ctx.send("⚠️ Un concours est déjà en cours dans ce salon !")
            return

        if winners < 1:
            logger.error(f"[CREATE] Invalid number of winners ({winners}). Must be at least 1.")
            await ctx.send("❌ Le nombre de gagnants doit être au moins 1.")
            return

        giveaway = Giveaway(name=name, prize=prize, winners=winners, duration=duration, channel=ctx.channel)
        self.active_giveaways[ctx.channel.id] = giveaway

        embed = discord.Embed(
            title=f"🎉 **Concours : {giveaway.name}** 🎉",
            description=(f"Récompense : **{giveaway.prize}**\n"
                         f"Nombre de gagnants : **{giveaway.winners}**\n"
                         f"Participants : **0**\n\n"
                         "Cliquez sur ✨ pour participer !"),
            color=discord.Color.purple()
        )
        embed.set_footer(text="Bonne chance à tous les participants !")

        view = GiveawayView(giveaway, self.bot)
        message = await ctx.send(embed=embed, view=view)
        giveaway.message = message
        logger.info(f"[CREATE] Giveaway '{name}' successfully created and active in channel {ctx.channel.id}.")

        self.bot.loop.create_task(self.auto_end_giveaway(giveaway))

    @commands.hybrid_command(name="concours_terminer", description="Termine un concours en cours et désigne les gagnants.")
    async def end_giveaway(self, ctx):
        if ctx.channel.id not in self.active_giveaways:
            await ctx.send("❌ Aucun concours actif dans ce salon.")
            return

        giveaway = self.active_giveaways.pop(ctx.channel.id)
        giveaway.ended = True

        winners = giveaway.get_winners()
        if winners:
            winner_mentions = ", ".join([winner.mention for winner in winners])
            embed = discord.Embed(
                title=f"🎉 **Concours terminé : {giveaway.name}** 🎉",
                description=f"Récompense : **{giveaway.prize}**\n\nGagnants : {winner_mentions}",
                color=discord.Color.dark_teal()
            )
        else:
            embed = discord.Embed(
                title=f"🎉 **Concours terminé : {giveaway.name}** 🎉",
                description=f"Récompense : **{giveaway.prize}**\n\nAucun participant n'a gagné.",
                color=discord.Color.dark_embed()
            )

        await giveaway.channel.send(embed=embed)

    @commands.hybrid_command(name="concours_relancer", description="Relance un concours et désigne un nouveau gagnant.")
    async def reroll_giveaway(self, ctx):
        if ctx.channel.id not in self.active_giveaways:
            await ctx.send("❌ Aucun concours actif dans ce salon.")
            return

        giveaway = self.active_giveaways[ctx.channel.id]

        if not giveaway.participants:
            await ctx.send("❌ Aucun participant pour ce concours !")
            return

        winners = giveaway.get_winners()
        if winners:
            winner_mentions = ", ".join([winner.mention for winner in winners])
            await ctx.send(f"🎉 Nouveau gagnant : {winner_mentions}")
        else:
            await ctx.send("❌ Impossible de sélectionner un gagnant.")

    async def auto_end_giveaway(self, giveaway):
        current_time = datetime.now(LOCAL_TZ)
        logger.info(f"[AUTO_END] Current time: {current_time}, Giveaway end time: {giveaway.end_time}")

        time_to_wait = (giveaway.end_time - current_time).total_seconds()
        if time_to_wait > 0:
            logger.info(f"[AUTO_END] Waiting {time_to_wait} seconds for giveaway '{giveaway.name}' to end.")
            await discord.utils.sleep_until(giveaway.end_time)
        else:
            logger.warning(f"[AUTO_END] Giveaway '{giveaway.name}' end time is in the past. Ending immediately.")

        if giveaway.channel.id in self.active_giveaways:
            logger.info(f"[AUTO_END] Ending giveaway '{giveaway.name}' now.")
            if giveaway.message:
                ctx = await self.bot.get_context(giveaway.message)
                await self.end_giveaway(ctx)
            else:
                logger.warning(
                    f"[AUTO_END] Giveaway '{giveaway.name}' has no associated message. Ending without context.")
                self.active_giveaways.pop(giveaway.channel.id, None)
                embed = discord.Embed(
                    title=f"🎉 **Concours terminé : {giveaway.name}** 🎉",
                    description=f"Récompense : **{giveaway.prize}**\n\nAucun participant n'a gagné.",
                    color=discord.Color.dark_embed()
                )
                await giveaway.channel.send(embed=embed)
        else:
            logger.info(f"[AUTO_END] Giveaway '{giveaway.name}' was already ended or not found in active giveaways.")

    @commands.hybrid_command(name="concours_participants",
                             description="Affiche la liste des participants du concours en cours.")
    async def show_participants(self, ctx):
        if ctx.channel.id not in self.active_giveaways:
            await ctx.send("❌ Aucun concours actif dans ce salon.")
            return

        giveaway = self.active_giveaways[ctx.channel.id]
        if not giveaway.participants:
            await ctx.send("Aucun participant pour ce concours pour le moment.")
            return

        participant_mentions = "\n".join([participant.mention for participant in giveaway.participants])
        embed = discord.Embed(
            title=f"👥 Participants du concours : {giveaway.name}",
            description=participant_mentions,
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Total : {len(giveaway.participants)} participants")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Concours(bot))
    logger.info("☑️ Cog Concours ajouté avec succès.")
