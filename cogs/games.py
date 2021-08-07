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
from random import randint

import discord
from discord.ext import commands, menus


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

    async def update(self, payload: discord.RawReactionActionEvent) -> None:
        """On payload, do that."""
        button = self.buttons[payload.emoji]
        if not self._running:
            return

        try:
            if button.lock:
                async with self._lock:
                    if self._running:
                        await button(self, payload)
            else:
                await button(self, payload)
        except Exception as error:
            embed = discord.Embed(colour=0xFF0000)
            embed.set_author(
                name=str(self.ctx.author),
                icon_url=str(self.ctx.author.avatar_url),
            )
            embed.title = f"{self.ctx.author.id} caused an error in connect 4"
            embed.description = f"{type(error).__name__} : {error}"
            if self.ctx.guild:
                embed.description += (
                    f"\nin {self.ctx.guild} "
                    f"({self.ctx.guild.id})\n   in {self.ctx.channel.name} "
                    f"({self.ctx.channel.id})")
            elif isinstance(self.ctx.channel, discord.DMChannel):
                embed.description += (
                    f"\nin a Private Channel ({self.ctx.channel.id})"  # noqa
                )
            else:
                embed.description += (
                    f"\nin the Group {self.ctx.channel.name} "
                    f"({self.ctx.channel.id})")
            formatted_tb = "".join(traceback.format_tb(error.__traceback__))
            embed.description += f"```\n{formatted_tb}```"
            embed.set_footer(
                text=f"{self.bot.user.name} Logging",
                icon_url=self.ctx.bot.user.avatar_url_as(static_format="png"),
            )
            embed.timestamp = datetime.utcnow()
            try:
                await self.bot.log_channel.send(embed=embed)
            except Exception:
                await self.bot.log_channel.send(
                    "Please check the logs for connect 4")
                raise error from None

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


class Games(commands.Cog):
    """Good games."""

    mine_difficulty = {  # mines, rows, columns
        "easy": (10, 8, 8),
        "medium": (40, 16, 16),
        "hard": (99, 32, 16),
    }

    mine_emoji = [
        "||" + str(i) +
        "\N{variation selector-16}\N{combining enclosing keycap}||"
        for i in range(9)
    ] + [
        "0\N{variation selector-16}\N{combining enclosing keycap}",
        # revealed zero
        "||\U0001f4a3||",  # bomb
    ]

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize Games."""
        self.bot = bot

    @commands.command(aliases=["c4"])
    async def connect4(self, ctx: commands.Context,
                       member: discord.Member) -> None:
        """Play connect 4 with a friend."""
        winner = await Connect4(ctx.author, member,
                                clear_reactions_after=True).prompt(ctx)
        if winner:
            await ctx.send(f"{winner.mention} won !")
        else:
            await ctx.send("Game cancelled")

    @staticmethod
    def neighbours(i: int, j: int, rows: int,
                   columns: int) -> t.List[t.Tuple[int, int]]:
        """Get a cell's neighbours for minesweeper."""
        final = []
        if i != 0:
            final.append((i - 1, j))
        if i != rows - 1:
            final.append((i + 1, j))
        if j != 0:
            final.append((i, j - 1))
        if j != columns - 1:
            final.append((i, j + 1))
        if 0 not in {i, j}:
            final.append((i - 1, j - 1))
        if i != rows - 1 and j != columns - 1:
            final.append((i + 1, j + 1))
        if i != 0 and j != columns - 1:
            final.append((i - 1, j + 1))
        if i != rows - 1 and j != 0:
            final.append((i + 1, j - 1))
        return final

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

        mines, rows, columns = self.mine_difficulty[difficulty]
        grid = [[0 for _ in range(columns)] for _ in range(rows)]
        click_x, click_y = randint(0, rows - 1), randint(0, columns - 1)
        grid[click_x][click_y] = -2
        i, j = click_x, click_y
        for _ in range(mines):
            while grid[i][j] < 0 or (abs(click_x - i) <= 1
                                     and abs(click_y - j) <= 1):
                i, j = randint(0, rows - 1), randint(0, columns - 1)
            grid[i][j] = -1
            for x, y in self.neighbours(i, j, rows, columns):
                if grid[x][y] != -1:
                    grid[x][y] += 1

        max_len = 99 // columns

        content = "\n".join([
            " ".join([self.mine_emoji[num] for num in row])
            for row in grid[:max_len]
        ])
        await ctx.send(f"Total number of mines: {mines}\n\n{content}")
        if rows * columns > 99:
            for i in range(1, (rows * columns) // 99):
                await ctx.send("\n".join([
                    " ".join([self.mine_emoji[num] for num in row])
                    for row in grid[max_len * i:max_len * (i + 1)]
                ]))


def setup(bot: commands.Bot) -> None:
    """Load the Games cog."""
    bot.add_cog(Games(bot))
