from solution.models import Solution, Plot
fittest = Solution()
fittest.prime()
fittest.save()
last_fit = 0
this_fit = 0
for i in range(100):
    for j in range(10):
        print "lap {lap}.{sublap}".format(lap=i, sublap=j),
        solutions = [fittest.copy() for n in range(10)]
        solutions = map(lambda s: s.mutate(), solutions)
        # solutions.append(fittest)
        fittest = max(solutions, key=lambda s: s.fitness())
        last_fit = this_fit
        this_fit = fittest.fitness()
        change = 0 if last_fit == 0 else (this_fit / last_fit) - 1
        print "fitness = {fitness} ({improvement:+.2%})".format(lap=i, fitness=this_fit, improvement=change)
    p = Plot(fittest)
    p.draw(i)


