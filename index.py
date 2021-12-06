# region IMPORTS
import datetime
import os
from os.path import exists
from dotenv import load_dotenv

import json
import pandas as pd
from pandas import json_normalize

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

from functions import grabtierdata, grabherotable, grabsummarydata


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
    head = "Timestamp,User,Command,Elo,Period,Sort,Role,View,ChartView,About,Show,HeroName"
    f = open(auditpath, 'w')
    f.write(f'{head}\n')
    f.close()
else:
    log.info(f"Found log at: {auditpath}")
# endregion

# region VERSION
version = "BETA Release Candidate Ver.03.11 (20211206)"
print(f"Starting Teddy-{version}...")
logging.info(f"Starting Teddy-{version}...")
# endregion

# region PERMISSIONS
guild_ids = [850386581135163489,832548513383972884]
log.info(f"Enabling for Server(s):{guild_ids}")

optin = [853806791150665748,873259572985495552]
optout = []

summaryroles = ['MLBB Official','DEV','Discord Bot Developer','Lead Moderator']
# endregion

# region VARIABLES
x = datetime.datetime.now()
today = x.strftime("%Y%m%d")

#rawpath = "/tmp/RankData/"
rawpath = "/var/www/html/RankData/"
histpath = "/var/www/html/timeline/summary.rd/"
avgpath = "/var/www/html/timeline/averages.rd/"
chartpath = "/var/www/html/reports/"
reportpath = "/var/www/html/summary-reports-png"

sort_by = ["wrank", "banrank", "urank"]
dsort_by = ["wrank_d", "banrank_d", "urank_d"]
prof = ["assassin","marksman","mage","tank","support","fighter"]
lanes = ["gold","exp","mid","jungle","roam"]
lvls = ["All", "Legend", "Mythic"]


runtimes = os.listdir(rawpath)
runtimes = sorted(runtimes, reverse=True)
latest_run = max(d for d in runtimes)
latest = os.path.join(rawpath, latest_run)
print(f'Latest JSON file: {latest}')

#build averages master table
summarycsv = f'{chartpath}csv/rd.averages.master.csv'
sumdf = grabsummarydata(summarycsv)

#build heroes master table
dfx = grabherotable(latest)
roji = {'All': '<:Epic:910268690098974740>', 'Legend': '<:Legend:910268716044914688>','Mythic': '<:Mythic:910268741181374534>'}

##### DISCORD LISTENERS #######

bot = commands.Bot(command_prefix="/td ", intents=discord.Intents.all())
slash = SlashCommand(bot, sync_commands=True)
# endregion

# region MAIN TD FUNCTION
@slash.slash(name="td",
             description="Use this command to get the most recent TierData!.",
             guild_ids=guild_ids,
             options=[
                 create_option(
                     name="elo",
                     description="Look at TierData by Player Performance!",
                     option_type=3,
                     required=False,
                     choices=[
                         create_choice(
                             name="All",
                             value="All"),
                         create_choice(
                             name="Legend+",
                             value="Legend"),
                         create_choice(
                             name="Mythic (400+)",
                             value="Mythic")
                     ]
                 ),
                 create_option(
                     name="period",
                     description="Look at TierData averages for the previous time-period.",
                     option_type=3,
                     required=False,
                     choices=[
                         create_choice(
                             name="Week",
                             value="Week"),
                         create_choice(
                             name="Month",
                             value="Month"),
                         create_choice(
                             name="3-Months",
                             value="Season"),
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
                             name="Ban",
                             value="ban"),
                         create_choice(
                             name="Use",
                             value="use"),
                         create_choice(
                             name="Delta",
                             value="delta")
                     ]
                 ),
                 create_option(
                     name="chartview",
                     description="Look at Different Chart Views!",
                     option_type=3,
                     required=False,
                     choices=[
                         create_choice(
                            name="TOP x WIN",
                             value="topxwin"),
                         create_choice(
                             name="TOP x BAN",
                             value="topxban"),
                         create_choice(
                             name="TOP x USE",
                             value="topxuse"),
                         create_choice(
                             name="TOP x WIN (box)",
                             value="topxwinbox"),
                         create_choice(
                             name="TOP x BAN (box)",
                             value="topxbanbox"),
                         create_choice(
                             name="TOP x USE (box)",
                             value="topxusebox")
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
                             value="data")
                        ]
                         )
                     ]
                 )

async def _overall(ctx, elo="All",period="Day", sort="Top", role="null", view="normal",chartview="null", about="null"):
    channelid = ctx.channel.id
    await ctx.send(f":bear: `Processing request...`")
    if channelid in optout:
        await ctx.channel.send(content="`Sorry, I'm not allowed to do that here. \nPlease try a different channel.`")
        channelname = ctx.channel.name
        log.info(f"Permission Denied for Channel: {channelname}({channelid})")
    else:
        #audit
        user = ctx.author
        audit.info(f"{user},td,{elo},{period},{sort},{role},{view},{chartview},{about},,")
        log.info(f"{user} used /dd")
# HELP VIEW
        if about!="null":
            if about=="show":
                about_title = "Teddy"
                desc = "Teddy (aka 'TD') is a MLBB TierData Bot made exclusively for the MLBB NA Discord Server.\n\n"
            elif about=="data":
                about_title = "The Data"
                desc = "TierData is provided by https://m.mobilelegends.com/en/rank through an API. Teddy fully synchronizes the data every day and is summarized by WIN,USE,and BAN: \n \
                              \n\nThe data is further sorted by the following attributes: \n**elo** (All, Legend+, Mythic 400pts+), \n \
                              \nIf you get a warning `No TierData Found.`. \nDon't worry! This means that the specific data file is *missing* and is likely being synchronized, so please be patient!"
            elif about=="commands":
                about_title = "Commands"
                desc = "Command Options List:\
                       \n\n`/td` - Show BAN%/WR%/USE% for this Week \
                       \n- `elo:(Normal,High,Very-High)`, default: `All-Levels` \
                       \n- `period:(Week,Month,3-Months)`, default: `Today` - Look at the tier data changes over a period of time! \
                       \n- `sort:(Top, Bottom)`, default: Top \
                       \n- `role:(Fighter,Mage,Support,Assassin,Marksman,Tank)`, default: `none` \
                       \n- `view:(Normal,Meta,Role,WinRate,BAN,Use)` default: `Normal` - The view changes from top5 BAN/WR/USE, top10 by BAN,WR,or USE, or top3 by Meta or Role \
                       \n- `chartview:(Elo x WIN/BAN/USE)+(box optional)`, default: `none` - Historical chart or averages, based on Top5 for each filter"

            #Declare Embed
            helpembed = discord.Embed(
                title=f" About: {about_title}",
                description=f"{desc}\n"
            )
            if about_title == "The Data":
                helpembed.set_image(url="https://github.com/p3hndrx/MLBB-TeddyBot/blob/main.rd/docs/img/sankeymatic_2000x1200.png?raw=true")
            helpembed.set_thumbnail(url="https://icons.iconarchive.com/icons/custom-icon-design/flatastic-2/256/help-desk-icon.png")

            if about=="show":
                helpembed.add_field(name=f"Version:",
                                    value=f"{version}\n\n")
                helpembed.add_field(name=f"How to Use:",
                                    value=f"Teddy provides the top 5 heroes sorted by their respective **WinRate%**, **BAN**, and **UseRate%** using the basic slash command: `/td`" \
                                          f"\n\nAdditional arguments allow you to inspect the tier data based on the elo attribute.."
                                          f"\nFor example, `/td elo:Legend ` will show you *top performing heroes in rank for the Legend+ elo bracket.*"
                                          f"\n\nYou can also filter by **role** (Assassin, Fighter, Mage, etc) and view the reverse **sort** of the tier. Give it a try!",
                                    inline=False
                                    )

            helpembed.set_author(name="p3", url="https://github.com/p3hndrx",
                                 icon_url="https://cdn.discordapp.com/avatars/336978363669282818/74ce51e0a6b2990a5c4153a8a7a36f37.png")

            await ctx.channel.send(embed=helpembed)
        else:
