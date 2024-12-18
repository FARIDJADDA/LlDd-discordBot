import asyncio
import json
import os
import discord
from discord.ext import commands
from utils.logger import logger

class Filters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_messages = {}
        self.banned_words_file = "data/banned_words.json"  # Nouveau chemin
        self.banned_words = self.load_banned_words()

    def load_banned_words(self):
        """Charge la liste des mots interdits depuis un fichier JSON."""
        os.makedirs("data", exist_ok=True)  # Crée le dossier data s'il n'existe pas
        if not os.path.exists(self.banned_words_file):
            logger.warning(f"Fichier '{self.banned_words_file}' introuvable. Création avec des valeurs par défaut.")
            default_words = ["spam", "insulte", "mot_interdit"]
            with open(self.banned_words_file, "w") as file:
                json.dump(default_words, file, indent=4)
            return default_words

        try:
            with open(self.banned_words_file, "r") as file:
                return json.load(file)
        except Exception as e:
            logger.error(f"Erreur lors du chargement des mots interdits : {e}")
            return []

    def save_banned_words(self):
        """Sauvegarde la liste des mots interdits dans un fichier JSON."""
        try:
            with open(self.banned_words_file, "w") as file:
                json.dump(self.banned_words, file, indent=4)
            logger.info(f"Liste des mots interdits sauvegardée avec succès dans '{self.banned_words_file}'.")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des mots interdits : {e}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Filtre les messages interdits et détecte le spam."""
        if message.author.bot:
            return

        # Détection des mots interdits
        lowered_content = message.content.lower()
        if any(word in lowered_content for word in self.banned_words):
            await message.delete()

            # Chargement de l'image locale pour l'embed
            image_path = "assets/lldd_bot_dsgn.jpg"
            if not os.path.exists(image_path):
                logger.warning(f"⚠️ L'image '{image_path}' est introuvable.")
                file = None
            else:
                file = discord.File(image_path, filename="lldd_bot_dsgn.jpg")

            embed = discord.Embed(
                title="🚫 Message supprimé",
                description=f"**{message.author.mention}**, ton message contenait un mot interdit !",
                color=discord.Color.dark_red(),
            )
            if file:
                embed.set_thumbnail(url="attachment://lldd_bot_dsgn.jpg")

            await message.channel.send(file=file, embed=embed, delete_after=5)
            logger.info(f"Message supprimé : '{message.content}' de {message.author}.")
            return

        # Détection de spam
        now = asyncio.get_event_loop().time()
        if message.author.id not in self.user_messages:
            self.user_messages[message.author.id] = []
        self.user_messages[message.author.id].append(now)
        self.user_messages[message.author.id] = [t for t in self.user_messages[message.author.id] if now - t < 10]

        if len(self.user_messages[message.author.id]) > 5:
            await message.delete()
            if not getattr(message.author, "spam_warning_sent", False):
                embed = discord.Embed(
                    title="⚠️ Avertissement de spam",
                    description=f"**{message.author.mention}**, arrête de spammer !",
                    color=discord.Color.dark_purple(),
                )
                await message.channel.send(embed=embed, delete_after=5)
                setattr(message.author, "spam_warning_sent", True)
            logger.info(f"Spam détecté et message supprimé pour {message.author}.")

    @commands.hybrid_command(name="add_banned_word", description="Ajoute un mot à la liste des mots interdits.")
    async def add_banned_word(self, ctx: commands.Context, word: str):
        """Ajoute un mot à la liste des mots interdits."""
        if word not in self.banned_words:
            self.banned_words.append(word)
            self.save_banned_words()
            await ctx.send(embed=discord.Embed(
                title="✅ Mot ajouté",
                description=f"Le mot **{word}** a été ajouté à la liste des mots interdits.",
                color=discord.Color.green(),
            ))
            logger.info(f"Mot ajouté : {word}")
        else:
            await ctx.send(embed=discord.Embed(
                title="⚠️ Mot existant",
                description=f"Le mot **{word}** est déjà dans la liste des mots interdits.",
                color=discord.Color.orange(),
            ))

    @commands.hybrid_command(name="remove_banned_word", description="Retire un mot de la liste des mots interdits.")
    async def remove_banned_word(self, ctx: commands.Context, word: str):
        """Retire un mot de la liste des mots interdits."""
        if word in self.banned_words:
            self.banned_words.remove(word)
            self.save_banned_words()
            await ctx.send(embed=discord.Embed(
                title="✅ Mot retiré",
                description=f"Le mot **{word}** a été retiré de la liste des mots interdits.",
                color=discord.Color.green(),
            ))
            logger.info(f"Mot retiré : {word}")
        else:
            await ctx.send(embed=discord.Embed(
                title="❌ Mot introuvable",
                description=f"Le mot **{word}** n'est pas dans la liste des mots interdits.",
                color=discord.Color.red(),
            ))

    @commands.hybrid_command(name="list_banned_words", description="Affiche la liste des mots interdits.")
    async def list_banned_words(self, ctx: commands.Context):
        """Affiche la liste des mots interdits."""
        banned_words_list = ", ".join(self.banned_words)
        embed = discord.Embed(
            title="📜 Liste des mots interdits",
            description=banned_words_list if self.banned_words else "Aucun mot interdit configuré.",
            color=discord.Color.dark_purple(),
        )
        embed.set_footer(text=f"Demandé par {ctx.author.name}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)
        logger.info("Liste des mots interdits envoyée.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Filters(bot))
