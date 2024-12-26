import os
import json
from discord.ext import commands
from discord import ui, ButtonStyle
from blagues_api import BlaguesAPI
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv(dotenv_path="config")

# Initialiser l'API avec le token
token = os.getenv("BLAGUES_API_TOKEN")
if not token:
    raise ValueError("Le token de l'API Blagues n'a pas été trouvé. Assurez-vous qu'il est configuré dans le fichier .env.")

blagues = BlaguesAPI(token)

# Charger ou créer le fichier de configuration des catégories autorisées
CONFIG_FILE = "blague_config.json"
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {"allowed_categories": []}  # Par défaut, aucune restriction

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        json.dump(config, file, ensure_ascii=False, indent=4)

config = load_config()

# Créer une vue interactive pour les blagues
class JokeView(ui.View):
    def __init__(self, joke):
        super().__init__(timeout=None)
        self.joke = joke
        self.add_item(JokeButton(self.joke))

class JokeButton(ui.Button):
    def __init__(self, joke):
        super().__init__(label="Voir la réponse", style=ButtonStyle.primary)
        self.joke = joke

    async def callback(self, interaction):
        await interaction.response.edit_message(
            content=f"**{self.joke.joke}**\n\n||{self.joke.answer}||", view=None
        )

# Commandes pour les blagues
class JokeCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="blague", description="Obtenez une blague aléatoire.")
    async def joke(self, ctx):
        """Commande principale pour obtenir une blague aléatoire."""
        try:
            # Récupérer une blague aléatoire
            joke = await blagues.random()

            # Envoyer la blague avec une vue interactive
            await ctx.send(
                content=f"**{joke.joke}**\n\nCliquez sur le bouton ci-dessous pour révéler la réponse.",
                view=JokeView(joke)
            )
        except Exception as e:
            await ctx.send("❌ Une erreur s'est produite en récupérant une blague.")
            print(f"Erreur lors de la récupération de la blague : {e}")

    @commands.hybrid_command(name="autoriser_blague", description="Configurer les catégories de blagues autorisées.")
    async def configure_joke_categories(self, ctx, category: str):
        """Permet de configurer les catégories autorisées sur le serveur."""
        allowed_categories = config.get("allowed_categories", [])

        if category in allowed_categories:
            allowed_categories.remove(category)
            await ctx.send(f"❌ La catégorie '{category}' a été désactivée.")
        else:
            allowed_categories.append(category)
            await ctx.send(f"☑️ La catégorie '{category}' a été activée.")

        # Sauvegarder la configuration
        config["allowed_categories"] = allowed_categories
        save_config(config)

async def setup(bot):
    await bot.add_cog(JokeCommands(bot))
    print("☑️ Cog des blagues chargé avec succès.")
