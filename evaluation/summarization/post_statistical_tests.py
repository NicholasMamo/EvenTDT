from scipy import stats

"""
Precision
"""

msm_p1 = {
	"FMMR Baseline": [0.1144, 0.1055, 0.1439, 0.1764, 0.2428, 0.1623],
	"FMMR": [0.1455, 0.1393, 0.2172, 0.1648, 0.2321, 0.1897],
	"Graph Baseline": [0.1177, 0.1064, 0.162, 0.1707, 0.2765, 0.1688],
	"Graph": [0.1841, 0.1807, 0.2208, 0.2054, 0.3539, 0.2231],
}

twitter_p1 = {
	"FMMR Baseline": [0.0694, 0.0893, 0.0401, 0.0926, 0.1822, 0.1595],
	"FMMR": [0.0872, 0.1258, 0.062, 0.0926, 0.2254, 0.1692],
	"Graph Baseline": [0.0735, 0.0866, 0.0388, 0.0992, 0.1816, 0.176],
	"Graph": [0.1147, 0.157, 0.0585, 0.098, 0.3417, 0.249],
}

msm_p2 = {
	"FMMR Baseline": [0.0303, 0.0169, 0.0393, 0.0472, 0.0622, 0.0512],
	"FMMR": [0.0223, 0.0154, 0.0662, 0.041, 0.0538, 0.0278],
	"Graph Baseline": [0.0328, 0.0169, 0.0386, 0.0457, 0.0749, 0.0521],
	"Graph": [0.0485, 0.0284, 0.0671, 0.0467, 0.0824, 0.0559],
}

twitter_p2 = {
	"FMMR Baseline": [0.0175, 0.0223, 0.0143, 0.0354, 0.0929, 0.0862],
	"FMMR": [0.0211, 0.0242, 0.023, 0.043, 0.0882, 0.0668],
	"Graph Baseline": [0.0188, 0.0214, 0.0138, 0.0395, 0.0895, 0.0966],
	"Graph": [0.0242, 0.0358, 0.0156, 0.0365, 0.1378, 0.1094],
}

"""
Recall
"""

msm_r1 = {
	"FMMR Baseline": [0.1746, 0.1904, 0.1583, 0.1873, 0.351, 0.2809],
	"FMMR": [0.2154, 0.2288, 0.1995, 0.2011, 0.3344, 0.2967],
	"Graph Baseline": [0.1742, 0.1904, 0.1605, 0.1892, 0.4119, 0.3084],
	"Graph": [0.25, 0.2341, 0.212, 0.2188, 0.3166, 0.3271],
}

twitter_r1 = {
	"FMMR Baseline": [0.1705, 0.2235, 0.1646, 0.2236, 0.4491, 0.3553],
	"FMMR": [0.2326, 0.2257, 0.2488, 0.2513, 0.3965, 0.3501],
	"Graph Baseline": [0.1763, 0.2139, 0.1841, 0.2542, 0.4424, 0.4143],
	"Graph": [0.2555, 0.241, 0.252, 0.2535, 0.4166, 0.3595],
}

msm_r2 = {
	"FMMR Baseline": [0.0395, 0.0349, 0.0548, 0.0441, 0.1077, 0.1284],
	"FMMR": [0.0348, 0.0312, 0.0787, 0.0457, 0.0798, 0.0914],
	"Graph Baseline": [0.0403, 0.0349, 0.0553, 0.0433, 0.1297, 0.1388],
	"Graph": [0.0559, 0.0368, 0.0647, 0.0479, 0.0808, 0.1342],
}

twitter_r2 = {
	"FMMR Baseline": [0.0414, 0.065, 0.0677, 0.0843, 0.2333, 0.1884],
	"FMMR": [0.0638, 0.044, 0.1094, 0.106, 0.1534, 0.168],
	"Graph Baseline": [0.0447, 0.0624, 0.0777, 0.105, 0.2225, 0.2243],
	"Graph": [0.0586, 0.0689, 0.093, 0.094, 0.1678, 0.1373],
}

"""
F1
"""

msm_f1 = {
	"FMMR Baseline": [0.1224, 0.1243, 0.1431, 0.1673, 0.2688, 0.1796],
	"FMMR": [0.1599, 0.1651, 0.186, 0.1702, 0.2698, 0.2072],
	"Graph Baseline": [0.1225, 0.1249, 0.1408, 0.1654, 0.3109, 0.1899],
	"Graph": [0.1659, 0.1868, 0.2064, 0.1848, 0.3269, 0.233],
}

twitter_f1 = {
	"FMMR Baseline": [0.0958, 0.1246, 0.0636, 0.1264, 0.2569, 0.2062],
	"FMMR": [0.1205, 0.1556, 0.0961, 0.1328, 0.2817, 0.2235],
	"Graph Baseline": [0.1006, 0.1202, 0.0623, 0.1373, 0.2553, 0.2315],
	"Graph": [0.1423, 0.1786, 0.0882, 0.1299, 0.3658, 0.2796],
}

msm_f2 = {
	"FMMR Baseline": [0.031, 0.0211, 0.043, 0.044, 0.0787, 0.0585],
	"FMMR": [0.0249, 0.0202, 0.0621, 0.042, 0.0635, 0.0348],
	"Graph Baseline": [0.0317, 0.0211, 0.0432, 0.0426, 0.0948, 0.0606],
	"Graph": [0.0368, 0.0293, 0.0629, 0.0419, 0.0798, 0.0651],
}

twitter_f2 = {
	"FMMR Baseline": [0.0239, 0.0329, 0.0235, 0.0488, 0.132, 0.1076],
	"FMMR": [0.0304, 0.0299, 0.0374, 0.06, 0.1102, 0.0935],
	"Graph Baseline": [0.0258, 0.0316, 0.0232, 0.0556, 0.1268, 0.1232],
	"Graph": [0.0317, 0.0435, 0.0246, 0.0498, 0.148, 0.1156],
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

print("P1")
print("MSM")
test("FMMR", "FMMR Baseline", msm_p1)
test("Graph", "Graph Baseline", msm_p1)

print()
print("Twitter")
test("FMMR", "FMMR Baseline", twitter_p1)
test("Graph", "Graph Baseline", twitter_p1)

print()
print("P2")
print("MSM")
test("FMMR Baseline", "FMMR", msm_p2)
test("Graph", "Graph Baseline", msm_p2)

print()
print("Twitter")
test("FMMR", "FMMR Baseline", twitter_p2)
test("Graph", "Graph Baseline", twitter_p2)

print()
print("-----------")
print()

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
test("FMMR Baseline", "FMMR", msm_r2)
test("Graph Baseline", "Graph", msm_r2)

print()
print("Twitter")
test("FMMR Baseline", "FMMR", twitter_r2)
test("Graph Baseline", "Graph", twitter_r2)



print()
print("-----------")
print()

print("F1")
print("MSM")
test("FMMR", "FMMR Baseline", msm_f1)
test("Graph", "Graph Baseline", msm_f1)

print()
print("Twitter")
test("FMMR", "FMMR Baseline", twitter_f1)
test("Graph", "Graph Baseline", twitter_f1)

print()
print("F2")
print("MSM")
test("FMMR Baseline", "FMMR", msm_f2)
test("Graph", "Graph Baseline", msm_f2)

print()
print("Twitter")
test("FMMR Baseline", "FMMR", twitter_f2)
test("Graph", "Graph Baseline", twitter_f2)
