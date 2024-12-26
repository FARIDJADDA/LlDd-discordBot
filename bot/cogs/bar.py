def render_bar(max_length, percentage):
    """
    Rendu d'une barre de progression.

    :param max_length: Longueur maximale de la barre.
    :param percentage: Pourcentage de progression (0-100).
    :return: Représentation de la barre.
    """
    filled_blocks = int(max_length * (percentage / 100))
    empty_blocks = max_length - filled_blocks
    bar = f"[{'█' * filled_blocks}{' ' * empty_blocks}]"
    return bar

async def setup(bot):
    pass
