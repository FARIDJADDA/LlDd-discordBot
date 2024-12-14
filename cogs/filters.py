from discord.ext import commands
import discord
import time
import json
import os
from utils.logger import logger  # Utilisation du logger global


class Filters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_messages = {}
        self.banned_words = self.load_banned_words()

    def load_banned_words(self):
        """Charger la liste des mots interdits depuis un fichier JSON"""
        try:
            with open("banned_words.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            logger.warning("Fichier 'banned_words.json' introuvable. Utilisation d'une liste par défaut.")
            return ["pute", "cul", "fuck", "porno"]

    def save_banned_words(self):
        """Sauvegarder la liste des mots interdits dans un fichier JSON"""
        try:
            with open("banned_words.json", "w") as file:
                json.dump(self.banned_words, file, indent=4)
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des mots interdits : {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Filtre les messages interdits et détecte le spam"""
        if message.author == self.bot.user:
            return

        # Détection des mots interdits
        lowered_content = message.content.lower()
        if any(word in lowered_content for word in self.banned_words):
            await message.delete()
            await message.channel.send(f"{message.author.mention}, ton message contient un mot interdit.")
            log_channel = discord.utils.get(message.guild.channels, name="logs")
            log_message = f"Message interdit supprimé : '{message.content}' par {message.author} dans {message.channel}"
            logger.info(log_message)  # Log local

            if log_channel:
                await log_channel.send(f"🚫 {message.author.mention}, ton message a été supprimé pour contenu interdit.")
            return

        # Détection de spam
        now = time.time()
        if message.author.id not in self.user_messages:
            self.user_messages[message.author.id] = []
        self.user_messages[message.author.id].append(now)
        self.user_messages[message.author.id] = [t for t in self.user_messages[message.author.id] if now - t < 10]

        if len(self.user_messages[message.author.id]) > 5:
            await message.delete()
            if not getattr(message.author, "spam_warning_sent", False):
                await message.channel.send(f"{message.author.mention}, arrête de spammer !")
                setattr(message.author, "spam_warning_sent", True)

            # Log pour spam
            log_message = f"Spam détecté : {message.author} dans {message.channel}"
            logger.info(log_message)  # Log local
            log_channel = discord.utils.get(message.guild.channels, name="logs")
            if log_channel:
                await log_channel.send(f"🚫 {message.author.mention}, ton message a été supprimé pour spam.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def add_banned_word(self, ctx, *, word):
        """Ajouter un mot à la liste des mots interdits"""
        if word not in self.banned_words:
            self.banned_words.append(word)
            self.save_banned_words()
            await ctx.send(f"Le mot `{word}` a été ajouté à la liste des mots interdits.")
            logger.info(f"Mot ajouté à la liste interdite : {word}")
        else:
            await ctx.send(f"Le mot `{word}` est déjà dans la liste.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def remove_banned_word(self, ctx, *, word):
        """Retirer un mot de la liste des mots interdits"""
        if word in self.banned_words:
            self.banned_words.remove(word)
            self.save_banned_words()
            await ctx.send(f"Le mot `{word}` a été retiré de la liste des mots interdits.")
            logger.info(f"Mot retiré de la liste interdite : {word}")
        else:
            await ctx.send(f"Le mot `{word}` n'est pas dans la liste.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def list_banned_words(self, ctx):
        """Lister tous les mots interdits"""
        banned_words_list = ", ".join(self.banned_words)
        await ctx.send(f"📜 Liste des mots interdits : {banned_words_list}")
        logger.info("Liste des mots interdits envoyée.")


async def setup(bot):
    await bot.add_cog(Filters(bot))
