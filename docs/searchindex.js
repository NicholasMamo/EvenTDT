Search.setIndex({docnames:["apd","config","consumers","index","nlp","other","summarization","tdt","tools","twitter","vsm","wikinterface"],envversion:{"sphinx.domains.c":1,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":1,"sphinx.domains.javascript":1,"sphinx.domains.math":2,"sphinx.domains.python":1,"sphinx.domains.rst":1,"sphinx.domains.std":1,sphinx:56},filenames:["apd.rst","config.rst","consumers.rst","index.rst","nlp.rst","other.rst","summarization.rst","tdt.rst","tools.rst","twitter.rst","vsm.rst","wikinterface.rst"],objects:{"":{apd:[0,0,0,"-"],config:[1,0,0,"-"],logger:[5,0,0,"-"],nlp:[4,0,0,"-"],objects:[5,0,0,"-"],summarization:[6,0,0,"-"],tdt:[7,0,0,"-"],tools:[8,0,0,"-"],twitter:[9,0,0,"-"],vsm:[10,0,0,"-"],wikinterface:[11,0,0,"-"]},"apd.extractors":{extractor:[0,0,0,"-"]},"apd.extractors.extractor":{Extractor:[0,1,1,""]},"apd.extractors.extractor.Extractor":{__weakref__:[0,2,1,""],extract:[0,3,1,""]},"apd.extractors.local":{entity_extractor:[0,0,0,"-"],token_extractor:[0,0,0,"-"]},"apd.extractors.local.entity_extractor":{EntityExtractor:[0,1,1,""]},"apd.extractors.local.entity_extractor.EntityExtractor":{__init__:[0,3,1,""],_combine_adjacent_entities:[0,3,1,""],_extract_entities:[0,3,1,""],extract:[0,3,1,""]},"apd.extractors.local.token_extractor":{TokenExtractor:[0,1,1,""]},"apd.extractors.local.token_extractor.TokenExtractor":{__init__:[0,3,1,""],extract:[0,3,1,""]},"apd.extrapolators":{extrapolator:[0,0,0,"-"]},"apd.extrapolators.external":{wikipedia_extrapolator:[0,0,0,"-"]},"apd.extrapolators.external.wikipedia_extrapolator":{WikipediaExtrapolator:[0,1,1,""]},"apd.extrapolators.external.wikipedia_extrapolator.WikipediaExtrapolator":{__init__:[0,3,1,""],_add_to_graph:[0,3,1,""],_get_first_sentence:[0,3,1,""],_has_year:[0,3,1,""],_link_frequency:[0,3,1,""],_most_central_edge:[0,3,1,""],_remove_brackets:[0,3,1,""],extrapolate:[0,3,1,""]},"apd.extrapolators.extrapolator":{Extrapolator:[0,1,1,""]},"apd.extrapolators.extrapolator.Extrapolator":{__weakref__:[0,2,1,""],extrapolate:[0,3,1,""]},"apd.filters":{filter:[0,0,0,"-"]},"apd.filters.filter":{Filter:[0,1,1,""]},"apd.filters.filter.Filter":{__weakref__:[0,2,1,""],filter:[0,3,1,""]},"apd.filters.local":{threshold_filter:[0,0,0,"-"]},"apd.filters.local.threshold_filter":{ThresholdFilter:[0,1,1,""]},"apd.filters.local.threshold_filter.ThresholdFilter":{__init__:[0,3,1,""],filter:[0,3,1,""]},"apd.ner_participant_detector":{NERParticipantDetector:[0,1,1,""]},"apd.ner_participant_detector.NERParticipantDetector":{__init__:[0,3,1,""]},"apd.participant_detector":{ParticipantDetector:[0,1,1,""]},"apd.participant_detector.ParticipantDetector":{__init__:[0,3,1,""],__weakref__:[0,2,1,""],detect:[0,3,1,""]},"apd.postprocessors":{postprocessor:[0,0,0,"-"]},"apd.postprocessors.external":{wikipedia_postprocessor:[0,0,0,"-"]},"apd.postprocessors.external.wikipedia_postprocessor":{WikipediaPostprocessor:[0,1,1,""]},"apd.postprocessors.external.wikipedia_postprocessor.WikipediaPostprocessor":{__init__:[0,3,1,""],_get_surname:[0,3,1,""],_remove_accents:[0,3,1,""],_remove_brackets:[0,3,1,""],postprocess:[0,3,1,""]},"apd.postprocessors.postprocessor":{Postprocessor:[0,1,1,""]},"apd.postprocessors.postprocessor.Postprocessor":{__weakref__:[0,2,1,""],postprocess:[0,3,1,""]},"apd.resolvers":{resolver:[0,0,0,"-"]},"apd.resolvers.external":{wikipedia_name_resolver:[0,0,0,"-"],wikipedia_search_resolver:[0,0,0,"-"]},"apd.resolvers.external.wikipedia_name_resolver":{WikipediaNameResolver:[0,1,1,""]},"apd.resolvers.external.wikipedia_name_resolver.WikipediaNameResolver":{__init__:[0,3,1,""],_disambiguate:[0,3,1,""],_resolve_unambiguous_candidates:[0,3,1,""],resolve:[0,3,1,""]},"apd.resolvers.external.wikipedia_search_resolver":{WikipediaSearchResolver:[0,1,1,""]},"apd.resolvers.external.wikipedia_search_resolver.WikipediaSearchResolver":{__init__:[0,3,1,""],_compute_score:[0,3,1,""],_get_first_sentence:[0,3,1,""],_has_year:[0,3,1,""],_remove_brackets:[0,3,1,""],resolve:[0,3,1,""]},"apd.resolvers.local":{token_resolver:[0,0,0,"-"]},"apd.resolvers.local.token_resolver":{TokenResolver:[0,1,1,""]},"apd.resolvers.local.token_resolver.TokenResolver":{__init__:[0,3,1,""],_construct_inverted_index:[0,3,1,""],_minimize_inverted_index:[0,3,1,""],resolve:[0,3,1,""]},"apd.resolvers.resolver":{Resolver:[0,1,1,""]},"apd.resolvers.resolver.Resolver":{__weakref__:[0,2,1,""],resolve:[0,3,1,""]},"apd.scorers":{scorer:[0,0,0,"-"]},"apd.scorers.local":{df_scorer:[0,0,0,"-"],log_df_scorer:[0,0,0,"-"],log_tf_scorer:[0,0,0,"-"],tf_scorer:[0,0,0,"-"],tfidf_scorer:[0,0,0,"-"]},"apd.scorers.local.df_scorer":{DFScorer:[0,1,1,""]},"apd.scorers.local.df_scorer.DFScorer":{_normalize:[0,3,1,""],_sum:[0,3,1,""],score:[0,3,1,""]},"apd.scorers.local.log_df_scorer":{LogDFScorer:[0,1,1,""]},"apd.scorers.local.log_df_scorer.LogDFScorer":{__init__:[0,3,1,""],score:[0,3,1,""]},"apd.scorers.local.log_tf_scorer":{LogTFScorer:[0,1,1,""]},"apd.scorers.local.log_tf_scorer.LogTFScorer":{__init__:[0,3,1,""],score:[0,3,1,""]},"apd.scorers.local.tf_scorer":{TFScorer:[0,1,1,""]},"apd.scorers.local.tf_scorer.TFScorer":{_normalize:[0,3,1,""],_sum:[0,3,1,""],score:[0,3,1,""]},"apd.scorers.local.tfidf_scorer":{TFIDFScorer:[0,1,1,""]},"apd.scorers.local.tfidf_scorer.TFIDFScorer":{__init__:[0,3,1,""],_normalize:[0,3,1,""],score:[0,3,1,""]},"apd.scorers.scorer":{Scorer:[0,1,1,""]},"apd.scorers.scorer.Scorer":{__weakref__:[0,2,1,""],_normalize:[0,3,1,""],score:[0,3,1,""]},"config.example":{conf:[1,0,0,"-"]},"config.example.conf":{ACCOUNTS:[1,4,1,""],LOG_LEVEL:[1,4,1,""]},"logger.logger":{LogLevel:[5,1,1,""],error:[5,5,1,""],info:[5,5,1,""],log_time:[5,5,1,""],set_logging_level:[5,5,1,""],warning:[5,5,1,""]},"nlp.document":{Document:[4,1,1,""]},"nlp.document.Document":{__init__:[4,3,1,""],__str__:[4,3,1,""],concatenate:[4,3,1,""],copy:[4,3,1,""],from_array:[4,3,1,""],to_array:[4,3,1,""]},"nlp.term_weighting":{scheme:[4,0,0,"-"],tf:[4,0,0,"-"],tfidf:[4,0,0,"-"]},"nlp.term_weighting.global_schemes":{filler:[4,0,0,"-"],idf:[4,0,0,"-"]},"nlp.term_weighting.global_schemes.filler":{Filler:[4,1,1,""]},"nlp.term_weighting.global_schemes.filler.Filler":{score:[4,3,1,""]},"nlp.term_weighting.global_schemes.idf":{IDF:[4,1,1,""]},"nlp.term_weighting.global_schemes.idf.IDF":{__init__:[4,3,1,""],from_documents:[4,3,1,""],score:[4,3,1,""]},"nlp.term_weighting.local_schemes":{"boolean":[4,0,0,"-"],tf:[4,0,0,"-"]},"nlp.term_weighting.local_schemes.boolean":{Boolean:[4,1,1,""]},"nlp.term_weighting.local_schemes.boolean.Boolean":{score:[4,3,1,""]},"nlp.term_weighting.local_schemes.tf":{TF:[4,1,1,""]},"nlp.term_weighting.local_schemes.tf.TF":{score:[4,3,1,""]},"nlp.term_weighting.scheme":{SchemeScorer:[4,1,1,""],TermWeightingScheme:[4,1,1,""]},"nlp.term_weighting.scheme.SchemeScorer":{__weakref__:[4,2,1,""],score:[4,3,1,""]},"nlp.term_weighting.scheme.TermWeightingScheme":{__init__:[4,3,1,""],__weakref__:[4,2,1,""],create:[4,3,1,""]},"nlp.term_weighting.tf":{TF:[4,1,1,""]},"nlp.term_weighting.tf.TF":{__init__:[4,3,1,""]},"nlp.term_weighting.tfidf":{TFIDF:[4,1,1,""]},"nlp.term_weighting.tfidf.TFIDF":{__init__:[4,3,1,""]},"nlp.tokenizer":{Tokenizer:[4,1,1,""]},"nlp.tokenizer.Tokenizer":{__init__:[4,3,1,""],__weakref__:[4,2,1,""],_split_hashtags:[4,3,1,""],tokenize:[4,3,1,""]},"objects.attributable":{Attributable:[5,1,1,""]},"objects.attributable.Attributable":{__init__:[5,3,1,""],__weakref__:[5,2,1,""]},"objects.exportable":{Exportable:[5,1,1,""]},"objects.exportable.Exportable":{__weakref__:[5,2,1,""],from_array:[5,3,1,""],get_class:[5,3,1,""],get_module:[5,3,1,""],to_array:[5,3,1,""]},"queues.consumers":{buffered_consumer:[2,0,0,"-"],consumer:[2,0,0,"-"],print_consumer:[2,0,0,"-"]},"queues.consumers.buffered_consumer":{BufferedConsumer:[2,1,1,""],SimulatedBufferedConsumer:[2,1,1,""]},"queues.consumers.buffered_consumer.BufferedConsumer":{__init__:[2,3,1,""],_consume:[2,3,1,""],_process:[2,3,1,""],_sleep:[2,3,1,""],run:[2,3,1,""]},"queues.consumers.buffered_consumer.SimulatedBufferedConsumer":{__init__:[2,3,1,""],_sleep:[2,3,1,""]},"queues.consumers.consumer":{Consumer:[2,1,1,""]},"queues.consumers.consumer.Consumer":{__init__:[2,3,1,""],__weakref__:[2,2,1,""],_consume:[2,3,1,""],_wait_for_input:[2,3,1,""],run:[2,3,1,""],stop:[2,3,1,""]},"queues.consumers.print_consumer":{PrintConsumer:[2,1,1,""]},"queues.consumers.print_consumer.PrintConsumer":{_consume:[2,3,1,""]},"queues.queue":{Queue:[2,1,1,""]},"queues.queue.Queue":{__init__:[2,3,1,""],__weakref__:[2,2,1,""],dequeue:[2,3,1,""],dequeue_all:[2,3,1,""],empty:[2,3,1,""],enqueue:[2,3,1,""],head:[2,3,1,""],length:[2,3,1,""],tail:[2,3,1,""]},"summarization.algorithms":{dgs:[6,0,0,"-"],mmr:[6,0,0,"-"],summarization:[6,0,0,"-"]},"summarization.algorithms.dgs":{DGS:[6,1,1,""]},"summarization.algorithms.dgs.DGS":{_compute_query:[6,3,1,""],_extract_communities:[6,3,1,""],_filter_documents:[6,3,1,""],_largest_communities:[6,3,1,""],_most_central_edge:[6,3,1,""],_score_documents:[6,3,1,""],_to_graph:[6,3,1,""],summarize:[6,3,1,""]},"summarization.algorithms.mmr":{MMR:[6,1,1,""]},"summarization.algorithms.mmr.MMR":{__init__:[6,3,1,""],_compute_query:[6,3,1,""],_compute_scores:[6,3,1,""],_compute_similarity_matrix:[6,3,1,""],_filter_documents:[6,3,1,""],_get_next_document:[6,3,1,""],summarize:[6,3,1,""]},"summarization.algorithms.summarization":{SummarizationAlgorithm:[6,1,1,""]},"summarization.algorithms.summarization.SummarizationAlgorithm":{__weakref__:[6,2,1,""],summarize:[6,3,1,""]},"summarization.summary":{Summary:[6,1,1,""]},"summarization.summary.Summary":{__init__:[6,3,1,""],__str__:[6,3,1,""],documents:[6,3,1,""],from_array:[6,3,1,""],to_array:[6,3,1,""]},"summarization.timeline":{timeline:[6,0,0,"-"]},"summarization.timeline.nodes":{cluster_node:[6,0,0,"-"],document_node:[6,0,0,"-"],node:[6,0,0,"-"]},"summarization.timeline.nodes.cluster_node":{ClusterNode:[6,1,1,""]},"summarization.timeline.nodes.cluster_node.ClusterNode":{__init__:[6,3,1,""],add:[6,3,1,""],get_all_documents:[6,3,1,""],similarity:[6,3,1,""]},"summarization.timeline.nodes.document_node":{DocumentNode:[6,1,1,""]},"summarization.timeline.nodes.document_node.DocumentNode":{__init__:[6,3,1,""],add:[6,3,1,""],get_all_documents:[6,3,1,""],similarity:[6,3,1,""]},"summarization.timeline.nodes.node":{Node:[6,1,1,""]},"summarization.timeline.nodes.node.Node":{__init__:[6,3,1,""],__weakref__:[6,2,1,""],add:[6,3,1,""],expired:[6,3,1,""],get_all_documents:[6,3,1,""],similarity:[6,3,1,""]},"summarization.timeline.timeline":{Timeline:[6,1,1,""]},"summarization.timeline.timeline.Timeline":{__init__:[6,3,1,""],__weakref__:[6,2,1,""],_create:[6,3,1,""],add:[6,3,1,""]},"tdt.algorithms":{cataldi:[7,0,0,"-"],eld:[7,0,0,"-"],tdt:[7,0,0,"-"],zhao:[7,0,0,"-"]},"tdt.algorithms.cataldi":{Cataldi:[7,1,1,""]},"tdt.algorithms.cataldi.Cataldi":{__init__:[7,3,1,""],_compute_burst:[7,3,1,""],_compute_burst_drops:[7,3,1,""],_get_bursty_terms:[7,3,1,""],_get_critical_drop_index:[7,3,1,""],detect:[7,3,1,""]},"tdt.algorithms.eld":{ELD:[7,1,1,""]},"tdt.algorithms.eld.ELD":{__init__:[7,3,1,""],_compute_burst:[7,3,1,""],_compute_coefficient:[7,3,1,""],_compute_decay:[7,3,1,""],detect:[7,3,1,""]},"tdt.algorithms.tdt":{TDTAlgorithm:[7,1,1,""]},"tdt.algorithms.tdt.TDTAlgorithm":{__weakref__:[7,2,1,""],detect:[7,3,1,""]},"tdt.algorithms.zhao":{Zhao:[7,1,1,""]},"tdt.algorithms.zhao.Zhao":{__init__:[7,3,1,""],detect:[7,3,1,""]},"tdt.nutrition":{memory:[7,0,0,"-"],store:[7,0,0,"-"]},"tdt.nutrition.memory":{MemoryNutritionStore:[7,1,1,""]},"tdt.nutrition.memory.MemoryNutritionStore":{__init__:[7,3,1,""],add:[7,3,1,""],all:[7,3,1,""],between:[7,3,1,""],get:[7,3,1,""],remove:[7,3,1,""]},"tdt.nutrition.store":{NutritionStore:[7,1,1,""]},"tdt.nutrition.store.NutritionStore":{__init__:[7,3,1,""],__weakref__:[7,2,1,""],add:[7,3,1,""],all:[7,3,1,""],between:[7,3,1,""],get:[7,3,1,""],remove:[7,3,1,""],since:[7,3,1,""],until:[7,3,1,""]},"tools.collect":{collect:[8,5,1,""],main:[8,5,1,""],save_meta:[8,5,1,""],setup_args:[8,5,1,""]},"tools.consume":{consumer:[8,5,1,""],main:[8,5,1,""],setup_args:[8,5,1,""]},"twitter.listener":{TweetListener:[9,1,1,""]},"twitter.listener.TweetListener":{__init__:[9,3,1,""],filter:[9,3,1,""],flush:[9,3,1,""],on_data:[9,3,1,""],on_error:[9,3,1,""]},"vsm.clustering":{cluster:[10,0,0,"-"]},"vsm.clustering.algorithms":{clustering:[10,0,0,"-"],no_k_means:[10,0,0,"-"],temporal_no_k_means:[10,0,0,"-"]},"vsm.clustering.algorithms.clustering":{ClusteringAlgorithm:[10,1,1,""]},"vsm.clustering.algorithms.clustering.ClusteringAlgorithm":{__init__:[10,3,1,""],__weakref__:[10,2,1,""],cluster:[10,3,1,""]},"vsm.clustering.algorithms.no_k_means":{NoKMeans:[10,1,1,""]},"vsm.clustering.algorithms.no_k_means.NoKMeans":{__init__:[10,3,1,""],_closest_cluster:[10,3,1,""],_freeze:[10,3,1,""],_reset_age:[10,3,1,""],_to_freeze:[10,3,1,""],_update_age:[10,3,1,""],cluster:[10,3,1,""]},"vsm.clustering.algorithms.temporal_no_k_means":{TemporalNoKMeans:[10,1,1,""]},"vsm.clustering.algorithms.temporal_no_k_means.TemporalNoKMeans":{__init__:[10,3,1,""],_update_age:[10,3,1,""],cluster:[10,3,1,""]},"vsm.clustering.cluster":{Cluster:[10,1,1,""]},"vsm.clustering.cluster.Cluster":{__init__:[10,3,1,""],centroid:[10,3,1,""],from_array:[10,3,1,""],get_intra_similarity:[10,3,1,""],get_representative_vectors:[10,3,1,""],recalculate_centroid:[10,3,1,""],similarity:[10,3,1,""],size:[10,3,1,""],to_array:[10,3,1,""],vectors:[10,3,1,""]},"vsm.vector":{Vector:[10,1,1,""],VectorSpace:[10,1,1,""]},"vsm.vector.Vector":{__init__:[10,3,1,""],copy:[10,3,1,""],dimensions:[10,3,1,""],from_array:[10,3,1,""],normalize:[10,3,1,""],to_array:[10,3,1,""]},"vsm.vector.VectorSpace":{__getitem__:[10,3,1,""],__weakref__:[10,2,1,""]},"vsm.vector_math":{augmented_normalize:[10,5,1,""],concatenate:[10,5,1,""],cosine:[10,5,1,""],cosine_distance:[10,5,1,""],euclidean:[10,5,1,""],magnitude:[10,5,1,""],manhattan:[10,5,1,""],normalize:[10,5,1,""]},"wikinterface.info":{ArticleType:[11,1,1,""],is_person:[11,5,1,""],types:[11,5,1,""]},"wikinterface.links":{_get_all_links:[11,5,1,""],_get_intro_links:[11,5,1,""],collect:[11,5,1,""],collect_recursive:[11,5,1,""]},"wikinterface.search":{collect:[11,5,1,""]},"wikinterface.text":{collect:[11,5,1,""]},apd:{ner_participant_detector:[0,0,0,"-"],participant_detector:[0,0,0,"-"]},logger:{logger:[5,0,0,"-"]},nlp:{document:[4,0,0,"-"],term_weighting:[4,0,0,"-"],tokenizer:[4,0,0,"-"]},objects:{attributable:[5,0,0,"-"],exportable:[5,0,0,"-"]},queues:{queue:[2,0,0,"-"]},summarization:{summary:[6,0,0,"-"]},tools:{collect:[8,0,0,"-"],consume:[8,0,0,"-"]},twitter:{extract_timestamp:[9,5,1,""],listener:[9,0,0,"-"]},vsm:{vector:[10,0,0,"-"],vector_math:[10,0,0,"-"]},wikinterface:{API_ENDPOINT:[11,4,1,""],construct_url:[11,5,1,""],info:[11,0,0,"-"],is_error_response:[11,5,1,""],links:[11,0,0,"-"],revert_redirects:[11,5,1,""],search:[11,0,0,"-"],text:[11,0,0,"-"]}},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","attribute","Python attribute"],"3":["py","method","Python method"],"4":["py","data","Python data"],"5":["py","function","Python function"]},objtypes:{"0":"py:module","1":"py:class","2":"py:attribute","3":"py:method","4":"py:data","5":"py:function"},terms:{"abstract":[0,2,4,5,6,7,10],"boolean":[0,2,4,9,10,11],"break":7,"byte":[],"case":[0,2,4,7],"class":[0,2,3,4,6,7,8,9,10,11],"default":[0,6,7,8,9,10],"export":[4,5,6,10],"float":[0,2,6,7,10],"function":[0,2,4,5,6,7,9,10,11],"import":[4,5,7],"int":[0,1,2,4,7,8,9,10,11],"long":[2,10],"new":[0,2,4,5,6,10,11],"return":[0,2,4,5,6,7,8,9,10,11],"static":[4,5,6,10],"true":[0,2,4,9,11],"try":[0,7],"while":2,Aging:7,DGS:6,For:[0,4,6,7],Its:0,That:2,The:[0,1,2,4,5,6,7,8,9,10,11],Their:11,Then:[0,4,7],There:[0,2],These:[0,4,6,7,11],Use:6,__delattr__:[],__dir__:[],__eq__:[],__format__:[],__ge__:[],__getattribute__:[],__getitem__:10,__gt__:[],__hash__:[],__init__:[0,2,4,5,6,7,9,10],__init_subclass__:[],__le__:[],__lt__:[],__ne__:[],__new__:[],__reduce__:[],__reduce_ex__:[],__repr__:[],__setattr__:[],__sizeof__:[],__str__:[4,6],__subclasscheck__:[],__subclasshook__:[],__weakref__:[0,2,4,5,6,7,10],_add_to_graph:0,_closest_clust:10,_combine_adjacent_ent:0,_compute_burst:7,_compute_burst_drop:7,_compute_coeffici:7,_compute_decai:7,_compute_queri:6,_compute_scor:[0,6],_compute_similarity_matrix:6,_construct_inverted_index:0,_consum:2,_creat:6,_dimens:[],_disambigu:0,_extract_commun:6,_extract_ent:0,_filter_docu:6,_freez:10,_frozen_clust:[],_get_all_link:11,_get_bursty_term:7,_get_critical_drop_index:7,_get_first_sent:0,_get_intro_link:11,_get_next_docu:6,_get_surnam:0,_has_year:0,_how_:7,_largest_commun:6,_link_frequ:0,_minimize_inverted_index:0,_most_central_edg:[0,6],_normal:0,_process:2,_process_hashtag:[],_remove_acc:0,_remove_bracket:0,_reset_ag:10,_resolve_unambiguous_candid:0,_score_docu:6,_sleep:2,_split_hashtag:4,_sum:0,_to_freez:10,_to_graph:6,_update_ag:10,_wait_for_input:2,_what_:7,abc:[],abcmeta:[],about:[0,4,6,8,10,11],absorb:6,accent:[0,4],accept:[0,2,4,6,7,8],access:11,access_token:1,access_token_secret:1,accord:[0,4,6,7,11],account:[1,8],account_:[],accumul:[2,7,9,10],accur:[],across:0,activ:[2,6,10],actual:[0,4,6],add:[0,2,4,5,6,7,9],add_vector:[],added:[0,2,6,10,11],adding:10,addit:[0,4,5,8,10,11],adopt:[4,7],after:[0,2,7],age:10,aim:[0,10],algorithm:[0,3],all:[0,2,4,6,7,8,9,10],allow:2,almost:0,alon:7,alreadi:[6,11],also:[0,2,4,6,7,10],alt:4,altern:[0,6],although:6,altogeth:11,alwai:[6,9],ambigu:0,among:7,amount:10,analog:0,anew:0,ani:[0,2,4,6,7,8,9,10,11],anoth:[0,6,7],anymor:10,apart:2,apd:3,api:[0,1,8,11],api_endpoint:11,appear:[0,4,7,11],appli:0,applic:5,approach:[4,6,7],arg:[0,2,4,6,7,8,10,11],argpars:8,argument:[2,4,6,7,8,10,11],argumenttypeerror:8,around:[0,6],arrai:[4,5,6,10],arriv:[2,9,10],arsen:8,arswat:8,articl:[0,11],articletyp:11,ask:2,assign:[0,4,6],associ:[0,4,10],assum:[0,4,6,10,11],assumpt:4,async:2,asynchron:8,attribut:[2,4,5,6,9,10],augment:10,augmented_norm:10,auth:8,automat:[3,6],avail:[2,4,6,7,8,10],averag:[7,10],avoid:[],awak:2,azzopardi:10,back:5,barcelona:0,base:[0,2,3,4,6,7,9,10],baselin:0,basi:[4,10],basic:[0,6,11],batch:2,becaus:[7,10],becom:[0,2],been:[2,9,10,11],befor:[1,2,4,6,7,9,10],begin:[4,7],behavior:9,being:[0,6,7,9,10],below:0,between:[0,2,4,6,7,10],beyond:0,bias:0,bigger:7,binari:0,bind:7,birth:11,bit:2,block:10,bool:[0,2,4,7,9,10,11],bool_:4,borrow:7,both:[2,7],bound:[0,7],bracket:0,broad:7,broader:7,broadli:7,buffer:2,bufferedconsum:2,build:[4,6,10],built:6,bulk:9,burst:7,burst_k:7,bursti:7,cach:[],calcul:[7,10],call:[0,2,7,10],came:7,camel:4,can:[0,2,4,5,6,7,10,11],candid:[0,6],cannot:6,capabl:[],captur:6,care:0,case_fold:[0,4],cataldi:[],cdot:[4,7,10],central:[0,6],centroid:[6,10],certain:[0,6,10],chain:0,chang:[0,4,7,10],charact:[4,6],character:4,character_normalization_count:4,check:[0,2,4,6,9,10,11],checkpoint:7,chronolog:[],chunk:0,clear:7,clear_dimens:[],closest:10,cls:5,cluster:[3,6,7],clusteringalgorithm:10,clusternod:6,code:4,collect:[2,3,9,10,11],collect_recurs:11,collected_link:11,collector:11,colloqui:0,combin:[0,4,7],come:8,command:8,common:[0,2],commonli:[0,4],commun:[0,2,6],compar:[0,6,7,10],comparison:6,complet:4,compon:[0,4,6,7],comput:[0,4,6,7,10],concaten:[4,6,10],concept:[0,7],conclud:0,conf:1,config:1,configur:[3,8],conjunct:[0,4],connect:8,consid:[0,6,7,9],consist:10,constraint:0,construct:[0,4,6,11],construct_url:11,constructor:[0,4,8],consum:[3,8],consumer_kei:1,consumer_secret:1,consumpt:[2,3],contain:[0,4,6,7,8,10,11],content:[2,3,11],context:7,continu:[2,9,11],contrain:7,contrari:2,contrast:0,control:4,convert:[4,6,8],copi:[1,4,10],corpora:8,corpu:[0,8],correspond:[0,4,6,7,8],cos_:10,cosd_:10,cosin:10,cosine_dist:10,could:[0,6,11],count:0,cover:2,creat:[0,2,4,5,6,7,8,9,10],created_at:6,creation:[],credenti:1,credibl:0,critic:7,critical_drop_index:7,current:[6,7,10,11],custom:[],cut:0,data:[2,3,6,7,9],databas:7,dataset:8,date:11,decai:7,decay_r:7,decreas:0,deem:0,defin:[0,2,4,5,6,7,10],definit:0,degre:7,delai:2,delattr:[],denomin:7,depend:[0,4],dequeu:2,dequeue_al:2,descend:[0,7],describ:[0,8,10],design:7,desir:11,detail:1,detect:[3,6],detector:0,develop:7,df_scorer:[],dfscorer:0,dict:[0,1,4,5,6,7,8,9,10,11],dictionari:[0,4,5,6,7,9,10,11],differ:[0,1,4,6,8,10],dimens:[0,4,10],dir:[],directli:4,directori:8,disabl:2,disambigu:[0,11],discard:[0,2],discuss:7,disproportion:0,disregard:2,distanc:10,distinguish:[0,4],divers:6,docuemnt:[],document:[0,2,6,7,10],documentnod:6,documentsc:0,docunet:6,doe:[0,6,10],doesn:6,domain:0,download:9,draw:7,drop:7,due:0,each:[0,2,4,6,7,8,9,10,11],earli:[],earlier:0,easi:11,easier:[4,11],edg:[0,6],effici:7,either:[6,11],eixst:[],eld:[6,7],element:2,elsewher:0,emerg:7,emoji:4,empti:[0,2,5,6,10],emul:0,enabl:0,encapsul:[6,7],encod:8,end:[0,2,4,7,9],endpoint:11,english:8,enough:[0,10],enqueu:2,enter:2,entir:[7,9],entiti:[0,4],entity_extractor:[],entityextractor:0,environ:2,equal:[4,6],equat:7,equival:[4,6,10],error:[5,9,11],essenti:6,euclidean:10,event:[0,2,6,7,8,9],event_:[],eventdt:[1,2,4,5,7,8,10],ever:6,everi:8,exactli:2,exampl:[0,1,6,7],exce:[6,10],except:0,exclud:[0,11],exclus:7,exist:[0,7,10,11],expans:0,expect:[0,2,7,8,10,11],expens:11,expir:[2,6],expiri:6,explain:6,exploit:0,exponenti:[7,11],express:4,extend:0,extern:[],extract:[0,6,11],extract_timestamp:9,extractor:3,extrapol:3,f_i:10,f_j:[],facet:6,facilit:[6,9],factor:[0,7],fail:11,fals:[0,2,4,7,10,11],far:[2,6,7],featur:[4,7,10],fetch:[0,10,11],field:[2,4,10],fifo:2,fifth:0,file:[2,8,9],filenam:8,fill:1,fill_:4,filler:4,filter:[3,9],find:[0,4,6,7],finish:[2,9],fire:7,first:[0,2,4,6,7,8,10],first_level_link:0,first_level_similar:0,flag:[2,9],flush:9,fold:[0,4],follow:[2,4,6,7],form:[0,7,11],formal:0,format:0,formatt:[],former:[4,7],formula:[7,10],found:[0,2,6,11],fourth:0,frac:[4,7,10],freez:10,freeze_period:10,frequenc:[0,4],from:[0,2,4,5,6,7,8,9,10,11],from_arrai:[4,5,6,10],from_docu:4,frozen:10,frozen_clust:10,full:[0,5],func:10,furthermor:[],gain:7,game:7,gener:[0,2,6,7,10],get:[0,2,4,5,6,7,8,9,10,11],get_all_docu:6,get_class:5,get_dimens:[],get_intra_similar:10,get_modul:5,get_representative_vector:10,getattr:[],girvan:0,give:[0,4,7],given:[0,2,4,5,6,7,8,9,10,11],global:[],global_schem:4,goal:6,goe:0,graph:[0,6],greatli:[6,7],greedi:6,group:[6,10],grow:11,half:7,halv:7,handl:[0,7,9],handler:8,happen:[4,6,7],has:[0,2,6,7,8,9,10,11],hash:4,hashtag:4,have:[0,2,4,5,6,7,9,10,11],head:2,heart:7,help:[5,8,9,10,11],helper:[],here:0,high:10,higher:[0,4,5,6],highest:[0,7,10],histor:7,hog:10,hour:[8,9],how:[2,7],howev:[0,4,6,7],http:11,human:[6,7],ideal:6,ident:0,identifi:[0,6,7],idf:[0,4],idf_:4,idl:2,idli:2,ignor:2,immedi:6,implement:[0,2,5,6,7,8],importantli:6,inact:[2,10],includ:[0,2,4,5,6,7,10],inclus:[6,7,10],incom:[2,6,10],increas:7,increment:10,index:[0,3,7,8],indexerror:10,indic:[0,2,4,7,9,10,11],individu:[0,7],info:[3,5],inform:[0,4,5,6,11],inherit:0,initi:[2,4,5,10],initialize_dimens:[],inner:[0,7],input:[0,2,7,8],instanc:[0,4,5,6,10],instanti:[4,10],instead:[0,2,5,6,10],integ:[2,7,10,11],interfac:[5,7,11],intern:6,interpret:7,interrupt:2,intersect:10,intra:10,introduc:[2,7],introduct:11,introduction_onli:11,invalid:[0,5,8],invers:4,invert:0,inverted_index:0,invok:2,is_error_respons:11,is_person:11,isn:6,isol:7,issubclass:[],item:2,its:[0,2,4,8,10],itself:[6,9],ivar:[],job:0,join:6,json:[5,8],just:[7,10],keep:[2,4,7,8,10],keep_redirect:[],kei:[0,4,5,6,7,9,10,11],keyerror:[],keyword:[0,4,6,8,10,11],kind:2,know:2,knowledg:0,known:0,kwarg:[0,4,6,7,8,10,11],lambda:6,lang:8,languag:[3,8,10],larg:0,larger:7,largest:6,last:[0,2,7,10],later:[4,7],latest:[6,11],latter:[4,7],leak:[],learn:[4,8,10],least:[4,6,10],length:[2,4,6,8],less:[0,6,7],level:[0,1,5,11],lies:7,lifetim:6,like:2,likeli:10,limit:11,line:8,link:[0,3],lisen:9,list:[0,1,2,4,5,6,7,8,9,10,11],listen:[2,8],littl:7,load:5,local:7,local_schem:4,log:[0,1,4,5,7],log_df_scor:[],log_level:1,log_tf_scor:[],log_tim:5,logarithm:[0,7],logdfscor:0,logger:[1,3],loglevel:[1,5],logtfscor:0,longer:10,look:[0,6,11],loop:8,lose:7,lot:2,low:0,lower:[0,6],lowercas:4,machin:6,made:[0,4,6,11],magnitud:10,mai:[0,2,4,6,10],main:[0,4,8],maintain:10,make:[0,4,6,10,11],mamo:[],manag:6,manhattan:10,mani:[0,9],map:0,margin:6,mark:7,match:0,math:3,mathemat:10,matrix:6,max_inact:2,max_tim:[2,8,9],maxim:[6,10],maximum:[0,2,6,9],mean:[0,10],meant:10,measur:[6,7],mechan:7,memori:[7,10],memorynutritionstor:7,mention:[4,11],mere:2,messag:[2,5],meta:8,metadata:8,method:[0,2,6,7,10],metric:[7,10],might:0,min_burst:7,min_length:4,min_similar:6,minim:[0,6,10],minimum:[0,4,6,7,10],minut:[0,8],miss:11,mmr:6,mode:8,model:[3,4,7],modifi:0,modul:[3,5,7,11],more:[0,4,6,8,10,11],moreov:6,most:[0,2,4,6,7,10],much:7,multipl:[0,4],multipli:4,must:[4,6,7,8],n_t:4,name:[0,2,5,9,10,11],natur:[3,7,8,10],necessari:[2,6],necessit:7,need:[4,7,9,11],neg:[0,2,4,6,7],ner:0,ner_participant_detector:[],nerparticipantdetector:0,nest:0,networkx:[0,6],newest:2,newman:0,next:[0,2,6],nlp:[0,3,10],nltk:[0,4],node:0,node_typ:6,nokmean:10,non:[6,7,10],none:[0,2,4,5,6,7,8,9,10,11],normal:[0,2,4,5,10,11],normalize_scor:0,normalize_special_charact:4,normalize_word:4,notat:4,note:[0,4],noth:2,notimpl:[],notion:7,number:[0,2,4,7,8,9,10,11],nutr_:7,nutr_k:7,nutrit:3,nutritionstor:7,oauth:8,oauthhandl:8,object:[0,2,4,5,6,7,9,10],obtain:11,occur:[2,10],off:[0,7],offer:[5,6],often:[0,2,4,11],old:7,older:7,oldest:2,on_data:9,on_error:9,onc:11,one:[0,4,6,8,10],onli:[0,5,6,7,9,10,11],onward:7,open:9,oper:[0,6,8,11],option:[4,8],order:[0,2,6,7],ordered_enum:[],orderedenum:5,org:11,origin:[0,4],other:[0,2,3,4,6,7,11],otherwis:[0,4,10,11],out:[0,2,4,6,10],outcom:[],outer:[0,6],outgo:[0,11],outgoing_link:0,outlin:[2,7],output:[0,2,6,8,9],output_:[],outsid:4,over:[0,2,10],overcom:0,overhead:7,overli:0,overload:11,overrid:9,overridden:[],overwrit:7,own:8,p_i:10,packag:9,page:[0,3,11],pair:[0,10],paper:[],param:[],paramat:0,paramet:[0,2,4,5,6,7,8,9,10,11],paritit:6,particip:[3,6,7],participant_detector:[],participantdetector:0,particular:[0,7,11],partit:6,pass:[4,6,8,10,11],past:7,path:[0,5,6],penal:4,perform:[0,6],period:[2,6,7,8,10],person:[0,7,11],php:11,physic:7,pick:6,pickl:[],pivot:7,plain:[4,11],point:[0,2],pointer:9,popular:[4,7],porter:4,porterstemm:4,posit:[6,7,11],possibl:0,post_rat:7,postproces:0,postprocess:0,postprocessor:3,potenti:0,praticip:0,precis:6,predominantli:[7,11],prepar:2,present:[6,7],previou:[0,7],print:[2,9],printconsum:[2,8],problem:0,process:[0,2,3,6,9,10],produc:6,product:[0,10],program:8,progress:7,promot:4,proper:0,properti:[4,6,10],proport:0,provid:[0,2,4,6,10,11],publish:10,punctuat:4,python:[0,1,2,4,5,6,7,8,9,10,11],q_i:10,queri:6,queue:3,rac:[],radic:0,rais:[0,2,4,5,6,7,8,10,11],rank:0,rare:4,rate:[2,7],ratio:7,read:[2,4,8,9,10],real:[0,2,7,9,10],reason:[0,4],recalcul:10,recalculate_centroid:10,receiv:[0,2,4,6,7,8,9,10],recent:[7,10],recognit:0,recurs:11,redirect:11,reduc:[0,4],redund:6,refer:[0,2,4,5,6,7,10],relat:[8,10],relev:[0,6],relevan:0,remain:0,remov:[0,2,4,7,10],remove_acc:0,remove_alt_cod:4,remove_bracket:0,remove_hashtag:4,remove_ment:4,remove_numb:4,remove_punctu:4,remove_unicode_ent:4,remove_url:4,remove_vector:[],reorder:6,repeat:4,replac:[0,4],repr:[],repres:[0,4,7,10,11],represent:[0,4,6,10],representind:6,request:[10,11],requir:[0,4,5,8,9],rerank:6,rescal:[0,7],research:10,reset:[9,10],resolut:0,resolv:[3,11],respect:[0,5,6,7],respons:[0,7,11],result:[0,7,11],retain:[0,4,9,10],retir:10,retorn:11,retriev:[0,7],retrospect:7,revers:6,revert:11,revert_redirect:11,revis:11,revolv:0,routin:7,rtpye:10,rtype:[],run:[2,7,8],runtimeerror:11,said:[0,6],same:[0,2,4,5,10],save:[8,9],save_meta:8,scheme:0,schemescor:4,score:[0,4,6,10],scorer:[3,4],script:8,search:[0,3],second:[0,2,4,6,7,8,9,10],second_level_link:0,second_level_similar:0,secondli:0,see:[],seed:11,seek:0,seen:7,select:[6,7],self:[],send:11,sensor:7,sentenc:[0,6],separ:[0,6,7,11],set:[0,1,2,4,5,6,7,8,9,10,11],set_dimens:[],set_logging_level:5,setattr:[],setup_arg:8,sfrac:[],share:0,shorter:6,shortest:[0,6],should:[0,2,4,7,8,9,10,11],show:5,signatur:[],signific:7,silent:9,similar:[0,6,10],similarity_measur:10,similarli:0,simpl:[0,4,6,7],simplest:[0,4],simpli:[0,4],simplic:0,simul:2,simulatedbufferedconsum:2,simultan:[6,9,10],sinc:[2,4,7,10],singl:[0,10,11],six:0,sixth:0,size:10,skip:[2,9],sleep:2,slide:7,slow:0,small:2,smallest:10,social:7,some:[2,5],someth:7,sort:[0,7],sought:10,sourc:[0,6],space:[3,4],special:2,specif:[2,6],specifi:0,spend:[2,8,9],spike:7,split:[4,6,7,8],split_hashtag:4,sport:7,sqrt:[7,10],sqrt_:[],stage:2,start:[2,5,7,9,11],state:[2,6,7,10],statu:9,stdout:9,stem:[0,4],stemmer:4,step:[0,4],still:[0,2,6],stop:2,stopword:4,storag:7,store:[3,4,5,6,8,10],store_frozen:10,str:[0,2,4,5,6,7,8,9,10,11],stream:[7,9],string:[0,4,5,6,8,11],structur:[2,7],studi:7,subclass:[],subject:[0,10],subtract:10,succe:7,success:6,suitabl:7,sum:[],sum_:[7,10],summar:3,summari:6,summarizationalgorithm:6,summat:0,suppli:4,support:8,surnam:0,surname_onli:0,synchron:8,system:7,tabl:[0,4],tag:4,tail:2,take:[0,2,4,6,10,11],taken:[0,7],target:0,task:[4,6,8,10],tdt:[0,2,3,4,5,6,8,9,10],tdtalgorithm:7,techniqu:7,tempor:10,temporalnokmean:10,term:[0,3,7,11],term_weight:[],terminolog:7,termweight:4,termweightingschem:[0,4],text:[0,3,4,6],tf_:4,tf_scorer:[],tfidf:[0,4],tfidf_:4,tfidf_scor:[],tfidfscor:0,tfscorer:0,than:[0,4,6,7,10],thei:[0,2,4,6,7,9,10,11],them:[0,2,4,6,7,8,9,10],themselv:6,therefor:[0,6,7],thet:7,thi:[0,2,4,6,7,8,9,10,11],thing:10,third:0,those:[0,4,7,11],three:0,threshold:[0,9,10],threshold_filt:[],thresholdfilt:0,through:[0,6,11],thu:[0,6,7],tightli:0,time:[0,2,4,5,6,7,9,10],time_attribut:[],timelin:[3,7,8],timestamp:[2,6,7,9,10],timestmap:7,titl:[0,11],to_arrai:[4,5,6,10],todo:[],togeth:[0,6,8,10],token:[0,3],token_extractor:[],token_resolv:[],tokenextractor:0,tokenresolv:0,too:2,tool:3,top:0,topic:[3,6],topmost:0,total:4,toward:0,track:[3,6,8],track_:[],tradition:4,transform:[0,4],tree:0,tri:[0,6],tupl:[0,6,7,10],turn:2,tweepi:[8,9],tweet:[2,8,9],tweetlisten:[8,9],twevent:8,twice:0,twitter:[1,3,5,7,8],two:[0,2,4,7,8],type:[0,2,4,5,6,7,8,9,10,11],typeerror:10,unambigu:0,unchang:7,uncommon:4,understand:[2,6,8],understanding_:[],unicod:4,union:10,uniqu:6,unless:6,unlik:[0,2],unresolv:0,unset:[],until:[2,7,9],updat:[9,10],update_threshold:9,upon:10,url:[4,11],use:[0,4,6,7,8,10,11],used:[0,2,4,6,7,9,10,11],useless:6,uses:[0,4,6,7,11],using:[0,1,2,4,7,9,10,11],usual:0,v_1:[],v_2:[],v_n:10,valid:[5,9,11],valu:[0,2,4,5,6,7,9,10,11],valueerror:[0,2,4,5,6,7,10,11],vari:[6,7],variabl:[0,1,2,4,5,6,7,9,10,11],variant:10,variou:2,vartyp:[],vector:[2,3,4,6],vector_math:[],vectorspac:10,veri:[0,4,11],volum:7,vsm:[3,4,6],w_i:[],wai:[0,2,4,6],wait:[2,9],warn:5,watford:8,weak:[0,2,4,5,6,7,10],weigh:4,weight:[0,3,6,7,10],well:[0,6,7],were:[0,6],what:6,whatsoev:0,when:[0,2,4,5,6,7,8,9,10,11],where:[0,2,4,7,8,10,11],whether:[0,2,4,6,9,10,11],which:[0,4,5,6,7,9,10,11],whole:0,whose:[0,7,10,11],why:0,wikimedia:11,wikinterfac:3,wikipedia:[0,11],wikipedia_extrapol:[],wikipedia_name_resolv:[],wikipedia_postprocessor:[],wikipedia_search_resolv:[],wikipediaextrapol:0,wikipedianameresolv:0,wikipediapostprocessor:0,wikipediasearchresolv:0,window:[2,7],within:0,without:[0,2,10,11],word:[0,4,7],work:[0,4,7,10],workflow:2,worth:7,would:7,write:[8,9],written:[8,9],wrong:7,x_j:[],xxxxxxxxxxxxxxxxxxxxxxxxx:1,xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx:1,xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx:1,year:0,yet:9,you:[5,8,10],zero:[7,10],zhao:[]},titles:["5. Automatic Participant Detection (APD)","0. Configuration","9. Consumers","Welcome to EvenTDT\u2019s documentation!","3. Natural Language Processing (NLP)","10. Other","7. Summarization","6. Topic Detection and Tracking (TDT)","1. Tools","8. Twitter","2. Vector Space Model (VSM)","4. Wikinterface"],titleterms:{"class":5,algorithm:[6,7,10],apd:0,automat:0,base:5,carbonel:6,cataldi:7,cluster:10,collect:8,common:4,configur:1,consum:2,consumpt:8,data:8,detect:[0,7],document:[3,4],eventdt:3,extern:0,extractor:0,extrapol:0,filter:0,global:4,goldstein:6,indic:3,info:11,languag:4,link:11,listen:9,local:[0,4],logger:5,mamo:[6,7],math:10,model:10,natur:4,nlp:4,node:6,nutrit:7,other:5,particip:0,postprocessor:0,process:4,queue:2,resolv:0,scheme:4,scorer:0,search:11,simpl:2,space:10,store:7,summar:6,tabl:3,tdt:7,term:4,text:11,timelin:6,token:4,tool:8,topic:7,track:7,twitter:9,vector:10,vsm:10,weight:4,welcom:3,wikinterfac:11,zhao:7}})