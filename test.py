from solution.models import Solution
s = Solution()
s.save()

for n in range(1, 20):
	s.mutate()
	s.plot.draw(n)


