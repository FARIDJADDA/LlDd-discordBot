import discord
from discord.ext import commands
from discord import ui, ButtonStyle
from utils.logger import logger
from .poll_management import Poll


class PollView(ui.View):
    def __init__(self, poll, author_id):
        super().__init__(timeout=None)
        self.poll = poll
        self.author_id = author_id  # Pour permettre uniquement à l'auteur de fermer le sondage

        # Ajouter un bouton pour chaque option
        for i, option in enumerate(poll.options):
            self.add_item(VoteButton(option, i, self.poll))

        # Bouton pour terminer le sondage
        self.add_item(ClosePollButton(poll, author_id))


class VoteButton(ui.Button):
    def __init__(self, option, index, poll):
        super().__init__(style=ButtonStyle.primary, label=option, custom_id=f"vote_{index}")
        self.poll = poll
        self.option = option

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user

        if self.poll.ended:
            await interaction.response.send_message("❌ Le sondage est clôturé, vous ne pouvez plus voter.", ephemeral=True)
            return

        if not self.poll.is_user_allowed(user):
            await interaction.response.send_message("❌ Vous n'êtes pas autorisé à voter dans ce sondage.", ephemeral=True)
            return

        # Ajouter le vote
        self.poll.vote(user, self.option)
        await interaction.response.send_message(f"☑️ Votre vote pour \"{self.option}\" a été enregistré.", ephemeral=True)

        # Mettre à jour l'affichage des résultats
        embed = interaction.message.embeds[0]
        embed.description = f"**{self.poll.question}**\n\n{self.poll.render_results()}"
        await interaction.message.edit(embed=embed)



class ClosePollButton(ui.Button):
    def __init__(self, poll, author_id):
        super().__init__(style=ButtonStyle.danger, label="🔒 Clôturer le sondage", custom_id="close_poll")
        self.poll = poll
        self.author_id = author_id  # Stocker l'ID de l'auteur pour vérifier les permissions

    async def callback(self, interaction: discord.Interaction):
        # Vérifie si l'utilisateur est l'auteur du sondage
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("❌ Seul l'auteur du sondage peut le clôturer.", ephemeral=True)
            return

        self.poll.ended = True
        # Désactiver les boutons
        for item in self.view.children:
            item.disabled = True
        self.view.stop()

        # Mettre à jour l'embed avec les résultats finaux
        embed = interaction.message.embeds[0]
        embed.title = "📊 Sondage terminé"
        embed.color = discord.Color.dark_teal()
        embed.description = f"**{self.poll.question}**\n\n{self.poll.render_results()}"
        await interaction.message.edit(embed=embed, view=self.view)
        await interaction.response.send_message("☑️ Le sondage a été clôturé.")


class PollCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_polls = {}

    @commands.hybrid_command(name="create_poll", description="Crée un nouveau sondage.")
    async def create_poll(self, ctx, question: str, options: str):
        """
        Créer un nouveau sondage avec une question et des options.
        Les options doivent être séparées par des points-virgules (;).
        Exemple : /create_poll question: "Votre couleur préférée ?" options: "Rouge;Bleu;Vert"
        """
        options_list = [opt.strip() for opt in options.split(";") if opt.strip()]

        if len(options_list) < 2:
            await ctx.send("❌ Vous devez fournir au moins deux options pour créer un sondage.")
            return

        if len(options_list) > 15:
            await ctx.send("❌ Vous ne pouvez pas avoir plus de 15 options dans un sondage.")
            return

        if ctx.channel.id in self.active_polls:
            await ctx.send("⚠️ Un sondage est déjà actif dans ce salon. Veuillez le terminer avant d'en créer un autre.")
            return

        poll = Poll(question, options_list)
        self.active_polls[ctx.channel.id] = poll

        embed = discord.Embed(
            title="🗳️ Sondage",
            description=f"**{poll.question}**\n\n{poll.render_results()}",
            color=discord.Color.purple()
        )
        embed.set_footer(text="Utilisez les boutons ci-dessous pour voter.")

        view = PollView(poll, ctx.author.id)
        poll.message = await ctx.send(embed=embed, view=view)
        self.active_polls[ctx.channel.id] = poll  # Stocker le sondage avec le message correctement défini

        logger.info(f"[POLL CREATED] Un sondage a été créé par {ctx.author} dans le salon {ctx.channel}. Question: {poll.question}")

    @commands.hybrid_command(name="end_poll", description="Termine un sondage actif et affiche les résultats.")
    async def end_poll(self, ctx):
        """Clôturer un sondage actif et afficher les résultats."""
        poll = self.active_polls.pop(ctx.channel.id, None)

        if not poll:
            await ctx.send("❌ Aucun sondage actif à terminer dans ce salon.")
            return

        if not poll.message:  # Vérifie si le message du sondage existe
            await ctx.send("❌ Impossible de trouver le message associé au sondage.")
            return

        poll.ended = True

        # Désactiver les boutons
        for item in poll.message.components[0].children:
            item.disabled = True

        # Mettre à jour l'embed avec les résultats finaux
        embed = discord.Embed(
            title="📊 Sondage terminé",
            description=f"**{poll.question}**\n\n{poll.render_results()}",
            color=discord.Color.green()
        )
        await poll.message.edit(embed=embed, view=None)
        await ctx.send("☑️ Le sondage a été clôturé.")


async def setup(bot):
    await bot.add_cog(PollCommands(bot))
    logger.info("☑️ Cog des commandes de sondage chargé avec succès.")
