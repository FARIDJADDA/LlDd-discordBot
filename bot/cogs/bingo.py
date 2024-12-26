import discord
import random
from discord.ext import commands
from utils.logger import logger

class Bingo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_bingo = None
        self.players = []

    @commands.hybrid_command(name="bingo", help="Commandes pour gérer le jeu de Bingo.")
    async def bingo(self, ctx):
        """
        Commande d'entrée pour le Bingo. Affiche les options disponibles.
        """
        embed = discord.Embed(
            title="✨ Commandes Bingo",
            description="Voici les commandes disponibles :\n\n"
                        "- **`/bingo start`** : Démarrer une partie de Bingo.\n"
                        "- **`/bingo join`** : Rejoindre une partie en cours.\n"
                        "- **`/bingo stop`** : Arrêter la partie en cours.",
            color=discord.Color.purple()
        )
        embed.set_footer(text="LlddBot - Que le jeu commence !", icon_url=self.bot.user.avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="bingo_start", help="Démarre un jeu de Bingo.")
    async def bingo_start(self, ctx: commands.Context, max_number: int = 100, hints: bool = False):
        """
        Démarre un jeu de Bingo.
        :param max_number: Le nombre maximum pour le Bingo (par défaut 100).
        :param hints: Activer ou non les indices (par défaut False).
        """
        if self.current_bingo:
            await ctx.send(embed=discord.Embed(
                title="⚠️ Un jeu est déjà en cours !",
                description="Attendez que le jeu actuel se termine avant de démarrer un nouveau.",
                color=discord.Color.purple()
            ))
            return

        if max_number < 10:
            await ctx.send(embed=discord.Embed(
                title="❌ Nombre invalide",
                description="Le nombre maximum doit être supérieur ou égal à 10.",
                color=discord.Color.dark_embed()
            ))
            return

        self.current_bingo = {
            "number": random.randint(1, max_number),
            "guesses": [],
            "max_number": max_number,
            "hints": hints,
            "start_time": discord.utils.utcnow()
        }
        self.players = []

        embed = discord.Embed(
            title="✨ Bingo lancé !",
            description=f"Un nombre entre **1** et **{max_number}** a été choisi.\nTrouvez-le pour gagner !",
            color=discord.Color.purple()
        )
        embed.set_footer(text="Bonne chance à tous !", icon_url=self.bot.user.avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="bingo_join", help="Rejoindre un jeu de Bingo en cours.")
    async def bingo_join(self, ctx: commands.Context):
        """
        Permet à un joueur de rejoindre une partie de Bingo en cours.
        """
        if not self.current_bingo:
            await ctx.send(embed=discord.Embed(
                title="❌ Aucun jeu actif",
                description="Aucun jeu de Bingo n'est actuellement en cours. Lancez une partie avec `/bingo start`.",
                color=discord.Color.dark_embed()
            ))
            return

        if ctx.author in self.players:
            await ctx.send(embed=discord.Embed(
                title="⚠️ Déjà inscrit",
                description="Vous avez déjà rejoint la partie en cours.",
                color=discord.Color.purple()
            ))
            return

        self.players.append(ctx.author)
        await ctx.send(embed=discord.Embed(
            title="☑️ Inscription réussie",
            description=f"{ctx.author.mention} a rejoint la partie de Bingo !",
            color=discord.Color.dark_teal()
        ))

    @commands.hybrid_command(name="bingo_stop", help="Termine le jeu de Bingo en cours.")
    @commands.has_permissions(administrator=True)
    async def bingo_stop(self, ctx: commands.Context):
        """
        Termine le jeu de Bingo en cours.
        """
        if not self.current_bingo:
            await ctx.send(embed=discord.Embed(
                title="❌ Aucun jeu en cours",
                description="Il n'y a aucun jeu de Bingo actif.",
                color=discord.Color.dark_embed()
            ))
            return

        embed = discord.Embed(
            title="🛑 Bingo terminé",
            description="Le jeu de Bingo en cours a été annulé.",
            color=discord.Color.purple()
        )
        embed.add_field(name="🎯 Nombre à trouver", value=str(self.current_bingo["number"]), inline=False)
        await ctx.send(embed=embed)
        self.current_bingo = None
        self.players = []

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not self.current_bingo or message.author.bot:
            return

        try:
            guess = int(message.content)
        except ValueError:
            return

        if guess in self.current_bingo["guesses"]:
            await message.channel.send(f"{message.author.mention}, ce nombre a déjà été proposé !", delete_after=5)
            return

        self.current_bingo["guesses"].append(guess)

        if guess == self.current_bingo["number"]:
            elapsed_time = (discord.utils.utcnow() - self.current_bingo["start_time"]).seconds
            embed = discord.Embed(
                title="🎉 Jeu du Bingo",
                description=f"Le vainqueur du bingo est {message.author.mention} !",
                color=discord.Color.dark_teal()
            )
            embed.add_field(name="🎯 Nombre trouvé", value=str(self.current_bingo["number"]), inline=False)
            embed.set_footer(text=f"Le nombre a été trouvé en {elapsed_time} secondes !", icon_url=self.bot.user.avatar.url)
            await message.channel.send(embed=embed)
            self.current_bingo = None
            self.players = []
            return

        if self.current_bingo["hints"] and self.current_bingo["max_number"] > 200:
            number = self.current_bingo["number"]
            if abs(guess - number) <= self.current_bingo["max_number"] * 0.1:
                await message.add_reaction("🔥")
            elif abs(guess - number) <= self.current_bingo["max_number"] * 0.3:
                hint = "plus haut" if guess < number else "plus bas"
                await message.channel.send(f"🔍 Indice : Essayez **{hint}** !", delete_after=5)

async def setup(bot: commands.Bot):
    """Ajoute le cog au bot."""
    await bot.add_cog(Bingo(bot))
    logger.info("☑️ Cog Bingo ajouté avec succès.")
