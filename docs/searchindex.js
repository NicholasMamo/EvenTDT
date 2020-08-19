Search.setIndex({docnames:["ate","consumers","index","nlp","other","summarization","tdt","tools","twitter","vsm","wikinterface"],envversion:{"sphinx.domains.c":1,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":1,"sphinx.domains.javascript":1,"sphinx.domains.math":2,"sphinx.domains.python":1,"sphinx.domains.rst":1,"sphinx.domains.std":1,sphinx:56},filenames:["ate.rst","consumers.rst","index.rst","nlp.rst","other.rst","summarization.rst","tdt.rst","tools.rst","twitter.rst","vsm.rst","wikinterface.rst"],objects:{"":{ate:[0,0,0,"-"],logger:[4,0,0,"-"],nlp:[3,0,0,"-"],objects:[4,0,0,"-"],queues:[1,0,0,"-"],summarization:[5,0,0,"-"],tdt:[6,0,0,"-"],tools:[7,0,0,"-"],twitter:[8,0,0,"-"],vsm:[9,0,0,"-"],wikinterface:[10,0,0,"-"]},"ate.application":{event:[0,0,0,"-"]},"ate.application.event":{EF:[0,1,1,""],EFIDF:[0,1,1,""],Entropy:[0,1,1,""],LogEF:[0,1,1,""],Variability:[0,1,1,""]},"ate.application.event.EF":{extract:[0,2,1,""]},"ate.application.event.EFIDF":{__init__:[0,2,1,""],extract:[0,2,1,""]},"ate.application.event.Entropy":{__init__:[0,2,1,""],extract:[0,2,1,""]},"ate.application.event.LogEF":{__init__:[0,2,1,""],extract:[0,2,1,""]},"ate.application.event.Variability":{__init__:[0,2,1,""],extract:[0,2,1,""]},"ate.bootstrapping":{Bootstrapper:[0,1,1,""],DummyBootstrapper:[0,1,1,""],probability:[0,0,0,"-"]},"ate.bootstrapping.Bootstrapper":{__weakref__:[0,3,1,""],bootstrap:[0,2,1,""],to_list:[0,2,1,""]},"ate.bootstrapping.DummyBootstrapper":{bootstrap:[0,2,1,""]},"ate.bootstrapping.probability":{chi:[0,0,0,"-"],llratio:[0,0,0,"-"],pmi:[0,0,0,"-"]},"ate.bootstrapping.probability.chi":{ChiBootstrapper:[0,1,1,""]},"ate.bootstrapping.probability.chi.ChiBootstrapper":{bootstrap:[0,2,1,""]},"ate.bootstrapping.probability.llratio":{LogLikelihoodRatioBootstrapper:[0,1,1,""]},"ate.bootstrapping.probability.llratio.LogLikelihoodRatioBootstrapper":{bootstrap:[0,2,1,""]},"ate.bootstrapping.probability.pmi":{PMIBootstrapper:[0,1,1,""]},"ate.bootstrapping.probability.pmi.PMIBootstrapper":{__init__:[0,2,1,""],bootstrap:[0,2,1,""]},"ate.extractor":{DummyExtractor:[0,1,1,""],Extractor:[0,1,1,""]},"ate.extractor.DummyExtractor":{extract:[0,2,1,""]},"ate.extractor.Extractor":{__weakref__:[0,3,1,""],extract:[0,2,1,""],to_list:[0,2,1,""]},"ate.linguistic":{nouns:[0,4,1,""],vocabulary:[0,4,1,""]},"ate.stat":{corpus:[0,0,0,"-"],probability:[0,0,0,"-"],tf:[0,0,0,"-"],tfidf:[0,0,0,"-"]},"ate.stat.corpus":{ComparisonExtractor:[0,1,1,""],DummyComparisonExtractor:[0,1,1,""],rank:[0,0,0,"-"],specificity:[0,0,0,"-"],tfdcf:[0,0,0,"-"]},"ate.stat.corpus.ComparisonExtractor":{__init__:[0,2,1,""]},"ate.stat.corpus.DummyComparisonExtractor":{extract:[0,2,1,""]},"ate.stat.corpus.rank":{RankExtractor:[0,1,1,""]},"ate.stat.corpus.rank.RankExtractor":{__init__:[0,2,1,""],extract:[0,2,1,""]},"ate.stat.corpus.specificity":{SpecificityExtractor:[0,1,1,""]},"ate.stat.corpus.specificity.SpecificityExtractor":{__init__:[0,2,1,""],extract:[0,2,1,""]},"ate.stat.corpus.tfdcf":{TFDCFExtractor:[0,1,1,""]},"ate.stat.corpus.tfdcf.TFDCFExtractor":{extract:[0,2,1,""]},"ate.stat.probability":{cached:[0,4,1,""],joint_vocabulary:[0,4,1,""],p:[0,4,1,""]},"ate.stat.tf":{TFExtractor:[0,1,1,""]},"ate.stat.tf.TFExtractor":{extract:[0,2,1,""]},"ate.stat.tfidf":{TFIDFExtractor:[0,1,1,""]},"ate.stat.tfidf.TFIDFExtractor":{__init__:[0,2,1,""],extract:[0,2,1,""]},"logger.logger":{LogLevel:[4,1,1,""],error:[4,4,1,""],info:[4,4,1,""],log_time:[4,4,1,""],set_logging_level:[4,4,1,""],warning:[4,4,1,""]},"nlp.cleaners":{Cleaner:[3,1,1,""],tweet_cleaner:[3,0,0,"-"]},"nlp.cleaners.Cleaner":{__init__:[3,2,1,""],__weakref__:[3,3,1,""],clean:[3,2,1,""]},"nlp.cleaners.tweet_cleaner":{TweetCleaner:[3,1,1,""]},"nlp.cleaners.tweet_cleaner.TweetCleaner":{__init__:[3,2,1,""],clean:[3,2,1,""]},"nlp.document":{Document:[3,1,1,""]},"nlp.document.Document":{__init__:[3,2,1,""],__str__:[3,2,1,""],concatenate:[3,2,1,""],copy:[3,2,1,""],from_array:[3,2,1,""],to_array:[3,2,1,""]},"nlp.tokenizer":{Tokenizer:[3,1,1,""]},"nlp.tokenizer.Tokenizer":{__init__:[3,2,1,""],__weakref__:[3,3,1,""],pos:[3,3,1,""],tokenize:[3,2,1,""]},"nlp.weighting":{SchemeScorer:[3,1,1,""],TermWeightingScheme:[3,1,1,""],global_schemes:[3,0,0,"-"],local_schemes:[3,0,0,"-"],tf:[3,0,0,"-"],tfidf:[3,0,0,"-"]},"nlp.weighting.SchemeScorer":{__weakref__:[3,3,1,""],score:[3,2,1,""]},"nlp.weighting.TermWeightingScheme":{__init__:[3,2,1,""],__weakref__:[3,3,1,""],create:[3,2,1,""]},"nlp.weighting.global_schemes":{filler:[3,0,0,"-"],idf:[3,0,0,"-"]},"nlp.weighting.global_schemes.filler":{Filler:[3,1,1,""]},"nlp.weighting.global_schemes.filler.Filler":{score:[3,2,1,""]},"nlp.weighting.global_schemes.idf":{IDF:[3,1,1,""]},"nlp.weighting.global_schemes.idf.IDF":{__init__:[3,2,1,""],from_array:[3,2,1,""],from_documents:[3,2,1,""],score:[3,2,1,""],to_array:[3,2,1,""]},"nlp.weighting.local_schemes":{"boolean":[3,0,0,"-"],tf:[3,0,0,"-"]},"nlp.weighting.local_schemes.boolean":{Boolean:[3,1,1,""]},"nlp.weighting.local_schemes.boolean.Boolean":{score:[3,2,1,""]},"nlp.weighting.local_schemes.tf":{TF:[3,1,1,""]},"nlp.weighting.local_schemes.tf.TF":{score:[3,2,1,""]},"nlp.weighting.tf":{TF:[3,1,1,""]},"nlp.weighting.tf.TF":{__init__:[3,2,1,""]},"nlp.weighting.tfidf":{TFIDF:[3,1,1,""]},"nlp.weighting.tfidf.TFIDF":{__init__:[3,2,1,""],from_array:[3,2,1,""],to_array:[3,2,1,""]},"objects.attributable":{Attributable:[4,1,1,""]},"objects.attributable.Attributable":{__init__:[4,2,1,""],__weakref__:[4,3,1,""]},"objects.exportable":{Exportable:[4,1,1,""]},"objects.exportable.Exportable":{__weakref__:[4,3,1,""],decode:[4,2,1,""],encode:[4,2,1,""],from_array:[4,2,1,""],get_class:[4,2,1,""],get_module:[4,2,1,""],to_array:[4,2,1,""]},"queues.Queue":{__init__:[1,2,1,""],__weakref__:[1,3,1,""],dequeue:[1,2,1,""],dequeue_all:[1,2,1,""],empty:[1,2,1,""],enqueue:[1,2,1,""],head:[1,2,1,""],length:[1,2,1,""],tail:[1,2,1,""]},"queues.consumers":{Consumer:[1,1,1,""],buffered_consumer:[1,0,0,"-"],eld_consumer:[1,0,0,"-"],fire_consumer:[1,0,0,"-"],print_consumer:[1,0,0,"-"],stat_consumer:[1,0,0,"-"],zhao_consumer:[1,0,0,"-"]},"queues.consumers.Consumer":{__init__:[1,2,1,""],__weakref__:[1,3,1,""],run:[1,2,1,""],stop:[1,2,1,""]},"queues.consumers.buffered_consumer":{BufferedConsumer:[1,1,1,""],SimulatedBufferedConsumer:[1,1,1,""]},"queues.consumers.buffered_consumer.BufferedConsumer":{__init__:[1,2,1,""],run:[1,2,1,""]},"queues.consumers.buffered_consumer.SimulatedBufferedConsumer":{__init__:[1,2,1,""]},"queues.consumers.eld_consumer":{ELDConsumer:[1,1,1,""]},"queues.consumers.eld_consumer.ELDConsumer":{__init__:[1,2,1,""],understand:[1,2,1,""]},"queues.consumers.fire_consumer":{FIREConsumer:[1,1,1,""]},"queues.consumers.fire_consumer.FIREConsumer":{__init__:[1,2,1,""]},"queues.consumers.print_consumer":{PrintConsumer:[1,1,1,""]},"queues.consumers.stat_consumer":{StatConsumer:[1,1,1,""]},"queues.consumers.zhao_consumer":{ZhaoConsumer:[1,1,1,""]},"queues.consumers.zhao_consumer.ZhaoConsumer":{__init__:[1,2,1,""]},"summarization.algorithms":{SummarizationAlgorithm:[5,1,1,""],dgs:[5,0,0,"-"],mmr:[5,0,0,"-"]},"summarization.algorithms.SummarizationAlgorithm":{__weakref__:[5,3,1,""],summarize:[5,2,1,""]},"summarization.algorithms.dgs":{DGS:[5,1,1,""]},"summarization.algorithms.dgs.DGS":{__init__:[5,2,1,""],summarize:[5,2,1,""]},"summarization.algorithms.mmr":{MMR:[5,1,1,""]},"summarization.algorithms.mmr.MMR":{__init__:[5,2,1,""],summarize:[5,2,1,""]},"summarization.summary":{Summary:[5,1,1,""]},"summarization.summary.Summary":{__init__:[5,2,1,""],__str__:[5,2,1,""],documents:[5,2,1,""],from_array:[5,2,1,""],to_array:[5,2,1,""]},"summarization.timeline":{Timeline:[5,1,1,""],nodes:[5,0,0,"-"]},"summarization.timeline.Timeline":{__init__:[5,2,1,""],add:[5,2,1,""],from_array:[5,2,1,""],to_array:[5,2,1,""]},"summarization.timeline.nodes":{Node:[5,1,1,""],cluster_node:[5,0,0,"-"],document_node:[5,0,0,"-"],topical_cluster_node:[5,0,0,"-"]},"summarization.timeline.nodes.Node":{__init__:[5,2,1,""],add:[5,2,1,""],expired:[5,2,1,""],get_all_documents:[5,2,1,""],similarity:[5,2,1,""]},"summarization.timeline.nodes.cluster_node":{ClusterNode:[5,1,1,""]},"summarization.timeline.nodes.cluster_node.ClusterNode":{__init__:[5,2,1,""],add:[5,2,1,""],from_array:[5,2,1,""],get_all_documents:[5,2,1,""],similarity:[5,2,1,""],to_array:[5,2,1,""]},"summarization.timeline.nodes.document_node":{DocumentNode:[5,1,1,""]},"summarization.timeline.nodes.document_node.DocumentNode":{__init__:[5,2,1,""],add:[5,2,1,""],from_array:[5,2,1,""],get_all_documents:[5,2,1,""],similarity:[5,2,1,""],to_array:[5,2,1,""]},"summarization.timeline.nodes.topical_cluster_node":{TopicalClusterNode:[5,1,1,""]},"summarization.timeline.nodes.topical_cluster_node.TopicalClusterNode":{__init__:[5,2,1,""],add:[5,2,1,""],from_array:[5,2,1,""],similarity:[5,2,1,""],to_array:[5,2,1,""]},"tdt.algorithms":{TDTAlgorithm:[6,1,1,""],cataldi:[6,0,0,"-"],eld:[6,0,0,"-"],zhao:[6,0,0,"-"]},"tdt.algorithms.TDTAlgorithm":{__weakref__:[6,3,1,""],detect:[6,2,1,""]},"tdt.algorithms.cataldi":{Cataldi:[6,1,1,""]},"tdt.algorithms.cataldi.Cataldi":{__init__:[6,2,1,""],detect:[6,2,1,""]},"tdt.algorithms.eld":{ELD:[6,1,1,""]},"tdt.algorithms.eld.ELD":{__init__:[6,2,1,""],detect:[6,2,1,""]},"tdt.algorithms.zhao":{Zhao:[6,1,1,""]},"tdt.algorithms.zhao.Zhao":{__init__:[6,2,1,""],detect:[6,2,1,""]},"tdt.nutrition":{NutritionStore:[6,1,1,""],memory:[6,0,0,"-"]},"tdt.nutrition.NutritionStore":{__init__:[6,2,1,""],__weakref__:[6,3,1,""],add:[6,2,1,""],all:[6,2,1,""],between:[6,2,1,""],copy:[6,2,1,""],get:[6,2,1,""],remove:[6,2,1,""],since:[6,2,1,""],until:[6,2,1,""]},"tdt.nutrition.memory":{MemoryNutritionStore:[6,1,1,""]},"tdt.nutrition.memory.MemoryNutritionStore":{__init__:[6,2,1,""],add:[6,2,1,""],all:[6,2,1,""],between:[6,2,1,""],copy:[6,2,1,""],get:[6,2,1,""],remove:[6,2,1,""]},"tools.bootstrap":{bootstrap:[7,4,1,""],filter_candidates:[7,4,1,""],generate_candidates:[7,4,1,""],load_candidates:[7,4,1,""],load_seed:[7,4,1,""],main:[7,4,1,""],method:[7,4,1,""],setup_args:[7,4,1,""],update_scores:[7,4,1,""]},"tools.collect":{collect:[7,4,1,""],main:[7,4,1,""],save_meta:[7,4,1,""],setup_args:[7,4,1,""]},"tools.consume":{consume:[7,4,1,""],consume_process:[7,4,1,""],consumer:[7,4,1,""],main:[7,4,1,""],scheme:[7,4,1,""],setup_args:[7,4,1,""],stream_process:[7,4,1,""],understand:[7,4,1,""],understand_process:[7,4,1,""]},"tools.idf":{construct:[7,4,1,""],main:[7,4,1,""],save:[7,4,1,""],setup_args:[7,4,1,""],tokenize:[7,4,1,""],update:[7,4,1,""]},"tools.tokenizer":{get_tags:[7,4,1,""],get_text:[7,4,1,""],main:[7,4,1,""],prepare_output:[7,4,1,""],setup_args:[7,4,1,""],tokenize_corpus:[7,4,1,""]},"twitter.corpus":{aggregate:[8,0,0,"-"]},"twitter.corpus.aggregate":{aggregate:[8,4,1,""]},"twitter.file":{FileReader:[8,1,1,""],simulated_reader:[8,0,0,"-"],staggered_reader:[8,0,0,"-"]},"twitter.file.FileReader":{__init__:[8,2,1,""],__weakref__:[8,3,1,""],read:[8,2,1,""],reading:[8,2,1,""],skip:[8,2,1,""],stop:[8,2,1,""]},"twitter.file.simulated_reader":{SimulatedFileReader:[8,1,1,""]},"twitter.file.simulated_reader.SimulatedFileReader":{__init__:[8,2,1,""],read:[8,2,1,""]},"twitter.file.staggered_reader":{StaggeredFileReader:[8,1,1,""]},"twitter.file.staggered_reader.StaggeredFileReader":{__init__:[8,2,1,""],read:[8,2,1,""]},"twitter.listeners":{queued_tweet_listener:[8,0,0,"-"],tweet_listener:[8,0,0,"-"]},"twitter.listeners.queued_tweet_listener":{QueuedTweetListener:[8,1,1,""]},"twitter.listeners.queued_tweet_listener.QueuedTweetListener":{__init__:[8,2,1,""],filter:[8,2,1,""],on_data:[8,2,1,""],on_error:[8,2,1,""]},"twitter.listeners.tweet_listener":{TweetListener:[8,1,1,""]},"twitter.listeners.tweet_listener.TweetListener":{__init__:[8,2,1,""],filter:[8,2,1,""],flush:[8,2,1,""],on_data:[8,2,1,""],on_error:[8,2,1,""]},"vsm.clustering":{algorithms:[9,0,0,"-"],cluster:[9,0,0,"-"]},"vsm.clustering.algorithms":{ClusteringAlgorithm:[9,1,1,""],no_k_means:[9,0,0,"-"],temporal_no_k_means:[9,0,0,"-"]},"vsm.clustering.algorithms.ClusteringAlgorithm":{__init__:[9,2,1,""],__weakref__:[9,3,1,""],cluster:[9,2,1,""]},"vsm.clustering.algorithms.no_k_means":{NoKMeans:[9,1,1,""]},"vsm.clustering.algorithms.no_k_means.NoKMeans":{__init__:[9,2,1,""],cluster:[9,2,1,""]},"vsm.clustering.algorithms.temporal_no_k_means":{TemporalNoKMeans:[9,1,1,""]},"vsm.clustering.algorithms.temporal_no_k_means.TemporalNoKMeans":{__init__:[9,2,1,""],cluster:[9,2,1,""]},"vsm.clustering.cluster":{Cluster:[9,1,1,""]},"vsm.clustering.cluster.Cluster":{__init__:[9,2,1,""],centroid:[9,2,1,""],from_array:[9,2,1,""],get_intra_similarity:[9,2,1,""],get_representative_vectors:[9,2,1,""],recalculate_centroid:[9,2,1,""],similarity:[9,2,1,""],size:[9,2,1,""],to_array:[9,2,1,""],vectors:[9,2,1,""]},"vsm.vector":{Vector:[9,1,1,""],VectorSpace:[9,1,1,""]},"vsm.vector.Vector":{__init__:[9,2,1,""],copy:[9,2,1,""],dimensions:[9,2,1,""],from_array:[9,2,1,""],normalize:[9,2,1,""],to_array:[9,2,1,""]},"vsm.vector.VectorSpace":{__getitem__:[9,2,1,""],__weakref__:[9,3,1,""]},"vsm.vector_math":{augmented_normalize:[9,4,1,""],concatenate:[9,4,1,""],cosine:[9,4,1,""],cosine_distance:[9,4,1,""],euclidean:[9,4,1,""],magnitude:[9,4,1,""],manhattan:[9,4,1,""],normalize:[9,4,1,""]},"wikinterface.info":{ArticleType:[10,1,1,""],is_person:[10,4,1,""],types:[10,4,1,""]},"wikinterface.links":{collect:[10,4,1,""],collect_recursive:[10,4,1,""]},"wikinterface.search":{collect:[10,4,1,""]},"wikinterface.text":{collect:[10,4,1,""]},ate:{application:[0,0,0,"-"],bootstrapping:[0,0,0,"-"],extractor:[0,0,0,"-"],linguistic:[0,0,0,"-"],stat:[0,0,0,"-"],total_documents:[0,4,1,""]},logger:{logger:[4,0,0,"-"]},nlp:{cleaners:[3,0,0,"-"],document:[3,0,0,"-"],tokenizer:[3,0,0,"-"],weighting:[3,0,0,"-"]},objects:{attributable:[4,0,0,"-"],exportable:[4,0,0,"-"]},queues:{Queue:[1,1,1,""],consumers:[1,0,0,"-"]},summarization:{algorithms:[5,0,0,"-"],summary:[5,0,0,"-"],timeline:[5,0,0,"-"]},tdt:{algorithms:[6,0,0,"-"],nutrition:[6,0,0,"-"]},tools:{bootstrap:[7,0,0,"-"],cache_exists:[7,4,1,""],collect:[7,0,0,"-"],consume:[7,0,0,"-"],idf:[7,0,0,"-"],is_file:[7,4,1,""],is_json:[7,4,1,""],load:[7,4,1,""],meta:[7,4,1,""],save:[7,4,1,""],tokenizer:[7,0,0,"-"]},twitter:{corpus:[8,0,0,"-"],extract_timestamp:[8,4,1,""],file:[8,0,0,"-"],listeners:[8,0,0,"-"]},vsm:{vector:[9,0,0,"-"],vector_math:[9,0,0,"-"]},wikinterface:{API_ENDPOINT:[10,5,1,""],construct_url:[10,4,1,""],info:[10,0,0,"-"],is_error_response:[10,4,1,""],links:[10,0,0,"-"],revert_redirects:[10,4,1,""],search:[10,0,0,"-"],text:[10,0,0,"-"]}},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","method","Python method"],"3":["py","attribute","Python attribute"],"4":["py","function","Python function"],"5":["py","data","Python data"]},objtypes:{"0":"py:module","1":"py:class","2":"py:method","3":"py:attribute","4":"py:function","5":"py:data"},terms:{"2ln":0,"\u03c4":0,"abstract":[0,1,3,4,5,6,8,9],"boolean":[0,1,7,8,9,10],"break":[1,6,9],"case":[0,1,3,5,6,10],"class":[0,2,3,5,6,7,8,9,10],"default":[0,1,3,5,6,7,8,9,10],"enum":10,"export":[3,4,5,7,9],"final":[1,3,5,6],"float":[0,1,5,6,7,8,9],"function":[0,1,3,4,5,6,7,8,9,10],"import":[1,3,4,6,8,9],"int":[0,1,3,6,7,8,9,10],"long":[0,1,5,8,9],"new":[0,1,3,4,5,6,7,8,9,10],"null":0,"public":1,"return":[0,1,3,4,5,6,7,8,9,10],"static":[3,4,5,8,9],"true":[0,1,3,8,9,10],"try":[4,6],"while":[1,5,8],ATE:2,Adding:5,Aging:6,DGS:1,For:[0,3,5,6,8,9,10],Not:3,That:[0,1,3,5,8,9],The:[2,3,4,6,7,8,9,10],Their:10,Then:[0,3,5,6],There:[1,5],These:[0,1,3,5,6,8,10],Use:5,Used:[1,7],Using:0,With:0,__getitem__:9,__init__:[0,1,3,4,5,6,7,8,9],__str__:[3,5],__weakref__:[0,1,3,4,5,6,8,9],_add_docu:[],_all_:9,_brevity_scor:[],_cluster:[],_compute_queri:[],_compute_scor:[],_compute_similarity_matrix:[],_construct_idf:1,_consum:[],_creat:[],_create_checkpoint:[],_detect_particip:1,_detect_top:[],_documents_sinc:[],_emotion_scor:[],_extract_commun:[],_filter_clust:[],_filter_docu:[],_filter_tweet:[],_get_next_docu:[],_how_:[],_io:8,_largest_commun:[],_latest_timestamp:[],_most_central_edg:[],_process:[],_remove_documents_befor:[],_remove_old_checkpoint:[],_score_docu:[],_sleep:[],_start:[],_stop:[],_summarization_bas:[],_to_docu:[],_to_graph:[],_unixselectoreventloop:7,_wait_for_input:[],_what_:[],abl:0,about:[0,1,3,5,6,7,9,10],absolut:[],absorb:5,accent:3,accept:[0,1,3,5,6,7,8,9],access:[5,9,10],accompani:[3,5,8],accord:[3,5,6,8,10],account:7,accumul:[0,1,8],accur:5,accuraci:6,achiev:[6,9],acm:[],across:[0,3,6,9,10],action:10,activ:[1,5,8,9],actual:[0,1,3,8],add:[1,3,4,5,6,7,8,9],added:[1,5,9,10],adding:[1,8,9],addit:[0,1,3,4,5,6,7,8,9,10],adject:7,adopt:[3,6],advanc:0,advantag:9,adverb:7,affect:[1,6],afford:5,after:[1,3,6,7,8,9],again:[3,9],against:[0,5],agg:8,aggreg:5,agnost:[1,8],ago:[],akin:[],algorithm:[2,8],all:[0,1,3,5,6,7,8,9,10],allow:[0,1,5,8,9],almost:1,alon:[],along:9,alongsid:3,alreadi:[0,5,7,8,10],also:[0,1,3,5,6,8,9],alt:3,alt_code_pattern:3,altern:7,although:[0,1,5,6,8,9,10],altogeth:10,alwai:[3,5,6,7,8,9,10],among:[0,1,6],amount:7,analysi:0,ani:[0,1,3,5,6,7,8,9,10],anoth:[0,1,6],anyth:[4,8],apart:[0,1,3,5,6],apd:2,api:[1,7,8,10],api_endpoint:10,appear:[0,3,6],appli:[5,6],applic:[2,3,4,5,6,8],approach:[0,1,3,5,6,8,9],appropri:[3,5,8],area:0,arg:[1,3,5,6,7,8,9,10],argpars:7,argument:[1,3,5,6,7,8,9,10],argumenttypeerror:7,around:[1,5],arrai:[3,4,5,7,9],arriv:[1,5,7,8,9],arsen:7,arswat:7,articl:10,articletyp:10,asid:9,ask:[1,8],assess:5,assign:[3,5,9],assignedd:3,associ:[2,3,5,9],assum:[0,3,5,6,7,10],assumpt:[3,6,7],async:[1,8],asynchron:7,asyncio:7,attent:[3,6],attribut:[0,3,4,5,7,8,9],augment:9,augmented_norm:9,auth:7,author:[0,1],automat:[1,2,3,5,6,7,8,9,10],autoproxi:7,avail:[0,3,6,7,10],averag:[1,9],avoid:5,awak:[],awar:3,azzopardi:[1,9],back:[3,4,5,7,9],background:0,backlog:[],backward:5,balanc:5,base:[0,1,2,3,5,6,7,8,9],baselin:[0,1],basi:9,basic:[1,2,3,5,9,10],batch:[],becaus:[0,1,3,5,6,8,9,10],becom:[3,6,9],been:[1,7,8,9,10],befor:[0,1,3,5,6,7,8,9],beforehand:8,begin:[1,3,6,7,8],behavior:[0,6,9],behind:5,being:[0,1,6,8,9],belong:[0,5],better:0,between:[0,1,3,5,6,7,9],big:[1,3],bin:8,bin_siz:8,biographi:[],birth:10,bit:[],bleu:5,block:9,blueprint:6,bool:[0,1,3,6,7,8,9,10],bool_:3,boost:0,bootstrap:[2,7],bootstrapp:0,borrow:6,bot:[],both:[0,1,5,7],bottleneck:5,bound:[0,6,9],box:8,breviti:5,bridg:5,broad:6,broader:[],broadli:6,bucklei:3,buffer:[],buffered_consum:[],bufferedconsum:1,build:[1,3,5,9],built:5,bulk:[],bunch:8,bundl:10,burst:[1,6],burst_k:6,bursti:[],c_d:0,c_f:9,c_g:0,cach:[0,3,4,7],cache_dir:7,cache_exist:7,calcul:[0,1,3,5,6,8,9],call:[1,3,6,8,9],came:6,camel:3,camel_case_pattern:3,can:[0,1,3,4,5,6,7,8,9,10],candid:[0,1,5,7],candidate_fil:7,cannot:[3,4,5,6,7,9],capabl:3,capit:3,capitalize_first:3,captur:5,case_fold:3,cataldi:1,cdot:[0,3,6,9],cell:0,central:[1,5],centroid:[1,5,9],certain:[3,8,9],chang:[1,3,5,6,8,9],chapter:9,charact:[3,5,7,8],character:3,character_normalization_count:3,check:[1,3,4,5,6,7,8,9,10],checkpoint:[1,6],chi:7,chibootstrapp:[0,7],choic:5,choos:5,chosen:3,chronolog:5,chung:0,chunk:0,clean:3,cleaner:[1,2,5],clear:[1,6],close:[0,5,6,8],closest:9,cls:4,cluster:[1,2,6,7],clusteringalgorithm:9,clusternod:5,code:3,collaps:3,collapse_new_lin:3,collapse_whitespac:3,collecct:10,collect:[0,1,2,8,9,10],collect_recurs:10,collectd:1,collected_link:10,collector:10,column:0,com:[],combin:[0,3,6],come:[0,7],comm:7,command:[1,7],common:[0,5,6,7,9],commonli:[1,3],commun:[5,7],compar:[0,5,6,9],comparison:5,comparisonextractor:0,compat:6,compil:0,complement:[],complet:[1,3,5,6,8],complete_sent:3,complex:[0,9,10],compon:[3,5],comput:[0,1,3,5,6,9],concaten:[3,5,8,9],concept:[6,9,10],conceptu:5,concernedd:1,condit:5,configur:[2,3,7,8],conjunct:[1,3],connect:[6,7,8,10],consecut:[1,3,6],consid:[0,1,5,6,7,8],consist:0,constant:[3,8],constantli:1,construct:[1,3,5,7,9,10],construct_url:10,constructor:[0,1,3,5,7],consum:[2,5,7,8],consume_process:7,consumpt:[1,7],contain:[0,1,3,5,6,7,8,9,10],content:[1,2,3,10],context:6,contigu:3,conting:0,continu:[8,10],continuesreceiv:1,contrain:6,contrari:[1,8],contribut:3,control:[3,5,8],convers:[0,10],convert:[0,3,4,7],cooldown:1,copi:[3,6,9],corpora:[1,3,7,8],corpu:[1,2,3,5,7],correl:0,correspond:[3,5,6,7,8,9],cos_:9,cosd_:9,cosin:[5,9],cosine_dist:9,could:[8,10],count:[0,3,7,8],cover:[1,6],creat:[0,1,3,4,5,6,7,8,9],created_at:[5,8],creation:5,critic:6,cross:0,crucial:5,current:[5,6],custom:1,cutoff:0,d_u:[],data:[0,1,2,4,5,6,8],databas:6,dataset:7,date:10,dcf:0,dcf_t:0,deal:0,decai:[1,6],decay_r:6,decid:[1,5],decis:[5,6],decod:4,decor:8,decreas:10,deem:[],deep:6,def:8,defin:[0,1,3,4,5,6,8,9],definit:5,degre:6,delai:1,delin:6,denomin:[3,9],depend:[3,5,6,7,8,9],deploi:6,dequeu:1,dequeue_al:1,deriv:[6,9],descend:[5,6],describ:[0,8],design:[1,3,6,8],desir:[],detail:[1,3],detect:[1,2,5],detector:2,detriment:0,develop:[0,1],develpo:[],dict:[0,1,3,4,5,6,7,8,9,10],dictat:5,dictionari:[0,1,3,4,5,6,7,8,9,10],dictproxi:7,did:[],differ:[3,5,6,7,8,9,10],difficult:6,dimens:[1,3,9],direct:9,directli:3,directori:7,disabl:[1,3],disambigu:10,discard:1,discuss:[1,5,6],displai:3,disproportion:0,disregard:[],distanc:9,distinguish:3,distribut:0,diverg:[],divers:5,document:[1,6,7,8,9],documentnod:5,documet:[],docunet:5,doe:[0,3,5,6,7,8,9],doesn:0,doi:[],don:3,done:[4,7],doubl:8,down:[6,9],download:[3,8],drop:6,dummi:0,dummybootstrapp:0,dummycomparisonextractor:0,dummyextractor:0,duplic:7,dure:[1,6,9],dynam:[1,5,6],each:[0,1,3,5,6,7,8,9,10],earlier:[0,1],easi:[],easier:[1,3,6,10],easili:[0,3],edg:[],effect:6,effici:[6,9,10],efidf:0,either:[0,1,4,5,6,7,10],elaps:[5,8,9],eld:5,eldconsum:[1,6,7,9],element:1,els:[4,5,8],elsewher:9,emerg:[1,6],emoji:3,emot:[],empir:0,empti:[0,1,3,4,5,9],emul:8,enabl:3,encapsul:[1,5,6],encod:[4,7,8],encount:3,end:[0,1,3,6,7,8,9],endpoint:10,enforc:6,english:7,enough:6,enqueu:[1,8],ensur:[3,5],enter:1,entir:[6,8],entiti:[3,7],entityextractor:[],environ:1,equal:[0,1,3,5,6],equat:0,equival:[3,5,9],error:[0,1,3,4,8,10],especi:[0,1],essenti:[1,3,5],estim:0,euclidean:9,evalu:8,even:[0,5,6,9],event:[1,5,6,7,8],eventdt:[1,3,4,6,7,9,10],ever:5,everi:[0,1,7,8,9],exactli:1,examin:1,exampl:[0,1,3,5,6,8,9,10],exce:[5,8,9],except:[5,6,8],exclud:[0,6,7,10],exclus:[0,1,6],exist:[1,6,7,9],expect:[0,1,4,6,7,8,9,10],expens:10,experienc:1,experiment:8,expir:[1,5,8],expiri:5,explain:[5,6],exponenti:10,express:[0,3,10],extra:8,extract:[2,3,7,8,10],extract_timestamp:8,extractin:1,extractor:2,extrapol:2,f_i:9,facet:5,facil:5,facilit:8,fact:[3,5,9],factor:5,fail:[1,5],faith:1,fals:[0,1,3,6,7,8,9,10],far:[1,5,6,9],fast:6,faster:3,favor:5,favorit:[],featur:[3,6,8,9],fed:1,feed:8,fetch:[8,9,10],few:[0,1,5,8],fewer:[6,7,8],fidel:8,field:[0,8],fifo:1,file:[0,1,2,7],filenam:7,fileread:[1,8],filter:[1,2,7,8],filter_candid:7,find:[1,5,6,9,10],finish:[1,8],fire:6,fireconsum:[1,7],first:[0,1,3,5,6,7,8,9],flag:[1,7,8],flexibl:[1,5],flush:8,focu:0,focus:5,fold:3,follow:[0,1,3,5,8],foral:0,foreign:10,form:[5,6,10],former:3,formula:9,found:[0,7,8,10],frac:[0,3,6,9],fraction:[],fragment:[3,5],free:6,freez:[1,9],freeze_period:[1,9],frequenc:[6,7],frequent:0,from:[0,1,3,4,5,6,7,8,9,10],from_arrai:[3,4,5,9],from_docu:3,frozen:9,frozen_clust:9,fuel:6,full:[4,6,7],funaction:[],func:9,gain:[],game:[1,6],gener:[0,1,3,5,6,7,8,9,10],generate_candid:7,get:[0,1,3,4,5,6,7,8,9,10],get_all_docu:5,get_class:4,get_intra_similar:9,get_modul:4,get_representative_vector:9,get_tag:7,get_text:7,girvan:5,girvan_newman:5,give:[0,3,6],given:[0,1,3,4,5,6,7,8,9,10],global:[0,6],global_schem:3,goal:[3,5,9],goe:5,golstein:5,gomez:10,gone:6,good:9,goooaaaal:3,govern:8,graph:10,greater:[1,6],greatli:[5,6],greedi:5,ground:[],group:[5,8,9],grow:10,h_b:0,habit:0,half:[1,6,8],halv:[1,6],hand:[3,8],handl:8,handler:7,happen:[1,5,6,8,10],has:[0,1,3,5,6,7,8,9,10],hash:3,hashtag:3,hashtag_pattern:3,have:[0,1,3,4,5,6,7,8,9,10],head:1,hello:3,help:[3,4,6,7,8,10],helper:10,here:[3,6,9],hide:5,high:[0,3,8,9],higher:[0,1,3,4,6],highest:[5,9],highli:0,histor:6,hog:9,hood:10,hour:[7,8],how:[0,1,3,5,6,9],howev:[1,3,5,6,8,9],http:10,human:[1,5,6],hybrid:0,hypothesi:0,idea:5,ideal:1,ident:1,identifi:[0,1,3,5,6],idf:[1,7],idf_:3,idl:8,idli:1,ignor:[0,1,5,8],ignore_unknown:0,immedi:[1,5,8],implement:[0,1,3,4,5,6,7,8,9],importantli:[],impos:6,improv:[3,9],inact:[5,7,9],incid:0,includ:[0,1,3,4,5,6,7,8,9,10],inclus:[0,1,5,6,9],incom:[5,7,8,9],incomplet:3,inconsist:0,increas:6,increment:[1,9],indefinit:[1,7],independ:0,index:[2,6,7],indic:[0,1,3,6,7,8,9,10],individu:[1,6,9],inequ:9,infin:0,infinit:0,influenc:[3,5],info:[2,4],inform:[3,4,5,9,10],inherit:[3,4,5,7,9],initi:[1,3,4,5,6,9],inner:[],input:[0,1,5,6,7,8],instal:3,instanc:[1,3,4,5,6,9],instanti:[3,5,6],instead:[0,1,4,5,7,8,9],instruct:8,integ:[0,6,8,9,10],interest:1,interfac:[4,6,9,10],intern:10,interpret:6,intersect:9,intra:[7,9],introduc:[1,6],introduct:10,introduction_onli:10,intuit:0,invalid:[4,7],invok:[0,1,9],involv:3,is_error_respons:10,is_fil:7,is_json:7,is_person:10,isn:5,item:[0,1],iter:[0,5,7,9],its:[0,1,3,5,6,7,8,9],itself:[1,5,7],ivar:[],join:5,joint:0,joint_vocabulari:0,json:[0,4,7,8,10],just:[3,6,8,9],keep:[1,3,6,7,10],kei:[0,1,3,4,6,7,8,9,10],kept:7,keyerror:8,keyword:[0,1,3,5,7,8,9,10],kind:[0,1,3,5],kit:0,kleinberg:6,know:9,knowledg:[],known:0,kwarg:[1,3,5,6,7,8,9,10],lambda:[0,5],lang:7,languag:[2,7],laplac:3,larg:[0,1,3,5,6,8],larger:[1,6],largest:[1,5,8],last:[0,1,3,8,9],latenc:1,later:[1,5,6],latest:[5,9],latter:[3,5],lead:0,leagu:10,learn:[0,2,7],least:[0,3,5,9],leav:0,left:5,len:[3,8],length:[1,3,5,6,7,8],less:[0,1,5,6,7],let:10,letter:3,level:[4,8,10],lexicon:0,librari:9,lies:6,lifetim:5,like:[0,1,3,5,6,7,8,9,10],likeli:9,limit:10,line:[0,1,3,7,8],linguist:2,link:2,lionel:10,lisen:[],list:[0,1,3,4,5,6,7,8,9,10],listen:[1,2,7],listo:5,littl:[0,1,6],liu:0,live:1,load:[0,1,4,7],load_candid:7,load_se:7,local:[0,6],local_schem:3,log:[3,4,6,7],log_bp_i:0,log_tim:4,logarithm:6,logef:0,logger:2,loglevel:4,loglikelihoodratiobootstrapp:0,longer:5,look:[0,1,3,5,6,7,8,9,10],loop:7,lope:0,lose:6,lost:6,lot:[0,1,3,5,6,8,9],low:[0,3,8],lower:[0,9],lowercas:3,machin:[1,2,5],made:[0,1,3,5,9],magnitud:9,mai:[0,1,3,5,6,8,9],main:[0,3,5,7,9],maintain:[1,5,6,8,9],make:[1,3,5,6,8,9,10],mamo:3,manag:[5,7],manchest:3,manchesterunit:3,manhattan:9,mani:[0,3,8,9,10],manifest:9,manipul:[5,9],map:3,margin:1,mark:6,match:5,mathemat:9,matrix:5,max:7,max_candid:7,max_inact:[1,7],max_intra_similar:[1,7],max_lin:8,max_se:7,max_tim:[5,7,8],maxim:6,maximum:[0,1,5,6,7,8],mean:[0,1,3,4,5,6,8],meant:[0,1,3,6,8],meantim:8,measur:[0,5,6,9],mechan:[0,6],media:[],memori:9,memorynutritionstor:6,mention:[0,3,8,10],mention_pattern:3,mere:[1,8],messag:4,messi:10,met:5,meta:7,metadata:7,method:[0,1,5,6,7,9],metric:[0,9],metrid:6,middl:3,might:[0,1],mimick:1,min:7,min_burst:[1,6],min_length:3,min_similar:5,min_siz:[1,7],mine:[2,3],minim:[1,5],minimum:[0,1,3,5,6,7,9],minut:[1,7,8],miss:[3,10],misspel:0,mistak:3,mitig:3,mmr:1,mode:7,model:[2,6],modifi:8,modul:[2,4,5,6,10],mono:0,more:[0,1,3,5,6,7,9,10],moreov:[5,8],most:[0,1,3,5,6,7,8,9],mostli:0,move:[1,8],much:0,multipl:[0,1,3],multipli:3,multiprocess:7,must:[0,3,5,6,7,8,9],n_d:0,n_g:0,n_t:3,name:[1,3,4,7,8,9,10],namespac:7,natur:[1,2,6,7],navig:10,necessari:[1,4,5],necessarili:5,necessit:[0,5],need:[0,3,5,6,8,9,10],needless:[3,8],neg:[0,1,3,5,6,8],neither:[0,7],networkx:5,newer:[],newest:1,newlin:8,newman:5,next:1,nichola:3,nicholasmamo:3,nlp:[2,5,9],nltk:3,node:[],node_typ:5,noisi:3,nokmean:9,non:[5,6],none:[0,1,3,4,5,6,7,8,9,10],nor:0,normal:[1,3,4,5,7,8,9,10],normalize_special_charact:3,normalize_word:3,note:[0,3,5,6],noth:[0,1],notion:6,noun:[0,7],nterm:[],number:[0,1,3,5,6,7,8,9,10],number_pattern:3,nutr_:6,nutr_k:6,nutrit:[1,2],nutritionnutrit:[],nutritionstor:[1,6],nyphoon:[],oauth:7,oauthhandl:7,object:[0,1,2,3,4,6,7,8,9],observ:[0,6,9],obtain:[0,10],occur:0,occurr:0,off:6,offer:[0,4],often:[0,1,3,6,9],old:[1,3,5,6],older:1,oldest:1,on_data:8,on_error:8,onc:[3,9,10],one:[0,1,3,5,6,7,8,9,10],ones:[1,6],ongo:8,onli:[0,1,3,4,5,6,7,8,9,10],onlin:9,onward:6,open:[0,8],oper:[1,3,7,8,10],opportun:[1,8],option:[3,5,7],order:[1,3,5,6,8],orderedenum:4,org:10,origin:[0,1,3,5,6,7,8,9],other:[0,1,2,3,5,6,7,8,9,10],otherwis:[0,1,3,5,8,9,10],out:[0,1,6,7,8],outcom:0,outer:[],outgo:10,outlin:[0,1,6,9],output:[0,1,3,5,6,7,8],outsid:3,over:[0,5,6,7,8,9],overal:[3,6],overcom:5,overhead:6,overlin:0,overload:[],overrid:[],overriden:0,overwrit:6,overwritten:7,own:[1,3,5,9],p_d:0,p_g:0,p_i:[0,9],pace:8,packag:[0,1,3,5,6,8,10],page:10,pai:[3,6],pair:0,pairwis:5,paper:[0,1,6,9],papineni:[],param:8,paramet:[0,1,3,4,5,6,7,8,9,10],parent:3,paritit:[],park:0,pars:[0,10],part:[0,1,3,5,6,7,8],particip:[1,2,5,6],particular:[0,6,8,10],partit:[],pass:[1,3,5,7,8,9,10],past:6,path:[0,4,7],pattern:[0,3,6,10],peak:6,peer:0,penal:[3,6],penalti:[],pend:8,peopl:[6,10],per:8,perfectli:0,perform:[0,1,3,8,9,10],period:[1,3,5,6,7,8,9],person:[6,10],php:10,physic:[1,6],pick:[1,5],piec:3,pip:3,pivot:[6,8],place:0,plain:[3,10],plan:[],player:10,pmi:7,pmibootstrapp:[0,7],point:[0,1,5,6,8],pointer:8,polici:0,popul:1,popular:[0,3,6],porter:3,porterstemm:3,pos:3,posit:[0,5,6,10],possibl:[0,1,3,4,8,9],post:2,post_rat:6,practic:6,pre:[1,2,3,5],precis:[1,5],predict:8,predominantli:6,preferr:8,prefix:3,premedit:[],premier:10,prepar:[],prepare_output:7,present:[1,3,5,6,8],pretend:8,previou:[5,6],previous:[],primarili:0,principl:0,print:8,printconsum:[1,7],problem:[6,8],process:[0,1,2,5],processor:2,prod_:0,produc:[5,9],product:[0,3,5],program:7,progress:[6,8],project:10,promot:[0,3],proper:7,proper_noun:7,properti:[5,9],propos:[0,5],provid:[0,1,3,5,6,7,9,10],pseudo:[],publish:8,punctuat:3,punish:0,purpos:[0,3,6,9],python:[0,1,3,4,5,6,7,8,9,10],q_i:9,qualiti:5,quasi:[],queri:[5,10],queu:[],queue:[2,7,8],queuedlisten:[],queuedtweetlisten:8,quick:[3,8],quickli:8,r_b:0,r_d:0,rais:[0,3,4,5,6,7,8,9,10],rang:0,rank:[],rankextractor:0,rare:3,rate:[0,6,8],rather:5,ratio:6,reach:8,read:[1,3,6,7,8,9],reader:2,readi:8,readili:[3,10],real:[6,8,9],realiti:[3,5,6],realli:6,reason:[3,6,8],recalcul:9,recalculate_centroid:9,receiv:[1,3,5,6,7,8,9],recent:[5,6],recommend:5,reconaiss:1,record:[1,3,10],recurs:[4,10],redirect:10,reduc:3,redund:5,ref:[],refer:[0,1,3,4,5,6,8,9,10],reflect:0,regardless:5,regular:[3,10],rel:[6,7],relat:[5,7,9,10],relev:0,reli:8,reliabl:6,remov:[1,3,5,6,7,8,9],remove_alt_cod:3,remove_hashtag:3,remove_ment:3,remove_numb:3,remove_punctu:3,remove_retweet:7,remove_retweet_prefix:3,remove_unicode_ent:3,remove_url:3,reorder:5,repeat:[3,5,7],repetit:0,replac:[0,3],replace_ment:3,repli:[],replic:8,report:[1,6],repres:[0,1,3,5,6,7,8,9,10],represent:[3,5,9],representind:[],request:[9,10],requir:[0,3,4,6,7,8],rerank:5,research:0,reset:8,resid:3,resolv:[2,10],resourc:[3,5],respect:[0,3,4,6],respons:[3,5,8,10],rest:[3,5,8],restrict:[0,6],result:[1,3,6,8,10],retain:[3,5,7,8,9],retir:[5,9],retorn:[],retriev:[3,6,9,10],retrospect:[6,7],retweet:[1,3,7],retweeted_statu:8,revers:10,revert:10,revert_redirect:10,review:0,revolv:[1,5],role:1,root:6,routin:6,row:0,rtpye:9,rtype:8,rule:2,run:[1,3,6,7],runtimeerror:10,s_d:[],safe:1,said:[5,6,10],salton:3,same:[0,1,3,4,5,7,8,9],sampl:7,save:[3,7,8],save_meta:7,scheme:[0,1,7],schemescor:3,score:[0,3,5,7,8],scorer:[2,3],scratch:9,screen:3,script:[7,9],search:2,second:[1,5,6,7,8,9],see:9,seed:[0,7,10],seed_fil:7,seek:5,seen:6,select:[5,9],semant:0,semin:5,send:[8,10],sens:8,sensor:[1,6],sent:10,sentenc:[3,5],separ:[0,1,5,6,10],sequenc:0,seri:8,serial:7,serializ:[4,7],set:[0,1,3,4,5,6,7,8,9,10],set_logging_level:4,setup_arg:7,sever:[6,10],shallow:0,share:[6,7],sharp:6,shorter:5,shortest:[],should:[0,1,3,5,6,7,8,9,10],show:4,side:10,signifi:0,signific:[0,6],similar:[0,1,3,5,6,7,9],similarity_measur:9,similarli:[0,1],simpl:[0,3,5,6,8,10],simpli:[0,1,3,9,10],simplic:5,simul:1,simulatedbufferedconsum:1,simulatedfileread:8,simultan:[1,5,8],sinc:[0,3,5,6,8,9,10],singl:[0,3,9],siplit:1,situat:[1,8],size:[1,5,6,7,9],skeleton:0,skip:[1,7,8,9],skip_lin:8,skip_rat:8,skip_tim:[7,8],sleep:8,slew:[],slide:[1,6],slow:6,small:[0,9],smaller:6,smallest:1,smooth:3,snapshot:[],social:[1,6],solut:[1,8],some:[1,3,4,8,9],someon:[],someth:[5,6],sometim:10,soon:8,sort:[5,6],sought:[7,9],sourc:[],space:[2,3,8],spam:[],span:1,spars:1,speak:8,special:[0,1,5,9],specif:[1,3,5,6,8],specifi:[3,6,7,8,9],specificityextractor:0,sped:7,speech:[0,3,7],speed:[3,7,8],spend:[1,7,8],spent:8,spike:6,spite:5,split:[1,3,5,6,7],split_hashtag:3,sport:[1,6],sqrt:[6,9],squar:6,stage:6,stagger:[],staggeredfileread:8,standard:[0,3,6,10],start:[0,1,3,4,6,8,10],statconsum:[1,7],state:[1,5,6,8,9],statist:2,statu:8,steadi:8,stem:[0,1,3,7],stem_cach:3,stemmer:3,step:[1,3,5,6],still:[1,8],stop:[1,5,7,8],stopword:[3,7],storag:6,store:[0,1,2,3,4,5,7,8,9],store_frozen:9,str:[0,3,4,5,6,7,8,9,10],strain:8,stream:[1,6,7,8],stream_process:7,streamlisten:8,string:[0,1,3,4,5,7,8,10],strip:3,strong:0,structur:[0,1,5,6],studi:[1,6],subject:5,subset:0,succe:6,success:[],suffer:0,suffic:0,suffix:7,suggest:3,suitabl:6,sum:9,sum_:[0,6,9],summar:[1,2,3,6],summari:[1,2],summarization_bas:[],summarizationalgorithm:[5,6],summat:9,suppli:[1,3],support:[1,6,7,8,10],surg:1,surnam:10,surpris:0,symbol:[],symmetr:0,synchron:7,syntax:3,system:6,t_1:0,t_2:0,tab:3,tabl:[0,1,3,7],tackl:6,tag:[3,7],tail:[0,1],take:[0,1,3,5,9],taken:[0,6,8],talk:6,target:[0,5],task:[0,1,3,7,8],tdt:[0,1,2,3,4,5,7,8,9],tdtalgorithm:[1,6],techniqu:[5,6,9],tell:5,temporalnokmean:[1,9],tend:0,term:[1,2,6,7,8,9,10],termhood:0,terminolog:[0,6],termweight:3,termweightingschem:[1,3,7],test:[0,8],text:[0,2,3,5,7,8,9],textiowrapp:8,textual:5,tf_:3,tf_t:0,tfdcfextractor:0,tfextractor:0,tfidf:[0,1,3,7],tfidf_:3,tfidfextractor:0,than:[0,1,3,5,6,7,10],thei:[0,1,3,5,6,8,9,10],them:[0,1,3,5,6,7,8,9,10],theme:6,themselv:9,theori:0,thereefor:5,therefor:[0,1,3,5,6,8,9],thet:6,thi:[0,1,3,4,5,6,7,8,9,10],thing:6,those:[0,3,6],thought:6,thousand:[],three:[5,6,9],threshold:[1,7,8,9],through:[0,1,4,5,7,9,10],thu:[0,5,9],ties:1,time:[0,3,4,5,6,7,8,9,10],time_window:1,timeli:9,timelin:[0,1,2,6,7],timestamp:[1,5,6,8,9],timestamp_m:8,timestmap:6,titl:10,to_arrai:[3,4,5,7,9],to_list:0,togeth:[0,1,3,6,7,8,9],tokan:[],token:[0,1,2,5,7],tokenize_corpu:7,tokenize_pattern:3,tokenized_corpu:7,tokenizezr:[],too:[5,10],tool:[0,1,2,6],top:[0,8],topic:[1,2,7,9],topicalclusternod:5,total:[0,3],total_docu:0,track:[1,2,5,7,8,10],transform:[1,3],translat:0,tri:[5,6,7],triangl:9,trivial:3,tupl:[0,1,6,7],turn:0,tweepi:[7,8],tweet:[1,5,6,7],tweetclean:[1,3],tweetlisten:[1,7,8],twevent:7,twice:[],twitter:[0,1,2,3,4,6,7],two:[0,1,3,5,6,7,8,9],txt:7,type:[0,1,3,4,5,6,7,8,9,10],typo:0,unchang:6,uncommon:3,undefin:9,under:[8,10],underli:[1,3],understand:[1,5,7],understand_process:7,understood:[],undesir:3,unequ:5,unicod:[3,7],uniform:[3,6,9],union:9,uniqu:[3,5],unit:3,unix_ev:7,unknown:0,unless:5,unlik:[1,6,8],unpopular:6,unspecifi:9,until:[1,6,8],unus:9,updat:[1,7,9],update_scor:7,upenn_tagset:3,url:[3,10],url_pattern:3,usabl:1,use:[0,1,3,5,6,7,8,9,10],used:[0,1,3,5,6,7,8,9,10],useful:[0,8,10],useless:[],user:3,usernam:3,uses:[0,1,3,5,6,7,9,10],using:[0,1,3,5,6,7,8,9,10],usual:[3,5],v_b:0,v_d:0,v_f:9,v_n:9,vagu:5,valid:[1,4,10],valu:[0,1,3,4,5,6,7,8,9,10],valueerror:[0,3,4,5,6,7,8,9,10],vari:[5,6,8],variabl:[1,3,4,5,6,8,9,10],variant:9,variou:[],vartyp:[],vastli:6,vector:[2,3,5],vectori:[],vectorspac:[3,9],verb:7,veri:[0,1,3,5,6,9,10],version:3,versu:0,via:0,virtual:8,vocabulari:[0,7],volatil:8,volum:[1,6,8],vsm:[2,3],wai:[0,3,5,6],wait:[1,7,8],wake:1,want:3,warn:4,watford:7,weak:[0,1,3,4,5,6,8,9],weigh:3,weight:[0,1,2,5,7,9],well:[3,6,8],were:[0,7,8,10],what:[0,5,6,10],whatev:[1,5],whatsoev:[],when:[0,1,3,4,5,6,7,8,9,10],where:[0,1,3,4,5,6,7,8,9,10],wherea:[1,3,5],whether:[0,1,3,5,6,7,8,9,10],which:[0,1,3,4,5,6,7,8,9,10],white:3,whitespac:3,whose:[6,7,9,10],why:[6,9],wikimedia:10,wikinterfac:2,wikipedia:10,window:[6,8],within:8,without:[0,1,3,6,7,8,9,10],word:[0,3,6,7,9],word_normalization_pattern:3,work:[0,1,3,6,8],workflow:1,world:3,worth:[],would:[1,3,5,10],wouldn:9,wrap:[8,9],write:[0,7,8],written:[7,8],xclude:7,yet:[1,8,9],you:[1,3,4,5,6,7,8,9,10],your:[1,3],yourself:9,zaho:[],zero:[6,7,8],zhao:[],zhaoconsum:[1,7]},titles:["11. Automatic Term Extraction (ATE)","9. Consumers","Welcome to EvenTDT\u2019s documentation!","3. Natural Language Processing (NLP)","12. Other","7. Summarization","6. Topic Detection and Tracking (TDT)","1. Tools","8. Twitter","2. Vector Space Model (VSM)","4. Wikinterface"],titleterms:{"boolean":3,"class":[1,4],ATE:0,DGS:5,The:[0,1,5],aggreg:8,algorithm:[0,1,5,6,7,9],applic:0,automat:0,base:4,basic:0,bootstrap:0,buffer:1,carbonel:5,cataldi:6,chi:0,cleaner:3,cluster:[5,9],collect:7,common:3,comparison:0,consum:1,corpora:0,corpu:[0,8],data:7,detect:6,differ:0,disjoint:0,document:[0,2,3,5],domain:0,eld:[1,6],entropi:0,event:0,eventdt:2,extract:0,extractor:0,file:8,filler:3,fire:1,frequenc:[0,3],global:3,goldstein:5,graph:5,idf:[0,3],indic:2,info:10,inform:0,invers:[0,3],languag:3,likelihood:0,linguist:0,link:10,listen:8,local:3,log:0,logarithm:0,logger:4,mamo:[1,5,6],margin:5,math:9,maxim:5,mean:9,memori:6,mmr:5,model:9,mutual:0,natur:3,nlp:3,node:5,nutrit:6,object:5,other:4,pmi:0,pointwis:0,pre:7,print:1,probabl:0,process:[3,7,8],queu:8,queue:1,rank:0,ratio:0,reader:8,real:1,relev:5,scheme:3,search:10,simpl:1,simul:8,space:9,specif:0,squar:0,stagger:8,statist:[0,1],store:6,summar:5,summari:5,tabl:2,tdt:6,tempor:9,term:[0,3],text:10,time:1,timelin:5,token:3,tool:7,topic:[5,6],track:6,tweet:[3,8],twitter:8,variabl:0,vector:9,vsm:9,weight:3,welcom:2,wikinterfac:10,window:1,zhao:[1,6]}})