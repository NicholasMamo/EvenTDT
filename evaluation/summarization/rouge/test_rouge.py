"""
Transform the CSV file into ROUGE files.
"""

import csv
import os
import re
import shutil
import sys

from pyrouge import Rouge155

SRC = "/home/memonick/evaluation/summarization/rouge/src"
OUT = "/home/memonick/evaluation/summarization/rouge/out"
MACHINE = "machine"
REFERENCE = "reference"
BASELINE = "baseline"
FMMR = "fmmr"
GRAPH = "graph"

header_lines = 2
machine_summaries = []
reference_summaries = []

def evaluate(name):
	r = Rouge155(rouge_dir="/home/memonick/.pyrouge/", log_level=0)
	r.system_dir = os.path.join(OUT, name, MACHINE)
	r.model_dir = os.path.join(OUT, name, REFERENCE)
	r.model_filename_pattern = "[A-Z].#ID#.txt"
	r.system_filename_pattern = "(\d+).txt"
	output = r.convert_and_evaluate()
	output_dict = r.output_to_dict(output)
	print("p: %.4f\tr: %.4f\tf1: %.4f" % (
		output_dict["rouge_1_precision"],
		output_dict["rouge_1_recall"],
		output_dict["rouge_1_f_score"]))

evaluate("test")
