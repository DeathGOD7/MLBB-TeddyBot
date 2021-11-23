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

import logging
# endregion

def grabtierdata(data):

    df = json_normalize(data, ['data', 'data'])

    # convert from strings:
    df['win'] = list(map(lambda x: x[:-1], df['win'].values))
    df['use'] = list(map(lambda x: x[:-1], df['use'].values))
    df['ban'] = list(map(lambda x: x[:-1], df['ban'].values))

    df['win'] = [float(x) for x in df['win'].values]
    df['use'] = [float(x) for x in df['use'].values]
    df['ban'] = [float(x) for x in df['ban'].values]

    # add ranking column
    df = df.sort_values(by=['use'], ascending=False)
    df['urank'] = range(1, len(df) + 1)
    df = df.sort_values(by=['win'], ascending=False)
    df['wrank'] = range(1, len(df) + 1)
    df = df.sort_values(by=['ban'], ascending=False)
    df['banrank'] = range(1, len(df) + 1)

    #### Add Icon Column
    df['o'] = df['name'].str.lower()
    df['o'] = df['o'].str.replace(r"[\"\'\.\-, ]", '', regex=True)
    df['-'] = df['o'].map(mojimap.moji)

    df = df.round(2)
    del df['o']
    return df

def grabsummarydata(path):

    #check paths first
    print(path)
    if os.path.exists(path):

        lvls = ['All', 'Legend', 'Mythic']
        dfx = pd.DataFrame(columns=['name','-','elo','win_w', 'use_w', 'ban_w','urank_w','wrank_w','banrank_w',
                                    'win_m', 'use_m', 'ban_m','urank_m','wrank_m','banrank_m',
                                    'win_s', 'use_s', 'ban_s','urank_s','wrank_s','banrank_s'])

        for l in lvls:
            df = pd.read_csv(path)
            df = df[df['elo']==l]
            # add ranking column
            df = df.sort_values(by=['use_w'], ascending=False)
            df['urank_w'] = range(1, len(df) + 1)
            df = df.sort_values(by=['win_w'], ascending=False)
            df['wrank_w'] = range(1, len(df) + 1)
            df = df.sort_values(by=['ban_w'], ascending=False)
            df['banrank_w'] = range(1, len(df) + 1)

            df = df.sort_values(by=['use_m'], ascending=False)
            df['urank_m'] = range(1, len(df) + 1)
            df = df.sort_values(by=['win_m'], ascending=False)
            df['wrank_m'] = range(1, len(df) + 1)
            df = df.sort_values(by=['ban_m'], ascending=False)
            df['banrank_m'] = range(1, len(df) + 1)

            df = df.sort_values(by=['use_s'], ascending=False)
            df['urank_s'] = range(1, len(df) + 1)
            df = df.sort_values(by=['win_s'], ascending=False)
            df['wrank_s'] = range(1, len(df) + 1)
            df = df.sort_values(by=['ban_s'], ascending=False)
            df['banrank_s'] = range(1, len(df) + 1)

            #print(df)
            dfx = pd.concat([dfx, df], axis=0)

        #### Add Icon Column
        dfx['o'] = dfx['name'].str.lower()
        dfx['o'] = dfx['o'].str.replace(r"[\"\'\.\-, ]", '', regex=True)
        dfx['-'] = dfx['o'].map(mojimap.moji)
        del dfx['o']
        #print(dfx)
        return dfx
    else:
        print(f"{path} not found.")
