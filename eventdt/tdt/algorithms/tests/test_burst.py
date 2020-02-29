import math

s = 4
t = 5

print("Numerator")
num_sum = []
for c in range(t - s, t):
	print(c - (t - s))
	num_sum.append(c - (t - s))

print("Denominator")
denom_sum = []
for c in range(0, s):
	print(c)
	denom_sum.append(c)

print("Num sum:", sum([1/math.sqrt(math.exp(i)) for i in num_sum]))
print("Denom sum:", sum([1/math.sqrt(math.exp(i)) for i in denom_sum]))
