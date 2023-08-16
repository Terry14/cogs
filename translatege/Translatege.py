"""translate-ge cog for Red-DiscordBot by Terbi."""
import random
from contextlib import suppress
from typing import ClassVar, Union

import discord
from redbot.core import commands

from .pcx_lib import type_message


class Translatege(commands.Cog):
    """translatege."""

    __author__ = "Terbi"
    __version__ = "1.0.1"
    #
    # Red methods
    #

    def format_help_for_context(self, ctx: commands.Context) -> str:
        """Show version in help."""
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\n\nCog Version: {self.__version__}"

    async def red_delete_data_for_user(self, *, _requester: str, _user_id: int) -> None:
        """Nothing to delete."""
        return

    #
    # Command methods
    #

    @commands.command(aliases=["ge"])
    async def translatege(self, ctx: commands.Context, *, text: Union[str, None] = None) -> None:
        """translategeize the replied to message, previous message, or your own text."""
        if not text:
            if hasattr(ctx.message, "reference") and ctx.message.reference:
                with suppress(
                    discord.Forbidden, discord.NotFound, discord.HTTPException
                ):
                    message_id = ctx.message.reference.message_id
                    if message_id:
                        text = (await ctx.fetch_message(message_id)).content
            if not text:
                messages = [message async for message in ctx.channel.history(limit=2)]
                # [0] is the command, [1] is the message before the command
                text = messages[1].content or "I can't translate that!"
        await type_message(
            ctx.channel,
            self.translatege_string(text),
            allowed_mentions=discord.AllowedMentions(
                everyone=False, users=False, roles=False
            ),
        )

    #
    # Public methods
    #

    def translatege_string(self, string: str) -> str:
        """translatege and return a string."""
        converted = ""
        current_word = ""
        for letter in string:
            if letter.isprintable() and not letter.isspace():
                current_word += letter
            elif current_word:
                converted += self.translatege_word(current_word) + letter
                current_word = ""
            else:
                converted += letter
        if current_word:
            converted += self.translatege_word(current_word)
        return converted

    def translatege_word(self, word: str) -> str:
        """translatege and return a word.

        Thank you to the following for inspiration:
        https://github.com/senguyen1011/UwUinator
        """
        word = word.lower()
        ge = word.rstrip(".?!,")
        punctuations = word[len(ge) :]
        final_punctuation = punctuations[-1] if punctuations else ""
        extra_punctuation = punctuations[:-1] if punctuations else ""

        # Process punctuation
        # if final_punctuation == "." and not random.randint(0, 3):
        #     final_punctuation = random.choice(self.KAOMOJI_JOY)
        # if final_punctuation == "?" and not random.randint(0, 2):
        #     final_punctuation = random.choice(self.KAOMOJI_CONFUSE)
        # if final_punctuation == "!" and not random.randint(0, 2):
        #     final_punctuation = random.choice(self.KAOMOJI_JOY)
        # if final_punctuation == "," and not random.randint(0, 3):
        #     final_punctuation = random.choice(self.KAOMOJI_EMBARRASSED)
        # if final_punctuation and not random.randint(0, 4):
        #     final_punctuation = random.choice(self.KAOMOJI_SPARKLES)

        # Full word exceptions
        # if uwu in ("you're", "youre"):
        #     uwu = "ur"
        # elif uwu == "fuck":
        #     uwu = "fwickk"
        # elif uwu == "shit":
        #     uwu = "poopoo"
        # elif uwu == "bitch":
        #     uwu = "meanie"
        # elif uwu == "asshole":
        #     uwu = "b-butthole"
        # elif uwu in ("dick", "penis"):
        #     uwu = "peenie"
        # elif uwu in ("cum", "semen"):
        #     uwu = "cummies"
        # elif uwu == "ass":
        #     uwu = "boi pussy"
        # elif uwu in ("dad", "father"):
        #     uwu = "daddy"
        # Normal word conversion
        # else:
            # Protect specific word endings from changes
            # protected = ""
        if len(ge) <= 3 and ge not in ["and", "bed"]:
            pass
        elif ge[-1] in "bdgmnprsty" or ge[-2:] == "eo":
            ge = ge + "ge"
        elif ge[-2:] in ["ch", "re"]:
            ge = ge[:-2] + "ge"
        elif ge[-3:] == "ine":
            ge = ge[:-3] + "inge"

        # If ending in ge, occasionally add more ge
        if ge[-2:] == "ge" and random.random() < 0.02:
            ge += "ge"*random.randint(1,4)

        # Add back punctuations and return
        return ge + extra_punctuation + final_punctuation