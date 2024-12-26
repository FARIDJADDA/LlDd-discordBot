import os
import logging
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
from pythonjsonlogger import jsonlogger
from dotenv import load_dotenv

# Charger les variables d'environnement depuis `config`
load_dotenv(dotenv_path="config")


def setup_logger(log_file=None, level=logging.INFO, backup_count=5):
    """
    Configure le logger pour écrire dans un fichier et afficher dans la console.
    Ajoute un gestionnaire JSON pour analyser les logs si nécessaire.

    Args:
        log_file (str): Chemin du fichier de log.
        level (int): Niveau de log.
        backup_count (int): Nombre de sauvegardes des fichiers de log.

    Returns:
        logging.Logger: Instance configurée du logger.
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logger = logging.getLogger('discord_bot')

    if logger.hasHandlers():
        return logger  # Évite les doublons

    logger.setLevel(level)

    # Vérifier si le dossier du fichier de log existe
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Gestionnaire de rotation basée sur la date
        try:
            file_handler = TimedRotatingFileHandler(
                log_file, when="midnight", interval=1, backupCount=backup_count, encoding="utf-8"
            )
            file_handler.setFormatter(logging.Formatter(log_format))
            file_handler.setLevel(logging.DEBUG)  # DEBUG+ dans le fichier
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"⚠️ Impossible de configurer le fichier de log : {e}")

        # Gestionnaire de logs JSON pour analyse externe
        json_file = log_file.replace(".log", ".json")
        try:
            json_handler = RotatingFileHandler(json_file, maxBytes=5 * 1024 * 1024, backupCount=backup_count)
            json_formatter = jsonlogger.JsonFormatter(log_format)
            json_handler.setFormatter(json_formatter)
            json_handler.setLevel(logging.DEBUG)
            logger.addHandler(json_handler)
        except Exception as e:
            print(f"⚠️ Impossible de configurer le fichier JSON de log : {e}")

    # Gestionnaire pour la console (INFO+)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(console_handler)

    return logger


# Variables d'environnement pour la configuration
log_file_path = os.getenv('LOG_FILE', 'logs/bot.log')
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
log_backup_count = int(os.getenv('LOG_BACKUP_COUNT', 5))

valid_log_levels = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "NOTSET": logging.NOTSET,
}

log_level_value = valid_log_levels.get(log_level, logging.INFO)

# Création du logger principal
try:
    logger = setup_logger(log_file=log_file_path, level=log_level_value, backup_count=log_backup_count)
    logger.info(f"Logger configuré avec succès. Niveau : {log_level}, Fichier : {log_file_path}")
except Exception as e:
    print(f"⚠️ Erreur lors de la configuration du logger : {e}")

# Configurer les logs Discord avec un niveau configurable
discord_log_level = os.getenv('DISCORD_LOG_LEVEL', 'WARNING').upper()
discord_logger = logging.getLogger("discord")
discord_logger.setLevel(valid_log_levels.get(discord_log_level, logging.WARNING))
discord_logger.addHandler(logging.StreamHandler())
logger.info("Logger Discord configuré avec succès.")

# Exemple pour envoyer des logs critiques dans un salon Discord
class DiscordErrorHandler(logging.Handler):
    def __init__(self, bot, channel_id):
        super().__init__()
        self.bot = bot
        self.channel_id = channel_id

    async def send_error(self, message):
        channel = self.bot.get_channel(self.channel_id)
        if channel:
            await channel.send(f"⚠️ **Erreur Critique** : {message}")

    def emit(self, record):
        if record.levelno >= logging.CRITICAL:
            log_entry = self.format(record)
            self.bot.loop.create_task(self.send_error(log_entry))


# Exemple d'initialisation du gestionnaire d'erreur critique :
# discord_handler = DiscordErrorHandler(bot, channel_id=1234567890)
# discord_handler.setLevel(logging.CRITICAL)
# discord_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
# logger.addHandler(discord_handler)
