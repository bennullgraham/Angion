from angion.generation import Generation

g = Generation()
while True:
    g.next_generation()

# from angion.fractal import Fractal
# from angion.expression import Expression
# from angion.solver import solve
# import angion.db as db

# f = Fractal()
# f.length_function = Expression()
# f.radiance_function = Expression()
# f.orientation_function = Expression()
# f.termination_function = Expression()

# db.create()
# db.inter(f)
# f = db.unearth(1)

# solve(f)
# print f.fitness
