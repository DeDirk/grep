# Display settings
WINDOW = {
    'WIDTH': 1200,
    'HEIGHT': 800,
    'FPS': 60
}

# Colors for rendering
COLORS = {
    'BLUE': (0, 0, 255),
    'WHITE': (255, 255, 255),
    'RED': (255, 0, 0),
    'OTHER_RED': (197, 0, 0),
    'BLACK': (0, 0, 0),
    'GREEN': (0, 255, 0),
    'GRAY': (128, 128, 128),
    'DARKGREY': (64, 64, 64),
    'YELLOW': (255, 255, 0),
    'PURPLE': (128, 0, 128),
    'DARK_PURPLE': (64, 0, 64),
    'PROJECTILE': (0, 0, 0),
}

# Player configuration
PLAYER = {
    'RADIUS': 10,
    'MOVEMENT': {
        'BASE_SPEED': 5,
        'SPRINT_MULTIPLIER': 2.0,
        'ACCELERATION': 1,
        'DECELERATION': 1,
    },
    'HEALTH': {
        'MAX': 60,
        'DAMAGE_PER_FRAME': 1,
    },
    'STAMINA': {
        'MAX': 180,
        'RECOVERY_RATE': 0.1,
        'EXHAUSTION_THRESHOLD': 0.3,
        'BAR': {
            'FADE_TIME': 30,
            'WIDTH': 40,
            'HEIGHT': 5,
            'OFFSET_Y': 10,
        }
    },
    'PROJECTILE': {
        'RADIUS': 2,
        'SPEED': 15,
        'COLOR': COLORS['BLACK'],
        'INACCURACY': 0.1,
        'VARIATION': 0.1,
    }
}

# Enemy configuration
ENEMY = {
    'RADIUS': 50,
    'HEALTH': {
        'PHASE_1': 1000,
        'PHASE_2': 1000,
        'PHASE_3': 1000,
    },
    'MOVEMENT': {
        'BASE_SPEED': 6,
        'ACCELERATION': 2,
        'DECELERATION': 2,
        'DASH_SPEED': 13,
        'SLOW_SPEED': 3,
        'SWEEP': {
            'AMPLITUDE': 6,
            'FREQUENCY': 0.1,
            'SPEED': 0.5,
        },
        'DASH': {
            'DURATION': 500,
            'PAUSE_DURATION': 700,
            'SPEED': 12,
        },
    },
    'PROJECTILE': {
        'BASIC': {
            'RADIUS': 20,
            'SPEED': 15,
            'COLOR': COLORS['RED'],
            'DAMAGE_PER_FRAME': 1,
            'SHRINK_RATE': 0.8,
            'MIN_SIZE': 1,
        },
        'PHASE_TWO': {
            'RADIUS': 30,
            'SPEED': 4,
            'COLOR': COLORS['DARK_PURPLE'],
            'DAMAGE_PER_FRAME': 8,
            'SHRINK_RATE': 0.9,
            'MIN_SIZE': 2,
        },
        'PREDICTIVE': {
            'RADIUS': 25,
            'SPEED': 10,
            'COLOR': COLORS['PURPLE'],
            'DAMAGE_PER_FRAME': 10,
            'SHRINK_RATE': 0.85,
            'MIN_SIZE': 1,
        }
    },
    'WALL_INTERACTION': {
        'SLOWDOWN_FACTOR': 0.001,
    },
    'PHASE_TRANSITION': {
        'DURATION': 1500,
    }
}

# Camera settings
CAMERA = {
    'LERP_SPEED': 0.1,
    'DEADZONE': 100,
}
# Item settings
ITEMS = {
    'SPAWN': {
        'CHANCE': 0.02,
        'MIN_DISTANCE': 500,  # Minimum distance between items
    },
    'LIFETIME': 20000,  # 20 seconds in milliseconds
    'STAMINA_RESTORE': 0.5,  # 50% of max stamina
}

# Level Generation settings
LEVEL = {
    'ROOM': {
        'MIN_SIZE': 150,
        'SPAWN_SIZE': 750,
    },
    'WALL': {
        'THICKNESS': 15,
        'GAP_SIZE': 60,
    },
    'GENERATION': {
        'MAX_DEPTH': 2,
        'SPLIT_CHANCE': 0.3,
        'CHUNK_RADIUS': 2,
        'GAPS_PER_WALL': {
            'MIN': 1,
            'MAX': 1,
        }
    },
    'CHUNK_GENERATION_RADIUS': 2,
    'GAP_SIZE': 60,
    'SPLIT_CHANCE': 0.3,
}

# Controller configuration
CONTROLLER = {
    'BUTTONS': {
        'A': 0,
        'B': 1,
        'X': 2,
        'Y': 3,
        'BACK': 4,
        'GUIDE': 5,
        'START': 6,
        'LEFTSTICK': 7,
        'RIGHTSTICK': 8,
        'LEFTBUMPER': 9,
        'RIGHTBUMPER': 10,
    },
    'ACTIONSDS4': {
        'SHOOT': 'RIGHTBUMPER',
        'SPRINT': 'LEFTBUMPER',
        'ACTION': 'X',
        'MENU': 'START'
    },
    # These names are not correct, need to fix structure so it works for both controllers
    'ACTIONS360': {
        'SHOOT': 'GUIDE',
        'SPRINT': 'BACK',
        'ACTION': 'X',
        'MENU': 'LEFTSTICK'
    },
    'INPUT': {
        'STICK_DEADZONE': 0.01,
    },
    'RUMBLE': {
        'DURATION': 10,
        'LOW_FREQ_MIN': 0.1,
        'LOW_FREQ_MAX': 0.5,
        'HIGH_FREQ': 0.0,
    },
    'DEBUG': False
}

EFFECTS = {
    'BOOST': {
        'PARTICLE_COUNT': 5,
        'LIFETIME': (10, 20),
        'SPEED': (2, 5),
        'SPREAD': 45,  # degrees
    },
    'WALL_HIT': {
        'PARTICLE_COUNT': (5, 10),
        'LIFETIME': (15, 25),
        'SPEED': (3, 6),
        'SPREAD': 90,  # degrees
    },
    'PHASE_CHANGE': {
        'PARTICLE_COUNT': 100,
        'LIFETIME': 200,
        'INWARD_DELAY': 20,
    },
    'MOVEMENT_CHANGE': {
        'PARTICLE_COUNT': 24,
        'LIFETIME': 30,
        'SPEED': 4,
    }
}
