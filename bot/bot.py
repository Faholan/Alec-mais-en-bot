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

import typing as t
from asyncio import all_tasks

import aiohttp
import discord
from discord.ext import commands

from . import sh


class AlecMaisEnBot(commands.Bot):
    """The subclassed bot class."""

    used_intents = discord.Intents(
        guilds=True,
        members=False,
        bans=False,
        emojis=False,
        integrations=False,
        webhooks=False,
        invites=False,
        voice_states=True,
        presences=False,
        guild_messages=True,
        dm_messages=False,
        reactions=True,
        typing=False,
    )

    def __init__(self) -> None:
        """Initialize the bot."""
        self.token: t.Optional[str] = None

        self.first_on_ready = True
        # makes it so on_ready behaves differently on first call
        # used in the info command

        # self.pool: asyncpg.pool.Pool = None
        # self.postgre_connection: t.Dict[str, t.Any] = {}
        # PostgreSQL connection

        self.admins: t.List[int] = []

        self.aio_session: aiohttp.ClientSession = None
        # Used for all internet fetches

        self.log_channel: discord.TextChannel = None
        self.log_channel_id = 0
        # Important channels

        self.extensions_list: t.List[str] = []

        self.guild_id = 0

        self.cwkalip = "127.0.0.1:9999"

        super().__init__(
            command_prefix="a!",
            intents=self.used_intents,
        )

        self.load_extension("data.data")
        # You can load an extension only after __init__ has been called
        if not self.log_channel_id:
            raise ValueError(
                "No log channel configured. One is required to proceed")

    async def on_ready(self) -> None:
        """Operations processed when the bot's ready."""
        await self.change_presence(activity=discord.Game("a!help"))

        for guild in self.guilds:
            if guild.id != self.guild_id:
                await guild.leave()

        if self.first_on_ready:
            self.first_on_ready = False

            # self.pool = await asyncpg.create_pool(
            #     min_size=5,
            #     max_size=100,
            #     **self.postgre_connection,
            # )
            # postgresql setup

            self.aio_session = aiohttp.ClientSession()

            self.log_channel = self.get_channel(self.log_channel_id)

            report = []
            success = 0
            for ext in self.extensions_list:
                if ext not in self.extensions:
                    try:
                        self.load_extension(ext)
                        report.append(f"✅ | **Extension loaded** : `{ext}`")
                        success += 1
                    except commands.ExtensionFailed as error:
                        report.append(
                            f"❌ | **Extension error** : `{ext}` "
                            f"({type(error.original)} : {error.original})")
                    except commands.ExtensionNotFound:
                        report.append(f"❌ | **Extension not found** : `{ext}`")
                    except commands.NoEntryPointError:
                        report.append(f"❌ | **setup not defined** : `{ext}`")
            # Load every single extension
            # Looping on the /cogs and /bin folders does not allow fine control

            embed = discord.Embed(
                title=(
                    f"{success} extensions were loaded & "
                    f"{len(self.extensions_list) - success} extensions were "
                    "not loaded"),
                description="\n".join(report),
                colour=discord.Colour.green(),
            )
            await self.log_channel.send(embed=embed)
        else:
            await self.log_channel.send("on_ready called again")

    async def close(self) -> None:
        """Do some cleanup."""
        await self.aio_session.close()
        for task in all_tasks(loop=self.loop):
            task.cancel()
        for ext in tuple(self.extensions):
            self.unload_extension(ext)
        # await self.pool.close()
        await super().close()

    async def cog_reloader(
        self,
        ctx: commands.Context,
        extensions: t.List[str],
    ) -> None:
        """Reload cogs."""
        report = []
        success = 0
        self.reload_extension("data.data")
        # First of all, reload the data file
        total_reload = len(extensions) or len(self.extensions_list)
        if extensions:
            for ext in extensions:
                if ext in self.extensions_list:
                    try:
                        try:
                            self.reload_extension(ext)
                            success += 1
                            report.append(
                                f"✅ | **Extension reloaded** : `{ext}`")
                        except commands.ExtensionNotLoaded:
                            self.load_extension(ext)
                            success += 1
                            report.append(
                                f"✅ | **Extension loaded** : `{ext}`")
                    except commands.ExtensionFailed as error:
                        report.append(
                            f"❌ | **Extension error** : `{ext}` "
                            f"({type(error.original)} : {error.original})")
                    except commands.ExtensionNotFound:
                        report.append(f"❌ | **Extension not found** : `{ext}`")
                    except commands.NoEntryPointError:
                        report.append(f"❌ | **setup not defined** : `{ext}`")
                else:
                    report.append(f"❌ | `{ext}` is not a valid extension")
        else:
            for ext in self.extensions_list:
                try:
                    try:
                        self.reload_extension(ext)
                        success += 1
                        report.append(f"✔️ | **Extension reloaded** : `{ext}`")
                    except commands.ExtensionNotLoaded:
                        self.load_extension(ext)
                        report.append(f"✔️ | **Extension loaded** : `{ext}`")
                except commands.ExtensionFailed as error:
                    report.append(
                        f"❌ | **Extension error** : `{ext}` "
                        f"({type(error.original)} : {error.original})")
                except commands.ExtensionNotFound:
                    report.append(f"❌ | **Extension not found** : `{ext}`")
                except commands.NoEntryPointError:
                    report.append(f"❌ | **setup not defined** : `{ext}`")
        not_loaded = total_reload - success
        embed = discord.Embed(
            title=(
                f"{success} "
                f"{'extension was' if success == 1 else 'extensions were'} "
                f"loaded & {total_reload - success} "
                f"{'extension was' if not_loaded == 1 else 'extensions were'}"
                " not loaded"),
            description="\n".join(report),
            colour=discord.Colour.green(),
        )
        await self.log_channel.send(embed=embed)
        await ctx.send(embed=embed)

    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Leave unauthorized guilds."""
        if guild.id != self.guild_id:
            await guild.leave()

    async def httpcat(
        self,
        ctx: commands.Context,
        code: int,
        title: str = discord.Embed.Empty,
        description: str = discord.Embed.Empty,
    ) -> None:
        """Funny error picture."""
        embed = discord.Embed(title=title,
                              colour=discord.Colour.red(),
                              description=description)
        embed.set_image(url=f"https://http.cat/{code}.jpg")
        try:
            await ctx.send(embed=embed)
        except discord.Forbidden:
            pass

    async def fetch_answer(
        self,
        ctx: commands.Context,
        *content,
        timeout: int = 30,
    ) -> discord.Message:
        """Get an answer."""

        # Helper function for getting an answer in a set of possibilities

        def check(message: discord.Message) -> bool:
            """Check the message."""
            return (message.author == ctx.author
                    and (message.channel == ctx.channel)
                    and message.content.lower() in content)

        return await self.wait_for("message", check=check, timeout=timeout)

    async def fetch_confirmation(
        self,
        ctx: commands.Context,
        question: str,
        timeout: int = 30,
    ) -> bool:
        """Get a yes or no reaction-based answer."""
        message = await ctx.send(question)
        await message.add_reaction("\U00002705")  # ✅
        await message.add_reaction("\U0000274c")  # ❌

        def check(payload: discord.RawReactionActionEvent) -> bool:
            """Decide whether or not to process the reaction."""
            return (
                payload.message_id,
                payload.channel_id,
                payload.user_id,
            ) == (
                message.id,
                message.channel.id,
                ctx.author.id,
            ) and payload.emoji.name in {"\U00002705", "\U0000274c"}

        payload = await self.wait_for(
            "raw_reaction_add",
            check=check,
            timeout=timeout,
        )
        return payload.emoji.name == "\U00002705"

    async def shell(self, ctx, argument: str):
        with sh.ShellReader(argument) as reader:
            prefix = "```" + reader.highlight

            paginator = sh.WrappedPaginator(prefix=prefix, max_size=1975)
            paginator.add_line(f"{reader.ps1} {argument}\n")

            interface = sh.PaginatorInterface(self,
                                              paginator,
                                              owner=ctx.author)
            self.loop.create_task(interface.send_to(ctx))

            async for line in reader:
                if interface.closed:
                    return
                await interface.add_line(line)

        await interface.add_line(f"\n[status] Return code {reader.close_code}")

    def load_extension(self,
                       name: str,
                       *,
                       package: t.Optional[str] = None) -> None:
        """Load an extension."""
        super().load_extension(f"bot.{name}", package=package)

    def launch(self) -> None:
        """Launch the bot."""
        self.run(self.token)
