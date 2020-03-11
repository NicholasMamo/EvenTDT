#!/bin/bash

# Go to the script directory.
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
source variables.sh

usage() {
	echo -e "${HIGHLIGHT}Usage: sh $0 [-t <apd|base|nlp|queue|summarization|tdt|vector|wikipedia>]"${DEFAULT};
}

apd_tests() {
	echo -e "${HIGHLIGHT}APD${DEFAULT}"

	echo -e "${HIGHLIGHT}Extractors${DEFAULT}"
	python3 -m unittest eventdt.apd.extractors.local.tests.test_entity_extractor
	python3 -m unittest eventdt.apd.extractors.local.tests.test_token_extractor

	echo -e "${HIGHLIGHT}Scorers${DEFAULT}"
	python3 -m unittest eventdt.apd.scorers.local.tests.test_df_scorer
	python3 -m unittest eventdt.apd.scorers.local.tests.test_log_df_scorer
	python3 -m unittest eventdt.apd.scorers.local.tests.test_tf_scorer
	python3 -m unittest eventdt.apd.scorers.local.tests.test_log_tf_scorer
	python3 -m unittest eventdt.apd.scorers.local.tests.test_tfidf_scorer

	echo -e "${HIGHLIGHT}Filters${DEFAULT}"
	python3 -m unittest eventdt.apd.filters.local.tests.test_threshold_filter

	echo -e "${HIGHLIGHT}Resolvers${DEFAULT}"
	python3 -m unittest eventdt.apd.resolvers.local.tests.test_token_resolver
	python3 -m unittest eventdt.apd.resolvers.external.tests.test_wikipedia_name_resolver
	python3 -m unittest eventdt.apd.resolvers.external.tests.test_wikipedia_search_resolver

	echo -e "${HIGHLIGHT}Extrapolators${DEFAULT}"
	python3 -m unittest eventdt.apd.extrapolators.external.tests.test_wikipedia_extrapolator

	echo -e "${HIGHLIGHT}Postprocessors${DEFAULT}"
	python3 -m unittest eventdt.apd.postprocessors.external.tests.test_wikipedia_postprocessor

	echo -e "${HIGHLIGHT}Participant detectors${DEFAULT}"
	python3 -m unittest eventdt.apd.tests.test_ner_participant_detector
}

base_tests() {
	echo -e "${HIGHLIGHT}Attributable${DEFAULT}"
	python3 -m unittest eventdt.objects.tests.test_attributable
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

queue_tests() {
	echo -e "${HIGHLIGHT}Queue${DEFAULT}"
	python3 -m unittest eventdt.queues.queue.tests.test_queue
}

summarization_tests() {
	echo -e "${HIGHLIGHT}Summarization${DEFAULT}"

	python3 -m unittest eventdt.summarization.tests.test_summary

	echo -e "${HIGHLIGHT}Algorithms${DEFAULT}"
	python3 -m unittest eventdt.summarization.algorithms.tests.test_mmr
	python3 -m unittest eventdt.summarization.algorithms.tests.test_dgs

	echo -e "${HIGHLIGHT}Timeline${DEFAULT}"
	echo -e "${HIGHLIGHT}Nodes${DEFAULT}"
	python3 -m unittest eventdt.summarization.timeline.nodes.tests.test_document_node

	# echo -e "${HIGHLIGHT}Scorer${DEFAULT}"
	# python3 -m unittest eventdt.summarization.scorers.tests.test_scorers
	#
	# echo -e "${HIGHLIGHT}Cleaning${DEFAULT}"
	# python3 -m unittest eventdt.vsm.nlp.cleaners.tests.test_cleaners
	return
}

topic_detection_tests() {
	echo -e "${HIGHLIGHT}Topic Detection${DEFAULT}"

	echo -e "${HIGHLIGHT}Memory Nutrition Store${DEFAULT}"
	python3 -m unittest eventdt.tdt.nutrition.tests.test_memory_nutrition_store

	echo -e "${HIGHLIGHT}Algorithms${DEFAULT}"
	python3 -m unittest eventdt.tdt.algorithms.tests.test_cataldi
	python3 -m unittest eventdt.tdt.algorithms.tests.test_zhao
	python3 -m unittest eventdt.tdt.algorithms.tests.test_eld
}

vector_tests() {
	echo -e "${HIGHLIGHT}Vectors${DEFAULT}"
	python3 -m unittest eventdt.vsm.tests.test_vector

	echo -e "${HIGHLIGHT}Vector math${DEFAULT}"
	python3 -m unittest eventdt.vsm.tests.test_vector_math

	echo -e "${HIGHLIGHT}Clusters${DEFAULT}"
	python3 -m unittest eventdt.vsm.clustering.tests.test_cluster

	echo -e "${HIGHLIGHT}Clustering algorithms${DEFAULT}"
	python3 -m unittest eventdt.vsm.clustering.algorithms.tests.test_no_k_means
	python3 -m unittest eventdt.vsm.clustering.algorithms.tests.test_temporal_no_k_means
}

wikipedia_tests() {
	echo -e "${HIGHLIGHT}Wikipedia${DEFAULT}"

	python3 -m unittest eventdt.wikinterface.tests.test_info
	python3 -m unittest eventdt.wikinterface.tests.test_links
	python3 -m unittest eventdt.wikinterface.tests.test_package
	python3 -m unittest eventdt.wikinterface.tests.test_search
	python3 -m unittest eventdt.wikinterface.tests.test_text
}

if getopts "t:" o
then
	case "${OPTARG}" in
		apd)
			apd_tests
			;;
		base)
			base_tests
			;;
		nlp)
			nlp_tests
			;;
		queue)
			queue_tests
			;;
		summarization)
			summarization_tests
			;;
		tdt)
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
	base_tests
	nlp_tests
	graph_tests
	queue_tests
	summarization_tests
	topic_detection_tests
	vector_tests
	wikipedia_tests
fi
