def mutate((fractals)):
    for f in fractals:
        f.length_function.mutate()
        f.radiance_function.mutate()
        f.orientation_function.mutate()
        f.termination_function.mutate()
