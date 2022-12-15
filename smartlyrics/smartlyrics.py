import asyncio
import re
from typing import Optional, Union

import aiohttp
import discord
import lavalink
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.commands import Context
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu


class SmartLyrics(commands.Cog):
    """
    Gets lyrics for your current song.
    """

    __version__ = "2.0.1"

    def __init__(self, bot: Red):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.regex = re.compile(
            (
                r"((\[)|(\()).*(of?ficial|feat\.?|"
                r"ft\.?|audio|video|lyrics?|remix|HD).*(?(2)]|\))"
            ),
            flags=re.I,
        )
        # thanks wyn - https://github.com/TheWyn/Wyn-RedV3Cogs/blob/master/lyrics/lyrics.py#L12-13

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())

    async def red_delete_data_for_user(self, **kwargs):
        return

    def format_help_for_context(self, ctx: Context):
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\n\nCog Version: {self.__version__}"

    async def get_lyrics(
        self, *, query: str = None, spotify_id: str = None
    ) -> Optional[dict]:

        if spotify_id:
            params = {
                "spotify_id": spotify_id,
            }
        else:
            params = {
                "query": query,
            }

        headers = {
            "User-Agent": f'SmartLyrics/{self.__version__} ("https://github.com/kaogurai/cogs")',
        }

        async with self.session.get(
            "https://api.flowery.pw/v1/lyrics", params=params, headers=headers
        ) as resp:
            if resp.status != 200:
                return
            return await resp.json()

    # adapted https://github.com/Cog-Creators/Red-DiscordBot/blob/V3/develop/redbot/cogs/mod/names.py#L112-L126
    def get_user_status_song(
        self, user: Union[discord.Member, discord.User]
    ) -> Optional[str]:
        listening_statuses = [
            s for s in user.activities if s.type == discord.ActivityType.listening
        ]
        if not listening_statuses:
            return
        for listening_status in listening_statuses:
            if isinstance(listening_status, discord.Spotify):
                return listening_status.track_id

    async def create_menu(
        self, ctx: Context, results: dict, source: Optional[str] = None
    ):
        embeds = []
        embed_content = [p for p in pagify(results["lyrics"]["text"], page_length=750)]
        for index, page in enumerate(embed_content):
            embed = discord.Embed(
                color=await ctx.embed_color(),
                title=f"{results['track']['title']} by {results['track']['artist']}",
                description=page,
            )
            if results["track"]["media"]["artwork"] is not None:
                embed.set_thumbnail(url=results["track"]["media"]["artwork"])
            if len(embed_content) != 1:
                if source:
                    embed.set_footer(
                        text=f"Source: {source} | Page {index + 1}/{len(embed_content)}"
                    )
                else:
                    embed.set_footer(text=f"Page {index + 1}/{len(embed_content)}")
            else:
                if source:
                    embed.set_footer(text=f"Source: {source}")
            embeds.append(embed)

        if len(embed_content) != 1:
            asyncio.create_task(
                menu(ctx, embeds, controls=DEFAULT_CONTROLS, timeout=120)
            )
        else:
            await ctx.send(embed=embeds[0])

    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    @commands.command(aliases=["l", "ly"])
    async def lyrics(self, ctx: Context, *, query: Optional[str] = None):
        """
        Gets the lyrics for your current song.

        If a query (song name) is provided, it will immediately search that.
        Next, it checks if you are in VC and a song is playing.
        Then, it checks if you are listening to a song on spotify.
        Lastly, it checks your last.fm account for your latest song.

        If all of these provide nothing, it will simply ask you to name a song.
        """
        async with ctx.typing():
            if query:
                if len(query) > 2000:
                    return
                results = await self.get_lyrics(query=query)
                if results:
                    await self.create_menu(ctx, results)
                    return
                else:
                    await ctx.send(f"Nothing was found for `{query}`")
                    return

            lastfmcog = self.bot.get_cog("LastFM")

            if ctx.author.voice and ctx.guild.me.voice:
                if ctx.author.voice.channel == ctx.guild.me.voice.channel:
                    try:
                        player = lavalink.get_player(ctx.guild.id)
                    except KeyError:  # no player for that guild
                        player = None
                    if player and player.current:
                        title = player.current.title
                        if "-" not in title:
                            title = player.current.author + " " + title

                        results = await self.get_lyrics(query=title)
                        if results:
                            await self.create_menu(ctx, results, "Voice Channel")
                            return
                        else:
                            await ctx.send(f"Nothing was found for `{title}`")
                            return

            spotify_id = self.get_user_status_song(ctx.author)
            if spotify_id:
                results = await self.get_lyrics(spotify_id=spotify_id)
                if results:
                    await self.create_menu(ctx, results, "Spotify")
                    return
                else:
                    await ctx.send(f"Nothing was found for your spotify song.")
                    return

            username = await lastfmcog.config.user(ctx.author).lastfm_username()
            if lastfmcog and username:
                try:
                    (
                        trackname,
                        artistname,
                        albumname,
                        imageurl,
                    ) = await lastfmcog.get_current_track(ctx, username)
                except:
                    await ctx.send("Please provide a query to search.")
                    return

                trackname = f"{trackname} {artistname}"
                results = await self.get_lyrics(query=trackname)
                if results:
                    await self.create_menu(ctx, results, "Last.fm")
                    return
                else:
                    await ctx.send(f"Nothing was found for `{trackname}`")
                    return

            await ctx.send("Please provide a query to search.")
