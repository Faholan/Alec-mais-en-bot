"""MIT License.

Copyright (c) 2020-2021 Faholan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import traceback
import typing as t
from datetime import datetime
from itertools import cycle
from random import choice, randint, shuffle

import discord
from discord.ext import commands, menus

COLORS = (
    "\U0001f534",
    "\U0001f535",
    "\U0001f7e4",
    "\U0001f7e3",
    "\U0001f7e2",
    "\U0001f7e0",
)

BLACK = "\U000026ab"
WHITE = "\U000026aa"


class Connect4(menus.Menu):
    """How to play connect4."""

    def __init__(self, *players, **kwargs) -> None:
        """Initialize the game."""
        super().__init__(**kwargs)
        self.winner = None
        self.id_dict = {players[i].id: i + 1 for i in range(len(players))}
        self.ids = cycle(list(self.id_dict))
        self.players = players
        self.next = next(self.ids, None)
        self.status = [
            ":black_large_square:", ":green_circle:", ":red_circle:"
        ]
        self.state = [[0 for _ in range(6)] for __ in range(7)]

    async def on_menu_button_error(self, exc) -> None:
        """Manage exceptions."""
        embed = discord.Embed(colour=0xFF0000)
        embed.set_author(
            name=str(self.ctx.author),
            icon_url=str(self.ctx.author.avatar_url),
        )
        embed.title = f"{self.ctx.author.id} caused an error in connect 4"
        embed.description = f"{type(exc).__name__} : {exc}"
        embed.description += f"\nin {self.ctx.channel.name} ({self.ctx.channel.id})"

        formatted_tb = "".join(traceback.format_tb(exc.__traceback__))
        embed.description += f"```\n{formatted_tb}```"
        embed.set_footer(
            text="Alec mais en logger",
            icon_url=self.ctx.bot.user.avatar_url_as(static_format="png"),
        )
        embed.timestamp = datetime.utcnow()
        try:
            await self.bot.log_channel.send(embed=embed)
        except Exception:
            await self.bot.log_channel.send(
                "Please check the logs for Connect 4")
            raise exc from None

    def reaction_check(self, payload: discord.RawReactionActionEvent) -> bool:
        """Whether or not to process the payload."""
        if payload.message_id != self.message.id:
            return False

        return payload.user_id == self.next and payload.emoji in self.buttons

    def get_embed(self) -> discord.Embed:
        """Generate the next embed."""
        return discord.Embed(description="\n".join([
            "".join([self.status[column[5 - i]] for column in self.state])
            for i in range(6)
        ]))

    async def send_initial_message(
        self,
        ctx: commands.Context,
        _,
    ) -> discord.Message:
        """Send the first message."""
        return await ctx.send(
            content=ctx.author.mention,
            embed=self.get_embed(),
        )

    async def action(
        self,
        number: int,
        payload: discord.RawReactionActionEvent,
    ) -> None:
        """Do something."""
        if 0 not in self.state[number]:
            return
        self.next = next(self.ids, None)
        next_id = self.id_dict[payload.user_id]
        self.state[number][self.state[number].index(0)] = next_id
        await self.embed_updating()
        check = self.check(next_id)
        if check:
            self.winner = self.players[next_id - 1]
            return self.stop()

    def check(self, user_id: int) -> bool:
        """Did you win."""
        schema = str(user_id) + 3 * f", {user_id}"
        if any(schema in str(x) for x in self.state):
            return True
        for i in range(6):
            if schema in str([column[i] for column in self.state]):
                return True
        for diagonal in range(3):
            lines = [
                [self.state[3 + diagonal - i][i] for i in range(4 + diagonal)],
                [
                    self.state[i - diagonal - 4][-i - 1]
                    for i in range(4 + diagonal)
                ],
                [self.state[i - diagonal - 4][i] for i in range(4 + diagonal)],
                [
                    self.state[3 + diagonal - i][-i - 1]
                    for i in range(4 + diagonal)
                ],
            ]
            if any(schema in str(line) for line in lines):
                return True
        return False

    async def embed_updating(self) -> None:
        """Update the embed."""
        await self.message.edit(
            content=self.players[self.id_dict[self.next] - 1].mention,
            embed=self.get_embed(),
        )

    @menus.button("1\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_1(self, payload: discord.RawReactionActionEvent) -> None:
        """First column."""
        await self.action(0, payload)

    @menus.button("2\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_2(self, payload: discord.RawReactionActionEvent) -> None:
        """Second column."""
        await self.action(1, payload)

    @menus.button("3\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_3(self, payload: discord.RawReactionActionEvent) -> None:
        """Third column."""
        await self.action(2, payload)

    @menus.button("4\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_4(self, payload: discord.RawReactionActionEvent) -> None:
        """Fourth column."""
        await self.action(3, payload)

    @menus.button("5\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_5(self, payload: discord.RawReactionActionEvent) -> None:
        """Fifth column."""
        await self.action(4, payload)

    @menus.button("6\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_6(self, payload: discord.RawReactionActionEvent) -> None:
        """Sixth column."""
        await self.action(5, payload)

    @menus.button("7\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_7(self, payload: discord.RawReactionActionEvent) -> None:
        """Seventh column."""
        await self.action(6, payload)

    @menus.button("\N{BLACK SQUARE FOR STOP}\ufe0f")
    async def on_stop(self, _) -> None:
        """Stop."""
        self.stop()

    async def prompt(self, ctx: commands.Context) -> discord.User:
        """Start it the real way."""
        await self.start(ctx, wait=True)
        return self.winner


class Mastermind(menus.Menu):
    """Play Mastermind."""

    def __init__(self, tries: int, **kwargs) -> None:
        """Initialize the mastermind."""
        clear_reactions_after = kwargs.pop("clear_reactions_after", True)
        self.max_tries = tries
        self.cur_try = 1
        self.lines: t.List[str] = []
        self.length = kwargs.pop("length", 4)
        self.secret = [choice(COLORS) for _ in range(self.length)]
        self.current: t.List[str] = []
        self.finished = False
        super().__init__(clear_reactions_after=clear_reactions_after, **kwargs)

    async def send_initial_message(self, ctx, channel) -> discord.Message:
        """Send the first message."""
        self.lines.append(f"{ctx.author.mention}'s Mastermind "
                          "(Turn {cur}/{total})")
        return await channel.send(self.content)

    @property
    def content(self) -> str:
        """Get the current message content."""
        return "\n".join(self.lines + ["".join(self.current)]).format(
            cur=self.cur_try, total=self.max_tries)

    async def on_menu_button_error(self, exc) -> None:
        """Manage exceptions."""
        embed = discord.Embed(colour=0xFF0000)
        embed.set_author(
            name=str(self.ctx.author),
            icon_url=str(self.ctx.author.avatar_url),
        )
        embed.title = f"{self.ctx.author.id} caused an error in Mastermind"
        embed.description = f"{type(exc).__name__} : {exc}"
        embed.description += f"\nin {self.ctx.channel.name} " f"({self.ctx.channel.id})"

        formatted_tb = "".join(traceback.format_tb(exc.__traceback__))
        embed.description += f"```\n{formatted_tb}```"
        embed.set_footer(
            text="Alec mais en logger",
            icon_url=self.ctx.bot.user.avatar_url_as(static_format="png"),
        )
        embed.timestamp = datetime.utcnow()
        try:
            await self.bot.log_channel.send(embed=embed)
        except Exception:
            await self.bot.log_channel.send(
                "Please check the logs for Mastermind")
            raise exc from None

    async def dot(self, color: str) -> None:
        """Add a colored dot."""
        if self.finished:
            return
        if len(self.current) < self.length:
            self.current.append(color)
            await self.message.edit(content=self.content)

    @menus.button("\U0001f534")
    async def red(self, _: discord.RawReactionActionEvent) -> None:
        """Add a red dot."""
        await self.dot("\U0001f534")

    @menus.button("\U0001f535")
    async def blue(self, _: discord.RawReactionActionEvent) -> None:
        """Add a blue dot."""
        await self.dot("\U0001f535")

    @menus.button("\U0001f7e4")
    async def brown(self, _: discord.RawReactionActionEvent) -> None:
        """Add a brown dot."""
        await self.dot("\U0001f7e4")

    @menus.button("\U0001f7e3")
    async def purple(self, _: discord.RawReactionActionEvent) -> None:
        """Add a purple dot."""
        await self.dot("\U0001f7e3")

    @menus.button("\U0001f7e2")
    async def green(self, _: discord.RawReactionActionEvent) -> None:
        """Add a green dot."""
        await self.dot("\U0001f7e2")

    @menus.button("\U0001f7e0")
    async def orange(self, _: discord.RawReactionActionEvent) -> None:
        """Add an orange dot."""
        await self.dot("\U0001f7e0")

    @menus.button("\N{BLACK LEFT-POINTING TRIANGLE}\U0000fe0f")
    async def rollback(self, _: discord.RawReactionActionEvent) -> None:
        """Delete the last dot."""
        if self.finished:
            return
        if self.current:
            self.current.pop()
            await self.message.edit(content=self.content)

    @menus.button("\U00002705")
    async def validate(self, _: discord.RawReactionActionEvent) -> None:
        """Try the current configuration."""
        if self.finished:
            return
        if len(self.current) != 4:
            return

        start = "".join(self.current) + " " * 10

        if self.current == self.secret:
            self.finished = True
            self.lines.append(start + BLACK * 4)
            self.lines.append("You won !")
        else:
            current = self.current.copy()
            secret = self.secret.copy()

            result = []

            i = 0
            while i < len(current):
                if current[i] == secret[i]:
                    result.append(BLACK)
                    current.pop(i)
                    secret.pop(i)
                else:
                    i += 1
            for elem in current:
                if elem in secret:
                    result.append(WHITE)
                    secret.remove(elem)

            shuffle(result)

            self.lines.append(start + "".join(result))

            if self.cur_try == self.max_tries:
                self.finished = True
                self.lines.append("You lost !")
            else:
                self.cur_try += 1

        self.current = []
        await self.message.edit(content=self.content)

    @menus.button("\U0001f504")
    async def restart(self, _: discord.RawReactionActionEvent) -> None:
        """Restart the game."""
        self.secret = [choice(COLORS) for _ in range(self.length)]
        self.cur_try = 1

        self.finished = False
        self.lines = self.lines[:1]
        self.current = []

        await self.message.edit(content=self.content)

    @menus.button("\N{BLACK SQUARE FOR STOP}\ufe0f")
    async def on_stop(self, _: discord.RawReactionActionEvent) -> None:
        """Stop."""
        self.stop()


# The minesweeper is under the AGPL version 3 or any later version. Copyright Amelia Coutard.
class Minesweeper(menus.Menu):
    def __init__(self, difficulty):
        super().__init__()
        if difficulty == "easy":
            self.width = 8
            self.height = 8
            self.bomb_count = 10
        elif difficulty == "medium":
            self.width = 16
            self.height = 16
            self.bomb_count = 40
        elif difficulty == "hard":
            self.width = 32
            self.height = 32
            self.bomb_count = 99

        self.board = [[0 for j in range(self.width)]
                      for i in range(self.height)]
        self.revealed = [[False for j in range(self.width)]
                         for i in range(self.height)]
        self.x = self.width // 2
        self.y = self.height // 2

        for _ in range(self.bomb_count):
            x = randint(0, self.width - 1)
            y = randint(0, self.height - 1)
            while self.board[y][x] == -1:
                x = randint(0, self.width - 1)
                y = randint(0, self.height - 1)
            self.board[y][x] = -1
        for y, row in enumerate(self.board):
            for x, cell in enumerate(row):
                if cell != -1:
                    bombs = 0
                    if x > 0 and y > 0 and self.board[y - 1][x - 1] == -1:
                        bombs += 1
                    if y > 0 and self.board[y - 1][x] == -1:
                        bombs += 1
                    if x < self.width - 1 and y > 0 and self.board[y -
                                                                   1][x +
                                                                      1] == -1:
                        bombs += 1
                    if x < self.width - 1 and self.board[y][x + 1] == -1:
                        bombs += 1
                    if (x < self.width - 1 and y < self.height - 1
                            and self.board[y + 1][x + 1] == -1):
                        bombs += 1
                    if y < self.height - 1 and self.board[y + 1][x] == -1:
                        bombs += 1
                    if x > 0 and y < self.height - 1 and self.board[y + 1][
                            x - 1] == -1:
                        bombs += 1
                    if x > 0 and self.board[y][x - 1] == -1:
                        bombs += 1
                    self.board[y][x] = bombs

        self.failed = False
        self.won = False

    async def play(self, ctx):
        await self.start(ctx, wait=True)
        if self.failed:
            return "HA, you failed !"
        if self.won:
            return "Congrats !"
        return "Game Over."

    async def send_initial_message(self, ctx, _):
        return await ctx.send(self.render())

    @menus.button("\N{LEFTWARDS BLACK ARROW}")
    async def on_left(self, _):
        if self.x > 0:
            self.x -= 1
        await self.message.edit(content=self.render())

    @menus.button("\N{UPWARDS BLACK ARROW}")
    async def on_up(self, _):
        if self.y > 0:
            self.y -= 1
        await self.message.edit(content=self.render())

    @menus.button("\N{BLACK RIGHTWARDS ARROW}")
    async def on_right(self, _):
        if self.x < self.width - 1:
            self.x += 1
        await self.message.edit(content=self.render())

    @menus.button("\N{DOWNWARDS BLACK ARROW}")
    async def on_down(self, _):
        if self.y < self.height - 1:
            self.y += 1
        await self.message.edit(content=self.render())

    @menus.button("🚩")
    async def on_flag(self, _):
        self.revealed[self.y][self.x] = 2
        await self.message.edit(content=self.render())

    @menus.button("\N{PICK}")
    async def on_hole(self, _):
        if self.board[self.y][self.x] == -1:
            self.failed = True
            self.stop()
            return
        self.revealed[self.y][self.x] = 1
        if self.board[self.y][self.x] == 0:
            self.propagate(self.x, self.y)
        await self.message.edit(content=self.render())

    @menus.button("\N{BLACK SQUARE FOR STOP}\ufe0f")
    async def on_stop(self, _):
        self.stop()

    def propagate(self, x, y):
        if x > 0 and self.revealed[y][x - 1] != 1:
            self.revealed[y][x - 1] = 1
            if self.board[y][x - 1] == 0:
                self.propagate(x - 1, y)
        if x < self.width - 1 and self.revealed[y][x + 1] != 1:
            self.revealed[y][x + 1] = 1
            if self.board[y][x + 1] == 0:
                self.propagate(x + 1, y)
        if y > 0 and self.revealed[y - 1][x] != 1:
            self.revealed[y - 1][x] = 1
            if self.board[y - 1][x] == 0:
                self.propagate(x, y - 1)
        if y < self.height - 1 and self.revealed[y + 1][x] != 1:
            self.revealed[y + 1][x] = 1
            if self.board[y + 1][x] == 0:
                self.propagate(x, y + 1)

    def render(self):
        result = "```"
        for y, row in enumerate(zip(self.board, self.revealed)):
            for x, cell in enumerate(zip(row[0], row[1])):
                if x == self.x and y == self.y:
                    result += "XX"
                elif cell[1] == 0:
                    result += "██"
                elif cell[1] == 1:
                    result += [
                        "  ",
                        "1 ",
                        "2 ",
                        "3 ",
                        "4 ",
                        "5 ",
                        "6 ",
                        "7 ",
                        "8 ",
                        "  ",
                    ][cell[0]]
                elif cell[1] == 2:
                    result += "▶ "
            result += "\n"
        result += "```"
        return result


class Games(commands.Cog):
    """Good games."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize Games."""
        self.bot = bot

    @commands.command(aliases=["c4"])
    async def connect4(self, ctx: commands.Context,
                       member: discord.Member) -> None:
        """Play connect 4 with a friend."""
        if member == ctx.author:
            await ctx.send("You can't play with only yourself !")
            return
        if member.bot:
            await ctx.send("This member is a bot. Play with a human !")
            return

        winner = await Connect4(ctx.author, member,
                                clear_reactions_after=True).prompt(ctx)
        if winner:
            await ctx.send(f"{winner.mention} won !")
        else:
            await ctx.send("Game cancelled")

    @commands.command(aliases=["master"])
    async def mastermind(self,
                         ctx: commands.Context,
                         difficulty="easy") -> None:
        """Play Mastermind in Discord.

        Difficulty may be easy (12 tries), medium (10 tries) or hard (8 tries)
        """

        difficulty = difficulty.lower().strip()
        difficulties = {"easy": 12, "medium": 10, "hard": 8}
        if difficulty not in difficulties:
            await ctx.send(
                "difficulty must be one of `easy`, `medium` or `hard`")
            return

        await Mastermind(difficulties[difficulty]).start(ctx)

    @commands.command(aliases=["mines"])
    async def minesweeper(self, ctx: commands.Context, difficulty="easy"):
        """Play minesweeper in Discord.

        Difficulty may be easy (8x8, 10 mines), medium (16x16, 40 mines) or hard (32x32, 99 mines)
        At the beginning, a random cell holding the number zero is revealed
        """
        difficulty = difficulty.lower().strip()
        if difficulty not in {"easy", "medium", "hard"}:
            await ctx.send(
                "difficulty must be one of `easy`, `medium` or `hard`")
            return

        mine = Minesweeper(difficulty)
        ending = await mine.play(ctx)
        await ctx.send(ending)


def setup(bot: commands.Bot) -> None:
    """Load the Games cog."""
    bot.add_cog(Games(bot))
