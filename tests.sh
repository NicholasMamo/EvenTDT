#!/bin/bash

# Go to the script directory.
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
source variables.sh
source venv/bin/activate

usage() {
	echo -e "${HIGHLIGHT}Usage: sh $0 [-t <apd|ate|base|nlp|queue|summarization|tdt|twitter|vector|wikipedia>]"${DEFAULT};
}

apd_tests() {
	echo -e "${HIGHLIGHT}APD${DEFAULT}"

	echo -e "${HIGHLIGHT}Extractors${DEFAULT}"
	python3 -m unittest eventdt.apd.extractors.local.tests.test_twitterner_entity_extractor
	python3 -m unittest eventdt.apd.extractors.local.tests.test_entity_extractor
	python3 -m unittest eventdt.apd.extractors.local.tests.test_token_extractor

	echo -e "${HIGHLIGHT}Scorers${DEFAULT}"
	python3 -m unittest eventdt.apd.scorers.local.tests.test_df_scorer
	python3 -m unittest eventdt.apd.scorers.local.tests.test_log_df_scorer
	python3 -m unittest eventdt.apd.scorers.local.tests.test_tf_scorer
	python3 -m unittest eventdt.apd.scorers.local.tests.test_log_tf_scorer
	python3 -m unittest eventdt.apd.scorers.local.tests.test_tfidf_scorer

	echo -e "${HIGHLIGHT}Filters${DEFAULT}"
	python3 -m unittest eventdt.apd.filters.local.tests.test_rank_filter
	python3 -m unittest eventdt.apd.filters.local.tests.test_threshold_filter

	echo -e "${HIGHLIGHT}Resolvers${DEFAULT}"
	python3 -m unittest eventdt.apd.resolvers.tests.test_resolver
	python3 -m unittest eventdt.apd.resolvers.local.tests.test_token_resolver
	python3 -m unittest eventdt.apd.resolvers.external.tests.test_wikipedia_name_resolver
	python3 -m unittest eventdt.apd.resolvers.external.tests.test_wikipedia_search_resolver

	echo -e "${HIGHLIGHT}Extrapolators${DEFAULT}"
	python3 -m unittest eventdt.apd.extrapolators.external.tests.test_wikipedia_extrapolator

	echo -e "${HIGHLIGHT}Postprocessors${DEFAULT}"
	python3 -m unittest eventdt.apd.postprocessors.external.tests.test_wikipedia_postprocessor

	echo -e "${HIGHLIGHT}Participant detectors${DEFAULT}"
	python3 -m unittest eventdt.apd.tests.test_ner_participant_detector
	python3 -m unittest eventdt.apd.tests.test_eld_participant_detector
}

ate_tests() {
	echo -e "${HIGHLIGHT}ATE${DEFAULT}"
	python3 -m unittest eventdt.ate.tests.test_package
	python3 -m unittest eventdt.ate.tests.test_extractor

	echo -e "${HIGHLIGHT}Application${DEFAULT}"
	python3 -m unittest eventdt.ate.application.tests.test_event

	echo -e "${HIGHLIGHT}Bootstrapping${DEFAULT}"
	python3 -m unittest eventdt.ate.bootstrapping.tests.test_package
	python3 -m unittest eventdt.ate.bootstrapping.probability.tests.test_chi
	python3 -m unittest eventdt.ate.bootstrapping.probability.tests.test_llratio
	python3 -m unittest eventdt.ate.bootstrapping.probability.tests.test_pmi

	echo -e "${HIGHLIGHT}Linguistic${DEFAULT}"
	python3 -m unittest eventdt.ate.linguistic.tests.test_package

	echo -e "${HIGHLIGHT}Statistical${DEFAULT}"
	python3 -m unittest eventdt.ate.stat.corpus.tests.test_package
	python3 -m unittest eventdt.ate.stat.corpus.tests.test_rank
	python3 -m unittest eventdt.ate.stat.corpus.tests.test_specificity
	python3 -m unittest eventdt.ate.stat.corpus.tests.test_tfdcf
	python3 -m unittest eventdt.ate.stat.probability.tests.test_package
	python3 -m unittest eventdt.ate.stat.tests.test_tf
	python3 -m unittest eventdt.ate.stat.tests.test_tfidf

	echo -e "${HIGHLIGHT}Concepts${DEFAULT}"
	python3 -m unittest eventdt.ate.concepts.tests.test_package
	python3 -m unittest eventdt.ate.concepts.tests.test_gnclustering
}

