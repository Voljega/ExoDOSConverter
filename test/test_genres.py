# Tester file for genre metadata mapping

import pandas as pd
from logger import Logger
from metadatahandler import MetadataHandler, GENRE_MAPPER
from tabulate import tabulate

logger = Logger()

exo_folder = r'Z:\\'

mdh = MetadataHandler(exo_folder, 'eXoDOS v5', False, logger)
data = mdh.parseXmlMetadata()

result = []
for name in data:
    game = data[name]
    oldGenre = '' # mdh.buildGenre_old(game) <-- uncomment and place old function to run side by side
    newGenre = mdh.buildGenre(game)
    genres = sorted([g.strip() for g in list(set(game.genres))])
    if oldGenre != newGenre:
        if 'Interactive Movie' in genres:
            continue
        if oldGenre not in ['Sports', 'Strategy-Gestion', 'Race']:
            result.append( (name, str(genres), oldGenre, newGenre) )

df = pd.DataFrame(result, columns=['name', 'exo', 'old', 'new'])
df.to_csv(r'.\game_genres_compare.csv')

print(tabulate(df, tablefmt='psql'))
