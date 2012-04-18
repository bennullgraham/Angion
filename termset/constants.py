from decimal import Decimal

# amount to vary terms by if mutating. 0.1 = +/- 10%.
MUTE_VARIABILITY = Decimal(0.1)

NUM_MUTE_TERMS = 3

# chance to add new terms to a term set
CREATE_TERM_CHANCE = Decimal(0.1)

# chance to delete a term
DELETE_TERM_CHANCE = Decimal(0.1)
