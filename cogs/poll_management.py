import discord
from utils.logger import logger
from .bar import render_bar


class Poll:
    def __init__(self, question, options, multi_vote=False, voter_role=None):
        self.question = question
        self.options = options[:15]  # Limite à 15 options maximum
        self.multi_vote = multi_vote
        self.voter_role = voter_role
        self.votes = {option: 0 for option in self.options}
        self.user_votes = {}  # Dictionnaire pour suivre les votes des utilisateurs
        self.message = None
        self.ended = False

    def vote(self, user, option):
        """Gérer le vote d'un utilisateur pour une option."""
        if not self.multi_vote and user.id in self.user_votes:
            # Annuler le vote précédent si multi-vote désactivé
            previous_option = self.user_votes[user.id]
            self.votes[previous_option] -= 1

        # Enregistre le nouveau vote
        self.user_votes[user.id] = option
        self.votes[option] += 1

    def cancel_vote(self, user):
        """Annuler le vote d'un utilisateur."""
        if user.id in self.user_votes:
            previous_option = self.user_votes.pop(user.id)
            self.votes[previous_option] -= 1

    def render_results(self):
        """Générer les résultats du sondage sous forme de texte avec barres de progression."""
        total_votes = sum(self.votes.values())
        results = []

        for option, count in self.votes.items():
            part = (count / total_votes) * 100 if total_votes > 0 else 0
            bar = render_bar(20, part)  # Utilise render_bar pour générer une barre de progression
            results.append(f"{option}: {count} votes {bar} ({part:.1f}%)")

        return "\n".join(results)

    def is_user_allowed(self, user):
        """Vérifie si l'utilisateur est autorisé à voter."""
        if self.voter_role:
            return self.voter_role in [role.id for role in user.roles]
        return True  # Par défaut, tout le monde est autorisé

    def results(self):
        """Retourner les résultats triés par nombre de votes."""
        return sorted(self.votes.items(), key=lambda x: x[1], reverse=True)

async def setup(bot):
    pass