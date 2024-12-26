import discord
from discord.ext import commands
from discord.ui import Button, View
import random


class MorpionGame:
    def __init__(self, player1, player2=None, difficulty="Facile"):
        self.player1 = player1
        self.player2 = player2 or "LlddBot"
        self.difficulty = difficulty
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.current_player = player1
        self.winner = None

    def make_move(self, row, col):
        if self.board[row][col] == " ":
            self.board[row][col] = "X" if self.current_player == self.player1 else "O"
            if self.check_winner(row, col):
                self.winner = self.current_player
            elif self.check_draw():
                self.winner = "draw"
            else:
                self.current_player = self.player1 if self.current_player != self.player1 else self.player2
            return True
        return False

    def bot_move(self):
        if self.difficulty == "Facile":
            self.random_move()
        elif self.difficulty == "Normale":
            if not self.block_or_win_move():
                self.random_move()
        elif self.difficulty == "Difficile":
            self.minimax_move()

    def random_move(self):
        empty_cells = [(row, col) for row in range(3) for col in range(3) if self.board[row][col] == " "]
        if empty_cells:
            row, col = random.choice(empty_cells)
            self.make_move(row, col)

    def block_or_win_move(self):
        for symbol in ["O", "X"]:  # Check for winning move (O) first, then blocking move (X)
            for row in range(3):
                for col in range(3):
                    if self.board[row][col] == " ":
                        self.board[row][col] = symbol
                        if self.check_winner(row, col):
                            self.board[row][col] = " "  # Reset cell
                            self.make_move(row, col)
                            return True
                        self.board[row][col] = " "  # Reset cell
        return False

    def minimax_move(self):
        best_score = float('-inf')
        best_move = None

        for row in range(3):
            for col in range(3):
                if self.board[row][col] == " ":
                    self.board[row][col] = "O"
                    score = self.minimax(0, False)
                    self.board[row][col] = " "
                    if score > best_score:
                        best_score = score
                        best_move = (row, col)

        if best_move:
            self.make_move(*best_move)

    def minimax(self, depth, is_maximizing):
        if self.check_draw():
            return 0
        for row in range(3):
            for col in range(3):
                if self.board[row][col] != " ":
                    if self.check_winner(row, col):
                        return 1 if is_maximizing else -1

        if is_maximizing:
            best_score = float('-inf')
            for row in range(3):
                for col in range(3):
                    if self.board[row][col] == " ":
                        self.board[row][col] = "O"
                        score = self.minimax(depth + 1, False)
                        self.board[row][col] = " "
                        best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for row in range(3):
                for col in range(3):
                    if self.board[row][col] == " ":
                        self.board[row][col] = "X"
                        score = self.minimax(depth + 1, True)
                        self.board[row][col] = " "
                        best_score = min(score, best_score)
            return best_score

    def check_winner(self, row, col):
        symbol = self.board[row][col]
        return (
            all(self.board[row][i] == symbol for i in range(3)) or
            all(self.board[i][col] == symbol for i in range(3)) or
            all(self.board[i][i] == symbol for i in range(3)) or
            all(self.board[i][2 - i] == symbol for i in range(3))
        )

    def check_draw(self):
        return all(cell != " " for row in self.board for cell in row)

    def render_board(self):
        return "\n".join([" | ".join(row) for row in self.board])


