"""Shared code across multiple cogs.
   Taken from: https://github.com/PhasecoreX/PCXCogs
"""
import asyncio
from collections.abc import Mapping
from contextlib import suppress
from typing import Any

import discord
from redbot.core import __version__ as redbot_version
from redbot.core import commands
from redbot.core.utils import common_filters
from redbot.core.utils.chat_formatting import box

headers = {"user-agent": "Red-DiscordBot/" + redbot_version}

MAX_EMBED_SIZE = 5900
MAX_EMBED_FIELDS = 20
MAX_EMBED_FIELD_SIZE = 1024

async def type_message(
    destination: discord.abc.Messageable, content: str, **kwargs: Any  # noqa: ANN401
):
    """Simulate typing and sending a message to a destination.

    Will send a typing indicator, wait a variable amount of time based on the length
    of the text (to simulate typing speed), then send the message.
    """
    content = common_filters.filter_urls(content)
    with suppress(discord.HTTPException):
        async with destination.typing():
            await asyncio.sleep(max(0.25, min(2.5, len(content) * 0.01)))
        return await destination.send(content=content, **kwargs)
