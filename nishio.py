import asyncio
from http import client
import discord
from setuptools import Command
import youtube_dl
from discord.ext import commands
import json
import glob
import os
import requests


if os.path.exists("./config.json"):
    config_file = open('config.json', 'r')
    config = json.load(config_file)
else:
    print("Make sure to rename 'config.example.json' to 'config.json'")
    exit(-1)

youtube_dl.utils.bug_reports_message = lambda: ''


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
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['a', 'av'])
    async def avatar(self, ctx, *,  avamember: discord.Member = None):
        """Returns someone's avatar"""
        if (avamember == None):
            await ctx.send(ctx.message.author.avatar_url)
        else:

            userAvatarUrl = avamember.avatar_url
            await ctx.send(userAvatarUrl)

    @commands.command(aliases=['ui', 'i'])
    async def userinfo(self, ctx, *,  pinged_user: discord.Member = None):
        """returns the user's info"""

        if (pinged_user == None):

            embed = discord.Embed(title="Userinfo command", url="https://github.com/inthecatsdreams/nishio",
                                  description=ctx.message.author.display_name + "'s info", color=ctx.message.author.color)
            embed.set_author(name=ctx.message.author.display_name)
            embed.set_thumbnail(url=ctx.message.author.avatar_url)
            embed.add_field(name="Registered on ",
                            value=ctx.message.author.created_at, inline=True)
            embed.add_field(name="Joined on ",
                            value=ctx.message.author.joined_at, inline=True)
            embed.add_field(
                name="User id ", value=ctx.message.author.id, inline=True)
            embed.add_field(name="Colour representing the user ",
                            value=ctx.message.author.color)
            
            embed.set_footer(text=f"userinfo command invoked by {ctx.message.author.display_name}")
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Userinfo command", url="https://github.com/inthecatsdreams/nishio",
                                  description=pinged_user.display_name + "'s info", color=pinged_user.color)
            embed.set_author(name=pinged_user.display_name)
            embed.set_thumbnail(url=pinged_user.avatar_url)
            embed.add_field(name="Registered on ",
                            value=pinged_user.created_at, inline=True)
            embed.add_field(name="Joined on ",
                            value=pinged_user.joined_at, inline=True)
            embed.add_field(
                name="User id ", value=pinged_user.id, inline=True)
            embed.add_field(name="Colour representing the user ",
                            value=pinged_user.color)
            embed.set_footer(text=f"userinfo command invoked by {ctx.message.author.display_name}")
            await ctx.send(embed=embed)

    @commands.command()
    async def booru(self, ctx):
        """Browse safebooru (danbooru is haram)"""
        query = ctx.message.content.split(" ")[1]
        api_url = f"https://safebooru.donmai.us/posts.json?random=true&tags={query}&rating=safe&limit=1"
        r = requests.get(api_url)
        pic = r.json()[0]["file_url"]
        embed = discord.Embed(title=f"result for {query}", url=pic)
        embed.set_image(url=pic)

        await ctx.send(embed=embed)


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['b'])
    async def ban(self, ctx, *,  pinged_user: discord.Member = None):
        """Ban someone"""
        if (pinged_user == None):
            await ctx.send("Please mention a user to ban.")
        else:
            await pinged_user.ban()
            await ctx.send(f"{pinged_user.display_name} has been banned.")

    @commands.command(aliases=['k'])
    async def kick(self, ctx, *,  pinged_user: discord.Member = None):
        """Kick someone"""
        if (pinged_user == None):
            await ctx.send("Please mention a user to kick.")
        else:
            await pinged_user.kick()
            await ctx.send(f"{pinged_user.display_name} has been kicked.")

    @commands.command(aliases=['un'])
    async def unban(self, ctx, *, member):
        """Unban someone"""
        banned_users = await ctx.guild.bans()

        member_name, member_discriminator = member.split('#')
        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.channel.send(f"{user.mention} has been unbanned.")


bot = commands.Bot(command_prefix=commands.when_mentioned_or(config["prefix"]),
                   description='**I am still a WIP please blame inthecatsdreams#2187 if I break**:')


@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')
    game = discord.Game(f"{config['prefix']}help | ready soon :tm:")
    await bot.change_presence(status=discord.Status.do_not_disturb, activity=game)


bot.add_cog(General(bot))
bot.add_cog(Moderation(bot))
bot.run(config["token"])