# OTHER VIEWS
            if os.path.isdir(latest):  # check for raw data path

                dt = period.replace("Day", "Today").replace("Week", "Past 7 Days").replace("Month", "Past 30 Days").replace("Season", "Past 90 Days")

                #### FIND FILE
                jsonfile = f'{latest}/{elo}.json'
                if os.path.exists(jsonfile):

                    runtime = latest.replace(rawpath, "")

                    #### COLOR DECORATION and THUMBNAIL####
                    if elo == "All":
                        color = discord.Color.teal()
                        ico = "https://static.wikia.nocookie.net/mobile-legends/images/2/26/Epic.png"
                    elif elo == "Legend":
                        color = discord.Color.gold()
                        ico = "https://static.wikia.nocookie.net/mobile-legends/images/1/10/Legend.png"
                    elif elo == "Mythic":
                        color = discord.Color.purple()
                        ico = "https://static.wikia.nocookie.net/mobile-legends/images/e/ec/Mythic.png"

                    #### DECLARE EMBED ####
                    embed = discord.Embed(
                        title=f"TierData for {dt}",
                        description=f"{sort} Heroes (Elo:{elo})\n",
                        color=color)

                    #### Generate Thumbnail ####
                    embed.set_thumbnail(url=ico)

#CHART VIEW TYPE 1: All ROLES
                    if chartview!="null" and role=="null":
                        view = "null"
                        box = 0
                        

                        #region Elo Conditions
                        if chartview=="topxwin":
                            requestchart = "Top X Win"
                            filename = f"{elo}.win.png"
                            charttype = "baseXall.rd"

                        elif chartview=="topxban":
                            requestchart = "Top X BAN"
                            filename = f"{elo}.ban.png"
                            charttype = "baseXall.rd"

                        elif chartview=="topxuse":
                            requestchart = "Top X USE"
                            filename = f"{elo}.use.png"
                            charttype = "baseXall.rd"

                        elif chartview=="topxwinbox":
                            requestchart = "Top X Win (box)"
                            filename = f"{elo}.win.png"
                            charttype = "baseXall-box.rd"
                            box=1

                        elif chartview=="topxbanbox":
                            requestchart = "Top X BAN (box)"
                            filename = f"{elo}.ban.png"
                            charttype = "baseXall-box.rd"
                            box=1

                        elif chartview=="topxusebox":
                            requestchart = "Top X USE (box)"
                            filename = f"{elo}.use.png"
                            charttype = "baseXall-box.rd"
                            box=1
                        #endregion

                        chart = f"{chartpath}{charttype}/{filename}"

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
                        md = elo.replace("All", "All-Elo")
                        role = role.capitalize()

                        if chartview == "topxwin":
                            requestchart = "Top X Win"
                            filename = f"{role}.win.png"
                            charttype = "baseXrole.rd"

                        elif chartview == "topxban":
                            requestchart = "Top X BAN"
                            filename = f"{role}.ban.png"
                            charttype = "baseXrole.rd"

                        elif chartview == "topxuse":
                            requestchart = "Top X USE"
                            filename = f"{role}.use.png"
                            charttype = "baseXrole.rd"

                        elif chartview == "topxwinbox":
                            requestchart = "Top X Win (box)"
                            filename = f"{role}.win.png"
                            charttype = "baseXrole-box.rd"
                            box = 1

                        elif chartview == "topxbanbox":
                            requestchart = "Top X BAN (box)"
                            filename = f"{role}.ban.png"
                            charttype = "baseXrole-box.rd"
                            box = 1

                        elif chartview == "topxusebox":
                            requestchart = "Top X USE (box)"
                            filename = f"{role}.use.png"
                            charttype = "baseXrole-box.rd"
                            box = 1

                        chart = f"{chartpath}{charttype}/{elo}/{filename}"

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

    ######## SHOW VIEW OPTIONS#
                            if view == "delta":
                                log.info(f"Request Delta View")

                                indexmissing = 0
                                if period == "Day":
                                    try:
                                        previous_run = min(runtimes[0], runtimes[1])
                                    except IndexError:
                                        indexmissing = 1
                                elif period == "Week":
                                    try:
                                        previous_run = min(runtimes[0], runtimes[7])
                                    except IndexError:
                                        indexmissing = 1
                                elif period == "Month":
                                    try:
                                        previous_run = min(runtimes[0], runtimes[30])
                                    except IndexError:
                                        indexmissing = 1
                                elif period == "Season":
                                    try:
                                        previous_run = min(runtimes[0], runtimes[90])
                                    except IndexError:
                                        indexmissing = 1

                                if indexmissing == 0:
                                    previous = os.path.join(rawpath, previous_run)
                                    embed.add_field(name=f"Delta View for: {previous_run} > {latest_run}", value=f"These tables represent the most dramatic changes for each of the criteria from the last time the stats were synchronized.\
                                                                              Sorted by the change in table rank, including the change in value.\n\n", inline=False)

                                    log.info(f"Delta Compare: {period} {previous}")

                                    # Check for Previous Files
                                    pjsonfile = f'{previous}/{elo}.json'
                                    if os.path.isdir(previous) and os.path.exists(pjsonfile):
                                        log.info("Requesting: " + jsonfile)
                                        log.info("Requesting: " + pjsonfile)
                                        pruntime = previous_run.replace(rawpath, "")

                                        # Load previous file
                                        with open(pjsonfile) as pj:
                                            pdata = json.load(pj)

                                            # build table
                                            pdf = grabtierdata(pdata)

                                            # build table
                                            df = grabtierdata(data)

                                            # MERGE CURRENT WITH PREVIOUS
                                            df = df.merge(pdf, how='left', on='name')

                                            # region DataFrame Calculations

                                            # CALCULATE DELTAS
                                            df['urank_d'] = df['urank_x'] - df['urank_y']
                                            df['wrank_d'] = df['wrank_x'] - df['wrank_y']
                                            df['banrank_d'] = df['banrank_x'] - df['banrank_y']

                                            df['win_d'] = df['win_y'] - df['win_x']
                                            df['use_d'] = df['use_y'] - df['use_x']
                                            df['ban_d'] = df['ban_y'] - df['ban_x']

                                            df['win_d'] = df['win_d'].round(2)
                                            df['use_d'] = df['use_d'].round(2)
                                            df['ban_d'] = df['ban_d'].round(2)
                                            # endregion
                                            #print(f"Merged Table:\n {df}")

                                            #region ColumnHeader Mappings

                                            r = "RATING"
                                            r = r.center(9, " ")
                                            rd = "R▲"
                                            rd = rd.center(6, " ")
                                            i = "-"
                                            i = i.center(2, " ")
                                            n = "NAME"
                                            n = n.center(13, " ")
                                            w = "WIN"
                                            w = w.center(6, " ")
                                            u = "USE"
                                            u = u.center(6, " ")
                                            k = "BAN"
                                            k = k.center(6, " ")

                                            wd = "WIN▲"
                                            wd = wd.center(6, " ")
                                            ud = "USE▲"
                                            ud = ud.center(6, " ")
                                            kd = "BAN▲"
                                            kd = kd.center(6, " ")

                                            # print (df.columns)
                                            #endregion

                                            for crit in dsort_by:
                                                report = "\n"

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
                                                    dfs = df.sort_values(str(crit), ascending=False).head(5)
                                                    #print(f"sorted by: {crit}:\n{df}")
                                                else:
                                                    dfs = df.sort_values(str(crit), ascending=False).tail(5)

                                                #### Add Icon Column
                                                dfs['o'] = dfs['name'].str.lower()
                                                dfs['o'] = dfs['o'].str.replace(r"[\"\'\.\-, ]", '', regex=True)
                                                dfs['-'] = dfs['o'].map(mojimap.moji)
                                                del dfs['o']
                                                #print(f"Current Table:\n {dfs}")

                                                #### Add Padding and FORMAT:


                                                #Rebuild Tables
                                                if crit == "wrank_d":
                                                    title = "WR+/-"
                                                    dfd = dfs.reindex(columns=[str(crit), '-', 'name','wrank_x','wrank_y','win_x', 'win_d'])
                                                    #print(f"Pre-Table for {crit}:\n {dfd}")

                                                    #concat & format field
                                                    dfd['wrank_d'] = dfd['wrank_d'].mask(dfd['wrank_d'] >= 0, ("+"+dfd['wrank_d'].astype(str)))
                                                    dfd['wrank'] = dfd['wrank_x'].astype(str)+" > "+ dfd['wrank_y'].astype(str)
                                                    dfd['win_d'] = dfd['win_d'].mask(dfd['win_d'] >= 0,("+" + dfd['win_d'].astype(str)))

                                                    #drop & reorder
                                                    cols = ['wrank_d', 'wrank', '-', 'name', 'win_x', 'win_d']
                                                    dfd = dfd[cols]

                                                    #add padding:
                                                    dfd['wrank'] = ('`' + dfd['wrank'].str.center(9) + '`')
                                                    dfd['wrank_d'] = dfd['wrank_d'].astype(str)
                                                    dfd['wrank_d'] = ('`' + dfd['wrank_d'].str.center(6) + '`')
                                                    dfd['name'] = ('`' + dfd['name'].str.center(13) + '`')
                                                    dfd['win_x'] = dfd['win_x'].astype(str)
                                                    dfd['win_x'] = ('`' + dfd['win_x'].str.center(6) + '`')
                                                    dfd['win_d'] = dfd['win_d'].astype(str)
                                                    dfd['win_d'] = ('`' + dfd['win_d'].str.center(6) + '`')

                                                    #format header:
                                                    dfd.rename(columns={'wrank_d': rd, 'wrank': r, '-': i, 'name': n, 'win_x': w, 'win_d':wd}, inplace=True)
                                                    dfd.columns = dfd.columns.astype(str)
                                                    dfd.columns = ('`' + dfd.columns + '`')

                                                elif crit == "banrank_d":
                                                    title = "BAN+/-"
                                                    dfd = dfs.reindex(columns=[str(crit), '-', 'name','banrank_x','banrank_y','ban_x', 'ban_d'])
                                                    #print(f"Pre-Table for {crit}:\n {dfd}")

                                                    # concat & format field
                                                    dfd['banrank_d'] = dfd['banrank_d'].mask(dfd['banrank_d'] >= 0, ("+" + dfd['banrank_d'].astype(str)))
                                                    dfd['banrank'] = dfd['banrank_x'].astype(str) + " > " + dfd['banrank_y'].astype(str)
                                                    dfd['ban_d'] = dfd['ban_d'].mask(dfd['ban_d'] >= 0,("+" + dfd['ban_d'].astype(str)))


                                                    cols = ['banrank_d', 'banrank', '-', 'name', 'ban_x', 'ban_d']
                                                    dfd = dfd[cols]

                                                    # add padding:
                                                    dfd['banrank'] = ('`' + dfd['banrank'].str.center(9) + '`')
                                                    dfd['banrank_d'] = dfd['banrank_d'].astype(str)
                                                    dfd['banrank_d'] = ('`' + dfd['banrank_d'].str.center(6) + '`')
                                                    dfd['name'] = ('`' + dfd['name'].str.center(13) + '`')
                                                    dfd['ban_x'] = dfd['ban_x'].astype(str)
                                                    dfd['ban_x'] = ('`' + dfd['ban_x'].str.center(6) + '`')
                                                    dfd['ban_d'] = dfd['ban_d'].astype(str)
                                                    dfd['ban_d'] = ('`' + dfd['ban_d'].str.center(6) + '`')

                                                    # format header:
                                                    dfd.rename(columns={'banrank_d': rd, 'banrank': r, '-': i, 'name': n, 'ban_x': k,'ban_d': kd}, inplace=True)
                                                    dfd.columns = dfd.columns.astype(str)
                                                    dfd.columns = ('`' + dfd.columns + '`')

                                                elif crit == "urank_d":
                                                    title = "Use+/-"
                                                    dfd = dfs.reindex(columns=[str(crit), '-', 'name','urank_x','urank_y','use_x', 'use_d'])
                                                    #print(f"Pre-Table for {crit}:\n {dfd}")

                                                    # concat & format field
                                                    dfd['urank_d'] = dfd['urank_d'].mask(dfd['urank_d'] >= 0,("+" + dfd['urank_d'].astype(str)))
                                                    dfd['urank'] = dfd['urank_x'].astype(str) + " > " + dfd['urank_y'].astype(str)
                                                    dfd['use_d'] = dfd['use_d'].mask(dfd['use_d'] >= 0,("+" + dfd['use_d'].astype(str)))

                                                    # drop & reorder
                                                    cols = ['urank_d', 'urank', '-', 'name', 'use_x', 'use_d']
                                                    dfd = dfd[cols]

                                                    # add padding:
                                                    dfd['urank'] = ('`' + dfd['urank'].str.center(9) + '`')
                                                    dfd['urank_d'] = dfd['urank_d'].astype(str)
                                                    dfd['urank_d'] = ('`' + dfd['urank_d'].str.center(6) + '`')
                                                    dfd['name'] = ('`' + dfd['name'].str.center(13) + '`')
                                                    dfd['use_x'] = dfd['use_x'].astype(str)
                                                    dfd['use_x'] = ('`' + dfd['use_x'].str.center(6) + '`')
                                                    dfd['use_d'] = dfd['use_d'].astype(str)
                                                    dfd['use_d'] = ('`' + dfd['use_d'].str.center(6) + '`')

                                                    # format header:
                                                    dfd.rename(columns={'urank_d': rd, 'urank': r, '-': i, 'name': n,'use_x': u, 'use_d': ud}, inplace=True)
                                                    dfd.columns = dfd.columns.astype(str)
                                                    dfd.columns = ('`' + dfd.columns + '`')

                                                #print(f"Rebuilt Table for {crit}:\n {dfd}")

                                                # OUTPUT TO TABLE
                                                table = dfd.to_string(index=False)

                                                # print(table)
                                                report += table



                                                #### ADD EMBED FOR TABLE
                                                embed.add_field(name=f"Sorted by {title}", value=f"{report}", inline=False)
                                    else:
                                        log.warning(f"Bad Request: Missing: {pjsonfile} \
                                                                    Make sure {previous_run} exists.")
                                        embed = discord.Embed(
                                            title=f"TierData for {dt} > {previous_run} (Delta Values)",
                                            description=f"{sort} Differences (Elo:{elo})\n",
                                            color=0xFF5733)
                                        embed.set_thumbnail(
                                            url="https://icons.iconarchive.com/icons/paomedia/small-n-flat/256/sign-error-icon.png")
                                        embed.add_field(name=f"No TierData Found",
                                                        value=f"Source file missing. Please try again after the next data sync or refine your search.",
                                                        inline=False)
                                elif indexmissing ==1:
                                    embed = discord.Embed(
                                        title=f"TierData for {dt} > ERROR",
                                        description=f"{sort} Differences (Elo:{elo})\n",
                                        color=0xFF5733)
                                    embed.set_thumbnail(
                                        url="https://icons.iconarchive.com/icons/paomedia/small-n-flat/256/sign-error-icon.png")
                                    embed.add_field(name=f"No TierData Found",
                                                    value=f"Not enough datapoints in requested time period",
                                                    inline=False)

                            elif view == "meta":
                                log.info(f"Request Meta View")
                                embed.add_field(name=f"Meta View: ", value=f"Heroes by Lane, Use%", inline=False)

                                for ln in lanes:
                                    report = "\n"

                                    # build table
                                    if period == "Day":
                                        log.info("Requesting: " + jsonfile)
                                        df = grabtierdata(data)
                                    elif period == "Week":
                                        dfw = sumdf[['name','-','elo','win_w','use_w','ban_w','wrank_w','urank_w','banrank_w']]
                                        dfw = dfw.rename(columns={"win_w": "win","use_w": "use","ban_w":"ban","wrank_w":"wrank","urank_w":"urank","banrank_w":"banrank"})
                                        df = dfw[dfw['elo'] == elo]
                                    elif period == "Month":
                                        dfw = sumdf[['name','-','elo','win_m','use_m','ban_m','wrank_m','urank_m','banrank_m']]
                                        dfw = dfw.rename(columns={"win_m": "win","use_m": "use","ban_m":"ban","wrank_m":"wrank","urank_m":"urank","banrank_m":"banrank"})
                                        df = dfw[dfw['elo'] == elo]
                                    elif period == "Season":
                                        dfw = sumdf[['name','-','elo','win_s','use_s','ban_s','wrank_s','urank_s','banrank_s']]
                                        dfw = dfw.rename(columns={"win_s": "win","use_s": "use","ban_s":"ban","wrank_s":"wrank","urank_s":"urank","banrank_s":"banrank"})
                                        df = dfw[dfw['elo'] == elo]

                                    rslt = getattr(laning, ln)
                                    df = df[df['name'].isin(rslt)]

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

                                    #### Add Padding and FORMAT:
                                    df['rank'] = df['urank'].astype(str)
                                    df['rank'] = ('`' + df['rank'].str.center(4) + '`')
                                    df['name'] = ('`' + df['name'].str.center(13) + '`')
                                    df['win'] = df['win'].astype(str)
                                    df['win'] = ('`' + df['win'].str.center(6) + '`')
                                    df['use'] = df['use'].astype(str)
                                    df['use'] = ('`' + df['use'].str.center(6) + '`')
                                    df['ban'] = df['ban'].astype(str)
                                    df['ban'] = ('`' + df['ban'].str.center(6) + '`')

                                    # REBUILD
                                    df = df.reindex(columns=['rank', '-', 'name', 'win', 'use', 'ban'])

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
                                    k = "BAN"
                                    k = k.center(6, " ")
                                    df.rename(columns={'rank': r, '-': i, 'name': n, 'win': w, 'use': u, 'ban': k}, inplace=True)
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

                                    # build table
                                    if period == "Day":
                                        log.info("Requesting: " + jsonfile)
                                        df = grabtierdata(data)
                                    elif period == "Week":
                                        dfw = sumdf[['name', '-', 'elo', 'win_w', 'use_w', 'ban_w', 'wrank_w', 'urank_w','banrank_w']]
                                        dfw = dfw.rename(columns={"win_w": "win", "use_w": "use", "ban_w": "ban", "wrank_w": "wrank","urank_w": "urank", "banrank_w": "banrank"})
                                        df = dfw[dfw['elo'] == elo]
                                    elif period == "Month":
                                        dfw = sumdf[['name', '-', 'elo', 'win_m', 'use_m', 'ban_m', 'wrank_m', 'urank_m','banrank_m']]
                                        dfw = dfw.rename(columns={"win_m": "win", "use_m": "use", "ban_m": "ban", "wrank_m": "wrank","urank_m": "urank", "banrank_m": "banrank"})
                                        df = dfw[dfw['elo'] == elo]
                                    elif period == "Season":
                                        dfw = sumdf[['name', '-', 'elo', 'win_s', 'use_s', 'ban_s', 'wrank_s', 'urank_s','banrank_s']]
                                        dfw = dfw.rename(columns={"win_s": "win", "use_s": "use", "ban_s": "ban", "wrank_s": "wrank","urank_s": "urank", "banrank_s": "banrank"})
                                        df = dfw[dfw['elo'] == elo]

                                    rslt = getattr(roles, p)
                                    df = df[df['name'].isin(rslt)]

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

                                    #### Add Padding and FORMAT:
                                    df['rank'] = df['urank'].astype(str)
                                    df['rank'] = ('`' + df['rank'].str.center(4) + '`')
                                    df['name'] = ('`' + df['name'].str.center(13) + '`')
                                    df['win'] = df['win'].astype(str)
                                    df['win'] = ('`' + df['win'].str.center(6) + '`')
                                    df['use'] = df['use'].astype(str)
                                    df['use'] = ('`' + df['use'].str.center(6) + '`')
                                    df['ban'] = df['ban'].astype(str)
                                    df['ban'] = ('`' + df['ban'].str.center(6) + '`')

                                    # REBUILD
                                    df = df.reindex(columns=['rank', '-', 'name', 'win', 'use', 'ban'])

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
                                    k = "BAN"
                                    k = k.center(6, " ")
                                    df.rename(columns={'rank': r, '-': i, 'name': n, 'win': w, 'use': u, 'ban': k}, inplace=True)
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

                                    # build table
                                    if period == "Day":
                                        log.info("Requesting: " + jsonfile)
                                        df = grabtierdata(data)
                                    elif period == "Week":
                                        dfw = sumdf[['name', '-', 'elo', 'win_w', 'use_w', 'ban_w', 'wrank_w', 'urank_w','banrank_w']]
                                        dfw = dfw.rename(
                                            columns={"win_w": "win", "use_w": "use", "ban_w": "ban", "wrank_w": "wrank","urank_w": "urank", "banrank_w": "banrank"})
                                        df = dfw[dfw['elo'] == elo]
                                    elif period == "Month":
                                        dfw = sumdf[['name', '-', 'elo', 'win_m', 'use_m', 'ban_m', 'wrank_m', 'urank_m','banrank_m']]
                                        dfw = dfw.rename(
                                            columns={"win_m": "win", "use_m": "use", "ban_m": "ban", "wrank_m": "wrank","urank_m": "urank", "banrank_m": "banrank"})
                                        df = dfw[dfw['elo'] == elo]
                                    elif period == "Season":
                                        dfw = sumdf[['name', '-', 'elo', 'win_s', 'use_s', 'ban_s', 'wrank_s', 'urank_s','banrank_s']]
                                        dfw = dfw.rename(
                                            columns={"win_s": "win", "use_s": "use", "ban_s": "ban", "wrank_s": "wrank","urank_s": "urank", "banrank_s": "banrank"})
                                        df = dfw[dfw['elo'] == elo]

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
                                        df = df.sort_values(crit, ascending=True).head(5)
                                    else:
                                        df = df.sort_values(crit, ascending=True).tail(5)

                                    #### Add Padding and FORMAT:
                                    df['rank'] = df[str(crit)].astype(str)
                                    df['rank'] = ('`' + df['rank'].str.center(4) + '`')
                                    df['name'] = ('`' + df['name'].str.center(13) + '`')
                                    df['win'] = df['win'].astype(str)
                                    df['win'] = ('`' + df['win'].str.center(6) + '`')
                                    df['use'] = df['use'].astype(str)
                                    df['use'] = ('`' + df['use'].str.center(6) + '`')
                                    df['ban'] = df['ban'].astype(str)
                                    df['ban'] = ('`' + df['ban'].str.center(6) + '`')

                                    # REBUILD
                                    df = df.reindex(columns=['rank', '-', 'name', 'win', 'use', 'ban'])

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
                                    k = "BAN"
                                    k = k.center(6, " ")
                                    df.rename(columns={'rank': r, '-': i, 'name': n, 'win': w, 'use': u, 'ban': k}, inplace=True)
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
                                    elif crit == "banrank":
                                        title = "BAN"
                                    elif crit == "urank":
                                        title = "Use%"

                                    #### ADD EMBED FOR TABLE
                                    embed.add_field(name=f"Sorted by {title}", value=f"{report}", inline=False)

                            elif view=="win" or view=="ban" or view=="use":
                                if view == "win":
                                    crit = "wrank"
                                    title = "WinRate"
                                elif view=="ban":
                                    crit = "banrank"
                                    title = "BAN"
                                elif view =="use":
                                    crit = "urank"
                                    title = "USE"

                                log.info(f"Request {title} View")

                                report = "\n"

                                if period == "Day":
                                    log.info("Requesting: " + jsonfile)
                                    df = grabtierdata(data)
                                elif period == "Week":
                                    dfw = sumdf[['name', '-', 'elo', 'win_w', 'use_w', 'ban_w', 'wrank_w', 'urank_w','banrank_w']]
                                    dfw = dfw.rename(
                                        columns={"win_w": "win", "use_w": "use", "ban_w": "ban", "wrank_w": "wrank","urank_w": "urank", "banrank_w": "banrank"})
                                    df = dfw[dfw['elo'] == elo]
                                elif period == "Month":
                                    dfw = sumdf[['name', '-', 'elo', 'win_m', 'use_m', 'ban_m', 'wrank_m', 'urank_m','banrank_m']]
                                    dfw = dfw.rename(
                                        columns={"win_m": "win", "use_m": "use", "ban_m": "ban", "wrank_m": "wrank","urank_m": "urank", "banrank_m": "banrank"})
                                    df = dfw[dfw['elo'] == elo]
                                elif period == "Season":
                                    dfw = sumdf[['name', '-', 'elo', 'win_s', 'use_s', 'ban_s', 'wrank_s', 'urank_s','banrank_s']]
                                    dfw = dfw.rename(
                                        columns={"win_s": "win", "use_s": "use", "ban_s": "ban", "wrank_s": "wrank","urank_s": "urank", "banrank_s": "banrank"})
                                    df = dfw[dfw['elo'] == elo]

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


                                #### Add Icon Column
                                df['o'] = df['name'].str.lower()
                                df['o'] = df['o'].str.replace(r"[\"\'\.\-, ]", '', regex=True)
                                df['-'] = df['o'].map(mojimap.moji)
                                del df['o']

                                #### Add Padding and FORMAT:
                                df['rank'] = df[str(crit)].astype(str)
                                df['rank'] = ('`' + df['rank'].str.center(4) + '`')
                                df['name'] = ('`' + df['name'].str.center(13) + '`')
                                df['win'] = df['win'].astype(str)
                                df['win'] = ('`' + df['win'].str.center(6) + '`')
                                df['use'] = df['use'].astype(str)
                                df['use'] = ('`' + df['use'].str.center(6) + '`')
                                df['ban'] = df['ban'].astype(str)
                                df['ban'] = ('`' + df['ban'].str.center(6) + '`')

                                # REBUILD
                                df = df.reindex(columns=['rank', '-', 'name', 'win', 'use', 'ban'])

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
                                k = "BAN"
                                k = k.center(6, " ")
                                df.rename(columns={'rank': r, '-': i, 'name': n, 'win': w, 'use': u, 'ban': k}, inplace=True)
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
                                                  f"\nTry using a filter such as `/td elo:Legend` to get more accurate results.",
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
                        title=f"TierData for {dt}",
                        description=f"{sort} Heroes (Elo:{elo})\n",
                        color=0xFF5733)
                    embed.set_thumbnail(url="https://icons.iconarchive.com/icons/paomedia/small-n-flat/256/sign-error-icon.png")
                    embed.add_field(name=f"No TierData Found", value=f"Source file missing. Please try again after the next data sync or refine your search.", inline=False)
                    await ctx.channel.send(embed=embed)
                    #await ctx.channel.send(content="```No TierData Found...```")
