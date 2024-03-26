"""
Voice Commands for the FortBot
"""

import logging
import asyncio
import discord
from discord.ext import commands
import yt_dlp

logger = logging.getLogger("discord")

yt_dlp.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn',
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDL(discord.PCMVolumeTransformer):
    """
    """
    def __init__(self, source, *, data, volume=5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        """
        """
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class FortVoice(commands.Cog):
    """
    """
    def __init__(self, bot) -> None:
        self.bot = bot

    async def _play_clip(self, ctx: commands.Context, url: str):
        """
        """
        player = await YTDL.from_url(url, loop=self.bot.loop,
                                     stream=True)
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
        ctx.voice_client.play(player,
                              after=lambda e: logger.error('Player error: %s').format(e)
                              if e else None)

    @commands.command(help="Connects the bot to the voice channel, \
                      required for voice based commands",
                      brief="Connect bot to voice")
    async def connect(self, ctx: commands.Context):
        """
        """
        if ctx.author.voice:
            if ctx.voice_client is not None:
                await ctx.voice_client.move_to(ctx.author.voice.channel)
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("But i'll be all alone! :(")
            raise commands.CommandError("Author not connected to a voice channel.")

    @commands.command(help="Disconnects the bot from the voice channel",
                      brief="Disconnect bot from voice")
    async def disconnect(self, ctx: commands.Context):
        """
        """
        await ctx.voice_client.disconnect(force=False)

    @commands.command(help="What a fucking nightmare!")
    async def nightmare(self, ctx: commands.Context):
        """
        """
        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
        if ctx.author.voice:
            async with ctx.typing():
                await self._play_clip(ctx, "https://www.youtube.com/watch?v=eJNRXYmNpKw")
        else:
            await ctx.send("You are not connected to a voice channel.")
            raise commands.CommandError("Author not connected to a voice channel.")

    @commands.command(help="Gotta thank the bus driver!")
    async def bus(self, ctx: commands.Context):
        """
        """
        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
        if ctx.author.voice:
            async with ctx.typing():
                await self._play_clip(ctx, "https://www.youtube.com/watch?v=ZbNHUA1FKi0")
        else:
            await ctx.send("You are not connected to a voice channel.")
            raise commands.CommandError("Author not connected to a voice channel.")
   
    @commands.command(help="oh dear")
    async def trouble(self, ctx: commands.Context):
        """
        """
        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
        if ctx.author.voice:
            async with ctx.typing():
                await self._play_clip(ctx, "https://www.youtube.com/watch?v=TTEJ3_hdPVM")
        else:
            await ctx.send("You are not connected to a voice channel.")
            raise commands.CommandError("Author not connected to a voice channel.")

    commands.command()
    async def bussing(self, ctx: commands.Context):
        """
        """
        raise NotImplementedError

async def setup(bot: commands.Bot):
    """
    """
    await bot.add_cog(FortVoice(bot))
