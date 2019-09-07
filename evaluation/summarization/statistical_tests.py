from scipy import stats

msm_r1 = {
	"FMMR Baseline": [0.1746, 0.1903, 0.1583, 0.1672, 0.3258, 0.2809],
	"FMMR": [0.2251, 0.2399, 0.1939, 0.1792, 0.3443, 0.2666],
	"Graph Baseline": [0.1742, 0.184, 0.1605, 0.1694, 0.3816, 0.3084],
	"Graph": [0.2517, 0.2462, 0.22, 0.183, 0.3858, 0.3315],
}

twitter_r1 = {
	"FMMR Baseline": [0.1705, 0.2235, 0.1985, 0.2236, 0.4566, 0.3553],
	"FMMR": [0.2892, 0.2702, 0.2147, 0.2649, 0.49, 0.3509],
	"Graph Baseline": [0.1763, 0.2139, 0.1841, 0.2542, 0.4498, 0.4143],
	"Graph": [0.2785, 0.2787, 0.2659, 0.2337, 0.4813, 0.395],
}

msm_r2 = {
	"FMMR Baseline": [0.0395, 0.0349, 0.0548, 0.0378, 0.1077, 0.1284],
	"FMMR": [0.0444, 0.0342, 0.0753, 0.0496, 0.1182, 0.1085],
	"Graph Baseline": [0.0403, 0.0338, 0.0553, 0.0371, 0.1297, 0.1388],
	"Graph": [0.0522, 0.0408, 0.0688, 0.0451, 0.1118, 0.1359],
}

twitter_r2 = {
	"FMMR Baseline": [0.0414, 0.065, 0.0828, 0.0843, 0.2411, 0.1884],
	"FMMR": [0.0791, 0.0496, 0.101, 0.1218, 0.2673, 0.1879],
	"Graph Baseline": [0.0447, 0.0624, 0.0777, 0.105, 0.2303, 0.2243],
	"Graph": [0.0647, 0.0592, 0.093, 0.0972, 0.2151, 0.1628],
}

def ttest(after, before, array):
	print("\tT-Test")
	p = stats.ttest_rel(array[after], array[before]).pvalue/2
	print("\tp-value: %.4f" % (p))
	return p

def wilcoxon(after, before, array):
	print("\tWilcoxon")
	p = stats.wilcoxon(array[after], array[before]).pvalue/2
	print("\tp-value: %.4f" % (p))
	return p

def test(after, before, array, alpha=0.05, nalpha=0.05):
	print("%s - %s" % (
		after, before
	))
	n = len(array[after])
	differences = [ array[after][i] - array[before][i] for i in range(0, n) ]
	normal = stats.shapiro(differences)[1] > alpha
	print("\tnormalcy: %.4f" % stats.shapiro(differences)[1])
	if normal:
		p = ttest(after, before, array)
	else:
		p = wilcoxon(after, before, array)

	if p > 0.05:
		print("\t%s = %s" % (after, before))
	else:
		print("\t%s > %s" % (after, before))

print("R1")
print("MSM")
test("FMMR", "FMMR Baseline", msm_r1)
test("Graph", "Graph Baseline", msm_r1)

print()
print("Twitter")
test("FMMR", "FMMR Baseline", twitter_r1)
test("Graph", "Graph Baseline", twitter_r1)

print()
print("R2")
print("MSM")
test("FMMR", "FMMR Baseline", msm_r2)
test("Graph", "Graph Baseline", msm_r2)

print()
print("Twitter")
test("FMMR", "FMMR Baseline", twitter_r2)
test("Graph", "Graph Baseline", twitter_r2)