# MISSING FOLDER
            else:
                log.warning(f"Bad Request: Missing: {latest}")
                await ctx.channel.send(content="```No TierData Reported Yet...```")

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
                     name="elo",
                     description="Look at TierData by Player Performance!",
                     option_type=3,
                     required=False,
                     choices=[
                         create_choice(
                             name="All",
                             value="All"),
                         create_choice(
                             name="Legend+",
                             value="Legend"),
                         create_choice(
                             name="Mythic (400+)",
                             value="Mythic")
                     ]
                 ),
                 create_option(
                     name="period",
                     description="Look at TierData for the previous time-period.",
                     option_type=3,
                     required=False,
                     choices=[
                         create_choice(
                             name="Week (7-days)",
                             value="Week"),
                         create_choice(
                             name="Month (30-days)",
                             value="Month"),
                         create_choice(
                             name="Season (90-days)",
                             value="Season")
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
async def test(ctx, hero: str, elo="All", period="Day", show="null", about="null"):
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
                       \n\n`/tdh hero: YOUR-HERO-NAME` (required) - Show BAN/WR%/USE% for this Hero by ELO \
                       \n- `elo:(All,Legend+,Mythic 400+)`, default: `All` \
                       \n- `show:(History, Averages)` default: `none` - The view changes from a historical view of BAN,WR,or USE -or- a box chart view of averages"
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
#LOOK FOR HERO
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
#HERO FOUND
            else:
                hn = result[0]

                # audit
                user = ctx.author
                # audit.info(f",{user},dd,{elo},{period},{sort},{role},{view},{chartview},{about},{show},{shero}")
                audit.info(f"{user},tdh,{elo},{period},,,,,,{show},{hn}")
                log.info(f"{user} used /ddh")

                log.info(f"Looking for... {hn}")
                hnl = hn.replace("-", "").replace("'", "").replace(".", "").replace(" ", "").lower()

                #### NEXT----  START TIERDATA
                ico = mojimap.moji[hnl]
                runtime = latest.replace(rawpath, "")
                portrait = heroicons.portrait[hnl]

                ###### Transform filters:

                dt = period.replace("Day", "Today").replace("Week", "This Week").replace("Month", "This Month").replace(
                    "Season", "This Season")
                dts = period.replace("Day","day7").replace("Week", "day7").replace("Month", "day30").replace("Season","day90")

                #### COLOR DECORATION
                if elo == "All":
                    color = discord.Color.teal()

                elif elo == "Legend":
                    color = discord.Color.gold()

                elif elo == "Mythic":
                    color = discord.Color.purple()


                #### DECLARE EMBED ####
                embed = discord.Embed(
                    title=f"TierData for {hn}",
                    description=f"\n",
                    color=color)

                embed.set_thumbnail(url=f"{portrait}")

#CHECK FOR HISTORY:
                if show=="history":
                    #SHOW HISTORY CHART
                    chart = f"{histpath}{elo}/{dts}/{hnl}.png"

                    if not os.path.exists(chart):
                        embed.add_field(name=f" {ico} Historical Summary:", value=f"`No Chart Available...`", inline=False)
                        log.warning(f"Missing Chart: {chart}")

                        #### ADD EMBED FOR Foot
                        embed.add_field(name=f"Source:",
                                        value=f"Data provided by https://m.mobilelegends.com/en/rank\nLast DataSync: {runtime}",
                                        inline=False)

                        await ctx.channel.send(embed=embed)

                    else:
                        embed.add_field(name=f" {ico} Historical Summary:", value=f"Changes in Win%, Use%, Ban% over Time.",
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
                    chart = f"{avgpath}{elo}/{dts}/{hnl}.png"

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
                                        value=f"Averages in Win%, Use%, Ban% over Time.",
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
# region STANDARD TABLE
                    if period == "Day":

                        #### Create Filters
                        nfilter = dfx.isin([hn]).any(axis=1)

                        if elo == "All":
                            efilter = dfx["elo"]
                        else:
                            efilter = dfx["elo"].isin([elo])

                        hdf = dfx[nfilter & efilter]

                        hdf = hdf.reindex(columns=['-','elo', 'win', 'use', 'ban', 'wrank', 'urank', 'banrank'])

                        #### Add Padding and FORMAT:
                        hdf['elo'] = ('`' + hdf['elo'].str.center(6) + '`')
                        hdf['win'] = hdf['win'].astype(str)
                        hdf['win'] = ('`' + hdf['win'].str.center(5) + '`')
                        hdf['use'] = hdf['use'].astype(str)
                        hdf['use'] = ('`' + hdf['use'].str.center(5) + '`')
                        hdf['ban'] = hdf['ban'].astype(str)
                        hdf['ban'] = ('`' + hdf['ban'].str.center(5) + '`')
                        hdf['wrank'] = hdf['wrank'].astype(str)
                        hdf['wrank'] = ('`' + hdf['wrank'].str.center(3) + '`')
                        hdf['urank'] = hdf['urank'].astype(str)
                        hdf['urank'] = ('`' + hdf['urank'].str.center(3) + '`')
                        hdf['banrank'] = hdf['banrank'].astype(str)
                        hdf['banrank'] = ('`' + hdf['banrank'].str.center(3) + '`')

                        # FORMAT COLUMN HEADER
                        e = "ELO"
                        e = e.center(6, " ")
                        i = "-"
                        i = i.center(2, " ")
                        w = "WIN%"
                        w = w.center(5, " ")
                        u = "USE%"
                        u = u.center(5, " ")
                        k = "BAN%"
                        k = k.center(5, " ")
                        wr = "WIN"
                        wr = wr.center(3, " ")
                        ur = "USE"
                        ur = ur.center(3, " ")
                        br = "BAN"
                        br = br.center(3, " ")
                        hdf.rename(columns={'-': i, 'elo': e, 'win': w, 'use': u, 'ban': k, 'wrank': wr, 'urank': ur,
                                            'banrank': br}, inplace=True)
                        hdf.columns = hdf.columns.astype(str)
                        hdf.columns = ('`' + hdf.columns + '`')

                        # print(hdf)
                    elif period == "Week":
                        #### Create Filters
                        nfilter = sumdf.isin([hn]).any(axis=1)

                        if elo == "All":
                            efilter = sumdf["elo"]
                        else:
                            efilter = sumdf["elo"].isin([elo])

                        hdf = sumdf[nfilter & efilter]
                        hdf = hdf.reindex(columns=['-', 'elo', 'win_w', 'use_w', 'ban_w'])
                        hdf['-'] = hdf['elo'].map(roji)

                        #### Add Padding and FORMAT:
                        hdf['elo'] = ('`' + hdf['elo'].str.center(6) + '`')
                        hdf['win_w'] = hdf['win_w'].astype(str)
                        hdf['win_w'] = ('`' + hdf['win_w'].str.center(5) + '`')
                        hdf['use_w'] = hdf['use_w'].astype(str)
                        hdf['use_w'] = ('`' + hdf['use_w'].str.center(5) + '`')
                        hdf['ban_w'] = hdf['ban_w'].astype(str)
                        hdf['ban_w'] = ('`' + hdf['ban_w'].str.center(5) + '`')

                        # FORMAT COLUMN HEADER
                        e = "ELO"
                        e = e.center(6, " ")
                        i = "-"
                        i = i.center(2, " ")
                        w = "WIN%"
                        w = w.center(5, " ")
                        u = "USE%"
                        u = u.center(5, " ")
                        k = "BAN%"
                        k = k.center(5, " ")
                        hdf.rename(columns={'-': i, 'elo': e, 'win_w': w, 'use_w': u, 'ban_w': k}, inplace=True)
                        hdf.columns = hdf.columns.astype(str)
                        hdf.columns = ('`' + hdf.columns + '`')

                        # print(hdf)
                    elif period == "Month":
                        #### Create Filters
                        nfilter = sumdf.isin([hn]).any(axis=1)

                        if elo == "All":
                            efilter = sumdf["elo"]
                        else:
                            efilter = sumdf["elo"].isin([elo])

                        hdf = sumdf[nfilter & efilter]
                        hdf = hdf.reindex(columns=['-', 'elo', 'win_m', 'use_m', 'ban_m'])
                        hdf['-'] = hdf['elo'].map(roji)

                        #### Add Padding and FORMAT:
                        hdf['elo'] = ('`' + hdf['elo'].str.center(6) + '`')
                        hdf['win_m'] = hdf['win_m'].astype(str)
                        hdf['win_m'] = ('`' + hdf['win_m'].str.center(5) + '`')
                        hdf['use_m'] = hdf['use_m'].astype(str)
                        hdf['use_m'] = ('`' + hdf['use_m'].str.center(5) + '`')
                        hdf['ban_m'] = hdf['ban_m'].astype(str)
                        hdf['ban_m'] = ('`' + hdf['ban_m'].str.center(5) + '`')

                        # FORMAT COLUMN HEADER
                        e = "ELO"
                        e = e.center(6, " ")
                        i = "-"
                        i = i.center(2, " ")
                        w = "WIN%"
                        w = w.center(5, " ")
                        u = "USE%"
                        u = u.center(5, " ")
                        k = "BAN%"
                        k = k.center(5, " ")
                        hdf.rename(columns={'-': i, 'elo': e, 'win_m': w, 'use_m': u, 'ban_m': k}, inplace=True)
                        hdf.columns = hdf.columns.astype(str)
                        hdf.columns = ('`' + hdf.columns + '`')

                        # print(hdf)
                    elif period == "Season":
                        #### Create Filters
                        nfilter = sumdf.isin([hn]).any(axis=1)

                        if elo == "All":
                            efilter = sumdf["elo"]
                        else:
                            efilter = sumdf["elo"].isin([elo])

                        hdf = sumdf[nfilter & efilter]
                        hdf = hdf.reindex(columns=['-', 'elo', 'win_s', 'use_s', 'ban_s'])
                        hdf['-'] = hdf['elo'].map(roji)

                        #### Add Padding and FORMAT:
                        hdf['elo'] = ('`' + hdf['elo'].str.center(6) + '`')
                        hdf['win_s'] = hdf['win_s'].astype(str)
                        hdf['win_s'] = ('`' + hdf['win_s'].str.center(5) + '`')
                        hdf['use_s'] = hdf['use_s'].astype(str)
                        hdf['use_s'] = ('`' + hdf['use_s'].str.center(5) + '`')
                        hdf['ban_s'] = hdf['ban_s'].astype(str)
                        hdf['ban_s'] = ('`' + hdf['ban_s'].str.center(5) + '`')

                        # FORMAT COLUMN HEADER
                        e = "ELO"
                        e = e.center(6, " ")
                        i = "-"
                        i = i.center(2, " ")
                        w = "WIN%"
                        w = w.center(5, " ")
                        u = "USE%"
                        u = u.center(5, " ")
                        k = "BAN%"
                        k = k.center(5, " ")
                        hdf.rename(columns={'-': i, 'elo': e, 'win_s': w, 'use_s': u, 'ban_s': k}, inplace=True)
                        hdf.columns = hdf.columns.astype(str)
                        hdf.columns = ('`' + hdf.columns + '`')

                        # print(hdf)

                    if hdf.empty:
                        hdf = "No data available."
                    else:
                        table = hdf.to_string(index=False)
                    embed.add_field(name=f" {ico} Summary for: {dt}", value=f"{table}", inline=False)

                    # endregion
# region DELTA TABLE
                    log.info(f"Request HERO Delta View")
                    log.info(f"Request Delta View")

                    indexmissing = 0
                    if period == "Day":
                        try:
                            previous_run = min(runtimes[0], runtimes[1])
                        except IndexError:
                            indexmissing = 1
                    elif period == "Week":
                        try:
                            previous_run = min(runtimes[0], runtimes[7])
                        except IndexError:
                            indexmissing = 1
                    elif period == "Month":
                        try:
                            previous_run = min(runtimes[0], runtimes[30])
                        except IndexError:
                            indexmissing = 1
                    elif period == "Season":
                        try:
                            previous_run = min(runtimes[0], runtimes[90])
                        except IndexError:
                            indexmissing = 1

                    if indexmissing == 0:
                        previous = os.path.join(rawpath, previous_run)
                        log.info(f"Delta Compare: {previous_run} > {latest_run}")
                        embed.add_field(name=f"Delta Compare:", value=f" {previous_run} > {latest_run}", inline=False)

                        #### Create Filters
                        nfilter = dfx.isin([hn]).any(axis=1)

                        if elo == "All":
                            efilter = dfx["elo"]
                        else:
                            efilter = dfx["elo"].isin([elo])

                        hldf = dfx[nfilter & efilter]
                        #hldf = chdf[nfilter & efilter]
                        hldf = hldf.reindex(columns=['-', 'elo', 'win', 'use', 'ban', 'wrank', 'urank', 'banrank'])

                        pdf = grabherotable(previous)
                        pnfilter = pdf.isin([hn]).any(axis=1)

                        if elo == "All":
                            pefilter = pdf["elo"]
                        else:
                            pefilter = pdf["elo"].isin([elo])

                        phdf = pdf[pnfilter & pefilter]
                        phdf = phdf.reindex(columns=['elo', 'win', 'use', 'ban', 'wrank', 'urank', 'banrank'])

                        if hldf.empty or phdf.empty:
                            embed.add_field(name=f"No Delta Data Found",
                                            value=f"Not enough datapoints in requested time period",
                                            inline=False)
                        else:

                            print(f"Current:\n{latest}\n{hldf}")
                            print(f"Previous:\n{previous}\n{phdf}")

                            df = hldf.merge(phdf, how='left', on='elo')
                            print(f"Merged Table:\n {df}")
                            # region DataFrame Calculations

                            # CALCULATE DELTAS
                            df['urank_d'] = df['urank_x'] - df['urank_y']
                            df['wrank_d'] = df['wrank_x'] - df['wrank_y']
                            df['banrank_d'] = df['banrank_x'] - df['banrank_y']

                            df['win_d'] = df['win_y'] - df['win_x']
                            df['use_d'] = df['use_y'] - df['use_x']
                            df['ban_d'] = df['ban_y'] - df['ban_x']

                            df['win_d'] = df['win_d'].round(2)
                            df['use_d'] = df['use_d'].round(2)
                            df['ban_d'] = df['ban_d'].round(2)
                            # endregion
                            #print(f"Calculated Table:\n {df}")

                            # region ColumnHeader Mappings

                            r = "RATING"
                            r = r.center(9, " ")
                            rd = "R▲"
                            rd = rd.center(6, " ")
                            i = "-"
                            i = i.center(2, " ")
                            w = "WIN"
                            w = w.center(6, " ")
                            u = "USE"
                            u = u.center(6, " ")
                            k = "BAN"
                            k = k.center(6, " ")

                            wd = "WIN▲"
                            wd = wd.center(6, " ")
                            ud = "USE▲"
                            ud = ud.center(6, " ")
                            kd = "BAN▲"
                            kd = kd.center(6, " ")

                            print (df.columns)
                            # endregion

                            for crit in dsort_by:
                                report = "\n"

                                if crit == "wrank_d":
                                    title = "WR+/-"
                                    dfd = df.reindex(
                                        columns=[str(crit), '-', 'wrank_x', 'wrank_y', 'win_x', 'win_d'])
                                    # print(f"Pre-Table for {crit}:\n {dfd}")

                                    # concat & format field
                                    dfd['wrank_d'] = dfd['wrank_d'].mask(dfd['wrank_d'] >= 0,
                                                                         ("+" + dfd['wrank_d'].astype(str)))
                                    dfd['wrank'] = dfd['wrank_x'].astype(str) + " > " + dfd['wrank_y'].astype(str)
                                    dfd['win_d'] = dfd['win_d'].mask(dfd['win_d'] >= 0,
                                                                     ("+" + dfd['win_d'].astype(str)))

                                    # drop & reorder
                                    cols = ['-','wrank_d', 'wrank', 'win_x', 'win_d']
                                    dfd = dfd[cols]

                                    # add padding:
                                    dfd['wrank'] = ('`' + dfd['wrank'].str.center(9) + '`')
                                    dfd['wrank_d'] = dfd['wrank_d'].astype(str)
                                    dfd['wrank_d'] = ('`' + dfd['wrank_d'].str.center(6) + '`')
                                    dfd['win_x'] = dfd['win_x'].astype(str)
                                    dfd['win_x'] = ('`' + dfd['win_x'].str.center(6) + '`')
                                    dfd['win_d'] = dfd['win_d'].astype(str)
                                    dfd['win_d'] = ('`' + dfd['win_d'].str.center(6) + '`')

                                    # format header:
                                    dfd.rename(columns={'wrank_d': rd, 'wrank': r, '-': i,'win_x': w,
                                                        'win_d': wd}, inplace=True)
                                    dfd.columns = dfd.columns.astype(str)
                                    dfd.columns = ('`' + dfd.columns + '`')

                                elif crit == "banrank_d":
                                    title = "BAN+/-"
                                    dfd = df.reindex(
                                        columns=[str(crit), '-', 'banrank_x', 'banrank_y', 'ban_x',
                                                 'ban_d'])
                                    # print(f"Pre-Table for {crit}:\n {dfd}")

                                    # concat & format field
                                    dfd['banrank_d'] = dfd['banrank_d'].mask(dfd['banrank_d'] >= 0,
                                                                             ("+" + dfd['banrank_d'].astype(str)))
                                    dfd['banrank'] = dfd['banrank_x'].astype(str) + " > " + dfd['banrank_y'].astype(
                                        str)
                                    dfd['ban_d'] = dfd['ban_d'].mask(dfd['ban_d'] >= 0,
                                                                     ("+" + dfd['ban_d'].astype(str)))

                                    cols = ['-', 'banrank_d', 'banrank', 'ban_x', 'ban_d']
                                    dfd = dfd[cols]

                                    # add padding:
                                    dfd['banrank'] = ('`' + dfd['banrank'].str.center(9) + '`')
                                    dfd['banrank_d'] = dfd['banrank_d'].astype(str)
                                    dfd['banrank_d'] = ('`' + dfd['banrank_d'].str.center(6) + '`')
                                    dfd['ban_x'] = dfd['ban_x'].astype(str)
                                    dfd['ban_x'] = ('`' + dfd['ban_x'].str.center(6) + '`')
                                    dfd['ban_d'] = dfd['ban_d'].astype(str)
                                    dfd['ban_d'] = ('`' + dfd['ban_d'].str.center(6) + '`')

                                    # format header:
                                    dfd.rename(
                                        columns={'banrank_d': rd, 'banrank': r, '-': i, 'ban_x': k,
                                                 'ban_d': kd}, inplace=True)
                                    dfd.columns = dfd.columns.astype(str)
                                    dfd.columns = ('`' + dfd.columns + '`')

                                elif crit == "urank_d":
                                    title = "Use+/-"
                                    dfd = df.reindex(
                                        columns=[str(crit), '-', 'urank_x', 'urank_y', 'use_x', 'use_d'])
                                    # print(f"Pre-Table for {crit}:\n {dfd}")

                                    # concat & format field
                                    dfd['urank_d'] = dfd['urank_d'].mask(dfd['urank_d'] >= 0,
                                                                         ("+" + dfd['urank_d'].astype(str)))
                                    dfd['urank'] = dfd['urank_x'].astype(str) + " > " + dfd['urank_y'].astype(str)
                                    dfd['use_d'] = dfd['use_d'].mask(dfd['use_d'] >= 0,
                                                                     ("+" + dfd['use_d'].astype(str)))

                                    # drop & reorder
                                    cols = [ '-', 'urank_d', 'urank','use_x', 'use_d']
                                    dfd = dfd[cols]

                                    # add padding:
                                    dfd['urank'] = ('`' + dfd['urank'].str.center(9) + '`')
                                    dfd['urank_d'] = dfd['urank_d'].astype(str)
                                    dfd['urank_d'] = ('`' + dfd['urank_d'].str.center(6) + '`')
                                    dfd['use_x'] = dfd['use_x'].astype(str)
                                    dfd['use_x'] = ('`' + dfd['use_x'].str.center(6) + '`')
                                    dfd['use_d'] = dfd['use_d'].astype(str)
                                    dfd['use_d'] = ('`' + dfd['use_d'].str.center(6) + '`')

                                    # format header:
                                    dfd.rename(columns={'urank_d': rd, 'urank': r, '-': i, 'use_x': u,
                                                        'use_d': ud}, inplace=True)
                                    dfd.columns = dfd.columns.astype(str)
                                    dfd.columns = ('`' + dfd.columns + '`')

                                # print(f"Rebuilt Table for {crit}:\n {dfd}")

                                # OUTPUT TO TABLE
                                table = dfd.to_string(index=False)

                                # print(table)
                                report += table
                                print(report)
                                #### ADD EMBED FOR TABLE
                                embed.add_field(name=f"{title}", value=f"{report}", inline=False)

                    elif indexmissing == 1:
                        embed.add_field(name=f"No Delta Data Found",
                                        value=f"Not enough datapoints in requested time period",
                                        inline=False)


                    # endregion


                    # IF OUTLIER
                    if outlier >= 1:
                        embed.add_field(name=f":rotating_light: Outlier Notice:",
                                        value=f":bear: Teddy has detected a statistically improbable anomaly in the data you have requested."
                                              f"\nTry using a filter such as `/tdh elo:Legend` to get more accurate results.",
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

    startupembed.set_thumbnail(
        url="https://icons.iconarchive.com/icons/custom-icon-design/flatastic-9/256/Accept-icon.png")

    for channel_id in optin:
        await bot.get_channel(channel_id).send(embed=startupembed)

# endregion

# region MOD COMMANDS
@bot.command(pass_context=True)
@commands.has_any_role(*summaryroles)
async def weeklysummary(ctx, channel: discord.TextChannel, reportnum):
    # confirmation
    await ctx.send(f"Sending Weekly Summary from {reportnum} to: {channel}")
    log.info(f"Sending Weekly Summary from {reportnum} to: {channel}")

    #build summary
    summaryembed = discord.Embed(
        title=f"WEEKLY SUMMARY REPORT - {reportnum}",
        description=f"Powered by :bear: TEDDY\n")

    summaryembed.set_thumbnail(
        url="https://icons.iconarchive.com/icons/graphicloads/polygon/256/stats-icon.png")

    channel = channel.id

    #check for report
    weeklyreport = f"{reportpath}/{reportnum}.png"
    if os.path.exists(weeklyreport):
        summaryembed.add_field(name=f"Weekly Tier Data Summary",
                               value=f"Please checkout the weekly summary powered by TEDDY! \
                                         Every week after the stats run, we summarize the findings and \
                                         produce this nifty infographic to demonstrate how players are performing! \
                                         Enjoy!", inline=False)
        file = discord.File(f"{weeklyreport}", filename=f"{reportnum}.png")
        summaryembed.set_image(url=f"attachment://{reportnum}.png")
        log.info(f"We have a weekly report!  Printing: {weeklyreport}")

        await bot.get_channel(channel).send(file=file, embed=summaryembed)
    else:
        log.info(f"No weekly report found: {weeklyreport}. Starting normally.")
        summaryembed.add_field(name=f"Messages:", value=f"No messages.", inline=False)

        await bot.get_channel(channel).send(embed=summaryembed)

    pass

@weeklysummary.error
async def weeklysummary_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        listsums = sorted(os.listdir(reportpath))
        listsums = [l.replace('.png', '') for l in listsums]

        reportnum = listsums[-1]
        channel = ctx.channel.id

        log.info(f"No arguments found. Generating Help Text")

        errorembed = discord.Embed(
            title=f"Missing arguments:",
            description=f"`/td weeklysummary` requires the following arguments:\n \
                        `channel` (e.g. this channel: `{channel}`)\n \
                        `reportnumber` (e.g. `{reportnum}`)\n\n \
                        You can optionally run: `/td listsummary` to view all available reports\n\n \
                        e.g.: `/td weeklysummary {channel} {reportnum}`")
        errorembed.set_thumbnail(
            url="https://icons.iconarchive.com/icons/hopstarter/sleek-xp-basic/256/Close-icon.png")
        await ctx.send(embed=errorembed)

@bot.command()
@commands.has_any_role(*summaryroles)
async def listsummary(ctx):
    listsums = sorted(os.listdir(reportpath))
    listsums = [l.replace('.png', '') for l in listsums]
    reportnum = listsums[-1]

    listsumembed = discord.Embed(
        title=f"Recent Weekly Summaries:",
        description=f"\n")
    listsumembed.set_thumbnail(
        url="https://icons.iconarchive.com/icons/graphicloads/polygon/256/stats-icon.png")
    listsumembed.add_field(name=f"List of recent Weekly Summaries:", value=f" \
    `{listsums}`\n\n\
    You may use these with `/td weeklysummary <channel> <report_date>` \
    Run `/td weeklysummary` with no arguments to see usage.", inline=False)
    log.info(f"Generating List of Summaries")
    await ctx.send(embed=listsumembed)
    pass

@bot.command()
@commands.has_any_role(*summaryroles)
async def info(ctx):
    modhelpembed = discord.Embed(
        title=f"Moderator Commands:",
        description=f"\n")
    modhelpembed.add_field(name=f"`/td weeklysummary <channel> <report_date>`", value=f" \
    Arguments required: channel, reportnumber.\n\nThis produces the weekly infographic and sends to specified channel\n \
    Requires Role(s): `{summaryroles}`. \nThis also only works on channels where TEDDY can post.", inline=False)
    modhelpembed.add_field(name=f"`/td listsummary `", value=f" \
        This produces a list of the available summary reports to be used with `/td weeklysummary`\n \
        Requires Role(s): `{summaryroles}`. \nThis also only works on channels where TEDDY can post.", inline=False)

    await ctx.send(embed=modhelpembed)
    pass
# endregion

# region DISCORD STUFF
# discord basic error handling:
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        log.error(f"Command Not Found")
    if isinstance(error, commands.MissingRequiredArgument):
        log.error(f"Function Missing Argument")
    if isinstance(error, commands.Forbidden):
        log.error(f"Missing Access")
    if isinstance(error, commands.MissingPermissions):
        log.error(f"Insufficient Permissions")
    if isinstance(error, commands.BotMissingPermissions):
        log.error(f"Insufficient Bot Permissions")
    else:
        log.error(f"Unspecified Error")
# endregion

bot.run(TOKEN)

