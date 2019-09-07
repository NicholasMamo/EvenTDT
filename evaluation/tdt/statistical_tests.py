from scipy import stats

precision = {
	"Full FMMR": [0.9000, 0.8679, 0.7429, 0.8281, 0.7778, 0.8261],
	"APD FMMR": [0.7288, 0.7925, 0.6410, 0.8148, 0.7576, 0.7143],
	"FMMR": [0.6522, 0.8621, 0.8636, 0.8491, 0.8182, 0.7500],
	"Full Graph": [0.8833, 0.9107, 0.7429, 0.8730, 0.6765, 0.8000],
	"APD Graph": [0.8448, 0.7925, 0.8158, 0.7667, 0.6333, 0.7143],
	"Graph": [0.8478, 0.8710, 0.9048, 0.8200, 0.7500, 0.7917],
	"Full Baseline": [0.6667, 0.4118, 0.4878, 0.3333, 0.4118, 0.5946],
	"APD Baseline": [0.3636, 0.4500, 0.1333, 0.4444, 0.2647, 0.5161],
	"Baseline": [0.7895, 0.4571, 0.3333, 0.3462, 0.0958, 0.4795],
}

recall = {
	"Full FMMR": [0.6364, 0.7647, 0.4118, 0.6875, 0.4118, 0.7692],
	"APD FMMR": [0.6364, 0.7647, 0.3529, 0.8750, 0.4118, 0.7692],
	"FMMR": [0.4545, 0.5294, 0.3529, 0.7500, 0.2941, 0.4615],
	"Full Graph": [0.8182, 0.7059, 0.5294, 0.7500, 0.4706, 0.7692],
	"APD Graph": [0.7727, 0.7647, 0.5294, 0.7500, 0.4118, 0.7692],
	"Graph": [0.5000, 0.6471, 0.3529, 0.7500, 0.3529, 0.5385],
	"Full Baseline": [0.0909, 0.0588, 0.4706, 0.1250, 0.5294, 0.6923],
	"APD Baseline": [0.0909, 0.0588, 0.0588, 0.1875, 0.5882, 0.4615],
	"Baseline": [0.4091, 0.1765, 0.4118, 0.3125, 0.5882, 0.8462],
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

print("Precision")
test("Full FMMR", "APD FMMR", precision)
test("FMMR", "APD FMMR", precision)
test("Full Graph", "APD Graph", precision)
test("Graph", "APD Graph", precision)
test("Full Baseline", "APD Baseline", precision)
test("Baseline", "APD Baseline", precision)

print()
print("Recall")
test("Full FMMR", "APD FMMR", recall)
test("APD FMMR", "FMMR", recall)
test("Full Graph", "APD Graph", recall)
test("APD Graph", "Graph", recall)
test("Full Baseline", "APD Baseline", recall)
test("Baseline", "APD Baseline", recall)
