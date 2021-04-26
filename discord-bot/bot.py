import logger
import discord
from openai_api import ApiHandler
from functools import wraps
from Prompts import language_map
from discord.ext import commands
from config import DISCORD_TOKEN, MONGO_URI, MONGO_DBNAME, PREFIX, OPENAI_TOKEN, PASSCODE
from helpers import user_parse, help_message
from Errors import *
import aiohttp
import aiofiles

bot = commands.Bot(command_prefix=PREFIX, help_command=None)

thumbs_up = "👍"
complete = "✅"

def check_auth(method):
    @wraps(method)
    async def _impl(self, *method_args, **method_kwargs):
        if self.authorized:
            method_output = method(self, *method_args, **method_kwargs)
            return await method_output
        else:
            return await self.ask_owner(method_args[0])

    return _impl

class GPTBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.__logger = logger.get_logger("openai_logger")
        self.__api = ApiHandler(self.__logger)
        self.language = "EN"
        self.authorized = False
        self.passcode = "{}".format(PASSCODE)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """
        From: https://gist.github.com/EvieePy/7822af90858ef65012ea500bcecf1612
        """

        if hasattr(ctx.command, 'on_error'):
            return
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return
        ignored = (commands.CommandNotFound,)
        error = getattr(error, 'original', error)
        if isinstance(error, ignored):
            return
        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} has been disabled.')
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        elif isinstance(error, commands.PrivateMessageOnly):
            try:
                await ctx.author.send(f'{ctx.command} can only be used in Private Messages.')
            except discord.HTTPException:
                pass

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        owner_id = guild.owner_id
        guild_id = guild.id
        guild_name = guild.name

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        guild_id = guild.id

    async def cog_before_invoke(self, ctx):
        await ctx.message.add_reaction(thumbs_up)

    async def cog_after_invoke(self, ctx):
        await ctx.message.remove_reaction(thumbs_up, self.bot.user)
        await ctx.message.add_reaction(complete)

    async def check_server_token(self, ctx):
        guild_id = ctx.guild.id

    @staticmethod
    async def prompt_setup(ctx):
        await ctx.send("Owner of this server hasn't configured the bot yet. If you're the owner, send this bot a DM "
                       "with command !setup.")

    @staticmethod
    async def empty_warning(ctx):
        await ctx.send("Hey, no empty prompts!")

    @staticmethod
    async def openai_down_warning(ctx):
        await ctx.send("OpenAI seems to be down. This sometimes happen and is usually resolved within minutes.")

    @staticmethod
    async def credit_warning(ctx):
        user_id, user_name = user_parse(ctx)
        await ctx.send("{}, your daily allowance is over. :cry:".format(user_name))

    @staticmethod
    async def not_admin_warning(ctx):
        user_id, user_name = user_parse(ctx)
        await ctx.send("{}, this command is only usable by admins.".format(user_name))

    @staticmethod
    async def ask_owner(ctx):
        user_id, user_name = user_parse(ctx)
        await ctx.send("{}, if you know the passcode to enable me write: !passcode the_passcode.".format(user_name))

    @commands.command()
    @check_auth
    async def answer(self, ctx, *prompt: str):
        usage = len(list("".join(prompt)))
        user_id, user_name = user_parse(ctx)
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.answer(prompt, language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @check_auth
    async def question(self, ctx, *prompt: str):
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.answer(prompt, language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @check_auth
    async def generate(self, ctx, *prompt: str):
        usage = len(list("".join(prompt)))
        user_id, user_name = user_parse(ctx)
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.generate(prompt, language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @check_auth
    async def complete(self, ctx, *prompt: str):
        usage = len(list("".join(prompt)))
        user_id, user_name = user_parse(ctx)
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.complete(prompt, language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @check_auth
    async def song(self, ctx, *prompt: str):
        user_id, user_name = user_parse(ctx)
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.song(song_name=prompt, language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @check_auth
    async def foulmouth(self, ctx, *prompt: str):
        user_id, user_name = user_parse(ctx)
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.foulmouth_answer(prompt, language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @check_auth
    async def sentiment(self, ctx, *prompt: str):
        user_id, user_name = user_parse(ctx)
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.sentiment(prompt, language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @check_auth
    async def emojify(self, ctx, *prompt: str):
        user_id, user_name = user_parse(ctx)
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.emojify(prompt, language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @check_auth
    async def sarcasm(self, ctx, *prompt: str):
        user_id, user_name = user_parse(ctx)
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.sarcastic_answer(prompt, language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @check_auth
    async def headline(self, ctx, *prompt: str):
        user_id, user_name = user_parse(ctx)
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.headline(prompt, language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @check_auth
    async def ad(self, ctx, *prompt: str):
        user_id, user_name = user_parse(ctx)
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.ad(prompt, language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @check_auth
    async def product(self, ctx, *prompt: str):
        user_id, user_name = user_parse(ctx)
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.product(prompt, language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @check_auth
    async def recipe(self, ctx, *prompt: str):
        user_id, user_name = user_parse(ctx)
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.recipe(prompt, language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @check_auth
    async def hood(self, ctx, *prompt: str):
        user_id, user_name = user_parse(ctx)
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.personality(prompt, "hood", language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @check_auth
    async def trump(self, ctx, *prompt: str):
        user_id, user_name = user_parse(ctx)
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.personality(prompt, "trump", language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @check_auth
    async def trumpy(self, ctx, *prompt: str):
        user_id, user_name = user_parse(ctx)
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.personality(prompt, "trumpy", language=self.language, stops=['Bush:'])
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @check_auth
    async def pedantic(self, ctx, *prompt: str):
        user_id, user_name = user_parse(ctx)
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.personality(prompt, "pedantic", language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))
    
    @commands.command()
    @check_auth
    async def qanon(self, ctx, *prompt: str):
        user_id, user_name = user_parse(ctx)
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.personality(prompt, "qanon", language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @check_auth
    async def woke(self, ctx, *prompt: str):
        user_id, user_name = user_parse(ctx)
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.personality(prompt, "woke", language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @check_auth
    async def tldr(self, ctx, *prompt: str):
        user_id, user_name = user_parse(ctx)
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.tldr(prompt, language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @commands.guild_only()
    @check_auth
    async def join(self, ctx):
        connected = ctx.author.voice
        if connected:
            await ctx.send("Coming in...")
            try:
                await connected.channel.connect()
            except Exception as e:
                await ctx.send(e)
        else:
            await ctx.send("What channel dude?")

    @commands.command()
    @commands.guild_only()
    @check_auth
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()

    @commands.command()
    async def ping(self, ctx):
        return await ctx.send(discord.utils.escape_mentions("I'm alive and well!"))

    @commands.command()
    async def passcode(self,ctx, *prompt:str):
        if "".join(prompt) == "{}".format(PASSCODE):
            self.authorized = not self.authorized
        message = 'Use me' if self.authorized else "I won't say anything now. Talk to Moises"
        return await ctx.send(message)    

    @commands.command()
    @check_auth
    async def say(self, ctx, *prompt: str):
        params = {
            "speaker": "donald-trump",
            "text": " ".join(prompt),
        }
        async with aiohttp.ClientSession() as session:
            async with session.post('https://mumble.stream/speak',json=params) as r:
                if r.status == 200:
                    await ctx.send('Listen')
                    try:
                        voice_channel = ctx.author.voice.channel
                        await ctx.send("I'm at {}".format(voice_channel))
                        voice_client = ctx.channel.guild.voice_client

                        f = await aiofiles.open('/tmp/trump.wav', mode='wb')
                        await f.write(await r.read())
                        await f.close()

                        player = discord.FFmpegPCMAudio('/tmp/trump.wav')
                        voice_client.play(player)
                        if voice_client.is_playing():
                            print("playing baby!")

                    except Exception as e:
                        await ctx.send("Could not speak because {}".format(e))
                    return result
                else:
                    await ctx.send(r.status)

    @commands.command()
    @check_auth
    async def trump_says(self, ctx, *prompt: str):
        answer = await self.__api.personality(prompt, "trumpy", language=self.language, stops=['Bush:'])
        params = {
            "speaker": "donald-trump",
            "text": answer,
        }
        await ctx.send(discord.utils.escape_mentions(answer))
        async with aiohttp.ClientSession() as session:
            async with session.post('https://mumble.stream/speak',json=params) as r:
                if r.status == 200:
                    await ctx.send('Listen')
                    try:
                        voice_channel = ctx.author.voice.channel
                        await ctx.send("I'm at {}".format(voice_channel))
                        voice_client = ctx.channel.guild.voice_client

                        f = await aiofiles.open('/tmp/trump.wav', mode='wb')
                        await f.write(await r.read())
                        await f.close()

                        player = discord.FFmpegPCMAudio('/tmp/trump.wav')
                        voice_client.play(player)
                        if voice_client.is_playing():
                            print("playing baby!")

                    except Exception as e:
                        await ctx.send("Could not speak because {}".format(e))
                    return result
                else:
                    await ctx.send(r.status)


if __name__ == "__main__":
    bot.add_cog(GPTBot(bot))
    bot.run(DISCORD_TOKEN)
