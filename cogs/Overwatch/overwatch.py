"""
This Cog is mostly for the Discord server I have with friends I play
Overwatch with. It isn't used on the Hatventures Community server but I
share it nonetheless. Some features will not make sense to you, but the
technical stuff is interesting enough that it deserves a look at.
"""

import json
import numpy as np
import pickle
from PIL import Image
import re

import aiohttp
import discord
from discord.ext import commands

from ..utils.dicts import AttrDict
from ..utils.gifs import random_gif

VALID_HEROES = [
    'all',
    'ana',
    'ashe',
    'baptiste',
    'bastion',
    'brigitte',
    'dVa',
    'doomfist',
    'genji',
    'hanzo',
    'junkrat',
    'lucio',
    'mccree',
    'mei',
    'mercy',
    'moira',
    'orisa',
    'pharah',
    'reaper',
    'reinhardt',
    'roadhog',
    'soldier76',
    'sombra',
    'symmetra',
    'torbjorn',
    'tracer',
    'widowmaker',
    'winston',
    'wreckingBall',
    'zarya',
    'zenyatta',
]
EMBED_COLOR = 0xF99E1A


class Overwatch(commands.Cog):
    """Commands for the GrandMasters."""

    def __init__(self, bot):
        self.bot = bot
        self.playing_overwatch = 0
        self.is_playing = False
        self.api_url = \
            'https://ow-api.com/v1/stats/pc/us/{battletag}/{type}/{heroes}'
        # self.api_url = 'https://ovrstat.com/stats/pc/us/{battletag}'
        with open('cogs/Overwatch/battletags.pkl', 'rb') as f:
            self.battletags = pickle.load(f)

        with open('cogs/Overwatch/zenyatta.json', 'r') as f:
            self.voice_lines = json.load(f)

        # Init guild and channel data, and activity status.
        self.bot.loop.create_task(self.load_data())

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Modify how many members are playing Overwatch, if it applies."""

        def is_game(x):
            return x.name == 'Overwatch'

        if before.activities != after.activities and not before.bot:
            # print('Cog Overwatch.on_member_update was called, game changed!')

            try:
                if any(map(is_game, after.activities)):
                    self.playing_overwatch += 1

            except AttributeError:
                pass

            try:
                if any(map(is_game, before.activities)):
                    self.playing_overwatch -= 1

            except AttributeError:
                pass

            if self.playing_overwatch > 0 and not self.is_playing:
                await self.play_overwatch()

            elif self.playing_overwatch == 0 and self.is_playing:
                await self.stop_overwatch()

    async def load_data(self):
        """Initialize some parameters, such as the number or members
        currently in Overwatch.
        """
        await self.bot.wait_until_ready()

        all_members = set([m for m in self.bot.get_all_members() if not m.bot])

        def is_game(x):
            return x.name == 'Overwatch'

        for m in all_members:
            try:
                if any(map(is_game, m.activities)):
                    self.playing_overwatch += 1
            except AttributeError:
                pass

        if self.playing_overwatch > 0:
            await self.play_overwatch()

    @commands.command(aliases=['decalre'])
    async def declare(self, ctx):
        """Send a gif to declare a game of Overwatch!"""

        # because xplio keeps making typos
        if ctx.invoked_with == 'decalre':
            _ing = 'decalring'
        else:
            _ing = 'declaring'

        vl = self.voice_lines['PreGame'] + \
            self.voice_lines['Objective'] + \
            self.voice_lines['Spawn'] + \
            self.voice_lines['Ability'] + \
            self.voice_lines['Fire'] + \
            self.voice_lines['Healing'] + \
            self.voice_lines['Kills'] + \
            self.voice_lines['Ultimate']
        vl = np.random.choice(vl)
        gif_url = await random_gif(self.bot.http_session, 'overwatch')
        description = (
            f'{vl} {ctx.author.mention} is {_ing}, join the fight.'
        )

        embed = discord.Embed(
            description=description,
            color=EMBED_COLOR,
        ).set_image(
            url=gif_url,
        )

        await ctx.send(embed=embed)

    @commands.group(aliases=['ow'])
    async def overwatch(self, ctx):
        """Shows stats for the player.
        The author must have registered their BattleTag beforehand.
        """
        await ctx.channel.trigger_typing()
        if ctx.invoked_subcommand is None:
            await ctx.send('Unknown subcommand.')

    @overwatch.command(name='register')
    async def overwatch_register(self, ctx, battletag):
        """Links the Discord User to their BattleTag."""

        # check if the provided BattleTag is in the right format
        valid = re.match(r'.*?#\d{4,5}', battletag)
        if not valid:
            content = (
                f'BattleTag {battletag} is not valid. Please enter '
                'in the format `username#01234`.'
            )
        else:
            # if it is valid, try to get the data
            payload = {
                'type': 'profile',
                'battletag': battletag.replace('#', '-'),
                'heroes': '',
            }
            async with self.bot.http_session.get(
                    self.api_url.format(**payload)) as resp:
                try:
                    resp.raise_for_status()
                except aiohttp.ClientResponseError:
                    # this is raised only if the status code is 4xx or 5xx
                    if resp.status < 500:  # is a 4xx error code
                        content = (
                            'Could not find that BattleTag. '
                            'Make sure you entered it correctly.'
                        )
                    else:  # is a 5xx error code
                        content = (
                            'Something went wrong but the BattleTag '
                            'seemed correct. I registered it anyway.'
                        )
                        self.battletags[ctx.author.id] = battletag
                else:
                    content = 'BattleTag registered successfully! Thank you!'
                    self.battletags[ctx.author.id] = battletag

            with open('cogs/Overwatch/battletags.pkl', 'wb') as f:
                pickle.dump(self.battletags, f)

        await ctx.send(content)

    @overwatch_register.error
    async def overwatch_register_error(self, ctx, error):
        """Error handling for the overwatch register subcommand."""

        if isinstance(error, commands.MissingRequiredArgument):
            try:
                battletag = self.battletags[ctx.author.id]
            except KeyError:
                battletag = None

            if battletag:
                await ctx.send(
                    f'Your current BattleTag is {battletag}. '
                    'If you want to change it, run `!ow register Name#01234`.'
                )
            else:
                await ctx.send(
                    'I do not have your BattleTag. If you want to '
                    'register it, run `!ow register Name#01234`.'
                )
        else:
            raise error

    async def overwatch_base(self, ctx, member, hero=''):
        """Get data and create the base Embed."""

        type_dict = {
            'profile': 'profile',
            'quickplay': 'complete',
            'competitive': 'complete',
            'hero': 'heroes',
        }
        type = type_dict[ctx.invoked_with]

        try:
            battletag = self.battletags[member.id]
        except KeyError as e:
            await ctx.send(
                f'Unknown BattleTag for member {member}. :frowning:'
            )
            raise e

        payload = {
            'type': type,
            'battletag': battletag.replace('#', '-'),
            'heroes': hero,
        }

        async with self.bot.http_session.get(
                self.api_url.format(**payload)) as resp:
            try:
                resp.raise_for_status()
            except aiohttp.ClientResponseError as e:
                await ctx.send(f':warning: Error code {resp.status}.')
                raise e

            data = await resp.json()
            with open('cogs/Overwatch/data.json', 'w') as f:
                # for debugging
                json.dump(data, f, indent=2, sort_keys=True)
            data = AttrDict.from_nested_dict(data)

        imgs = ['icon', 'levelIcon']
        if data['prestige'] % 6 != 0:
            imgs.append('prestigeIcon')
        for img in imgs:
            async with self.bot.http_session.get(
                    data[img].strip()) as resp:  # remove possible spaces
                if resp.status == 200:
                    with open(f'cogs/Overwatch/{img}.png', 'wb') as f:
                        f.write(await resp.content.read())

        # Edit profile portrait
        await self.bot.loop.run_in_executor(
            None, self._make_overwatch_profile_figure, data)

        title_dict = {
            'profile': 'profile',
            'quickplay': 'quickplay statistics',
            'competitive': 'competitive statistics',
            'hero': 'hero statistics',
        }
        title = title_dict[ctx.invoked_with]

        e = discord.Embed(
            title=f'Overwatch {title} for {member}.',
            type='rich',
            colour=EMBED_COLOR,
        )

        if data.private:
            e.set_footer(
                text=(
                    'Profile is private, for more info please '
                    'make it public in Overwatch > Options > Social > '
                    'Career Profile Visibility.'
                )
            )
        e.set_thumbnail(url='attachment://full.png')
        return data, e

    @overwatch.command(name='profile')
    async def overwatch_profile(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        try:
            data, e = await self.overwatch_base(ctx, member)
        except Exception as e:
            print('Raised', type(e).__name__, e)
            return

        e.add_field(
            name='BattleTag',
            value=data.name,
        )
        e.add_field(
            name='Level',
            value=data.level + 100 * data.prestige,
        )
        e.add_field(
            name='Endorsement Level',
            value=data.endorsement,
        )
        e.add_field(
            name='Games Won',
            value=data.gamesWon,
        )

        await ctx.send(embed=e, file=discord.File('cogs/Overwatch/full.png'))

    @overwatch.command(name='quickplay')
    async def overwatch_quickplay(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        try:
            data, e = await self.overwatch_base(ctx, member)
        except Exception as e:
            print('Raised', type(e).__name__, e)
            return

        # edict = e.to_dict()
        # edict['description'] = ':warning: Not yet fully implemented.'
        # e = discord.Embed.from_dict(edict)

        qpc = data.quickPlayStats.careerStats.allHeroes
        # general
        e.add_field(
            name='Kills',
            value=qpc.combat.eliminations,
        )
        e.add_field(
            name='Deaths',
            value=qpc.combat.deaths,
        )
        e.add_field(
            name='Games Won',
            value=qpc.game.gamesWon,
        )
        meds = []
        for med in ('Bronze', 'Silver', 'Gold', ''):
            try:
                meds.append(qpc.matchAwards[f'medals{med}'])
            except KeyError:
                meds.append(0)
        medB, medS, medG, medT = meds
        e.add_field(
            name='Medals',
            value=(f'{medB}:third_place: {medS}:second_place: '
                   f'{medG}:first_place: ({medT}:medal:)'),
            inline=False,
        )
        # offence
        e.add_field(
            name='Most Damage Done',
            value=qpc.best.allDamageDoneMostInGame,
        )
        e.add_field(
            name='Total Damage Done',
            value=qpc.combat.damageDone,
        )
        # assists
        e.add_field(
            name='Most Healing Done',
            value=qpc.best.healingDoneMostInGame,
        )
        e.add_field(
            name='Total Healing Done',
            value=qpc.assists.healingDone,
        )
        e.add_field(
            name='Defensive Assists',
            value=qpc.assists.defensiveAssists,
        )
        e.add_field(
            name='Offensive Assists',
            value=qpc.assists.offensiveAssists,
        )

        await ctx.send(embed=e, file=discord.File('cogs/Overwatch/full.png'))

    @overwatch.command(name='competitive')
    async def overwatch_competitive(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        try:
            data, e = await self.overwatch_base(ctx, member)
        except Exception as e:
            print('Raised', type(e).__name__, e)
            return

        # edict = e.to_dict()
        # edict['description'] = ':warning: Not yet implemented.'
        # e = discord.Embed.from_dict(edict)

        cc = data.competitiveStats.careerStats.allHeroes
        # general
        e.add_field(
            name='Kills',
            value=cc.combat.eliminations,
        )
        e.add_field(
            name='Deaths',
            value=cc.combat.deaths,
        )
        e.add_field(
            name='Games Won',
            value=cc.game.gamesWon,
        )
        meds = []
        for med in ('Bronze', 'Silver', 'Gold', ''):
            try:
                meds.append(cc.matchAwards[f'medals{med}'])
            except KeyError:
                meds.append(0)
        medB, medS, medG, medT = meds
        e.add_field(
            name='Medals',
            value=(f'{medB}:third_place: {medS}:second_place: '
                   f'{medG}:first_place: ({medT}:medal:)'),
            inline=False,
        )
        # offence
        e.add_field(
            name='Most Damage Done',
            value=cc.best.allDamageDoneMostInGame,
        )
        e.add_field(
            name='Total Damage Done',
            value=cc.combat.damageDone,
        )
        # assists
        e.add_field(
            name='Most Healing Done',
            value=cc.best.healingDoneMostInGame,
        )
        e.add_field(
            name='Total Healing Done',
            value=cc.assists.healingDone,
        )
        e.add_field(
            name='Defensive Assists',
            value=cc.assists.defensiveAssists,
        )
        e.add_field(
            name='Offensive Assists',
            value=cc.assists.offensiveAssists,
        )

        await ctx.send(embed=e, file=discord.File('cogs/Overwatch/full.png'))

    @overwatch.command(name='hero')
    async def overwatch_hero(self, ctx, member, hero=''):
        # try to see if first member is a discord.Member
        try:
            converter = commands.MemberConverter()
            member = await converter.convert(ctx, member)
        except commands.BadArgument:
            hero = member
            member = ctx.author

        try:
            data, e = await self.overwatch_base(ctx, member, hero)
        except Exception as ex:
            print('Raised', type(ex).__name__, ex)
            return

        edict = e.to_dict()
        edict['description'] = ':warning: Not yet implemented.'
        e = discord.Embed.from_dict(edict)

        await ctx.send(embed=e, file=discord.File('cogs/Overwatch/full.png'))

    @commands.Cog.listener(name='on_message')
    async def on_mention(self, message):
        """Send a Zenyatta voice line."""

        ctx = await self.bot.get_context(message)

        mentions = self.voice_lines['Ability'] + \
            self.voice_lines['Communication'] + \
            self.voice_lines['Hello']

        if ctx.me.mentioned_in(message) \
                and not message.author.bot \
                and not message.mention_everyone \
                and not message.content.startswith(self.bot.command_prefix):

            out = np.random.choice(mentions)
            await message.channel.send(out)

    async def play_overwatch(self):
        self.is_playing = True
        await self.bot.change_presence(activity=discord.Game(name='Overwatch'))

    async def stop_overwatch(self):
        self.is_playing = False
        await self.bot.change_presence(activity=None)

    def _make_overwatch_profile_figure(self, data):
        # load pictures
        icon = Image.open('cogs/Overwatch/icon.png')
        # resize icon to 256x256
        icon = icon.resize((128, 128), Image.ANTIALIAS)
        portrait = Image.open('cogs/Overwatch/levelIcon.png')
        prestige = Image.open('cogs/Overwatch/prestigeIcon.png')
        filter = Image.open(
            'cogs/Overwatch/portraitFilter.png').convert('RGBA')
        # create empty canvas
        new = Image.new('RGBA', portrait.size)
        # paste icon in the middle
        new.paste(icon, (64, 64))  # found by hand
        # trim the edges
        new = Image.composite(new, filter, filter)
        # paste portrait on top
        new.paste(portrait, mask=portrait)
        # paste prestige on top
        if data.prestige % 6 != 0:
            new.paste(prestige, (0, 128), mask=prestige)
        new.save('cogs/Overwatch/full.png')
        img = discord.File('cogs/Overwatch/full.png')

        return img
