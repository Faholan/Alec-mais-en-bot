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

import re
from random import randint

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
            match = self.rollre.match(prompt.lower())
            if match is None:
                await ctx.send("Sorry, I couldn't understand your prompt")
                return
            prompt = prompt[match.end():].lower()
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
                prompt = prompt[match.end():]
                positive = match.group(1) == "+"

        await ctx.send(f"Rolled a **{total}** ({' '.join(detailed)[2:]})")

    @commands.Cog.listener("on_message")
    async def ckwalip(self, message: discord.Message) -> None:
        """Send the IP."""
        if message.author.bot:
            return

        words = frozenset(message.content.lower().split(" "))

        if any((
                any(word in words for word in ("ip", "ip?", "l'ip", "l'ip?"))
                and any(word in words for word in ("ckwa", "kwa", "quoi")),
                "ckwalip" in message.content.lower(),
        )):
            await message.reply(self.bot.ckwalip)


def setup(bot: commands.Bot):
    """Load the cog."""
    bot.add_cog(Utility(bot))
