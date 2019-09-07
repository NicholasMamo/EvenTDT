"""
Transform the CSV file into ROUGE files.
"""

import csv
import os
import re
import shutil
import sys

from nltk.corpus import stopwords
from pyrouge import Rouge155

path = os.path.dirname(__file__)
path = os.path.join(path, "../../../libraries")
if path not in sys.path:
	sys.path.insert(1, path)

from vector.nlp.cleaners import tweet_cleaner

SRC = "/home/memonick/evaluation/summarization/rouge/src"
OUT = "/home/memonick/evaluation/summarization/rouge/out"
MACHINE = "machine"
REFERENCE = "reference"
BASELINE = "fbaseline"
GRAPH_BASELINE = "gbaseline"
FMMR = "fmmr"
GRAPH = "graph"

header_lines = 2
machine_summaries = []
reference_summaries = []

sentence_splitter = re.compile("[!.?]+")

def evaluate(name, type):
	r = Rouge155(rouge_dir="/home/memonick/.pyrouge/", log_level=0)
	r.system_dir = os.path.join(OUT, name, MACHINE)
	r.model_dir = os.path.join(OUT, name, REFERENCE)
	r.model_filename_pattern = "[A-Z].#ID#.txt"
	# NOTE: Only existing files are used in the evaluation (compare T1_LIVNAP.csv and T2_LIVNAP.csv).
	#		In T1, when an entire summary is removed, the result improves (the summary contributed below average).
	#		In T2, when that same summary is removed with bogus text, it is considered (it is no longer empty), which brings the average down because there is no overlap (hence, bogus text).
	r.system_filename_pattern = "%s.(\d+).txt" % type
	output = r.convert_and_evaluate(split_sentences=True) # makes no difference
	# print(output)
	output_dict = r.output_to_dict(output)
	print("%s\t%.4f\t%.4f\t%.4f" %
		(type[:2].upper(), output_dict["rouge_1_precision"], output_dict["rouge_1_recall"], output_dict["rouge_1_f_score"]))
	print("\t%.4f\t%.4f\t%.4f" %
		(output_dict["rouge_2_precision"], output_dict["rouge_2_recall"], output_dict["rouge_2_f_score"]))
	# print("\t%.4f\t%.4f\t%.4f" %
	# 	(output_dict["rouge_l_precision"], output_dict["rouge_l_recall"], output_dict["rouge_l_f_score"]))
	# print("\t%.4f\t%.4f\t%.4f" %
	# 	(output_dict["rouge_su*_precision"], output_dict["rouge_su*_recall"], output_dict["rouge_su*_f_score"]))

cleaner = tweet_cleaner.TweetCleaner()
if len(sys.argv) == 2:
	fullname = sys.argv[1]
	name = fullname[:fullname.index('.')]

	if os.path.isdir(os.path.join(OUT, name)):
		shutil.rmtree(os.path.join(OUT, name))
	os.mkdir(os.path.join(OUT, name))
	os.mkdir(os.path.join(OUT, name, MACHINE))
	os.mkdir(os.path.join(OUT, name, REFERENCE))

	with open(os.path.join(SRC, fullname), "r") as s:
		csv_reader = csv.reader(s, delimiter=',')
		for i, line in enumerate(csv_reader):
			if i > (header_lines - 1): # skip the headers
				base, gbaseline, fmmr, graph = line[:4]
				references = tuple(line[4:])
				if any(len(col) > 0 for col in references): # if there is a reference
				# if not any(len(col) == 0 for col in line):
					machine_summaries.append((base, gbaseline, fmmr, graph))
					reference_summaries.append(references)

	lengths = { "BF": [], "BG": [], "F": [], "G": [] }
	for i, (fbaseline, gbaseline, fmmr, graph) in enumerate(machine_summaries[:]):
		if len(fbaseline) > 0:
			with open(os.path.join(OUT, name, MACHINE, "%s.%s.txt" % (BASELINE, str(i + 1))), "w") as b:
				# print("B", i, len(cleaner.clean(fbaseline)))
				lengths["BF"].append(len(cleaner.clean(fbaseline).split()))
				b.write(cleaner.clean(fbaseline))

		if len(gbaseline) > 0:
			with open(os.path.join(OUT, name, MACHINE, "%s.%s.txt" % (GRAPH_BASELINE, str(i + 1))), "w") as b:
				# print("BG", i, len(cleaner.clean(fbaseline)))
				lengths["BG"].append(len(cleaner.clean(gbaseline).split()))
				b.write(cleaner.clean(gbaseline))

		if len(fmmr) > 0:
			with open(os.path.join(OUT, name, MACHINE, "%s.%s.txt" % (FMMR, str(i + 1))), "w") as f:
				# print("F", i, len(fmmr))
				lengths["F"].append(len(fmmr.split()))
				f.write(fmmr)

		if len(graph) > 0:
			with open(os.path.join(OUT, name, MACHINE, "%s.%s.txt" % (GRAPH, str(i + 1))), "w") as g:
				# print("G", i, len(graph))
				lengths["G"].append(len(graph.split()))
				g.write(graph)

	for l in ["BF", "F", "BG", "G"]:
		print("%s: %.2f words" % (l, sum(lengths[l])/len(lengths[l])))

	reference_names = ["G", "A", "S"]
	punctuation_pattern = re.compile("[!\.\?,]")
	for i, references in enumerate(reference_summaries[:]):
		# print(len(list(filter(lambda reference: len(reference) > 0, references))))
		for j, reference in enumerate(references):
			reference = cleaner.clean(reference)
			# reference = punctuation_pattern.sub("", reference)
			if len(reference) > 0 and len([ word for word in reference.lower().split() if word not in stopwords.words("english") ]) > 1: # > 1 due to references like "Here we go!"
				with open(os.path.join(OUT, name, REFERENCE, "%s.%s.txt" % (reference_names[j], str(i + 1))), "w") as r:
					r.write(reference)

	print("", "P", "R", "F1", sep="\t")
	evaluate(name, BASELINE)
	evaluate(name, FMMR)
	evaluate(name, GRAPH_BASELINE)
	evaluate(name, GRAPH)
