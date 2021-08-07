"""Rename this file to data.py.

MIT License.

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


def setup(bot):
    """Add all the data to the bot."""
    bot.extensions_list = [
        "bin.error",
        "bin.help",
        "cogs.games",
        "cogs.owner",
        "cogs.utility",
    ]
    if bot.first_on_ready:
        # Discord configuration
        bot.token = "THE BEAUTIFUL TOKEN OF MY DISCORD BOT"

        bot.log_channel_id = 00000000000000000

        bot.guild_id = 0

        bot.admins = []

        # bot.postgre_connection = {
        #     "user": "user",
        #     "password": "alec_mais_en_password",
        #     "database": "alec",
        #     "host": "127.0.0.1",
        #     "port": 5432,
        # }

        bot.lavalink_credentials = {
            "host": "127.0.0.1",
            "port": 2233,
            "password": "youshallnotpass",
            "region": "eu",
            "resume_key": "default_node",
        }

        bot.http.user_agent = "alec_mais_en_user_agent"

        bot.ckwalip = "127.0.0.1:9999"
