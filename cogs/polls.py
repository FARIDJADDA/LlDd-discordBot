import discord
import asyncio
from discord.ext import commands


class Polls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

    @commands.hybrid_command(name="poll", description="Crée un sondage interactif avec réactions et une minuterie optionnelle.")
    async def poll(self, ctx: commands.Context, question: str, options: str, duration: int = 0):
        """
        Crée un sondage interactif avec une question, des options et une durée optionnelle.
        Exemple : /poll "Votre film préféré ?" "Inception, Matrix, Interstellar" 5
        """
        # Séparer les options fournies
        option_list = [option.strip() for option in options.split(",")]

        if len(option_list) < 2 or len(option_list) > 10:
            await ctx.send(embed=discord.Embed(
                title="❌ Erreur",
                description="Le sondage doit contenir entre **2 et 10 options**.",
                color=discord.Color.red()
            ))
            return

        # Création de l'embed pour le sondage
        description = "\n".join([f"{self.reactions[i]} {option}" for i, option in enumerate(option_list)])
        embed = discord.Embed(
            title="📊 Sondage",
            description=f"**{question}**\n\n{description}",
            color=discord.Color.dark_purple()
        )
        embed.set_footer(text=f"Créé par {ctx.author} • Durée : {duration} minute(s)" if duration > 0 else f"Créé par {ctx.author}", icon_url=ctx.author.avatar.url)

        # Envoi du sondage
        poll_message = await ctx.send(embed=embed)

        # Ajout des réactions correspondantes
        for i in range(len(option_list)):
            await poll_message.add_reaction(self.reactions[i])

        # Gestion de la minuterie
        if duration > 0:
            await asyncio.sleep(duration * 60)  # Convertir la durée en secondes

            # Récupérer les réactions pour compter les votes
            poll_message = await ctx.channel.fetch_message(poll_message.id)
            results = []
            for i, reaction in enumerate(poll_message.reactions[:len(option_list)]):
                results.append((reaction.count - 1, option_list[i]))  # -1 pour exclure la réaction du bot

            # Trier les résultats par nombre de votes
            results.sort(reverse=True, key=lambda x: x[0])

            # Générer un embed pour les résultats
            result_description = "\n".join([f"**{votes}** votes - {option}" for votes, option in results])
            result_embed = discord.Embed(
                title="📊 Résultats du sondage",
                description=f"**{question}**\n\n{result_description}",
                color=discord.Color.green()
            )
            result_embed.set_footer(text="Merci pour votre participation !")
            await ctx.send(embed=result_embed)

    @poll.error
    async def poll_error(self, ctx, error):
        """Gestion des erreurs pour la commande /poll."""
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=discord.Embed(
                title="❌ Erreur",
                description="Format incorrect. Utilise `/poll \"Question\" \"Option1, Option2, Option3\" [Durée en minutes]`.",
                color=discord.Color.red()
            ))
        else:
            await ctx.send(embed=discord.Embed(
                title="❌ Erreur inattendue",
                description=str(error),
                color=discord.Color.red()
            ))
            raise error


async def setup(bot: commands.Bot):
    """Ajoute la cog au bot."""
    await bot.add_cog(Polls(bot))
