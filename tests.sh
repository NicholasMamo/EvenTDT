#!/bin/bash

# to run sh tests.sh [-t <vector|document|wikipedia>]

usage() {
	echo "Usage: sh $0 [-t <apd|document|graph|queue|summarization|topics|vector|wikipedia>]";
}

apd_tests() {
	# echo "=========="
	# echo "APD"
	# echo "=========="
	#
	# echo "----------"
	# echo "Extractor"
	# echo "----------"
	# python3 -m unittest eventdt.apd.extractors.local.tests.test_local_extractors
	# echo "----------"
	# echo "Scorer"
	# echo "----------"
	# python3 -m unittest eventdt.apd.scorers.local.tests.test_local_scorers
	# echo "----------"
	# echo "Resolver"
	# echo "----------"
	# python3 -m unittest eventdt.apd.resolvers.local.tests.test_local_resolvers
	# python3 -m unittest eventdt.apd.resolvers.external.tests.test_external_resolvers
	# echo "----------"
	# echo "Extrapolator"
	# echo "----------"
	# python3 -m unittest eventdt.apd.extrapolators.external.tests.test_external_extrapolators
	# echo "----------"
	# echo "Postprocessor"
	# echo "----------"
	# python3 -m unittest eventdt.apd.postprocessors.external.tests.test_external_postprocessors
	return
}

document_tests() {
	# echo "=========="
	# echo "Document"
	# echo "=========="
	#
	# echo "----------"
	# echo "Term Weighting"
	# echo "----------"
	# python3 -m unittest eventdt.vsm.nlp.tests.test_term_weighting
	#
	# echo "----------"
	# echo "Document"
	# echo "----------"
	# python3 -m unittest eventdt.vsm.nlp.tests.test_document
	#
	# echo "----------"
	# echo "Tokenizer"
	# echo "----------"
	# python3 -m unittest eventdt.vsm.nlp.tests.test_tokenizer
	#
	# echo "----------"
	# echo "Cleaning"
	# echo "----------"
	# python3 -m unittest eventdt.vsm.nlp.cleaners.tests.test_cleaners
	return
}

graph_tests() {
	# echo "=========="
	# echo "Graph"
	# echo "=========="
	# python3 -m unittest eventdt.graph.tests.test_graph
	return
}

queue_tests() {
	# echo "=========="
	# echo "Queue"
	# echo "=========="
	#
	# echo "----------"
	# echo "Base Queue"
	# echo "----------"
	# python3 -m unittest eventdt.queues.tests.test_queue
	#
	# echo "----------"
	# echo "Filter"
	# echo "----------"
	# python3 -m unittest eventdt.queues.consumer.filter.tests.test_filter
	return
}

summarization_tests() {
	# echo "=========="
	# echo "Summarization"
	# echo "=========="
	#
	# python3 -m unittest eventdt.summarization.tests.test_summary
	#
	# python3 -m unittest eventdt.summarization.algorithms.tests.test_mmr
	# python3 -m unittest eventdt.summarization.algorithms.tests.test_graph
	#
	# echo "----------"
	# echo "Scorer"
	# echo "----------"
	# python3 -m unittest eventdt.summarization.scorers.tests.test_scorers
	return
}

topic_detection_tests() {
# 	echo "=========="
# 	echo "Topic Detection"
# 	echo "=========="
#
# 	echo "----------"
# 	echo "Memory Nutrition Store"
# 	echo "----------"
# 	python3 -m unittest eventdt.topic_detection.nutrition_store.tests.test_memory_nutrition_store
#
# 	echo "----------"
# 	echo "Algorithms"
# 	echo "----------"
#
# 	echo ""
# 	echo "Mamo Algorithms"
# 	echo "----------"
# 	python3 -m unittest eventdt.topic_detection.algorithms.tests.test_mamo
#
# 	echo ""
# 	echo "Cataldi Algorithms"
# 	echo "----------"
# 	python3 -m unittest eventdt.topic_detection.algorithms.tests.test_cataldi
#
# 	echo ""
# 	echo "Zhao Algorithms"
# 	echo "----------"
# 	python3 -m unittest eventdt.topic_detection.algorithms.tests.test_zhao
	return
}

vector_tests() {
	# echo "=========="
	# echo "Vector"
	# echo "=========="
	# python3 -m unittest eventdt.vsm.tests.test_attributable

	echo "----------"
	echo "Vectors"
	echo "----------"
	python3 -m unittest eventdt.vsm.tests.test_vector

	# echo "----------"
	# echo "Vector Math"
	# echo "----------"
	# python3 -m unittest eventdt.vsm.tests.test_vector_math
	#
	# echo "----------"
	# echo "Clustering"
	# echo "----------"
	#
	# echo ""
	# echo "Base Cluster"
	# echo "----------"
	# python3 -m unittest eventdt.vsm.cluster.tests.test_cluster
	#
	# echo ""
	# echo "Algorithms"
	# echo "----------"
	# python3 -m unittest eventdt.vsm.cluster.algorithms.tests.test_no_k_means
}

wikipedia_tests() {
	# echo "=========="
	# echo "Wikipedia"
	# echo "=========="
	#
	# echo "----------"
	# echo "Link Collector"
	# echo "----------"
	# python3 -m unittest eventdt.wikinterface.tests.test_linkcollector
	return
}

if getopts "t:" o
then
	case "${OPTARG}" in
		apd)
			apd_tests
			;;
		document)
			document_tests
			;;
		graph)
			graph_tests
			;;
		queue)
			queue_tests
			;;
		summarization)
			summarization_tests
			;;
		topics)
			topic_detection_tests
			;;
		vector)
			vector_tests
			;;
		wikipedia)
			wikipedia_tests
			;;
		*)
			echo "Invalid argument"
			usage
			;;
	esac
else
	apd_tests
	document_tests
	graph_tests
	queue_tests
	topic_detection_tests
	vector_tests
	wikipedia_tests
fi
