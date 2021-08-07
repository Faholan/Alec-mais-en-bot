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

import asyncio
import io
import textwrap
import traceback
import typing as t
from contextlib import redirect_stdout

import discord
from discord.ext import commands


class OwnerError(commands.CheckFailure):
    """Error specific to this cog."""


class Owner(commands.Cog, command_attrs={"help": "Owner command"}):
    """Owner-specific commands."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize Owner."""
        self.bot = bot
        self._last_result = None
        self._stat_conn: t.Any = None
        self._stat_lock: t.Any = None

    @staticmethod
    def cleanup_code(content: str) -> str:
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith("```") and content.endswith("```"):
            return "\n".join(content.split("\n")[1:-1])

        # remove `foo`
        return content.strip("` \n")

    async def cog_check(self, ctx: commands.Context) -> bool:
        """Decide if you can run the command."""
        if await ctx.bot.is_owner(ctx.author):
            return True
        raise OwnerError()

    async def cog_command_error(self, ctx: commands.Context,
                                error: Exception) -> None:
        """Call that on error."""
        if isinstance(error, OwnerError):
            await ctx.bot.httpcat(
                ctx,
                401,
                "Only my owner can use the command " + ctx.invoked_with,
            )
            return
        raise error

    def cog_unload(self):
        """Do some cleanup."""
        if self._stat_conn:
            asyncio.create_task(self.bot.pool.release(self._stat_conn))
        self.bot.remove_listener(self.stats_listener)

    @commands.command(name="eval")
    async def _eval(self, ctx: commands.Context, *, body: str) -> None:
        """Evaluate a Python code."""
        env = {
            "bot": self.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message,
            "_": self._last_result,
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as error:
            await ctx.send(f"```py\n{error.__class__.__name__}: {error}\n```")
            return

        func = env["func"]
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception:
            value = stdout.getvalue()
            await ctx.send(f"```py\n{value}{traceback.format_exc()}\n```")
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction("\u2705")
            except discord.DiscordException:
                pass

            if ret is None:
                if value:
                    await ctx.send(f"```py\n{value}\n```")
            else:
                self._last_result = ret
                await ctx.send(f"```py\n{value}{ret}\n```")

    @commands.command()
    async def sh(self, ctx: commands.Context, *, argument: str):
        """Execute an arbitrary command."""
        await self.bot.shell(ctx, self.cleanup_code(argument))


def setup(bot: commands.Bot) -> None:
    """Load the Owner cog."""
    bot.add_cog(Owner(bot))
