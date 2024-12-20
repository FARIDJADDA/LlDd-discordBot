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
        ]

    @commands.hybrid_command(name="quiz", description="Lance un quiz simple sur le gaming.")
    async def quiz(self, ctx: commands.Context):
        """Pose une question sur le gaming avec 3 chances pour répondre."""
        question = random.choice(self.questions)
        attempts = 3

        embed = discord.Embed(
            title="🎮 **Quiz Gaming**",
            description=f"❓ {question['question']}\n\nTu as **{attempts} chances** de répondre correctement !",
            color=discord.Color.dark_embed()
        )
        embed.set_thumbnail(url="https://cdn.pixabay.com/photo/2024/05/24/16/40/ai-generated-8785422_640.jpg")  # Placeholder
        embed.set_footer(text=f"Bonne chance, {ctx.author.name} !", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed)

        def check(message):
            return message.channel == ctx.channel and message.author == ctx.author

        while attempts > 0:
            try:
                msg = await self.bot.wait_for("message", check=check, timeout=30.0)
                if msg.content.lower() == question["answer"].lower():
                    await ctx.send(embed=discord.Embed(
                        title="✅ Bonne réponse !",
                        description=f"🎉 Félicitations {ctx.author.mention} ! La réponse était **{question['answer']}**.",
                        color=discord.Color.dark_teal()
                    ))
                    return
                else:
                    attempts -= 1
                    await ctx.send(embed=discord.Embed(
                        title="❌ Mauvaise réponse",
                        description=f"Il te reste **{attempts} chances**.",
                        color=discord.Color.dark_purple()
                    ))
            except asyncio.TimeoutError:
                await ctx.send(embed=discord.Embed(
                    title="⏳ Temps écoulé !",
                    description=f"🕒 La bonne réponse était : **{question['answer']}**.",
                    color=discord.Color.dark_gray()
                ))
                return

        await ctx.send(embed=discord.Embed(
            title="❌ Plus de tentatives !",
            description=f"La bonne réponse était : **{question['answer']}**.",
            color=discord.Color.dark_embed()
        ))

    @commands.hybrid_command(name="dice_roll", description="Lance un ou plusieurs dés avec un nombre de faces personnalisé.")
    async def dice_roll(self, ctx: commands.Context, number_of_dice: int = 1, faces: int = 6):
        """Lance plusieurs dés avec un nombre de faces spécifié."""
        if number_of_dice <= 0 or faces <= 0:
            await ctx.send(embed=discord.Embed(
                title="⚠️ Erreur",
                description="Le nombre de dés et le nombre de faces doivent être supérieurs à 0.",
                color=discord.Color.dark_embed()
            ))
            return

        rolls = [random.randint(1, faces) for _ in range(number_of_dice)]
        rolls_str = ", ".join(map(str, rolls))
        total = sum(rolls)

        embed = discord.Embed(
            title="🎲 **Lancer de dés**",
            description=f"**Résultat :** {rolls_str}\n**Total :** {total}",
            color=discord.Color.dark_purple()  # Couleur Demon Slayer
        )
        embed.set_thumbnail(url="https://cdn.pixabay.com/photo/2024/05/24/16/40/ai-generated-8785422_640.jpg")  # Placeholder
        embed.set_footer(text=f"Lancé par {ctx.author.name}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="random_pick", description="Choisis un utilisateur au hasard parmi une liste.")
    async def random_pick(self, ctx: commands.Context, *, members: str):
        """Choisis un membre au hasard parmi une liste donnée."""
        try:
            mentions = members.split(",")
            valid_members = [discord.utils.get(ctx.guild.members, name=mention.strip()) for mention in mentions]
            valid_members = [member for member in valid_members if member]

            if not valid_members:
                await ctx.send(embed=discord.Embed(
                    title="⚠️ Erreur",
                    description="Aucun membre valide trouvé. Vérifiez vos mentions.",
                    color=discord.Color.dark_embed()
                ))
                return

            chosen_one = random.choice(valid_members)
            embed = discord.Embed(
                title="🎯 **Choix aléatoire**",
                description=f"🎉 Le membre choisi est : **{chosen_one.mention}** !",
                color=discord.Color.dark_embed()
            )
            embed.set_thumbnail(url="https://cdn.pixabay.com/photo/2024/05/24/16/40/ai-generated-8785422_640.jpg")  # Placeholder
            embed.set_footer(text=f"Demandé par {ctx.author.name}", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(embed=discord.Embed(
                title="❌ Erreur inattendue",
                description="Une erreur est survenue lors de l'exécution de la commande.",
                color=discord.Color.dark_embed()
            ))
            print(f"Erreur random_pick : {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Games(bot))
