import discord
import aiohttp
from discord.ext import commands
from dotenv import load_dotenv
import os

# Chargement des variables d'environnement
load_dotenv(dotenv_path="config")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Liste des modèles Hugging Face à tester dans l'ordre
MODELS = [
    "bigscience/bloom-560m",          # Premier modèle à tester
    "tiiuae/falcon-7b-instruct",      # Deuxième modèle
    "google/flan-t5-small"           # Troisième modèle
]

# URL de base pour l'API Hugging Face
API_BASE_URL = "https://api-inference.huggingface.co/models/"


class HuggingFaceChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def query_model(self, model_url: str, headers: dict, payload: dict) -> str:
        """
        Effectue une requête à un modèle Hugging Face et renvoie la réponse ou une erreur 503.
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(model_url, headers=headers, json=payload) as response:
                if response.status == 503:
                    raise Exception("503")  # Modèle indisponible
                elif response.status != 200:
                    raise Exception(f"Erreur API : {response.status}")
                result = await response.json()
                return result[0].get('generated_text', 'Aucune réponse générée.')

    @commands.hybrid_command(name="ask_hf", description="Pose une question à un modèle Hugging Face.")
    async def ask_hf(self, ctx: commands.Context, *, question: str):
        """
        Essaie plusieurs modèles Hugging Face et renvoie une réponse.
        """
        embed_loading = discord.Embed(
            title="💭 Hugging Face réfléchit...",
            description="Veuillez patienter pendant que je génère une réponse...",
            color=discord.Color.dark_purple()
        )
        loading_message = await ctx.send(embed=embed_loading)

        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        payload = {"inputs": question}

        for model in MODELS:
            try:
                # Construire l'URL du modèle
                model_url = f"{API_BASE_URL}{model}"
                print(f"🔄 Tentative avec le modèle : {model}")
                # Appeler le modèle
                answer = await self.query_model(model_url, headers, payload)

                # Si une réponse est obtenue, on affiche l'embed final
                embed_response = discord.Embed(
                    title="🤖 Réponse de Hugging Face",
                    description=answer,
                    color=discord.Color.dark_teal()
                )
                embed_response.set_footer(text=f"Question posée par {ctx.author} • Modèle : {model}",
                                          icon_url=ctx.author.avatar.url)
                await loading_message.edit(embed=embed_response)
                return  # On sort de la fonction si la réponse est réussie

            except Exception as e:
                # Gestion des erreurs pour chaque modèle
                if str(e) == "503":
                    print(f"⚠️ Le modèle {model} est indisponible (503). Tentative avec le suivant...")
                else:
                    print(f"❌ Erreur avec le modèle {model} : {e}")

        # Si aucun modèle n'a fonctionné
        embed_error = discord.Embed(
            title="❌ Tous les modèles sont indisponibles",
            description="Impossible de générer une réponse pour le moment. Veuillez réessayer plus tard.",
            color=discord.Color.dark_embed()
        )
        await loading_message.edit(embed=embed_error)


async def setup(bot: commands.Bot):
    """Ajoute la cog Hugging Face au bot."""
    await bot.add_cog(HuggingFaceChat(bot))
