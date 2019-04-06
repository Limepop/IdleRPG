"""
The IdleRPG Discord Bot
Copyright (C) 2018-2019 Diniboy and Gelbpunkt

This software is dual-licensed under the GNU Affero General Public License for non-commercial and the Travitia License for commercial use.
For more information, see README.md and LICENSE.md.
"""


import asyncio

from discord.ext import commands
from utils.checks import is_admin, user_has_char
from classes.converters import User


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @is_admin()
    @commands.command(aliases=["agive"], description="Gift money!", hidden=True)
    async def admingive(self, ctx, money: int, other: User):
        if not await user_has_char(self.bot, other.id):
            return await ctx.send("That person hasn't got a character.")
        await self.bot.pool.execute(
            'UPDATE profile SET money=money+$1 WHERE "user"=$2;', money, other.id
        )
        await ctx.send(
            f"Successfully gave **${money}** without a loss for you to **{other}**."
        )
        await self.bot.http.send_message(
            self.bot.config.admin_log_channel,
            f"**{ctx.author}** gave **${money}** to **{other}**.",
        )

    @is_admin()
    @commands.command(aliases=["aremove"], description="Delete money!", hidden=True)
    async def adminremove(self, ctx, money: int, other: User):
        if not await user_has_char(self.bot, other.id):
            return await ctx.send("That person hasn't got a character.")
        await self.bot.pool.execute(
            'UPDATE profile SET money=money-$1 WHERE "user"=$2;', money, other.id
        )
        await ctx.send(f"Successfully removed **${money}** from **{other}**.")
        channel = self.bot.get_channel(self.bot.config.admin_log_channel)
        await self.bot.http.send_message(
            self.bot.config.admin_log_channel,
            f"**{ctx.author}** removed **${money}** from **{other}**.",
        )

    @is_admin()
    @commands.command(
        aliases=["adelete"], description="Deletes a character.", hidden=True
    )
    async def admindelete(self, ctx, other: User):
        if other.id in ctx.bot.config.admins:
            return await ctx.send("Very funny...")
        if not await user_has_char(self.bot, other.id):
            return await ctx.send("That person doesn't have a character.")
        await self.bot.pool.execute('DELETE FROM profile WHERE "user"=$1;', other.id)
        await ctx.send("Successfully deleted the character.")
        await self.bot.http.send_message(
            self.bot.config.admin_log_channel, f"**{ctx.author}** deleted **{other}**."
        )

    @is_admin()
    @commands.command(aliases=["arename"], description="Changes a character name")
    async def adminrename(self, ctx, target: User):
        if target.id in ctx.bot.config.admins:
            return await ctx.send("Very funny...")
        if not await user_has_char(self.bot, target.id):
            return await ctx.send("That person doesn't have a character.")
        await ctx.send(
            "What shall the character's name be? (Minimum 3 Characters, Maximum 20)"
        )

        def mycheck(amsg):
            return (
                amsg.author == ctx.author
                and len(amsg.content) < 21
                and len(amsg.content) > 2
            )

        try:
            name = await self.bot.wait_for("message", timeout=60, check=mycheck)
        except asyncio.TimeoutError:
            return await ctx.send("Timeout expired.")
        name = name.content
        await self.bot.pool.execute(
            'UPDATE profile SET "name"=$1 WHERE "user"=$2;', name, target.id
        )
        await self.bot.http.send_message(
            self.bot.config.admin_log_channel,
            f"**{ctx.author}** renamed **{target}** to **{name}**.",
        )

    @is_admin()
    @commands.command(aliases=["acrate"], description="Gives crates to a user.")
    async def admincrate(self, ctx, target: User, amount: int = 1):
        await self.bot.pool.execute(
            'UPDATE profile SET "crates"="crates"+$1 WHERE "user"=$2;',
            amount,
            target.id,
        )
        await ctx.send(f"Successfully gave **{amount}** crates to **{target}**.")
        await self.bot.http.send_message(
            self.bot.config.admin_log_channel,
            f"**{ctx.author}** gave **{amount}** crates to **{target}**.",
        )

    @is_admin()
    @commands.command(aliases=["axp"], description="Gives XP to a user.")
    async def adminxp(self, ctx, target: User, amount: int):
        async with self.bot.pool.acquire() as conn:
            await conn.execute(
                'UPDATE profile SET "xp"="xp"+$1 WHERE "user"=$2;', amount, target.id
            )
        await ctx.send(f"Successfully gave **{amount}** XP to **{target}**.")
        await self.bot.http.send_message(
            self.bot.config.admin_log_channel,
            f"**{ctx.author}** gave **{amount}** XP to **{target}**.",
        )


def setup(bot):
    bot.add_cog(Admin(bot))
