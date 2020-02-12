#!/bin/bash

# Go to the script directory.
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
source variables.sh

usage() {
	echo -e "${HIGHLIGHT}Usage: sh $0 [-t <apd|nlp|graph|queue|summarization|topics|vector|wikipedia>]"${DEFAULT};
}

apd_tests() {
	echo -e "${HIGHLIGHT}APD${DEFAULT}"

	echo -e "${HIGHLIGHT}Extractor${DEFAULT}"
	python3 -m unittest eventdt.apd.extractors.local.tests.test_entity_extractor
	python3 -m unittest eventdt.apd.extractors.local.tests.test_token_extractor

	echo -e "${HIGHLIGHT}Scorer${DEFAULT}"
	python3 -m unittest eventdt.apd.scorers.local.tests.test_df_scorer
	python3 -m unittest eventdt.apd.scorers.local.tests.test_log_df_scorer
	python3 -m unittest eventdt.apd.scorers.local.tests.test_tf_scorer
	python3 -m unittest eventdt.apd.scorers.local.tests.test_log_tf_scorer
	python3 -m unittest eventdt.apd.scorers.local.tests.test_tfidf_scorer

	# echo -e "${HIGHLIGHT}Resolver${DEFAULT}"
	# python3 -m unittest eventdt.apd.resolvers.local.tests.test_local_resolvers
	# python3 -m unittest eventdt.apd.resolvers.external.tests.test_external_resolvers
	# echo -e "${HIGHLIGHT}Extrapolator${DEFAULT}"
	# python3 -m unittest eventdt.apd.extrapolators.external.tests.test_external_extrapolators
	# echo -e "${HIGHLIGHT}Postprocessor${DEFAULT}"
	# python3 -m unittest eventdt.apd.postprocessors.external.tests.test_external_postprocessors
	return
}

nlp_tests() {
	echo -e "${HIGHLIGHT}Term-weighting schemes${DEFAULT}"
	python3 -m unittest eventdt.nlp.term_weighting.local_schemes.tests.test_boolean
	python3 -m unittest eventdt.nlp.term_weighting.local_schemes.tests.test_tf
	python3 -m unittest eventdt.nlp.term_weighting.global_schemes.tests.test_idf
	python3 -m unittest eventdt.nlp.term_weighting.global_schemes.tests.test_filler
	python3 -m unittest eventdt.nlp.term_weighting.tests.test_tfidf
	python3 -m unittest eventdt.nlp.term_weighting.tests.test_tf

	echo -e "${HIGHLIGHT}Document${DEFAULT}"
	python3 -m unittest eventdt.nlp.tests.test_document

	echo -e "${HIGHLIGHT}Tokenizer${DEFAULT}"
	python3 -m unittest eventdt.nlp.tests.test_tokenizer

	return
}

graph_tests() {
	# echo -e "${HIGHLIGHT}Graph${DEFAULT}"
	# python3 -m unittest eventdt.graph.tests.test_graph
	return
}

queue_tests() {
	# echo -e "${HIGHLIGHT}Queue${DEFAULT}"
	#
	# echo -e "${HIGHLIGHT}Base Queue${DEFAULT}"
	# python3 -m unittest eventdt.queues.tests.test_queue
	#
	# echo -e "${HIGHLIGHT}Filter${DEFAULT}"
	# python3 -m unittest eventdt.queues.consumer.filter.tests.test_filter
	return
}

summarization_tests() {
	# echo -e "${HIGHLIGHT}Summarization${DEFAULT}"
	#
	# python3 -m unittest eventdt.summarization.tests.test_summary
	#
	# python3 -m unittest eventdt.summarization.algorithms.tests.test_mmr
	# python3 -m unittest eventdt.summarization.algorithms.tests.test_graph
	#
	# echo -e "${HIGHLIGHT}Scorer${DEFAULT}"
	# python3 -m unittest eventdt.summarization.scorers.tests.test_scorers
	#
	# echo -e "${HIGHLIGHT}Cleaning${DEFAULT}"
	# python3 -m unittest eventdt.vsm.nlp.cleaners.tests.test_cleaners
	return
}

topic_detection_tests() {
# 	echo -e "${HIGHLIGHT}Topic Detection${DEFAULT}"
#
# 	echo -e "${HIGHLIGHT}Memory Nutrition Store${DEFAULT}"
# 	python3 -m unittest eventdt.topic_detection.nutrition_store.tests.test_memory_nutrition_store
#
# 	echo -e "${HIGHLIGHT}Algorithms${DEFAULT}"
#
# 	echo -e "${HIGHLIGHT}${DEFAULT}"
# 	echo -e "${HIGHLIGHT}Mamo Algorithms${DEFAULT}"
# 	python3 -m unittest eventdt.topic_detection.algorithms.tests.test_mamo
#
# 	echo -e "${HIGHLIGHT}${DEFAULT}"
# 	echo -e "${HIGHLIGHT}Cataldi Algorithms${DEFAULT}"
# 	python3 -m unittest eventdt.topic_detection.algorithms.tests.test_cataldi
#
# 	echo -e "${HIGHLIGHT}${DEFAULT}"
# 	echo -e "${HIGHLIGHT}Zhao Algorithms${DEFAULT}"
# 	python3 -m unittest eventdt.topic_detection.algorithms.tests.test_zhao
	return
}

vector_tests() {
	# echo -e "${HIGHLIGHT}Vector${DEFAULT}"
	# python3 -m unittest eventdt.vsm.tests.test_attributable

	echo -e "${HIGHLIGHT}Vectors${DEFAULT}"
	python3 -m unittest eventdt.vsm.tests.test_vector

	echo -e "${HIGHLIGHT}Vector math${DEFAULT}"
	python3 -m unittest eventdt.vsm.tests.test_vector_math

	echo -e "${HIGHLIGHT}Clusters${DEFAULT}"
	python3 -m unittest eventdt.vsm.clustering.tests.test_cluster

	# echo -e "${HIGHLIGHT}Algorithms${DEFAULT}"
	# python3 -m unittest eventdt.vsm.cluster.algorithms.tests.test_no_k_means
}

wikipedia_tests() {
	# echo -e "${HIGHLIGHT}Wikipedia${DEFAULT}"
	#
	# echo -e "${HIGHLIGHT}Link Collector${DEFAULT}"
	# python3 -m unittest eventdt.wikinterface.tests.test_linkcollector
	return
}

if getopts "t:" o
then
	case "${OPTARG}" in
		apd)
			apd_tests
			;;
		nlp)
			nlp_tests
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
			echo -e "${ERROR}Invalid argument${DEFAULT}"
			usage
			;;
	esac
else
	apd_tests
	nlp_tests
	graph_tests
	queue_tests
	topic_detection_tests
	vector_tests
	wikipedia_tests
fi