attribute_tests() {
	echo -e "${HIGHLIGHT}Attribute extraction${DEFAULT}"
	python3 -m unittest eventdt.attributes.tests.test_profile

	echo -e "${HIGHLIGHT}Extractors${DEFAULT}"
	python3 -m unittest eventdt.attributes.extractors.tests.test_linguistic
}

base_tests() {
	echo -e "${HIGHLIGHT}Attributable${DEFAULT}"
	python3 -m unittest eventdt.objects.tests.test_attributable

	echo -e "${HIGHLIGHT}Exportable${DEFAULT}"
	python3 -m unittest eventdt.objects.tests.test_exportable

	echo -e "${HIGHLIGHT}Ordered Enum${DEFAULT}"
	python3 -m unittest eventdt.objects.tests.test_ordered_enum
}

ml_tests() {
	echo -e "${HIGHLIGHT}Association rules${DEFAULT}"
	python3 -m unittest eventdt.ml.association.tests.test_package
	python3 -m unittest eventdt.ml.association.algo.tests.test_apriori
}

nlp_tests() {
	echo -e "${HIGHLIGHT}Term-weighting schemes${DEFAULT}"
	python3 -m unittest eventdt.nlp.weighting.local_schemes.tests.test_boolean
	python3 -m unittest eventdt.nlp.weighting.local_schemes.tests.test_tf
	python3 -m unittest eventdt.nlp.weighting.global_schemes.tests.test_idf
	python3 -m unittest eventdt.nlp.weighting.global_schemes.tests.test_filler
	python3 -m unittest eventdt.nlp.weighting.tests.test_tfidf
	python3 -m unittest eventdt.nlp.weighting.tests.test_tf

	echo -e "${HIGHLIGHT}Document${DEFAULT}"
	python3 -m unittest eventdt.nlp.tests.test_document

	echo -e "${HIGHLIGHT}Tokenizer${DEFAULT}"
	python3 -m unittest eventdt.nlp.tests.test_tokenizer

	echo -e "${HIGHLIGHT}Cleaners${DEFAULT}"
	python3 -m unittest eventdt.nlp.cleaners.tests.test_cleaner
	python3 -m unittest eventdt.nlp.cleaners.tests.test_tweet_cleaner

	return
}

queue_tests() {
	echo -e "${HIGHLIGHT}Queue${DEFAULT}"
	python3 -m unittest eventdt.queues.tests.test_queue

	echo -e "${HIGHLIGHT}Consumers${DEFAULT}"
	python3 -m unittest eventdt.queues.consumers.tests.test_buffered_consumer
	python3 -m unittest eventdt.queues.consumers.tests.test_filter_consumer
	python3 -m unittest eventdt.queues.consumers.tests.test_token_filter_consumer
	python3 -m unittest eventdt.queues.consumers.tests.test_print_consumer
	python3 -m unittest eventdt.queues.consumers.tests.test_split_consumer
	python3 -m unittest eventdt.queues.consumers.tests.test_token_split_consumer
	python3 -m unittest eventdt.queues.consumers.tests.test_stat_consumer
	python3 -m unittest eventdt.queues.consumers.algorithms.tests.test_eld_consumer
	python3 -m unittest eventdt.queues.consumers.algorithms.tests.test_fire_consumer
	python3 -m unittest eventdt.queues.consumers.algorithms.tests.test_fuego_consumer
	python3 -m unittest eventdt.queues.consumers.algorithms.tests.test_zhao_consumer
}

