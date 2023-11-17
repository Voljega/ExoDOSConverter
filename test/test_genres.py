# Tester file for genre metadata mapping

import pandas as pd
from logger import Logger
from metadatahandler import MetadataHandler
from genre_mapping import GENRE_MAPPER
from util import buildCache
from tabulate import tabulate

logger = Logger()

exo_folder = r'Z:\\'
collection = 'eXoDOS v6'

def buildGenre_old(dosGame):
    if dosGame is not None and dosGame.genres is not None:
        if 'Flight Simulator' in dosGame.genres or 'Vehicle Simulation' in dosGame.genres:
            return 'Simulation'
        elif "Education" in dosGame.genres or "Quiz" in dosGame.genres:
            if "Adventure" in dosGame.genres or "Visual Novel" in dosGame.genres:
                return "Adventure-Visual"
            else:
                return 'Misc'
        elif "Racing" in dosGame.genres or "Driving" in dosGame.genres or "Racing / Driving" in dosGame.genres:
            return "Racing"
        elif 'Sports' in dosGame.genres:
            return 'Sports'
        elif 'Pinball' in dosGame.genres:
            return 'Pinball'
        elif "Puzzle" in dosGame.genres or "Board" in dosGame.genres or "Board / Party Game" in dosGame.genres \
                or "Casino" in dosGame.genres or 'Cards / Tiles' in dosGame.genres or 'Game Show' in dosGame.genres:
            return "Puzzle"
        elif 'Shooter' in dosGame.genres:
            return 'ShootEmUp'
        elif 'Platform' in dosGame.genres:
            return 'Platform'
        elif 'FPS' in dosGame.genres or 'First Person Shooter' in dosGame.genres:
            return 'Gun-FPS'
        elif 'Fighting' in dosGame.genres or 'Beat \'em Up' in dosGame.genres:
            return 'BeatEmUp'
        elif 'Strategy' in dosGame.genres and "Puzzle" not in dosGame.genres:
            return 'Strategy-Gestion'
        elif 'RPG' in dosGame.genres or 'Role-Playing' in dosGame.genres:
            return 'RPG'
        elif 'Interactive Fiction' in dosGame.genres:
            return "Adventure-Visual"
        elif "Adventure" in dosGame.genres and "Action" in dosGame.genres:
            return "Action-Adventure"
        elif "Adventure" in dosGame.genres or "Visual Novel" in dosGame.genres:
            return "Adventure-Visual"
        elif 'Simulation' in dosGame.genres and 'Managerial' in dosGame.genres:
            return 'Strategy-Gestion'
        elif 'Construction and Management Simulation' in dosGame.genres:
            return 'Strategy-Gestion'
        elif 'Simulation' in dosGame.genres:
            return 'Simulation'
        elif 'Shooter' in dosGame.genres:
            return 'ShootEmUp'
        elif 'Action' in dosGame.genres:
            return 'Action-Adventure'
        elif 'Arcade' in dosGame.genres or 'Life Simulation' in dosGame.genres:
            return 'Misc'
        elif 'Creativity' in dosGame.genres or 'App' in dosGame.genres or 'Reference' in dosGame.genres:
            return 'Tools'
        else:
            return 'Unknown'
    else:
        return 'Unknown'
            

# takes a while in the first run. 
# can be skipped by commenting out the use of self.cache in parseXmlMetadata
cache = buildCache('.\\', exo_folder, collection, logger)

mdh = MetadataHandler(exo_folder, collection, cache, logger)
data = mdh.parseXmlMetadata()

if len(data) == 0:
    raise ValueError("Unable to load metadata, exiting")

result = []
for name in data:
    game = data[name]
    oldGenre = buildGenre_old(game)
    newGenre = mdh.buildGenre(game, dict())
    genres = sorted([g.strip() for g in list(set(game.genres))])
    if oldGenre != newGenre:
        if 'Interactive Movie' in genres:
            continue
        if oldGenre not in ['Sports', 'Strategy-Gestion', 'Racing']:
            result.append( (name, str(genres), oldGenre, newGenre))

df = pd.DataFrame(result, columns=['name', 'exo', 'old', 'new'])
df.to_csv(r'.\game_genres_compare.csv')

print(tabulate(df, tablefmt='psql'))



