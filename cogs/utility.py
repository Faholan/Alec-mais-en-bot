"""Alec mais en utile.

Copyright (C) 2021  Faholan

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from random import randint
import re

import discord
from discord.ext import commands


class Utility(commands.Cog):
    """Alec mais en utile."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the cog."""
        self.bot = bot
        self.rollre = re.compile(r"\s*(\d+d?\d*)", re.I)
        self.signre = re.compile(r"\s*(\+|-)\s*")

    @commands.command()
    async def roll(self, ctx, *, prompt: str) -> None:
        """Roll one or more dices."""
        total = 0
        detailed = []
        positive = True
        while prompt:
            match = self.rollre.match(prompt)
            if match is None:
                await ctx.send("Sorry, I couldn't understand your prompt")
                return
            prompt = prompt[match.end():]
            if "d" in match.group(1):
                num, rawdice = match.group(1).split("d")
                dice = int(rawdice)
                if rawdice == "0":
                    await ctx.send("Sorry, 0-face dices don't exist")
                    return
                for _ in range(int(num)):
                    roll = randint(1, dice)
                    if positive:
                        total += roll
                        detailed.append(f"+ {roll}")
                    else:
                        total -= roll
                        detailed.append(f"- {roll}")
            else:
                value = int(match.group(1))
                if positive:
                    total += value
                    detailed.append(f"+ {value}")
                else:
                    total -= value
                    detailed.append(f"- {value}")

            match = self.signre.match(prompt)
            if match is None:
                if re.match(r"\s*\Z", prompt):
                    prompt = ""
                else:
                    await ctx.send("Unrecognized sign !")
            else:
                positive = match.group(1) == "+"

        await ctx.send(f"Rolled a **{total}** ({' '.join(detailed)})")


def setup(bot: commands.Bot):
    """Load the cog."""
    bot.add_cog(Utility(bot))