summarization_tests() {
	echo -e "${HIGHLIGHT}Summarization${DEFAULT}"

	python3 -m unittest eventdt.summarization.tests.test_summary

	echo -e "${HIGHLIGHT}Algorithms${DEFAULT}"
	python3 -m unittest eventdt.summarization.algorithms.tests.test_mmr
	python3 -m unittest eventdt.summarization.algorithms.tests.test_dgs

	echo -e "${HIGHLIGHT}Timeline${DEFAULT}"
	python3 -m unittest eventdt.summarization.timeline.tests.test_timeline

	echo -e "${HIGHLIGHT}Nodes${DEFAULT}"
	python3 -m unittest eventdt.summarization.timeline.nodes.tests.test_document_node
	python3 -m unittest eventdt.summarization.timeline.nodes.tests.test_cluster_node
	python3 -m unittest eventdt.summarization.timeline.nodes.tests.test_topical_cluster_node
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

tools_tests() {
	echo -e "${HIGHLIGHT}Tools${DEFAULT}"
	python3 -m unittest tools.tests.test_package

	echo -e "${HIGHLIGHT}Bootstrap${DEFAULT}"
	python3 -m unittest tools.tests.test_bootstrap

	echo -e "${HIGHLIGHT}Consumer${DEFAULT}"
	python3 -m unittest tools.tests.test_consume

	echo -e "${HIGHLIGHT}Correlation${DEFAULT}"
	python3 -m unittest tools.tests.test_correlation

	echo -e "${HIGHLIGHT}IDF${DEFAULT}"
	python3 -m unittest tools.tests.test_idf

	echo -e "${HIGHLIGHT}Participants${DEFAULT}"
	python3 -m unittest tools.tests.test_participants

	echo -e "${HIGHLIGHT}Summarization${DEFAULT}"
	python3 -m unittest tools.tests.test_summarize

	echo -e "${HIGHLIGHT}ATE${DEFAULT}"
	python3 -m unittest tools.tests.test_terms

	echo -e "${HIGHLIGHT}Shareable${DEFAULT}"
	python3 -m unittest tools.tests.test_shareable

	echo -e "${HIGHLIGHT}Tokenizer${DEFAULT}"
	python3 -m unittest tools.tests.test_tokenizer

	echo -e "${HIGHLIGHT}Evaluation${DEFAULT}"
	python3 -m unittest tools.evaluation.tests.test_package

	echo -e "${HIGHLIGHT}ATE${DEFAULT}"
	python3 -m unittest tools.evaluation.tests.test_ate
}

twitter_tests() {
	echo -e "${HIGHLIGHT}Twitter${DEFAULT}"
	python3 -m unittest eventdt.twitter.tests.test_package

	echo -e "${HIGHLIGHT}Listeners${DEFAULT}"
	python3 -m unittest eventdt.twitter.listeners.tests.test_tweet_listener
	python3 -m unittest eventdt.twitter.listeners.tests.test_queued_tweet_listener

	echo -e "${HIGHLIGHT}File Readers${DEFAULT}"
	python3 -m unittest eventdt.twitter.file.tests.test_simulated_reader
	python3 -m unittest eventdt.twitter.file.tests.test_staggered_reader

	echo -e "${HIGHLIGHT}Corpus${DEFAULT}"
	python3 -m unittest eventdt.twitter.corpus.tests.test_aggregate
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
		ate)
			ate_tests
			;;
		attributes)
		    attribute_tests
			;;
		base)
			base_tests
			;;
		ml)
			ml_tests
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
		tools)
			tools_tests
			;;
		twitter)
			twitter_tests
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
	ate_tests
	attribute_tests
	base_tests
	ml_tests
	nlp_tests
	queue_tests
	summarization_tests
	topic_detection_tests
	tools_tests
	twitter_tests
	vector_tests
	wikipedia_tests
fi
