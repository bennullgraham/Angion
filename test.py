from solution.models import Solution, Plot
fittest = Solution()
fittest.prime()
fittest.save()

for i in range(0, 10):
    solutions = [fittest.copy() for n in range(0, 10)]
    solutions = map(lambda s: s.mutate(), solutions)
    solutions.append(fittest)
    fittest = max(solutions, key=lambda s: s.fitness())
    print "lap {lap}, fitness = {fitness}".format(lap=i, fitness=fittest.fitness())
    p = Plot(fittest)
    p.draw(i)


