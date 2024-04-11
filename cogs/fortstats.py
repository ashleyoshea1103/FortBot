"""
Fortnite stats commands for Fortbot
"""

import io
import os
import logging
import aiohttp
import discord
from discord.ext import commands


logger = logging.getLogger("discord")


class FortStats(commands.Cog):
    """
    """

    API_URL = "https://fortniteapi.io"
    API_HEADERS = {"Authorization": os.getenv("API_TOKEN")}

    def __init__(self, bot) -> None:
        self.bot = bot

    async def _get_account_id(self, session: aiohttp.ClientSession,
                            account_name: str) -> str:
        async with session.get(f"{self.API_URL}/v2/lookup?username={account_name}") as req:
            if req.ok:
                data = await req.json()
                return data['account_id']

    async def _get_player_stats(self, session: aiohttp.ClientSession, player_id: str) -> dict:
        logger.info("Attempting to retrieve player stats for %s", player_id)
        try:
            async with session.get(f"{self.API_URL}/v1/stats?account={player_id}") as req:
                if req.ok:
                    data = await req.json()
                    return data['global_stats']
        except KeyError as e:
            logger.error(e)
    
    async def _get_shop(self, session: aiohttp.ClientSession) -> list[dict[str:str]]:
        async with session.get(f"{self.API_URL}/v2/shop?lang=en") as req:
            logger.info("Fetching details about the shop")
            if req.ok:
                data = await req.json()
                return data['shop']


    @commands.command(help="Get the number of kills across all seasons. Fetch for a different \
                      user by including epic name",
                      brief="Get kill count")
    async def kills(self, ctx: commands.Context, player: str = None):
        async with aiohttp.ClientSession(headers=self.API_HEADERS) as session:
            if player is None:
                player_id = await self._get_account_id(session, ctx.author.display_name)
            else:
                player_id = await self._get_account_id(session, player)
            try:
                stats = await self._get_player_stats(session, player_id)
                message = (f"Kills:\n"
                           f"Solo: {stats['solo']['kills']}\n"
                           f"Duo: {stats['duo']['kills']}\n"
                           f"Trio: {stats['trio']['kills']}\n"
                           f"Squads: {stats['squad']['kills']}")
                embed = discord.Embed(description=message)
                embed.colour = discord.Colour.red()
                await ctx.send(f"Here are the stats that you asked for @{ctx.author.display_name}:",
                               embed=embed)
            except KeyError:
                await ctx.send("Unable to fetch data from the Fornite API")

    @commands.command(help="Get the number of wins across all seasons. \
                      Fetch for a different user by including epic name",
                      brief="Get win count")
    async def wins(self, ctx: commands.Context, player: str = None):
        async with aiohttp.ClientSession(headers=self.API_HEADERS) as session:
            if player is None:
                player_id = await self._get_account_id(session, ctx.author.display_name)
            else:
                player_id = await self._get_account_id(session, player)
            try:
                stats = await  self._get_player_stats(session, player_id)
                message = (f"Wins:\n"
                           f"Solo: {stats['solo']['placetop1']}\n"
                           f"Duo: {stats['duo']['placetop1']}\n"
                           f"Trio: {stats['trio']['placetop1']}\n"
                           f"Squads: {stats['squad']['placetop1']}")
                embed = discord.Embed(description=message)
                embed.colour = discord.Colour.red()
                await ctx.send(f"Here are the stats that you asked for @{ctx.author.display_name}",
                               embed=embed)
            except KeyError as e:
                await ctx.send("Unable to fetch data from the Fortnite API")
                raise commands.CommandError("Unable to fetch data from the api") from e

    @commands.command(help="Get the K/D ratio across all seasons. \
                      Fetch for a different user by including epic name",
                      brief="Get K/D ratio")
    async def kd(self, ctx: commands.Context, player: str = None):
        async with aiohttp.ClientSession(headers=self.API_HEADERS) as session:
            if player is None:
                player_id = await self._get_account_id(session, ctx.author.display_name)
            else:
                player_id = await self._get_account_id(session, player)
            try:
                stats = await self._get_player_stats(session, player_id)
                message = (f"K/D:\n"
                           f"Solo: {stats['solo']['kd']}\n"
                           f"Duo: {stats['duo']['kd']}\n"
                           f"Trio: {stats['trio']['kd']}\n"
                           f"Squads: {stats['squad']['kd']}")
                embed = discord.Embed(description=message)
                embed.colour = discord.Colour.red()
                await ctx.send("Here are the stats that you asked for:", embed=embed)
            except KeyError as e:
                await ctx.send("Unable to fetch data from the Fornite API")
                raise commands.CommandError("Unable to fetch data from the api") from e
  
    @commands.command()
    async def shop_item(self, ctx: commands.Context, item: str):
        async with aiohttp.ClientSession(headers=self.API_HEADERS) as session:
            key_fields = ['displayName', 'firstReleaseDate', 'rarity', 'price']
            shop = await self._get_shop(session=session)
            for element in shop:
                filtered = {key: element[key] for key in key_fields}
                if item == element['displayName']:
                    await ctx.send(f"Here is information about {item}:")
                    await ctx.send(filtered)
                    return


async def setup(bot: commands.Bot):
    await bot.add_cog(FortStats(bot))
