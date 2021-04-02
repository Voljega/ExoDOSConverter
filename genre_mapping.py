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
    "['Board / Party Game', 'Role-Playing', 'Strategy']": Genre.PUZZLE,
    "['Platform', 'Shooter']":                Genre.SHMUP, 
}
