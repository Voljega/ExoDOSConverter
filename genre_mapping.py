from enum import Enum

class Genre(Enum):
    # the target genres we want to map to
    UNKNOWN             = "Unknown"
    MISC                = "Misc"
    ACTION_ADVENTURE    = "Action-Adventure"
    ADVENTURE_VISUAL    = "Adventure-Visual"
    BEATEMUP            = "BeatEmUp"
    FPS                 = "Gun-FPS"
    PINBALL             = "Pinball"
    PLATFORM            = "Platform"
    PUZZLE              = "Puzzle"
    RACING              = "Racing"
    RPG                 = "RPG"
    SIMULATION          = "Simulation"
    SHMUP               = "ShootEmUp"
    SPORTS              = "Sport"
    STRATEGY_MANAGEMENT = "Strategy-Management"
    TOOLS               = "Tools"

# defines direct mappings (i.e. if match, return the value)
GENRE_MAPPER = {
    'Action':               Genre.ACTION_ADVENTURE,
    'Adventure':            Genre.ADVENTURE_VISUAL,
    'App':                  Genre.TOOLS,
    'Arcade':               Genre.MISC,
    'Beat \'em Up':         Genre.BEATEMUP,
    'Board / Party Game':   Genre.PUZZLE,
    'Board':                Genre.PUZZLE,
    'Cards / Tiles':        Genre.PUZZLE,
    'Casino':               Genre.PUZZLE,
    'Construction and Management Simulation': Genre.STRATEGY_MANAGEMENT,
    'Creativity':           Genre.TOOLS,
    'Driving':              Genre.RACING,
    'FPS':                  Genre.FPS,
    'Fighting':             Genre.BEATEMUP,
    'First Person Shooter': Genre.FPS,
    'Flight Simulator':     Genre.SIMULATION,
    'Game Show':            Genre.PUZZLE,
    'Interactive Fiction':  Genre.ADVENTURE_VISUAL,
    'Interactive Movie':     Genre.ADVENTURE_VISUAL,
    'Life Simulation':      Genre.MISC,
    'Managerial':           Genre.STRATEGY_MANAGEMENT,
    'Pinball':              Genre.PINBALL,
    'Platform':             Genre.PLATFORM,
    'Puzzle':               Genre.PUZZLE,
    'RPG':                  Genre.RPG,
    'Racing / Driving':     Genre.RACING,
    'Racing':               Genre.RACING,
    'Reference':            Genre.TOOLS,    
    'Role-Playing':         Genre.RPG,
    'Paddle / Pong':        Genre.ACTION_ADVENTURE,
    'Shooter':              Genre.SHMUP,
    'Simulation':           Genre.SIMULATION,
    'Sports':               Genre.SPORTS,
    'Strategy':             Genre.STRATEGY_MANAGEMENT,
    'Text-Based':           Genre.ADVENTURE_VISUAL,
    'Vehicle Simulation':   Genre.SIMULATION,
    'Visual Novel':         Genre.ADVENTURE_VISUAL,
}    

# as above, but applies for combined genres (used for overides)
MULTI_GENRE_MAPPER = {
    "['Action', 'Arcade']":                   Genre.ACTION_ADVENTURE,
    "['Action', 'Adventure']":                Genre.ACTION_ADVENTURE,
    "['Action', 'Adventure', 'Fighting']":    Genre.BEATEMUP,
    "['Action', 'Adventure', 'Platform']":    Genre.PLATFORM,
    "['Action', 'Adventure', 'Text-Based']":  Genre.ACTION_ADVENTURE,
    "['Action', 'Adventure', 'Simulation']":  Genre.ACTION_ADVENTURE,
    "['Action', 'Fighting', 'Role-Playing']": Genre.BEATEMUP,
    "['Action', 'Platform', 'Role-Playing']": Genre.PLATFORM,
    "['Action', 'Adventure', 'Shooter']":     Genre.SHMUP,
    "['Action', 'Adventure', 'Platform', 'Puzzle']": Genre.PUZZLE,
    "['Action', 'Fighting', 'Shooter']":      Genre.SHMUP,
    "['Action', 'Fighting', 'Platform']":     Genre.PLATFORM,
    "['Action', 'Platform', 'Shooter']":      Genre.SHMUP,
    "['Action', 'Role-Playing', 'Shooter']":  Genre.SHMUP,
    "['Action', 'Adventure', 'Platform', 'Shooter']": Genre.SHMUP,
    "['Adventure', 'Fighting']":              Genre.BEATEMUP,
    "['Adventure', 'Platform']":              Genre.PLATFORM,
    "['Adventure', 'Simulation']":            Genre.ADVENTURE_VISUAL,
    "['Arcade', 'Paddle / Pong']":            Genre.MISC,
    "['Board / Party Game', 'Role-Playing']": Genre.PUZZLE,
    "['Board / Party Game', 'Role-Playing', 'Strategy']": Genre.PUZZLE,
    "['Platform', 'Shooter']":                Genre.SHMUP, 
}

# Convert multi genres exo collection format to a single one
def mapGenres(input_genres):
    # list unique genres and sort them - precedence is alphabetical unless overridden
    # (e.g. "Managerial" + "Simulation" -> "Managerial")
    genres = sorted([g.strip() for g in list(set(input_genres))])

    # first check for  multi-genre overrides
    if str(genres) in MULTI_GENRE_MAPPER:
        return MULTI_GENRE_MAPPER.get(str(genres)).value
    
    # classifies about ~90 games, the simulation aspect is more prominent
    if 'Vehicle Simulation' in genres or 'Flight Simulator' in genres:
        return Genre.SIMULATION.value  
        
    # recategorize education games
    if 'Education' in genres or 'Quiz' in genres:
        if 'Adventure' in genres or 'Visual Novel' in genres:
            return Genre.ADVENTURE_VISUAL.value
        return Genre.MISC.value
    
    # debatable, affects only a few games but usually the FPS aspect is more prominent than the rest
    if 'First Person Shooter' in genres:
        return Genre.FPS.value

    # RPG takes precedence over adventure and others for ~60 games
    if 'RPG' in genres or 'Role-Playing' in genres:
        return Genre.RPG.value
    
    # puzzle takes precedence for ~50 games e.g. lrunn2, jetpack, oddworld
    if 'Puzzle' in genres:
        return Genre.PUZZLE.value
    
    # from here on, ignore 'Action' or 'Arcade' if there are subgenres defined, 
    # otherwise they always take precedence
    if len(genres) > 1 and genres[0] == 'Action':
        genres.pop(0)
    if len(genres) > 1 and genres[0] == 'Arcade':
        genres.pop(0)
    
    # returns the first genre found, alphabetically
    for genre in genres:
        output = GENRE_MAPPER.get(genre, Genre.UNKNOWN)
        if output != Genre.UNKNOWN:
            return output.value
    
    # fallback - there are probably no genres defined (or Exo added a new genre name)
    return Genre.UNKNOWN.value
