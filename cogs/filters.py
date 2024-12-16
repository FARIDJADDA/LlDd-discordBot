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
        self.banned_words = self.load_banned_words()

    def load_banned_words(self):
        """Charge la liste des mots interdits depuis un fichier JSON."""
        try:
            if os.path.exists("banned_words.json"):
                with open("banned_words.json", "r") as file:
                    return json.load(file)
            else:
                logger.warning("Fichier 'banned_words.json' introuvable. Utilisation d'une liste par défaut.")
                return ["pute", "cul", "fuck", "porno"]
        except Exception as e:
            logger.error(f"Erreur lors du chargement des mots interdits : {e}")
            return ["pute", "cul", "fuck", "porno"]

    def save_banned_words(self):
        """Sauvegarde la liste des mots interdits dans un fichier JSON."""
        try:
            with open("banned_words.json", "w") as file:
                json.dump(self.banned_words, file, indent=4)
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
            await message.channel.send(f"{message.author.mention}, ton message contient un mot interdit.")
            log_channel = discord.utils.get(message.guild.channels, name="logs")
            if log_channel:
                await log_channel.send(f"🚫 {message.author.mention}, ton message a été supprimé pour contenu interdit.")
            logger.info(f"Message supprimé : '{message.content}' de {message.author}.")

        # Détection de spam
        now = asyncio.get_event_loop().time()
        if message.author.id not in self.user_messages:
            self.user_messages[message.author.id] = []
        self.user_messages[message.author.id].append(now)
        self.user_messages[message.author.id] = [t for t in self.user_messages[message.author.id] if now - t < 10]

        if len(self.user_messages[message.author.id]) > 5:
            await message.delete()
            if not getattr(message.author, "spam_warning_sent", False):
                await message.channel.send(f"{message.author.mention}, arrête de spammer !")
                setattr(message.author, "spam_warning_sent", True)
            logger.info(f"Spam détecté et message supprimé pour {message.author}.")

    @commands.hybrid_command(name="add_banned_word", description="Ajoute un mot à la liste des mots interdits.")
    async def add_banned_word(self, ctx: commands.Context, word: str):
        """Ajoute un mot à la liste des mots interdits."""
        if word not in self.banned_words:
            self.banned_words.append(word)
            self.save_banned_words()
            await ctx.send(f"✅ Le mot `{word}` a été ajouté à la liste des mots interdits.")
            logger.info(f"Mot ajouté : {word}")
        else:
            await ctx.send(f"❌ Le mot `{word}` est déjà dans la liste.")

    @commands.hybrid_command(name="remove_banned_word", description="Retire un mot de la liste des mots interdits.")
    async def remove_banned_word(self, ctx: commands.Context, word: str):
        """Retire un mot de la liste des mots interdits."""
        if word in self.banned_words:
            self.banned_words.remove(word)
            self.save_banned_words()
            await ctx.send(f"✅ Le mot `{word}` a été retiré de la liste des mots interdits.")
            logger.info(f"Mot retiré : {word}")
        else:
            await ctx.send(f"❌ Le mot `{word}` n'est pas dans la liste.")

    @commands.hybrid_command(name="list_banned_words", description="Affiche la liste des mots interdits.")
    async def list_banned_words(self, ctx: commands.Context):
        """Affiche la liste des mots interdits."""
        banned_words_list = ", ".join(self.banned_words)
        await ctx.send(f"📜 Liste des mots interdits : {banned_words_list}")
        logger.info("Liste des mots interdits envoyée.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Filters(bot))
