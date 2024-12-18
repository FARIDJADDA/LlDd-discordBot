import discord
from discord.ext import commands
from dotenv import load_dotenv
from openai import AsyncOpenAI  # Nouvelle manière d'importer le client OpenAI
import os

# Chargement de la clé API OpenAI depuis le fichier .env
load_dotenv(dotenv_path="config")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialisation du client OpenAI
client_openai = AsyncOpenAI(api_key=OPENAI_API_KEY)


class ChatGPT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ask", description="Pose une question à ChatGPT.")
    async def ask(self, ctx: commands.Context, *, question: str):
        """
        Pose une question à ChatGPT et récupère une réponse.
        Exemple : /ask Quelle est la capitale de la France ?
        """
        # Vérifie si la clé API est configurée
        if not OPENAI_API_KEY:
            embed_error = discord.Embed(
                title="❌ Clé API manquante",
                description="La clé API OpenAI n'est pas configurée. Contactez l'administrateur du bot.",
                color=discord.Color.dark_red()
            )
            await ctx.send(embed=embed_error)
            return

        # Affichage de l'embed de chargement
        embed_loading = discord.Embed(
            title="💭 ChatGPT réfléchit...",
            description="Veuillez patienter pendant que je génère une réponse...",
            color=discord.Color.dark_purple()
        )
        loading_message = await ctx.send(embed=embed_loading)

        try:
            # Appel à l'API OpenAI avec la nouvelle syntaxe
            response = await client_openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": question}
                ],
                max_tokens=100,  # Limitation des tokens
                temperature=0.7  # Température pour varier les réponses
            )

            # Extraction de la réponse
            answer = response.choices[0].message.content.strip()

            # Embed pour afficher la réponse
            embed_response = discord.Embed(
                title="🤖 Réponse de ChatGPT",
                description=answer,
                color=discord.Color.green()
            )
            embed_response.set_footer(text=f"Question posée par {ctx.author}", icon_url=ctx.author.avatar.url)

            await loading_message.edit(embed=embed_response)

        except Exception as e:
            # Gestion des erreurs API
            embed_error = discord.Embed(
                title="❌ Erreur",
                description="Une erreur est survenue lors de la génération de la réponse. Veuillez réessayer plus tard.",
                color=discord.Color.red()
            )
            await loading_message.edit(embed=embed_error)
            print(f"Erreur OpenAI : {e}")


async def setup(bot: commands.Bot):
    """Ajoute la cog ChatGPT au bot."""
    await bot.add_cog(ChatGPT(bot))
