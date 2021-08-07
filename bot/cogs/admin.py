"""Admin commands.

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

import discord
from discord.ext import commands


class AdminError(commands.CheckFailure):
    """Error specific to this cog."""


class Admin(commands.Cog):
    """Admin-only commands."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the cog."""
        self.bot = bot

    async def cog_check(self, ctx: commands.Context) -> bool:
        """Decide if you can run the command."""
        if await ctx.bot.is_owner(ctx.author):
            return True
        if ctx.author.id in self.bot.admins:
            return True
        raise AdminError()

    async def cog_command_error(self, ctx: commands.Context,
                                error: Exception) -> None:
        """Call that on error."""
        if isinstance(error, AdminError):
            await ctx.bot.httpcat(
                ctx,
                401,
                "Only my owner can use the command " + ctx.invoked_with,
            )
            return
        raise error

    @commands.command(ignore_extra=True)
    async def load(self, ctx: commands.Context, *extensions) -> None:
        """Load an extension."""
        if not extensions:
            await ctx.send("Please specify at least one extension to unload")
            return
        total_ext = len(extensions)
        report = []
        success = 0
        for ext in extensions:
            try:
                try:
                    self.bot.reload_extension(ext)
                    report.append(f"✅ | **Extension reloaded** : `{ext}`")
                except commands.ExtensionNotLoaded:
                    self.bot.load_extension(ext)
                    report.append(f"✅ | **Extension loaded** : `{ext}`")
                success += 1
            except commands.ExtensionFailed as error:
                report.append(f"❌ | **Extension error** : `{ext}` "
                              f"({type(error.original)} : {error.original})")
            except commands.ExtensionNotFound:
                report.append(f"❌ | **Extension not found** : `{ext}`")
            except commands.NoEntryPointError:
                report.append(f"❌ | **setup not defined** : `{ext}`")

        failure = total_ext - success
        embed = discord.Embed(
            title=(f"{success} "
                   f"{'extension was' if success == 1 else 'extensions were'} "
                   f"loaded & {failure} "
                   f"{'extension was' if failure == 1 else 'extensions were'}"
                   " not loaded"),
            description="\n".join(report),
            colour=discord.Colour.green(),
        )
        await self.bot.log_channel.send(embed=embed)
        await ctx.send(embed=embed)

    @commands.command(ignore_extra=True)
    async def logout(self, ctx: commands.Context) -> None:
        """Kill the bot."""
        await ctx.send("Logging out...")
        await self.bot.close()

    @commands.command()
    async def pull(self, ctx: commands.Context) -> None:
        """Pull the code from the remote repo."""
        await self.bot.shell(ctx, "git pull")

    @commands.command()
    async def reload(self, ctx: commands.Context, *extensions) -> None:
        """Reload extensions."""
        await self.bot.cog_reloader(ctx, extensions)

    @commands.command()
    async def unload(self, ctx: commands.Context, *extensions) -> None:
        """Unload extensions."""
        if "cogs.owner" in extensions:
            await ctx.send("You shouldn't unload me")
            return
        if not extensions:
            await ctx.send("Please specify at least one extension to unload")
            return
        total_ext = len(extensions)
        report = []
        success = 0
        for ext in extensions:
            try:
                self.bot.unload_extension(ext)
                success += 1
                report.append(f"✅ | **Extension unloaded** : `{ext}`")
            except commands.ExtensionNotLoaded:
                report.append(f"❌ | **Extension not loaded** : `{ext}`")

        failure = total_ext - success
        embed = discord.Embed(
            title=(f"{success} "
                   f"{'extension was' if success == 1 else 'extensions were'} "
                   f"unloaded & {failure} "
                   f"{'extension was' if failure == 1 else 'extensions were'} "
                   "not unloaded"),
            description="\n".join(report),
            colour=discord.Colour.green(),
        )
        await self.bot.log_channel.send(embed=embed)
        await ctx.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    """Load the admin cog."""
    bot.add_cog(Admin(bot))
