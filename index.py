# region IMPORTS
import datetime
import os
from os.path import exists
from dotenv import load_dotenv

import json
import pandas as pd

import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice

# IMPORT MOJI MAP
import mojimap
import roles
import heroes
import heroicons
import laning

import logging
# endregion

# region ENVIRONMENT
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
# endregion

# region LOGGING
  #check for audit path
auditpath = "/tmp/teddy-audit.csv"
logpath = "/tmp/teddy.log"
header=0
if not os.path.exists(auditpath):
    header=1

def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter(fmt='%(asctime)s: %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
    fileHandler = logging.FileHandler(log_file, mode='a')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    l.setLevel(level)
    l.addHandler(fileHandler)
    l.addHandler(streamHandler)

def setup_audit(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter(fmt='%(asctime)s,%(message)s',datefmt='%Y-%m-%d %H:%M:%S')
    fileHandler = logging.FileHandler(log_file, mode='a')
    fileHandler.setFormatter(formatter)
    l.setLevel(level)
    l.addHandler(fileHandler)

setup_logger('log', logpath)
setup_audit('audit', auditpath)
log = logging.getLogger('log')
audit = logging.getLogger('audit')

  #add CSV header if doesn't exist
if header ==1:
    log.info(f"Writing HEADER to audit log: {auditpath}")
    head = "Timestamp,User,Command,Region,Mode,Elo,Period,Sort,Role,View,ChartView,About,Show,HeroName"
    f = open(auditpath, 'w')
    f.write(f'{head}\n')
    f.close()
else:
    log.info(f"Found log at: {auditpath}")
# endregion

# region VERSION ####
version = "BETA Release Candidate Ver.02.106 (20211027)"
print(f"Starting Teddy-{version}...")
logging.info(f"Starting Teddy-{version}...")
# endregion

# region PERMISSIONS
guild_ids = [850386581135163489,832548513383972884]
print(f"Enabling for Server(s):{guild_ids}")
log.info(f"Enabling for Server(s):{guild_ids}")

optin = [853816389499748382,869691498952802355]
optout = []
# endregion

# region VARIABLES
x = datetime.datetime.now()
today = x.strftime("%Y%m%d")

#rawpath = "/tmp/TierData/"
rawpath = "/var/www/html/TierData/json/"
histpath = "/var/www/html/timeline/summary/"
avgpath = "/var/www/html/timeline/averages/"
chartpath = "/var/www/html/reports/"

prof = ["assassin","marksman","mage","tank","support","fighter"]
lanes = ["gold","exp","mid","jungle","roam"]

kdalim = 20
uselim = 0
winlim = 100

runtimes = os.listdir(rawpath)
runtimes = sorted(runtimes, reverse=True)
latest_run = max(d for d in runtimes)
latest_run = os.path.join(rawpath, latest_run)
print(latest_run)
# endregion

##### DISCORD LISTENERS #######

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
slash = SlashCommand(bot, sync_commands=True)

# region MAIN TD FUNCTION
@slash.slash(name="td",
             description="Use this command to get the most recent TierData!.",
             guild_ids=guild_ids,
             options=[
                 create_option(
                     name="region",
                     description="Look at TierData by REGION.",
                     option_type=3,
                     required=False,
                     choices=[
                         create_choice(
                             name="EU",
                             value="EU"),
                         create_choice(
                             name="NA",
                             value="NA"),
                         create_choice(
                             name="SA",
                             value="SA"),
                         create_choice(
                             name="SE",
                             value="SE")
                     ]
                 ),
                 create_option(
                     name="mode",
                     description="Look at TierData by GAME MODE.",
                     option_type=3,
                     required=False,
                     choices=[
                         create_choice(
                             name="Brawl",
                             value="Brawl"),
                         create_choice(
                             name="Classic",
                             value="Classic"),
                         create_choice(
                             name="Rank",
                             value="Rank")
                     ]
                 ),
                 create_option(
                     name="elo",
                     description="Look at TierData by Player Performance!",
                     option_type=3,
                     required=False,
                     choices=[
                         create_choice(
                             name="Normal",
                             value="Normal"),
                         create_choice(
                             name="High",
                             value="High"),
                         create_choice(
                             name="Very-High",
                             value="Very-High")
                     ]
                 ),
                 create_option(
                     name="period",
                     description="Look at TierData for the previous time-period.",
                     option_type=3,
                     required=False,
                     choices=[
                         create_choice(
                             name="Month",
                             value="Month"),
                         create_choice(
                             name="Week",
                             value="Week"),
                         create_choice(
                             name="All-Time",
                             value="AT")
                     ]
                 ),
                 create_option(
                     name="sort",
                     description="Look at Top Values or Bottom Values.",
                     option_type=3,
                     required=False,
                     choices=[
                         create_choice(
                             name="Top",
                             value="Top"),
                         create_choice(
                             name="Bottom",
                             value="Bottom")
                     ]
                 ),
                 create_option(
                     name="role",
                     description="Look at TierStats for your Favorite Role!",
                     option_type=3,
                     required=False,
                     choices=[
                         create_choice(
                             name="Fighter",
                             value="fighter"),
                         create_choice(
                             name="Mage",
                             value="mage"),
                         create_choice(
                             name="Support",
                             value="support"),
                         create_choice(
                             name="Assassin",
                             value="assassin"),
                         create_choice(
                             name="Marksman",
                             value="marksman"),
                         create_choice(
                             name="Tank",
                             value="tank")
                     ]
                 ),
                 create_option(
                     name="view",
                     description="Look at Different Views!",
                     option_type=3,
                     required=False,
                     choices=[
                         create_choice(
                             name="Normal",
                             value="normal"),
                         create_choice(
                             name="Meta",
                             value="meta"),
                         create_choice(
                             name="Role",
                             value="role"),
                         create_choice(
                             name="WinRate",
                             value="win"),
                         create_choice(
                             name="KDA",
                             value="kda"),
                         create_choice(
                             name="Use",
                             value="use")
                     ]
                 ),
                 create_option(
                     name="chartview",
                     description="Look at Different Chart Views!",
                     option_type=3,
                     required=False,
                     choices=[
                         create_choice(
                             name="Mode x WIN",
                             value="modexwin"),
                         create_choice(
                             name="Mode x KDA",
                             value="modexkda"),
                         create_choice(
                             name="Mode x USE",
                             value="modexuse"),
                        create_choice(
                             name="Mode x WIN (box)",
                             value="modexwinbox"),
                         create_choice(
                             name="Mode x KDA (box)",
                             value="modexkdabox"),
                         create_choice(
                             name="Mode x USE (box)",
                             value="modexusebox")
                     ]
                 ),
                 create_option(
                     name="about",
                     description="view README",
                     option_type=3,
                     required=False,
                     choices=[
                         create_choice(
                             name="Teddy",
                             value="show"),
                        create_choice(
                             name="Commands",
                             value="commands"),
                         create_choice(
                             name="The Data",
                             value="data"),
                         create_choice(
                             name="Outliers",
                             value="outlier")
                        ]
                         )
                     ]
                 )

async def _overall(ctx, region="All", mode="All", elo="All", period="Week", sort="Top", role="null", view="normal",chartview="null", about="null"):
    channelid = ctx.channel.id
    await ctx.send(f":bear: `Processing request...`")
    if channelid in optout:
        await ctx.channel.send(content="`Sorry, I'm not allowed to do that here. \nPlease try a different channel.`")
        channelname = ctx.channel.name
        log.info(f"Permission Denied for Channel: {channelname}({channelid})")
    else:
        #audit
        user = ctx.author
        audit.info(f"{user},dd,{region},{mode},{elo},{period},{sort},{role},{view},{chartview},{about},,")
        log.info(f"{user} used /dd")

        if about!="null":
            if about=="show":
                about_title = "Teddy"
                desc = "Teddy (aka 'TD') is a MLBB TierData Bot made exclusively for the MLBB NA Discord Server.\n\n"
            elif about=="data":
                about_title = "The Data"
                desc = "TierData is provided by https://m.mobilelegends.com/en/rank through an API. Teddy fully synchronizes the data every week which is initially summarized by **period**: \nWeek, Month, and All-Time. \
                              \n\nThe data is further sorted by the following attributes: \n**elo** (Normal, High, Very-High), \n**mode** (Classic, Rank, Brawl), \n**region** (EU,NA,SA,and SE.) \
                              \n\nAll together, this makes-up 384 datasets with over 24000 datapoints! \
                              \nIf you get a warning `No TierData Found.`. \nDon't worry! This means that the specific data file is *missing* and is likely being synchronized, so please be patient!"
            elif about=="commands":
                about_title = "Commands"
                desc = "Command Options List:\
                       \n\n`/td` - Show KDA/WR%/USE% for this Week \
                       \n- `region:(NA,SA,SE,EU)`, default:`All` \
                       \n- `mode:(Brawl,Classic,Rank)`, default: `All-Modes` \
                       \n- `elo:(Normal,High,Very-High)`, default: `All-Levels` \
                       \n- `period:(Month,Week,All-Time)`, default: `Week` \
                       \n- `sort:(Top, Bottom)`, default: Top \
                       \n- `role:(Fighter,Mage,Support,Assassin,Marksman,Tank)`, default: `none` \
                       \n- `view:(Normal,Meta,Role,WinRate,KDA,Use)` default: `Normal` - The view changes from top5 KDA/WR/USE, top10 by KDA,WR,or USE, or top3 by Meta or Role \
                       \n- `chartview:`(Mode x WIN/KDA/USE)+(box optional)`, default: `none` - Historical chart or averages, based on Top5 for each filter"

            elif about=="outlier":
                about_title = "Outliers"
                desc = "Occasionally, you may see an extremely high statistic like... 40 KDA?!? \n*How does this happen?* \
                            \n\nSeveral factors, when combined, create outliers. These include: small sample sizes, no region-defined, and no elo defined. \
                            \n\nWhen no attributes are defined, the API lumps them into the 'ALL' category. \
                            \nFor example, *a smurf account with no region or location services may get matched-up against inexperienced players, playing their main heroes, and averaging +30KDA for their first 20-30 games. Flex, Troll, and so forth*. \
                            \nIn this example, elo, region, and game-mode are unspecified. \
                            \nBy default, Teddy searches 'All-Modes','All-Regions', and 'All-Elo' \
                            \n\nIf you find an outlier, try defining an elo, region, or game mode to refine your search: \
                            \ne.g. `/td mode:Classic region:EU elo:High` will give you MORE ACCURATE data than: `/td` alone"
            #Declare Embed
            helpembed = discord.Embed(
                title=f" About: {about_title}",
                description=f"{desc}\n"
            )
            if about_title == "The Data":
                helpembed.set_image(url="https://github.com/p3hndrx/MLBB-TeddyBot/blob/main/docs/img/sankeymatic_3000x1200.png?raw=true")
            helpembed.set_thumbnail(url="https://icons.iconarchive.com/icons/custom-icon-design/flatastic-2/256/help-desk-icon.png")

            if about=="show":
                helpembed.add_field(name=f"Version:",
                                    value=f"{version}\n\n")
                helpembed.add_field(name=f"How to Use:",
                                    value=f"Teddy provides the top 5 heroes sorted by their respective **WinRate%**, **KDA**, and **UseRate%** using the basic slash command: `/td`" \
                                          f"\n\nAdditional arguments allow you to inspect the tier data based on the attributes: elo, mode, and region.."
                                          f"\nFor example, `/td mode:Rank region:NA` will show you *top performing heroes in rank for North America*"
                                          f"\n\nYou can also filter by **role** (Assassin, Fighter, Mage, etc) and view the reverse **sort** of the tier. Give it a try!",
                                    inline=False
                                    )

            helpembed.set_author(name="p3", url="https://github.com/p3hndrx",
                                 icon_url="https://cdn.discordapp.com/avatars/336978363669282818/74ce51e0a6b2990a5c4153a8a7a36f37.png")

            await ctx.channel.send(embed=helpembed)
        else:
            if os.path.isdir(latest_run):  # check for raw data path
                ##### START JSON SCRAPER ######
                #### Transform Arguments
                r = region.replace("All", "all")
                m = mode.replace("All", "All-Modes")
                lvl = elo.replace("All", "All-Levels")
                dt = period.replace("AT", "All-Time").replace("Week", "This Week").replace("Month", "This Month")

                #### FIND FILE
                jsonfile = f'{latest_run}/en/{r}/{period}.{lvl}.{m}.json'
                if os.path.exists(jsonfile):
                    log.info("Requesting: " + jsonfile)

                    runtime = latest_run.replace(rawpath, "")
                    sort_by = ["wrank", "kdarank", "urank"]

                    #### COLOR DECORATION and THUMBNAIL####
                    if mode == "Rank":
                        color = discord.Color.red()
                        ico = "https://static.wikia.nocookie.net/mobile-legends/images/4/40/Ranked.png"
                    elif mode == "Brawl":
                        color = discord.Color.blue()
                        ico = "https://static.wikia.nocookie.net/mobile-legends/images/3/37/Brawl.png"
                    elif mode == "Classic":
                        color = discord.Color.gold()
                        ico = "https://static.wikia.nocookie.net/mobile-legends/images/5/57/Classic.png"
                    else:
                        color = discord.Color.teal()
                        ico = "https://static.wikia.nocookie.net/mobile-legends/images/e/ec/Custom.png"

                    #### DECLARE EMBED ####
                    embed = discord.Embed(
                        title=f"{mode} TierData for {dt}",
                        description=f"{sort} Heroes (Region:{region}, Mode:{mode}, Elo:{elo})\n",
                        color=color)

                    #### Generate Thumbnail ####
                    embed.set_thumbnail(url=ico)

#CHART VIEWS
    #CHART VIEW TYPE 1: MODE
                    if chartview!="null" and role=="null":
                        view = "null"
                        box = 0
                        md=mode.replace("All", "All-modes")

                        #region Mode Conditions
                        if chartview=="modexwin":
                            requestchart = "Mode X Win"
                            filename = f"{md}.win.png"
                            charttype = "baseXmode"

                        elif chartview=="modexkda":
                            requestchart = "Mode X KDA"
                            filename = f"{md}.kda.png"
                            charttype = "baseXmode"

                        elif chartview=="modexuse":
                            requestchart = "Mode X USE"
                            filename = f"{md}.use.png"
                            charttype = "baseXmode"

                        elif chartview=="modexwinbox":
                            requestchart = "Mode X Win (box)"
                            filename = f"{md}.win.png"
                            charttype = "baseXmode-box"
                            box=1

                        elif chartview=="modexkdabox":
                            requestchart = "Mode X KDA (box)"
                            filename = f"{md}.kda.png"
                            charttype = "baseXmode-box"
                            box=1

                        elif chartview=="modexusebox":
                            requestchart = "Mode X USE (box)"
                            filename = f"{md}.use.png"
                            charttype = "baseXmode-box"
                            box=1
                        #endregion

                        chart = f"{chartpath}{charttype}/{r}/{lvl}/{filename}"

                        #Check to see if chart exists
                        if not os.path.exists(chart):
                            embed.add_field(name=f" Historical Summary:", value=f"`No Chart Available...`",
                                            inline=False)
                            log.warning(f"Missing Chart: {chart}")

                            await ctx.channel.send(embed=embed)
                        #display chart
                        else:
                            log.info(f"Reading Chart: {chart}")
                            file = discord.File(chart, filename=f"{filename}")
                            embed.set_image(url=f"attachment://{filename}")

                            if box==1:
                                embed.add_field(name=f"How to Read:",
                                            value=f"The boxplot shows the highest and lowest values for each. The line denotes the _median_ value and the ▲ denotes the _mean_. ○ denotes outliers, if detected.",
                                            inline=False)
                            log.info(f"Request:  {requestchart}")
                            embed.add_field(name=f" Requesting Chart: ", value=f" {requestchart}", inline=False)

                            #### ADD EMBED FOR Foot
                            embed.add_field(name=f"Source:",
                                            value=f"Data provided by https://m.mobilelegends.com/en/rank\nLast DataSync: {runtime}",
                                            inline=False)
                            await ctx.channel.send(file=file, embed=embed)
    #CHART VIEW TYPE 2: ROLE
                    elif chartview != "null" and role != "null":
                        view = "null"
                        box = 0
                        md = mode.replace("All", "All-modes")
                        role = role.capitalize()

                        if chartview == "modexwin":
                            requestchart = "Mode X Win"
                            filename = f"{role}.win.png"
                            charttype = "baseXrole"

                        elif chartview == "modexkda":
                            requestchart = "Mode X KDA"
                            filename = f"{role}.kda.png"
                            charttype = "baseXrole"

                        elif chartview == "modexuse":
                            requestchart = "Mode X USE"
                            filename = f"{role}.use.png"
                            charttype = "baseXrole"

                        elif chartview == "modexwinbox":
                            requestchart = "Mode X Win (box)"
                            filename = f"{role}.win.png"
                            charttype = "baseXrole-box"
                            box = 1

                        elif chartview == "modexkdabox":
                            requestchart = "Mode X KDA (box)"
                            filename = f"{role}.kda.png"
                            charttype = "baseXrole-box"
                            box = 1

                        elif chartview == "modexusebox":
                            requestchart = "Mode X USE (box)"
                            filename = f"{role}.use.png"
                            charttype = "baseXrole-box"
                            box = 1

                        chart = f"{chartpath}{charttype}/{r}/{m}/{lvl}/{filename}"

                            # Check to see if chart exists
                        if not os.path.exists(chart):
                            embed.add_field(name=f" Historical Summary:", value=f"`No Chart Available...`",
                                                inline=False)
                            log.warning(f"Missing Chart: {chart}")

                            await ctx.channel.send(embed=embed)
                        # display chart
                        else:
                            log.info(f"Reading Chart: {chart}")
                            file = discord.File(chart, filename=f"{filename}")
                            embed.set_image(url=f"attachment://{filename}")

                            if box == 1:
                                embed.add_field(name=f"How to Read:",
                                                value=f"The boxplot shows the highest and lowest values for each. The line denotes the _median_ value and the ▲ denotes the _mean_. ○ denotes outliers, if detected.",
                                                inline=False)

                            log.info(f"Request:  {requestchart}")
                            embed.add_field(name=f" Requesting Chart: ", value=f" {requestchart}", inline=False)

                            #### ADD EMBED FOR Foot
                            embed.add_field(name=f"Source:",
                                            value=f"Data provided by https://m.mobilelegends.com/en/rank\nLast DataSync: {runtime}",
                                            inline=False)

                            await ctx.channel.send(file=file, embed=embed)

### NORMAL FUNCTION
                    else:

                        ##### BUILD TABLES ####
                        outlier = 0
                        with open(jsonfile) as j:
                            data = json.load(j)
                            rows = [v for k, v in data["data"].items()]

                            ######## SHOW VIEW OPTIONS#
                            if view=="meta":
                                log.info(f"Request Meta View")
                                embed.add_field(name=f"Meta View: ", value=f"Heroes by Lane, Use%", inline=False)
                                for ln in lanes:
                                    report = "\n"
                                    df = pd.DataFrame(rows, columns=['urank','name', 'win', 'use', 'kda'])
                                    rslt = getattr(laning, ln)
                                    df = df[df['name'].isin(rslt)]

                                    # check for outlier
                                    if (df['kda'] > kdalim).any() or (df['win'] == winlim).any() or (df['use'] == uselim).any():
                                        outlier += 1

                                    if ln == 'roam':
                                        loji = '<:roam:864272305310924820>'
                                    elif ln == 'mid':
                                        loji = '<:mid:864272305201872896>'
                                    elif ln == 'jungle':
                                        loji = '<:jungle:864272305182212139>'
                                    elif ln == 'exp':
                                        loji = '<:exp:864272305160716328>'
                                    elif ln == 'gold':
                                        loji = '<:gold:864272305172381748>'

                                    if sort == "Top":
                                        df = df.sort_values('urank', ascending=True).head(3)
                                    else:
                                        df = df.sort_values('urank', ascending=True).tail(3)

                                    #replace outlier with xxx
                                    #df['kda'] = df['kda'].mask(df['kda'] > kdalim, 20.0)
                                    df['kda'] = df['kda'].mask(df['kda'] > kdalim, "---")

                                    #### Add Icon Column
                                    df['o'] = df['name'].str.lower()
                                    df['o'] = df['o'].str.replace(r"[\"\'\.\-, ]", '', regex=True)
                                    df['-'] = df['o'].map(mojimap.moji)
                                    del df['o']

                                    #### Add Padding and FORMAT:
                                    df['rank'] = df['urank'].astype(str)
                                    df['rank'] = ('`' + df['rank'].str.center(4) + '`')
                                    df['name'] = ('`' + df['name'].str.center(13) + '`')
                                    df['win'] = ('`' + df['win'].str.center(6) + '`')
                                    df['use'] = ('`' + df['use'].str.center(6) + '`')
                                    df['kda'] = df['kda'].astype(str)
                                    df['kda'] = ('`' + df['kda'].str.center(6) + '`')

                                    # REBUILD
                                    df = df.reindex(columns=['rank', '-', 'name', 'win', 'use', 'kda'])

                                    # FORMAT COLUMN HEADER
                                    r = "RANK"
                                    r = r.center(4, " ")
                                    i = "-"
                                    i = i.center(2, " ")
                                    n = "NAME"
                                    n = n.center(13, " ")
                                    w = "WIN"
                                    w = w.center(6, " ")
                                    u = "USE"
                                    u = u.center(6, " ")
                                    k = "KDA"
                                    k = k.center(6, " ")
                                    df.rename(columns={'rank': r, '-': i, 'name': n, 'win': w, 'use': u, 'kda': k}, inplace=True)
                                    df.columns = df.columns.astype(str)
                                    df.columns = ('`' + df.columns + '`')
                                    # print (df.columns)

                                    # OUTPUT TO TABLE
                                    table = df.to_string(index=False)

                                    # print(table)
                                    report += table

                                    title=ln.upper()

                                    #### ADD EMBED FOR TABLE
                                    embed.add_field(name=f"{title} {loji}", value=f"{report}", inline=False)

                            elif view=="role":
                                log.info(f"Request Role View")
                                embed.add_field(name=f"Role View: ", value=f"Heroes by Role, Use%", inline=False)
                                for p in prof:
                                    report = "\n"
                                    df = pd.DataFrame(rows, columns=['urank', 'name', 'win', 'use', 'kda'])
                                    rslt = getattr(roles, p)
                                    df = df[df['name'].isin(rslt)]

                                    # check for outlier
                                    if (df['kda'] > kdalim).any() or (df['win'] == winlim).any() or (
                                            df['use'] == uselim).any():
                                        outlier += 1
                                        log.info(f"We have an outlier.")

                                    if p == 'support':
                                        poji = '<:Support_Icon:864271610797490177>'
                                    elif p == 'mage':
                                        poji = '<:Mage_Icon:864271610966179901>'
                                    elif p == 'marksman':
                                        poji = '<:Marksman_Icon:864271610882293831>'
                                    elif p == 'assassin':
                                        poji = '<:Assassin_Icon:864271610663272479>'
                                    elif p == 'tank':
                                        poji = '<:Tank_Icon:864271610964738058>'
                                    elif p == 'fighter':
                                        poji = '<:Fighter_Icon:864271610986102784>'

                                    if sort == "Top":
                                        df = df.sort_values('urank', ascending=True).head(3)
                                    else:
                                        df = df.sort_values('urank', ascending=True).tail(3)

                                    #replace with xxx
                                    #df['kda'] = df['kda'].mask(df['kda'] > kdalim, 20.0)
                                    df['kda'] = df['kda'].mask(df['kda'] > kdalim, "---")

                                    #### Add Icon Column
                                    df['o'] = df['name'].str.lower()
                                    df['o'] = df['o'].str.replace(r"[\"\'\.\-, ]", '', regex=True)
                                    df['-'] = df['o'].map(mojimap.moji)
                                    del df['o']

                                    #### Add Padding and FORMAT:
                                    df['rank'] = df['urank'].astype(str)
                                    df['rank'] = ('`' + df['rank'].str.center(4) + '`')
                                    df['name'] = ('`' + df['name'].str.center(13) + '`')
                                    df['win'] = ('`' + df['win'].str.center(6) + '`')
                                    df['use'] = ('`' + df['use'].str.center(6) + '`')
                                    df['kda'] = df['kda'].astype(str)
                                    df['kda'] = ('`' + df['kda'].str.center(6) + '`')

                                    # REBUILD
                                    df = df.reindex(columns=['rank', '-', 'name', 'win', 'use', 'kda'])

                                    # FORMAT COLUMN HEADER
                                    r = "RANK"
                                    r = r.center(4, " ")
                                    i = "-"
                                    i = i.center(2, " ")
                                    n = "NAME"
                                    n = n.center(13, " ")
                                    w = "WIN"
                                    w = w.center(6, " ")
                                    u = "USE"
                                    u = u.center(6, " ")
                                    k = "KDA"
                                    k = k.center(6, " ")
                                    df.rename(columns={'rank': r, '-': i, 'name': n, 'win': w, 'use': u, 'kda': k}, inplace=True)
                                    df.columns = df.columns.astype(str)
                                    df.columns = ('`' + df.columns + '`')
                                    # print (df.columns)

                                    # OUTPUT TO TABLE
                                    table = df.to_string(index=False)

                                    # print(table)
                                    report += table

                                    title=p.upper()

                                    #### ADD EMBED FOR TABLE
                                    embed.add_field(name=f"{title} {poji}", value=f"{report}", inline=False)

                            elif view=="normal":
                                log.info(f"Request Normal View")
                                for crit in sort_by:
                                    report = "\n"
                                    df = pd.DataFrame(rows, columns=[str(crit), 'name', 'win', 'use', 'kda'])

                                    # check for outlier
                                    if (df['kda'] > kdalim).any() or (df['win'] == winlim).any() or (
                                            df['use'] == uselim).any():
                                        outlier += 1

                                        log.info(f"We have an outlier.")

                                    # filter by role
                                    if role != "null":
                                        rslt = getattr(roles, role)
                                        # print(rslt)
                                        df = df[df['name'].isin(rslt)]

                                        if role == 'support':
                                            imgurl = 'https://static.wikia.nocookie.net/mobile-legends/images/f/ff/Support_Icon.png'
                                        elif role == 'mage':
                                            imgurl = 'https://static.wikia.nocookie.net/mobile-legends/images/5/53/Mage_Icon.png'
                                        elif role == 'marksman':
                                            imgurl = 'https://static.wikia.nocookie.net/mobile-legends/images/1/10/Marksman_Icon.png'
                                        elif role == 'assassin':
                                            imgurl = 'https://static.wikia.nocookie.net/mobile-legends/images/3/3f/Assassin_Icon.png'
                                        elif role == 'tank':
                                            imgurl = 'https://static.wikia.nocookie.net/mobile-legends/images/f/f0/Tank_Icon.png'
                                        elif role == 'fighter':
                                            imgurl = 'https://static.wikia.nocookie.net/mobile-legends/images/1/1a/Fighter_Icon.png'

                                        embed.set_author(name=f"Filter by {role.upper()}", icon_url=imgurl)

                                        # sort
                                    if sort == "Top":
                                        df = df.sort_values(str(crit), ascending=True).head(5)
                                    else:
                                        df = df.sort_values(str(crit), ascending=True).tail(5)

                                    #replace with xxx
                                    #df['kda'] = df['kda'].mask(df['kda'] > kdalim, 20.0)
                                    df['kda'] = df['kda'].mask(df['kda'] > kdalim, "---")

                                    #### Add Icon Column
                                    df['o'] = df['name'].str.lower()
                                    df['o'] = df['o'].str.replace(r"[\"\'\.\-, ]", '', regex=True)
                                    df['-'] = df['o'].map(mojimap.moji)
                                    del df['o']

                                    #### Add Padding and FORMAT:
                                    df['rank'] = df[str(crit)].astype(str)
                                    df['rank'] = ('`' + df['rank'].str.center(4) + '`')
                                    df['name'] = ('`' + df['name'].str.center(13) + '`')
                                    df['win'] = ('`' + df['win'].str.center(6) + '`')
                                    df['use'] = ('`' + df['use'].str.center(6) + '`')
                                    df['kda'] = df['kda'].astype(str)
                                    df['kda'] = ('`' + df['kda'].str.center(6) + '`')

                                    # REBUILD
                                    df = df.reindex(columns=['rank', '-', 'name', 'win', 'use', 'kda'])

                                    # FORMAT COLUMN HEADER
                                    r = "RANK"
                                    r = r.center(4, " ")
                                    i = "-"
                                    i = i.center(2, " ")
                                    n = "NAME"
                                    n = n.center(13, " ")
                                    w = "WIN"
                                    w = w.center(6, " ")
                                    u = "USE"
                                    u = u.center(6, " ")
                                    k = "KDA"
                                    k = k.center(6, " ")
                                    df.rename(columns={'rank': r, '-': i, 'name': n, 'win': w, 'use': u, 'kda': k}, inplace=True)
                                    df.columns = df.columns.astype(str)
                                    df.columns = ('`' + df.columns + '`')
                                    # print (df.columns)

                                    # OUTPUT TO TABLE
                                    table = df.to_string(index=False)

                                    # print(table)
                                    report += table

                                    #### Create Report Title
                                    if crit == "wrank":
                                        title = "WinRate%"
                                    elif crit == "kdarank":
                                        title = "KDA"
                                    elif crit == "urank":
                                        title = "Use%"

                                    #### ADD EMBED FOR TABLE
                                    embed.add_field(name=f"Sorted by {title}", value=f"{report}", inline=False)

                            elif view=="win" or view=="kda" or view=="use":
                                if view == "win":
                                    crit = "wrank"
                                    title = "WinRate"
                                elif view=="kda":
                                    crit = "kdarank"
                                    title = "KDA"
                                elif view =="use":
                                    crit = "urank"
                                    title = "USE"

                                log.info(f"Request {title} View")

                                report = "\n"
                                df = pd.DataFrame(rows, columns=[str(crit), 'name', 'win', 'use', 'kda'])

                                # check for outlier
                                if (df['kda'] > kdalim).any() or (df['win'] == winlim).any() or (df['use'] == uselim).any():
                                    outlier += 1
                                    log.info(f"We have an outlier.")

                                # filter by role
                                if role != "null":
                                    rslt = getattr(roles, role)
                                    # print(rslt)
                                    df = df[df['name'].isin(rslt)]

                                    if role == 'support':
                                        imgurl = 'https://static.wikia.nocookie.net/mobile-legends/images/f/ff/Support_Icon.png'
                                    elif role == 'mage':
                                        imgurl = 'https://static.wikia.nocookie.net/mobile-legends/images/5/53/Mage_Icon.png'
                                    elif role == 'marksman':
                                        imgurl = 'https://static.wikia.nocookie.net/mobile-legends/images/1/10/Marksman_Icon.png'
                                    elif role == 'assassin':
                                        imgurl = 'https://static.wikia.nocookie.net/mobile-legends/images/3/3f/Assassin_Icon.png'
                                    elif role == 'tank':
                                        imgurl = 'https://static.wikia.nocookie.net/mobile-legends/images/f/f0/Tank_Icon.png'
                                    elif role == 'fighter':
                                        imgurl = 'https://static.wikia.nocookie.net/mobile-legends/images/1/1a/Fighter_Icon.png'

                                    embed.set_author(name=f"Filter by {role.upper()}", icon_url=imgurl)

                                    # sort
                                if sort == "Top":
                                    df = df.sort_values(str(crit), ascending=True).head(10)
                                else:
                                    df = df.sort_values(str(crit), ascending=True).tail(10)

                                #replace with xxx
                                #df['kda'] = df['kda'].mask(df['kda'] > kdalim, 20.0)
                                df['kda'] = df['kda'].mask(df['kda'] > kdalim, "---")

                                #### Add Icon Column
                                df['o'] = df['name'].str.lower()
                                df['o'] = df['o'].str.replace(r"[\"\'\.\-, ]", '', regex=True)
                                df['-'] = df['o'].map(mojimap.moji)
                                del df['o']

                                #### Add Padding and FORMAT:
                                df['rank'] = df[str(crit)].astype(str)
                                df['rank'] = ('`' + df['rank'].str.center(4) + '`')
                                df['name'] = ('`' + df['name'].str.center(13) + '`')
                                df['win'] = ('`' + df['win'].str.center(6) + '`')
                                df['use'] = ('`' + df['use'].str.center(6) + '`')
                                df['kda'] = df['kda'].astype(str)
                                df['kda'] = ('`' + df['kda'].str.center(6) + '`')

                                # REBUILD
                                df = df.reindex(columns=['rank', '-', 'name', 'win', 'use', 'kda'])

                                # FORMAT COLUMN HEADER
                                r = "RANK"
                                r = r.center(4, " ")
                                i = "-"
                                i = i.center(2, " ")
                                n = "NAME"
                                n = n.center(13, " ")
                                w = "WIN"
                                w = w.center(6, " ")
                                u = "USE"
                                u = u.center(6, " ")
                                k = "KDA"
                                k = k.center(6, " ")
                                df.rename(columns={'rank': r, '-': i, 'name': n, 'win': w, 'use': u, 'kda': k}, inplace=True)
                                df.columns = df.columns.astype(str)
                                df.columns = ('`' + df.columns + '`')
                                # print (df.columns)

                                # OUTPUT TO TABLE
                                table = df.to_string(index=False)

                                # print(table)
                                report += table



                                #### ADD EMBED FOR TABLE
                                embed.add_field(name=f"Sorted by {title}", value=f"{report}", inline=False)
                                #print(f"{report}")

                        #### ADD EMBED FOR OUTLIER
                        if outlier >= 1:
                            embed.add_field(name=f":rotating_light: Outlier Notice:",
                                            value=f":bear: Teddy has detected a statistically improbable anomaly in the data you have requested."
                                                  f"\nTry using a filter such as `/td mode:Rank` to get more accurate results.",
                                            inline=False)

                        #### ADD EMBED FOR Foot
                        embed.add_field(name=f"Source:",
                                        value=f"Data provided by https://m.mobilelegends.com/en/rank\nLast DataSync: {runtime}",
                                        inline=False)

                        #### SEND EMBED ####
                        await ctx.channel.send(embed=embed)

# MISSING JSON
                else:
                    log.warning(f"Bad Request: Missing: {jsonfile}")
                    embed = discord.Embed(
                        title=f"{mode} TierData for {dt}",
                        description=f"{sort} Heroes (Region:{region}, Mode:{mode}, Elo:{elo})\n",
                        color=0xFF5733)
                    embed.set_thumbnail(url="https://icons.iconarchive.com/icons/paomedia/small-n-flat/256/sign-error-icon.png")
                    embed.add_field(name=f"No TierData Found", value=f"Source file missing. Please try again after the next data sync or refine your search.", inline=False)
                    await ctx.channel.send(embed=embed)
                    #await ctx.channel.send(content="```No TierData Found...```")
# MISSING FOLDER
            else:
                log.warning(f"Bad Request: Missing: {latest_run}")
                await ctx.channel.send(content="```No TierData Reported Yet...```")

# endregion

# region HERO TABLE GENERATOR
regions = ["all", "NA", "SA", "SE", "EU"]
modes = ["All-Modes", "Rank", "Brawl", "Classic"]
lvls = ["All-Levels", "Normal", "High", "Very-High"]
periods = ["Week", "AT", "Month"]

# COMPILE HERO TABLES
log.info("Compiling Lookup")

# Create master table
dfx = pd.DataFrame(columns=['name', 'win', 'use', 'kda', 'region', 'period', 'elo', 'mode'])

if os.path.isdir(latest_run):  # check for raw data path
    #### FIND FILES
    for r in regions:
        for period in periods:
            for lvl in lvls:
                for m in modes:

                    jsonfile = f'{latest_run}/en/{r}/{period}.{lvl}.{m}.json'
                    if os.path.exists(jsonfile):
                        # print("Requesting: " + jsonfile)
                        log.info("Requesting: " + jsonfile)

                        ##### BUILD TABLES ####
                        with open(jsonfile) as j:
                            data = json.load(j)
                            rows = [v for k, v in data["data"].items()]

                            df = pd.DataFrame(rows, columns=['name', 'win', 'use', 'kda'])

                            df['region'] = f"{r}"
                            df['period'] = f"{period}"
                            df['elo'] = f"{lvl}"
                            df['mode'] = f"{m}"
                            # dfx.append(df, ignore_index = True)
                            dfx = pd.concat([dfx, df], axis=0)
                            # print(df)

                    else:
                        log.warning(f"Bad Request: Missing: {jsonfile}")
    # print(f"Combined:{dfx}")
else:
    log.warning(f"Bad Request: Missing: {latest_run}")

log.debug(f"{dfx}")
# endregion

# region HERO SEARCH FUNCTION
@slash.slash(name="tdh",
             description="This is a TierData Lookup by Hero",
             options=[
                 create_option(
                     name="hero",
                     description="Enter the Hero you'd like to find!",
                     option_type=3,
                     required=True
                 ),
                 create_option(
                     name="region",
                     description="Look at TierData by REGION.",
                     option_type=3,
                     required=False,
                     choices=[
                         create_choice(
                             name="EU",
                             value="EU"),
                         create_choice(
                             name="NA",
                             value="NA"),
                         create_choice(
                             name="SA",
                             value="SA"),
                         create_choice(
                             name="SE",
                             value="SE")
                     ]
                 ),
                 create_option(
                     name="mode",
                     description="Look at TierData by GAME MODE.",
                     option_type=3,
                     required=False,
                     choices=[
                         create_choice(
                             name="Brawl",
                             value="Brawl"),
                         create_choice(
                             name="Classic",
                             value="Classic"),
                         create_choice(
                             name="Rank",
                             value="Rank")
                     ]
                 ),
                 create_option(
                     name="elo",
                     description="Look at TierData by Player Performance!",
                     option_type=3,
                     required=False,
                     choices=[
                         create_choice(
                             name="Normal",
                             value="Normal"),
                         create_choice(
                             name="High",
                             value="High"),
                         create_choice(
                             name="Very-High",
                             value="Very-High")
                     ]
                 ),
                 create_option(
                     name="period",
                     description="Look at TierData for the previous time-period.",
                     option_type=3,
                     required=False,
                     choices=[
                         create_choice(
                             name="Month",
                             value="Month"),
                         create_choice(
                             name="Week",
                             value="Week"),
                         create_choice(
                             name="All-Time",
                             value="AT")
                     ]
                 ),
                 create_option(
                     name="show",
                     description="Look at TierData over-time.",
                     option_type=3,
                     required=False,
                     choices=[
                         create_choice(
                             name="History",
                             value="history"),
                         create_choice(
                             name="Averages",
                             value="averages")
                     ]
                 ),
                 create_option(
                     name="about",
                     description="view README",
                     option_type=3,
                     required=False,
                     choices=[
                         create_choice(
                             name="Teddy-HeroSearch",
                             value="show"),
                        create_choice(
                             name="Commands",
                             value="commands")
                        ]
                         )
             ])
async def test(ctx, hero: str, region="All", mode="All", elo="All", period="Week", show="null", about="null"):
    channelid = ctx.channel.id
    await ctx.send(f":bear: `Processing request...`")
    if channelid in optout:
        await ctx.channel.send(content="`Sorry, I'm not allowed to do that here. \nPlease try a different channel.`")
        channelname = ctx.channel.name
        log.info(f"Permission Denied for Channel: {channelname}({channelid})")
    else:

        #SHOW HELP
        if about!="null":
            if about=="show":
                about_title = "Teddy: Hero Search"
                desc = "Teddy Hero Search displays performance data for your favorite hero. \
                       \n\n How is this different from `/td`? \
                       \n `/td` looks at the tier list generated each week and shows you the overall performance of all heroes \
                       \n `/tdh` looks at a pre-compiled summary of all of the data and shows you a break-down for your hero. \
                       \n - Additionally, `/tdh` looks at historical data to produce trends. \
                       \n\n Give it a try!"
            elif about=="commands":
                about_title = "Commands"
                desc = "Command Options List:\
                       \n\n`/tdh hero: YOUR-HERO-NAME` (required) - Show KDA/WR%/USE% for this Hero by MODE, REGION, and ELO \
                       \n- `region:(NA,SA,SE,EU)`, default:`All` \
                       \n- `mode:(Brawl,Classic,Rank)`, default: `All-Modes` \
                       \n- `elo:(Normal,High,Very-High)`, default: `All-Levels` \
                       \n- `period:(Month,Week,All-Time)`, default: `Week` \
                       \n- `show:(History, Averages)` default: `none` - The view changes from a historical view of KDA,WR,or USE -or- a box chart view of averages"
            # Declare Embed
            helpembed = discord.Embed(
                    title=f" About: {about_title}",
                    description=f"{desc}\n"
                )

            helpembed.set_thumbnail(
                    url="https://icons.iconarchive.com/icons/custom-icon-design/flatastic-2/256/help-desk-icon.png")

            helpembed.set_author(name="p3", url="https://github.com/p3hndrx",
                                     icon_url="https://cdn.discordapp.com/avatars/336978363669282818/74ce51e0a6b2990a5c4153a8a7a36f37.png")
            await ctx.channel.send(embed=helpembed)
        else:

            names = heroes.list
            shero = hero.replace("-", "").replace("'", "").replace(".", "").replace(" ", "").lower()
            print(f"Searching {shero} from {hero}")
            log.debug(f"Searching {shero} from {hero}")

            ### FIRST---- Search Array for Hero
            #result = [v for v in names if shero in v.replace("-", "").replace("'", "").replace(".", "").replace(" ", "").lower()]

            #Try Exact Match
            result = [v for v in names if shero == v.replace("-", "").replace("'", "").replace(".", "").replace(" ", "").lower()]

            if len(result) == 0:
                result = [v for v in names if v.replace("-", "").replace("'", "").replace(".", "").replace(" ", "").lower().startswith(shero)]

            #Try Partial
            if len(result) == 0:
                await ctx.send(content=f"Could not find `{hero}`!")
            elif len(result) > 1:
                await ctx.send(content=f"Found more than one match.. did you mean:`{result}`?")
            else:
                hn = result[0]

                # audit
                user = ctx.author
                # audit.info(f",{user},dd,{region},{mode},{elo},{period},{sort},{role},{view},{chartview},{about},{show},{shero}")
                audit.info(f"{user},ddh,{region},{mode},{elo},{period},,,,,,{show},{hn}")
                log.info(f"{user} used /ddh")

                log.info(f"Looking for... {hn}")
                hnl = hn.replace("-", "").replace("'", "").replace(".", "").replace(" ", "").lower()

                #### NEXT----  START TIERDATA
                ico = mojimap.moji[hnl]
                runtime = latest_run.replace(rawpath, "")
                portrait = heroicons.portrait[hnl]

                ###### Transform filters:
                r = region.replace("All", "all")
                m = mode.replace("All", "All-Modes")
                lvl = elo.replace("All", "All-Levels")
                dt = period.replace("AT", "All-Time").replace("Week", "This Week").replace("Month", "This Month")

                #### COLOR DECORATION
                if mode == "Rank":
                    color = discord.Color.red()
                elif mode == "Brawl":
                    color = discord.Color.blue()
                elif mode == "Classic":
                    color = discord.Color.gold()
                else:
                    color = discord.Color.teal()

                #### DECLARE EMBED ####
                embed = discord.Embed(
                    title=f"TierData for {hn}",
                    description=f"(Region:{region}, Mode:{mode}, Elo:{elo})",
                    color=color)

                embed.set_thumbnail(url=f"{portrait}")

                #CHECK FOR HISTORY:
                if show=="history":
                    #SHOW HISTORY CHART
                    chart = f"{histpath}{r}/{m}/{lvl}/{hnl}.png"

                    if not os.path.exists(chart):
                        embed.add_field(name=f" {ico} Historical Summary:", value=f"`No Chart Available...`", inline=False)
                        log.warning(f"Missing Chart: {chart}")

                        #### ADD EMBED FOR Foot
                        embed.add_field(name=f"Source:",
                                        value=f"Data provided by https://m.mobilelegends.com/en/rank\nLast DataSync: {runtime}",
                                        inline=False)

                        await ctx.channel.send(embed=embed)

                    else:
                        embed.add_field(name=f" {ico} Historical Summary:", value=f"Changes in Win%, Use%, KDA over Time.",
                                    inline=False)
                        log.info(f"Reading Chart: {chart}")
                        file = discord.File(chart, filename=f"{hnl}.png")
                        embed.set_image(url=f"attachment://{hnl}.png")

                        #### ADD EMBED FOR Foot
                        embed.add_field(name=f"Source:",
                                        value=f"Data provided by https://m.mobilelegends.com/en/rank\nLast DataSync: {runtime}",
                                        inline=False)

                        await ctx.channel.send(file=file, embed=embed)
                # CHECK FOR HISTORY:
                if show == "averages":
                    # SHOW AVERAGES CHART
                    chart = f"{avgpath}{r}/{m}/{lvl}/{hnl}.png"

                    if not os.path.exists(chart):
                        embed.add_field(name=f" {ico} Historical Summary:", value=f"`No Chart Available...`", inline=False)
                        log.warning(f"Missing Chart: {chart}")

                        #### ADD EMBED FOR Foot
                        embed.add_field(name=f"Source:",
                                                value=f"Data provided by https://m.mobilelegends.com/en/rank\nLast DataSync: {runtime}",
                                                inline=False)

                        await ctx.channel.send(embed=embed)

                    else:
                        embed.add_field(name=f" {ico} Statistical Summary:",
                                        value=f"Averages in Win%, Use%, KDA over Time.",
                                        inline=False)
                        log.info(f"Reading Chart: {chart}")
                        file = discord.File(chart, filename=f"{hnl}.png")
                        embed.set_image(url=f"attachment://{hnl}.png")

                        #### ADD EMBED FOR Foot
                        embed.add_field(name=f"How to Read:",
                                        value=f"The boxplot shows the highest and lowest values for each. The line denotes the _median_ value and the ▲ denotes the _mean_. ○ denotes outliers, if detected.",
                                        inline=False)
                        embed.add_field(name=f"Source:",
                                                value=f"Data provided by https://m.mobilelegends.com/en/rank\nLast DataSync: {runtime}",
                                                inline=False)
                        await ctx.channel.send(file=file, embed=embed)

                if show == "null":
                    outlier = 0
                    #SHOW ALL TABLES
                    #### Create Filters
                    nfilter = dfx.isin([hn]).any(axis=1)
                    pfilter = dfx["period"].isin([period])
                    rfilter = dfx["region"].isin([r])
                    mfilter = dfx["mode"].isin([m])
                    efilter = dfx["elo"].isin([lvl])

                    sumdf = dfx[nfilter & rfilter & pfilter & mfilter & efilter]
                    sumdf = sumdf.reindex(columns=['region', 'elo', 'mode', 'win', 'use', 'kda'])

                    #Check for outlier
                    if (sumdf['kda'] > kdalim).any() or (sumdf['win'] == winlim).any() or (sumdf['use'] == uselim).any():
                        outlier += 1
                        log.info(f"We have an outlier.")

                    if sumdf.empty:
                        sumdf = "No data available."
                    else:
                        # replace outlier with xxx
                        sumdf['kda'] = sumdf['kda'].mask(sumdf['kda'] > kdalim, "---")
                        sumdf = sumdf.to_string(index=False)
                    embed.add_field(name=f" {ico} Summary for: {dt})", value=f"`{sumdf}`", inline=False)

                    ## CREATE EMBED FIELDS:
                    if r == "all":
                        rdf = dfx[nfilter & pfilter & mfilter & efilter]
                        rdf = rdf.reindex(columns=['region', 'elo', 'mode', 'win', 'use', 'kda'])
                        rdf.sort_values('region', ascending=True)
                        # Check for outlier
                        if (rdf['kda'] > kdalim).any() or (rdf['win'] == winlim).any() or (rdf['use'] == uselim).any():
                            outlier += 1
                            log.info(f"We have an outlier.")
                        if rdf.empty:
                            rdf = "No data available."
                        else:
                            #outlier
                            rdf['kda'] = rdf['kda'].mask(rdf['kda'] > kdalim, "---")
                            rdf = rdf.to_string(index=False)
                        embed.add_field(name=f"Sorted by Region:", value=f"`{rdf}`", inline=False)

                    if m == "All-Modes":
                        mdf = dfx[nfilter & pfilter & rfilter & efilter]
                        mdf = mdf.reindex(columns=['mode', 'region', 'elo', 'win', 'use', 'kda'])
                        mdf.sort_values('mode', ascending=True)
                        # Check for outlier
                        if (mdf['kda'] > kdalim).any() or (mdf['win'] == winlim).any() or (mdf['use'] == uselim).any():
                            outlier += 1
                            log.info(f"We have an outlier.")
                        if mdf.empty:
                            mdf = "No data available."
                        else:
                            #outlier
                            mdf['kda'] = mdf['kda'].mask(mdf['kda'] > kdalim, "---")
                            mdf = mdf.to_string(index=False)
                        embed.add_field(name=f"Sorted by Modes:", value=f"`{mdf}`", inline=False)

                    if lvl == "All-Levels":
                        edf = dfx[nfilter & pfilter & rfilter & mfilter]
                        edf = edf.reindex(columns=['elo', 'mode', 'region', 'win', 'use', 'kda'])
                        edf.sort_values('elo', ascending=True)
                        # Check for outlier
                        if (edf['kda'] > kdalim).any() or (edf['win'] == winlim).any() or (edf['use'] == uselim).any():
                            outlier += 1
                            log.info(f"We have an outlier.")
                        if edf.empty:
                            edf = "No data available."
                        else:
                            #outlier
                            edf['kda'] = edf['kda'].mask(edf['kda'] > kdalim, "---")
                            edf = edf.to_string(index=False)
                        embed.add_field(name=f"Sorted by Elo:", value=f"`{edf}`", inline=False)

                    # IF OUTLIER
                    if outlier >= 1:
                        embed.add_field(name=f":rotating_light: Outlier Notice:",
                                        value=f":bear: Teddy has detected a statistically improbable anomaly in the data you have requested."
                                              f"\nTry using a filter such as `/tdh mode:Rank` to get more accurate results.",
                                        inline=False)

                    #### ADD EMBED FOR Foot
                    embed.add_field(name=f"Source:",
                                        value=f"Data provided by https://m.mobilelegends.com/en/rank\nLast DataSync: {runtime}",
                                        inline=False)

                    await ctx.channel.send(embed=embed)

# endregion

# region INIT
@bot.event
async def on_ready():
    log.info('We have logged in as {0.user}'.format(bot))

    startupembed = discord.Embed(
       title=f"***Started Teddy-{version}",
       description=f"Everything is looking ok...\n")
    file = discord.File("/var/www/html/hello.png", filename=f"hello.png")
    startupembed.set_image(url=f"attachment://hello.png")
    await bot.get_channel(853806791150665748).send(file=file, embed=startupembed)
# endregion

# region DISCORD STUFF
# discord basic error handling:
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("```Missing a required argument.  Do td> help *command*```")
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("```You do not have the appropriate permissions to run this command.```")
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send("```I don't have sufficient permissions!```")
    else:
        print("error not caught")
        print(error)
# endregion

bot.run(TOKEN)
#
