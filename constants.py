##################
# Function terms #
##################

# 0 -> 1 chance a term will be mutated at all
MUTE_CHANCE = 0.5

# amount to vary terms by if mutating. 0.1 = +/- 10%.
MUTE_VARIABILITY = 0.5

# scaled pos/neg adjustements aren't repeatable (e.g. 20 -10% + 10% =/= 20)
# so we need a positive bias to adjust for it
MUTE_POSITIVE_BIAS = 1.0 / ((1 - MUTE_VARIABILITY) ** 2)

NUM_MUTE_TERMS = 1

# maximum terms in a termset
MAX_TERMS = 3

# chance to add new terms to a term set
CREATE_TERM_CHANCE = 0.0005

# chance to delete a term (multiplied by number of terms)
DELETE_TERM_CHANCE = 0.0005


##################
# Branching      #
##################
# how many segments has each point?
BRANCH_SEGMENTS = 2

# split into BRANCHING_FACTOR segments every BRANCH_DISTANCEth point
BRANCH_DISTANCE = 3

# Hard limit at this depth
RECURSION_LIMIT = 25

##################
# Plotting       #
##################

PLOT_SIZE = 1024
PLOT_MARGIN = 64
ORIGIN_X = PLOT_SIZE / 2.0
ORIGIN_Y = PLOT_SIZE / 2.0


##################
# Fitness test   #
##################

# spacing of grid used to check how well-covered the area is.
SERVICE_GRID_SPACING = 32
