# region IMPORTS

import os
from os.path import exists


import json
import pandas as pd
from pandas import json_normalize

import logging
# endregion

# region VARIABLES

APIpath = "/var/www/html/MLBB-API/v1/"
herofile = "hero-meta-final.json"
prof = ["assassin","marksman","mage","tank","support","fighter"]
lanes = ["gold","exp","mid","jungle","roam"]
# IMPORT MOJI MAP
with open(APIpath+herofile) as j:
    data = json.load(j)

    df = json_normalize(data, ['data'])
    df = df[df.hero_name != 'None']

    # fix punctuation
    df = df.replace('Chang-e', 'Chang\'e')
    df = df.replace('X-Borg', 'X.Borg')

    ### get hero moji (replaces mojimap.py)
    moji = df.set_index('uid')['discordmoji'].to_dict()

# endregion

# region Summary Table Gen Functions
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
    df['-'] = df['o'].map(moji)

    df = df.round(2)
    del df['o']
    return df

def grabsummarydata(path):

    #check paths first
    print(f'Summary Table Built from: {path}')
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
        dfx['-'] = dfx['o'].map(moji)
        del dfx['o']
        #print(dfx)
        return dfx
    else:
        print(f"{path} not found.")

def grabherotable(latest):
    # region HERO TABLE GENERATOR
    lvls = ["All", "Legend", "Mythic"]
    periods = ["Week", "Month", "Season"]

    print(f'Hero Table Built from: {latest}')
    # Create master table
    dfx = pd.DataFrame(columns=['name', 'win', 'use', 'ban', 'elo', 'urank', 'wrank', 'banrank'])

    if os.path.isdir(latest):  # check for raw data path
        #### FIND FILES

        for lvl in lvls:
            jsonfile = f'{latest}/{lvl}.json'
            if os.path.exists(jsonfile):
                print("Requesting: " + jsonfile)

                ##### BUILD TABLES ####
                with open(jsonfile) as j:
                    data = json.load(j)

                    # build table
                    df = grabtierdata(data)
                    df['elo'] = f"{lvl}"

                    # dfx.append(df, ignore_index = True)
                    dfx = pd.concat([dfx, df], axis=0)
                    # print(df)
            else:
                print(f"Bad Request: Missing: {jsonfile}")
    else:
        print(f"Bad Request: Missing: {latest}")

    # elomoji
    roji = {'All': '<:Epic:910268690098974740>', 'Legend': '<:Legend:910268716044914688>',
            'Mythic': '<:Mythic:910268741181374534>'}
    dfx['-'] = dfx['elo'].map(roji)

    return dfx
    print(f"Combined:{dfx}")
    # log.debug(f"{dfx}")
    # endregion

# endregion

# region API Functions


def heroesgen():
    jsonfile = APIpath + herofile

    if os.path.exists(jsonfile):
        print("Requesting: " + jsonfile)
        logging.info("Requesting: " + jsonfile)

        ##### BUILD LOOKUP TABLES ####
        with open(jsonfile) as j:
            data = json.load(j)

            df = json_normalize(data, ['data'])
            df = df[df.hero_name != 'None']



            #CONCISE FILTER
            dfh = df[["hero_name","mlid","uid","hero_icon","discordmoji","portrait","laning","class"]]
            #print(dfh)

            ### get hero list (replaces heroes.py)
            hlist = df['hero_name'].tolist()
            #print(list)

            ### get hero portraits (replaces heroicons.py)
            portrait = df.set_index('uid')['portrait'].to_dict()
            #print(portrait)

            ### generate lane groups (replaces laning.py)
            class laning:
                for lane in lanes:
                    lane = str(lane)

                    #dfl = df[df['laning'].str.contains(lane, na = False)]
                    #dfl = dfl[["hero_name"]]
                    dfl = df.set_index('laning').filter(like=lane, axis=0)
                    dfl = dfl[["hero_name"]]
                    # fix punctuation
                    dfl = dfl.replace(['Chang-e'], 'Chang\'e')
                    dfl = dfl.replace(['X-Borg'], 'X.Borg')
                    dfl = dfl.replace(['Yi Sun-Shin'], 'Yi Sun-shin')

                    #print(f"{lane}:{dfl}")

                    if lane == "gold":
                        gold = dfl['hero_name'].tolist()
                    if lane == "mid":
                        mid = dfl['hero_name'].tolist()
                    if lane == "roam":
                        roam = dfl['hero_name'].tolist()
                    if lane == "exp":
                        exp = dfl['hero_name'].tolist()
                    if lane == "jungle":
                        jungle = dfl['hero_name'].tolist()
            #print(laning)

            ### get hero moji (replaces mojimap.py)
            moji = df.set_index('uid')['discordmoji'].to_dict()
            #print(moji)

            ### generate role groups (replaces roles.py)
            class roles:
                for role in prof:
                    role = str(role)
                    role = role.capitalize()

                    dfr = df.set_index('class').filter(like=role, axis=0)
                    dfr = dfr[["hero_name"]]
                    # fix punctuation
                    dfr = dfr.replace(['Chang-e'], 'Chang\'e')
                    dfr = dfr.replace(['X-Borg'], 'X.Borg')
                    dfr = dfr.replace(['Yi Sun-Shin'], 'Yi Sun-shin')

                    #print(f"{role}:{dfr}")

                    if role == "Fighter":
                        fighter = dfr['hero_name'].tolist()
                    if role == "Tank":
                        tank = dfr['hero_name'].tolist()
                    if role == "Support":
                        support = dfr['hero_name'].tolist()
                    if role == "Assassin":
                        assassin = dfr['hero_name'].tolist()
                    if role == "Marksman":
                        marksman = dfr['hero_name'].tolist()
                    if role == "Mage":
                        mage = dfr['hero_name'].tolist()



            #return list, portrait, moji, gold, mid, roam, exp, jungle, fighter, tank, support, assassin, marksman, mage
            return hlist, portrait, moji, laning, roles

# endregion

#hlist, portrait, moji, laning, roles = heroesgen()
#print(hlist)
#print(getattr(laning,'gold'))
#print(getattr(roles,'fighter'))