from scipy import stats

recall = {
	"APD": [0.4878, 0.4634, 0.4146, 0.4634, 0.1951, 0.4146],
	"Baseline": [0.3171, 0.2683, 0.3171, 0.3171, 0.2195, 0.2195],
}

precision = {
	"APD": [0.4286, 0.4762, 0.3778, 0.4681, 0.1905, 0.34],
	"Baseline": [0.38, 0.24, 0.3, 0.34, 0.26, 0.22],
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

print("Recall")
test("APD", "Baseline", recall)

print()
print("Precision")
test("APD", "Baseline", precision)