class MorpionButton(Button):
    def __init__(self, row, col, game):
        super().__init__(style=discord.ButtonStyle.secondary, label="⬜", row=row)
        self.row = row
        self.col = col
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.game.current_player:
            await interaction.response.send_message("⚠️ Ce n'est pas votre tour !", ephemeral=True)
            return

        # Set the correct label and style before checking for winner
        current_player_symbol = "✖️" if self.game.current_player == self.game.player1 else "🔴"
        self.label = current_player_symbol
        self.style = (
            discord.ButtonStyle.secondary if current_player_symbol == "✖️" else discord.ButtonStyle.secondary
        )
        self.disabled = True

        if self.game.make_move(self.row, self.col):
            if self.game.winner:
                self.view.disable_all_items()
                winner_message = (
                    f"🏆 {self.game.winner.mention} a triomphé ! 🫡"
                    if isinstance(self.game.winner, discord.Member) else ("🏆 LlddBot a triomphé ! 🫡" if self.game.winner == "LlddBot" else "🤝 **Match nul !**")
                )
                await interaction.response.edit_message(
                    content=None,
                    embed=self.view.create_embed(
                        f"🎮 **Morpion - Résultat Final** 🎮\n\n{self.game.render_board()}\n\n{winner_message}",
                        discord.Color.dark_purple(),
                    ),
                    view=self.view,
                )
                # Terminer la partie
                self.view.end_game(interaction, self.game)
            else:
                current_player = self.game.current_player.mention if isinstance(self.game.current_player, discord.Member) else "LlddBot"
                await interaction.response.edit_message(
                    content=None,
                    embed=self.view.create_embed(
                        f"🎮 **Morpion** 🎮\n\n{self.game.render_board()}\n⚔️ À {current_player} de jouer !",
                        discord.Color.purple(),
                    ),
                    view=self.view,
                )

                if self.game.current_player == "LlddBot":
                    self.game.bot_move()
                    for child in self.view.children:
                        if isinstance(child, MorpionButton) and self.game.board[child.row][child.col] != " ":
                            child.label = "✖️" if self.game.board[child.row][child.col] == "X" else "🔴"
                            child.style = (
                                discord.ButtonStyle.secondary if child.label == "✖️" else discord.ButtonStyle.secondary
                            )
                            child.disabled = True

                    if self.game.winner:
                        self.view.disable_all_items()
                        winner_message = (
                            f"🏆 {self.game.winner.mention} a triomphé ! 🫡"
                            if isinstance(self.game.winner, discord.Member) else ("🏆 LlddBot a triomphé ! 🫡" if self.game.winner == "LlddBot" else "🤝 **Match nul !**")
                        )
                        await interaction.message.edit(
                            embed=self.view.create_embed(
                                f"🎮 **Morpion - Résultat Final** 🎮\n\n{self.game.render_board()}\n\n{winner_message}",
                                discord.Color.dark_purple(),
                            ),
                            view=self.view,
                        )
                        # Terminer la partie
                        self.view.end_game(interaction, self.game)
                    else:
                        current_player = self.game.current_player.mention if isinstance(self.game.current_player, discord.Member) else "LlddBot"
                        await interaction.message.edit(
                            embed=self.view.create_embed(
                                f"🎮 **Morpion** 🎮\n\n{self.game.render_board()}\n⚔️ À {current_player} de jouer !",
                                discord.Color.purple(),
                            ),
                            view=self.view,
                        )
        else:
            await interaction.response.send_message("⚠️ Cette case est déjà prise !", ephemeral=True)


class MorpionView(View):
    def __init__(self, game):
        super().__init__()
        self.game = game
        for row in range(3):
            for col in range(3):
                self.add_item(MorpionButton(row, col, self.game))

    def disable_all_items(self):
        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True

    def create_embed(self, description, color):
        embed = discord.Embed(
            title="🌌 **Morpion : L'Arène des Légendes** 🌌",
            description=description,
            color=color,
        )
        embed.set_footer(text="LlddBot - Que le combat commence !")
        return embed

    def end_game(self, interaction, game):
        cog = interaction.client.get_cog("Morpion")
        if cog:
            cog.active_games.pop(game.player1.id, None)
            if isinstance(game.player2, discord.Member):
                cog.active_games.pop(game.player2.id, None)


class Morpion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}

    @commands.hybrid_command(name="morpion", help="Lance une partie de morpion.")
    async def start_morpion(self, ctx, opponent: discord.Member = None, difficulty: str = "Facile"):
        if ctx.author.id in self.active_games:
            await ctx.send("⚠️ Vous avez déjà une partie en cours.")
            return
        if opponent and opponent.id in self.active_games:
            await ctx.send(f"⚠️ {opponent.display_name} est déjà en train de jouer.")
            return

        opponent = opponent or "LlddBot"
        if opponent == self.bot.user:
            opponent = "LlddBot"
        difficulty = difficulty.capitalize()
        if difficulty not in ["Facile", "Normale", "Difficile"]:
            await ctx.send("⚠️ Niveau de difficulté invalide. Choisissez parmi : Facile, Normale, Difficile.")
            return

        game = MorpionGame(ctx.author, opponent, difficulty)
        self.active_games[ctx.author.id] = game
        if isinstance(opponent, discord.Member):
            self.active_games[opponent.id] = game

        view = MorpionView(game)
        current_player = game.current_player.mention if isinstance(game.current_player, discord.Member) else "LlddBot"
        embed = view.create_embed(
            f"🌀 {ctx.author.mention} (🔴) contre {opponent.mention if isinstance(opponent, discord.Member) else 'LlddBot'} (✖️).\n\n⚔️ À {current_player} de commencer !",
            discord.Color.dark_purple(),
        )
        await ctx.send(embed=embed, view=view)

    async def end_game(self, interaction, game):
        self.active_games.pop(game.player1.id, None)
        if isinstance(game.player2, discord.Member):
            self.active_games.pop(game.player2.id, None)


async def setup(bot):
    await bot.add_cog(Morpion(bot))
