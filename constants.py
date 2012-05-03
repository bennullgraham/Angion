# amount to vary terms by if mutating. 0.1 = +/- 10%.
MUTE_VARIABILITY = 1.5

# scaled pos/neg adjustements aren't repeatable (e.g. 20 -10% + 10% =/= 20)
# so we need a positive bias to adjust for it
MUTE_POSITIVE_BIAS = 1.0 / ((1 - MUTE_VARIABILITY) ** 2)

NUM_MUTE_TERMS = 1

# maximum terms in a termset
MAX_TERMS = 3

# chance to add new terms to a term set
CREATE_TERM_CHANCE = 0.005

# chance to delete a term (multiplied by number of terms)
DELETE_TERM_CHANCE = 0.0005

# how many segments has each point?
BRANCHING_FACTOR = 2

# how much to scale down multipliers if an overflow occurs
OVERFLOW_REDUCTION_DIVISOR = 2

PLOT_SIZE = 512

PLOT_MARGIN = 64

ORIGIN_X = PLOT_SIZE / 2
ORIGIN_Y = PLOT_SIZE / 2

RECURSION_LIMIT = 18

# spacing of grid used to check how well-covered the area is
SERVICE_GRID_SPACING = 16
