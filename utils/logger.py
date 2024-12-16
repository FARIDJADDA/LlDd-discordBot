from dotenv import load_dotenv
import os
import logging
from logging.handlers import RotatingFileHandler

# Charger les variables depuis le fichier `config`
load_dotenv(dotenv_path="config")


def setup_logger(log_file=None, level=logging.INFO, backup_count=5):
    """
    Configure le logger pour écrire dans un fichier et afficher dans la console.

    Args:
        log_file (str): Nom du fichier de log.
        level (int): Niveau de log (ex: logging.INFO, logging.DEBUG).
        backup_count (int): Nombre de sauvegardes de fichiers de log.

    Returns:
        logging.Logger: Instance configurée du logger.
    """
    # Format des messages de log
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Création du logger
    logger = logging.getLogger('discord_bot')

    # Éviter d'ajouter plusieurs fois les mêmes gestionnaires
    if logger.hasHandlers():
        return logger

    logger.setLevel(level)

    # Gestionnaire de rotation des fichiers de log
    if log_file:
        try:
            file_handler = RotatingFileHandler(
                log_file, maxBytes=5 * 1024 * 1024, backupCount=backup_count
            )
            file_handler.setFormatter(logging.Formatter(log_format))
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"⚠️ Impossible de créer le fichier de log {log_file}. Erreur : {e}")

    # Gestionnaire pour la console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(console_handler)

    return logger


# Charger les variables d'environnement depuis `config`
log_file_path = os.getenv('LOG_FILE', 'bot.log')  # Par défaut, `bot.log` si `LOG_FILE` n'est pas défini
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()  # Par défaut, niveau `INFO` si `LOG_LEVEL` n'est pas défini
log_backup_count = int(os.getenv('LOG_BACKUP_COUNT', 5))  # Nombre de sauvegardes de fichiers de log (par défaut 5)

# Mapping des niveaux de log
valid_log_levels = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "NOTSET": logging.NOTSET,
}

# Obtenir le niveau de log valide
log_level_value = valid_log_levels.get(log_level, logging.INFO)

# Création du logger principal
try:
    logger = setup_logger(log_file=log_file_path, level=log_level_value, backup_count=log_backup_count)
    logger.info(f"Logger configuré avec succès. Niveau : {log_level}, Fichier : {log_file_path}")
except Exception as e:
    print(f"⚠️ Erreur lors de la configuration du logger : {e}")


# Configurer le logger pour Discord
discord_logger = logging.getLogger("discord")
discord_logger.setLevel(logging.WARNING)  # Réduit les logs inutiles
discord_logger.addHandler(logging.StreamHandler())
logger.info("Logger Discord configuré avec succès.")
