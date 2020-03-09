Search.setIndex({docnames:["apd","config","index","nlp","other","queues","summarization","tdt","tools","vsm","wikinterface"],envversion:{"sphinx.domains.c":1,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":1,"sphinx.domains.javascript":1,"sphinx.domains.math":2,"sphinx.domains.python":1,"sphinx.domains.rst":1,"sphinx.domains.std":1,sphinx:56},filenames:["apd.rst","config.rst","index.rst","nlp.rst","other.rst","queues.rst","summarization.rst","tdt.rst","tools.rst","vsm.rst","wikinterface.rst"],objects:{"":{apd:[0,0,0,"-"],config:[1,0,0,"-"],logger:[4,0,0,"-"],nlp:[3,0,0,"-"],objects:[4,0,0,"-"],summarization:[6,0,0,"-"],tdt:[7,0,0,"-"],tools:[8,0,0,"-"],vsm:[9,0,0,"-"],wikinterface:[10,0,0,"-"]},"apd.extractors":{extractor:[0,0,0,"-"]},"apd.extractors.extractor":{Extractor:[0,1,1,""]},"apd.extractors.extractor.Extractor":{__weakref__:[0,2,1,""],extract:[0,3,1,""]},"apd.extractors.local":{entity_extractor:[0,0,0,"-"],token_extractor:[0,0,0,"-"]},"apd.extractors.local.entity_extractor":{EntityExtractor:[0,1,1,""]},"apd.extractors.local.entity_extractor.EntityExtractor":{__init__:[0,3,1,""],_combine_adjacent_entities:[0,3,1,""],_extract_entities:[0,3,1,""],extract:[0,3,1,""]},"apd.extractors.local.token_extractor":{TokenExtractor:[0,1,1,""]},"apd.extractors.local.token_extractor.TokenExtractor":{__init__:[0,3,1,""],extract:[0,3,1,""]},"apd.extrapolators":{extrapolator:[0,0,0,"-"]},"apd.extrapolators.external":{wikipedia_extrapolator:[0,0,0,"-"]},"apd.extrapolators.external.wikipedia_extrapolator":{WikipediaExtrapolator:[0,1,1,""]},"apd.extrapolators.external.wikipedia_extrapolator.WikipediaExtrapolator":{__init__:[0,3,1,""],_add_to_graph:[0,3,1,""],_get_first_sentence:[0,3,1,""],_has_year:[0,3,1,""],_link_frequency:[0,3,1,""],_most_central_edge:[0,3,1,""],_remove_brackets:[0,3,1,""],extrapolate:[0,3,1,""]},"apd.extrapolators.extrapolator":{Extrapolator:[0,1,1,""]},"apd.extrapolators.extrapolator.Extrapolator":{__weakref__:[0,2,1,""],extrapolate:[0,3,1,""]},"apd.filters":{filter:[0,0,0,"-"]},"apd.filters.filter":{Filter:[0,1,1,""]},"apd.filters.filter.Filter":{__weakref__:[0,2,1,""],filter:[0,3,1,""]},"apd.filters.local":{threshold_filter:[0,0,0,"-"]},"apd.filters.local.threshold_filter":{ThresholdFilter:[0,1,1,""]},"apd.filters.local.threshold_filter.ThresholdFilter":{__init__:[0,3,1,""],filter:[0,3,1,""]},"apd.ner_participant_detector":{NERParticipantDetector:[0,1,1,""]},"apd.ner_participant_detector.NERParticipantDetector":{__init__:[0,3,1,""]},"apd.participant_detector":{ParticipantDetector:[0,1,1,""]},"apd.participant_detector.ParticipantDetector":{__init__:[0,3,1,""],__weakref__:[0,2,1,""],detect:[0,3,1,""]},"apd.postprocessors":{postprocessor:[0,0,0,"-"]},"apd.postprocessors.external":{wikipedia_postprocessor:[0,0,0,"-"]},"apd.postprocessors.external.wikipedia_postprocessor":{WikipediaPostprocessor:[0,1,1,""]},"apd.postprocessors.external.wikipedia_postprocessor.WikipediaPostprocessor":{__init__:[0,3,1,""],_get_surname:[0,3,1,""],_remove_accents:[0,3,1,""],_remove_brackets:[0,3,1,""],postprocess:[0,3,1,""]},"apd.postprocessors.postprocessor":{Postprocessor:[0,1,1,""]},"apd.postprocessors.postprocessor.Postprocessor":{__weakref__:[0,2,1,""],postprocess:[0,3,1,""]},"apd.resolvers":{resolver:[0,0,0,"-"]},"apd.resolvers.external":{wikipedia_name_resolver:[0,0,0,"-"],wikipedia_search_resolver:[0,0,0,"-"]},"apd.resolvers.external.wikipedia_name_resolver":{WikipediaNameResolver:[0,1,1,""]},"apd.resolvers.external.wikipedia_name_resolver.WikipediaNameResolver":{__init__:[0,3,1,""],_disambiguate:[0,3,1,""],_resolve_unambiguous_candidates:[0,3,1,""],resolve:[0,3,1,""]},"apd.resolvers.external.wikipedia_search_resolver":{WikipediaSearchResolver:[0,1,1,""]},"apd.resolvers.external.wikipedia_search_resolver.WikipediaSearchResolver":{__init__:[0,3,1,""],_compute_score:[0,3,1,""],_get_first_sentence:[0,3,1,""],_has_year:[0,3,1,""],_remove_brackets:[0,3,1,""],resolve:[0,3,1,""]},"apd.resolvers.local":{token_resolver:[0,0,0,"-"]},"apd.resolvers.local.token_resolver":{TokenResolver:[0,1,1,""]},"apd.resolvers.local.token_resolver.TokenResolver":{__init__:[0,3,1,""],_construct_inverted_index:[0,3,1,""],_minimize_inverted_index:[0,3,1,""],resolve:[0,3,1,""]},"apd.resolvers.resolver":{Resolver:[0,1,1,""]},"apd.resolvers.resolver.Resolver":{__weakref__:[0,2,1,""],resolve:[0,3,1,""]},"apd.scorers":{scorer:[0,0,0,"-"]},"apd.scorers.local":{df_scorer:[0,0,0,"-"],log_df_scorer:[0,0,0,"-"],log_tf_scorer:[0,0,0,"-"],tf_scorer:[0,0,0,"-"],tfidf_scorer:[0,0,0,"-"]},"apd.scorers.local.df_scorer":{DFScorer:[0,1,1,""]},"apd.scorers.local.df_scorer.DFScorer":{_normalize:[0,3,1,""],_sum:[0,3,1,""],score:[0,3,1,""]},"apd.scorers.local.log_df_scorer":{LogDFScorer:[0,1,1,""]},"apd.scorers.local.log_df_scorer.LogDFScorer":{__init__:[0,3,1,""],score:[0,3,1,""]},"apd.scorers.local.log_tf_scorer":{LogTFScorer:[0,1,1,""]},"apd.scorers.local.log_tf_scorer.LogTFScorer":{__init__:[0,3,1,""],score:[0,3,1,""]},"apd.scorers.local.tf_scorer":{TFScorer:[0,1,1,""]},"apd.scorers.local.tf_scorer.TFScorer":{_normalize:[0,3,1,""],_sum:[0,3,1,""],score:[0,3,1,""]},"apd.scorers.local.tfidf_scorer":{TFIDFScorer:[0,1,1,""]},"apd.scorers.local.tfidf_scorer.TFIDFScorer":{__init__:[0,3,1,""],_normalize:[0,3,1,""],score:[0,3,1,""]},"apd.scorers.scorer":{Scorer:[0,1,1,""]},"apd.scorers.scorer.Scorer":{__weakref__:[0,2,1,""],_normalize:[0,3,1,""],score:[0,3,1,""]},"config.example":{conf:[1,0,0,"-"]},"config.example.conf":{ACCOUNTS:[1,4,1,""],LOG_LEVEL:[1,4,1,""]},"logger.logger":{LogLevel:[4,1,1,""],error:[4,5,1,""],info:[4,5,1,""],log_time:[4,5,1,""],set_logging_level:[4,5,1,""],warning:[4,5,1,""]},"nlp.document":{Document:[3,1,1,""]},"nlp.document.Document":{__init__:[3,3,1,""],__str__:[3,3,1,""],concatenate:[3,3,1,""],from_array:[3,3,1,""],to_array:[3,3,1,""]},"nlp.term_weighting":{scheme:[3,0,0,"-"],tf:[3,0,0,"-"],tfidf:[3,0,0,"-"]},"nlp.term_weighting.global_schemes":{filler:[3,0,0,"-"],idf:[3,0,0,"-"]},"nlp.term_weighting.global_schemes.filler":{Filler:[3,1,1,""]},"nlp.term_weighting.global_schemes.filler.Filler":{score:[3,3,1,""]},"nlp.term_weighting.global_schemes.idf":{IDF:[3,1,1,""]},"nlp.term_weighting.global_schemes.idf.IDF":{__init__:[3,3,1,""],from_documents:[3,3,1,""],score:[3,3,1,""]},"nlp.term_weighting.local_schemes":{"boolean":[3,0,0,"-"],tf:[3,0,0,"-"]},"nlp.term_weighting.local_schemes.boolean":{Boolean:[3,1,1,""]},"nlp.term_weighting.local_schemes.boolean.Boolean":{score:[3,3,1,""]},"nlp.term_weighting.local_schemes.tf":{TF:[3,1,1,""]},"nlp.term_weighting.local_schemes.tf.TF":{score:[3,3,1,""]},"nlp.term_weighting.scheme":{SchemeScorer:[3,1,1,""],TermWeightingScheme:[3,1,1,""]},"nlp.term_weighting.scheme.SchemeScorer":{__weakref__:[3,2,1,""],score:[3,3,1,""]},"nlp.term_weighting.scheme.TermWeightingScheme":{__init__:[3,3,1,""],__weakref__:[3,2,1,""],create:[3,3,1,""]},"nlp.term_weighting.tf":{TF:[3,1,1,""]},"nlp.term_weighting.tf.TF":{__init__:[3,3,1,""]},"nlp.term_weighting.tfidf":{TFIDF:[3,1,1,""]},"nlp.term_weighting.tfidf.TFIDF":{__init__:[3,3,1,""]},"nlp.tokenizer":{Tokenizer:[3,1,1,""]},"nlp.tokenizer.Tokenizer":{__init__:[3,3,1,""],__weakref__:[3,2,1,""],_split_hashtags:[3,3,1,""],tokenize:[3,3,1,""]},"objects.attributable":{Attributable:[4,1,1,""]},"objects.attributable.Attributable":{__init__:[4,3,1,""],__weakref__:[4,2,1,""]},"objects.exportable":{Exportable:[4,1,1,""]},"objects.exportable.Exportable":{__weakref__:[4,2,1,""],from_array:[4,3,1,""],get_class:[4,3,1,""],get_module:[4,3,1,""],to_array:[4,3,1,""]},"queues.queue":{queue:[5,0,0,"-"]},"queues.queue.queue":{Queue:[5,1,1,""]},"queues.queue.queue.Queue":{__init__:[5,3,1,""],__weakref__:[5,2,1,""],dequeue:[5,3,1,""],dequeue_all:[5,3,1,""],empty:[5,3,1,""],enqueue:[5,3,1,""],head:[5,3,1,""],length:[5,3,1,""],tail:[5,3,1,""]},"summarization.algorithms":{mmr:[6,0,0,"-"],summarization:[6,0,0,"-"]},"summarization.algorithms.mmr":{MMR:[6,1,1,""]},"summarization.algorithms.mmr.MMR":{_compute_query:[6,3,1,""],_compute_scores:[6,3,1,""],_compute_similarity_matrix:[6,3,1,""],_filter_documents:[6,3,1,""],_get_next_document:[6,3,1,""],summarize:[6,3,1,""]},"summarization.algorithms.summarization":{SummarizationAlgorithm:[6,1,1,""]},"summarization.algorithms.summarization.SummarizationAlgorithm":{__weakref__:[6,2,1,""],summarize:[6,3,1,""]},"summarization.summary":{Summary:[6,1,1,""]},"summarization.summary.Summary":{__init__:[6,3,1,""],__str__:[6,3,1,""],documents:[6,3,1,""],from_array:[6,3,1,""],to_array:[6,3,1,""]},"tdt.algorithms":{cataldi:[7,0,0,"-"],eld:[7,0,0,"-"],tdt:[7,0,0,"-"],zhao:[7,0,0,"-"]},"tdt.algorithms.cataldi":{Cataldi:[7,1,1,""]},"tdt.algorithms.cataldi.Cataldi":{__init__:[7,3,1,""],_compute_burst:[7,3,1,""],_compute_burst_drops:[7,3,1,""],_get_bursty_terms:[7,3,1,""],_get_critical_drop_index:[7,3,1,""],detect:[7,3,1,""]},"tdt.algorithms.eld":{ELD:[7,1,1,""]},"tdt.algorithms.eld.ELD":{__init__:[7,3,1,""],_compute_burst:[7,3,1,""],_compute_coefficient:[7,3,1,""],_compute_decay:[7,3,1,""],detect:[7,3,1,""]},"tdt.algorithms.tdt":{TDTAlgorithm:[7,1,1,""]},"tdt.algorithms.tdt.TDTAlgorithm":{__weakref__:[7,2,1,""],detect:[7,3,1,""]},"tdt.algorithms.zhao":{Zhao:[7,1,1,""]},"tdt.algorithms.zhao.Zhao":{__init__:[7,3,1,""],detect:[7,3,1,""]},"tdt.nutrition":{memory:[7,0,0,"-"],store:[7,0,0,"-"]},"tdt.nutrition.memory":{MemoryNutritionStore:[7,1,1,""]},"tdt.nutrition.memory.MemoryNutritionStore":{__init__:[7,3,1,""],add:[7,3,1,""],all:[7,3,1,""],between:[7,3,1,""],get:[7,3,1,""],remove:[7,3,1,""]},"tdt.nutrition.store":{NutritionStore:[7,1,1,""]},"tdt.nutrition.store.NutritionStore":{__init__:[7,3,1,""],__weakref__:[7,2,1,""],add:[7,3,1,""],all:[7,3,1,""],between:[7,3,1,""],get:[7,3,1,""],remove:[7,3,1,""],since:[7,3,1,""],until:[7,3,1,""]},"tools.collect":{collect:[8,5,1,""],main:[8,5,1,""],save_meta:[8,5,1,""],setup_args:[8,5,1,""]},"vsm.clustering":{cluster:[9,0,0,"-"]},"vsm.clustering.algorithms":{clustering:[9,0,0,"-"],no_k_means:[9,0,0,"-"],temporal_no_k_means:[9,0,0,"-"]},"vsm.clustering.algorithms.clustering":{ClusteringAlgorithm:[9,1,1,""]},"vsm.clustering.algorithms.clustering.ClusteringAlgorithm":{__init__:[9,3,1,""],__weakref__:[9,2,1,""],cluster:[9,3,1,""]},"vsm.clustering.algorithms.no_k_means":{NoKMeans:[9,1,1,""]},"vsm.clustering.algorithms.no_k_means.NoKMeans":{__init__:[9,3,1,""],_closest_cluster:[9,3,1,""],_freeze:[9,3,1,""],_reset_age:[9,3,1,""],_to_freeze:[9,3,1,""],_update_age:[9,3,1,""],cluster:[9,3,1,""]},"vsm.clustering.algorithms.temporal_no_k_means":{TemporalNoKMeans:[9,1,1,""]},"vsm.clustering.algorithms.temporal_no_k_means.TemporalNoKMeans":{__init__:[9,3,1,""],_update_age:[9,3,1,""],cluster:[9,3,1,""]},"vsm.clustering.cluster":{Cluster:[9,1,1,""]},"vsm.clustering.cluster.Cluster":{__init__:[9,3,1,""],centroid:[9,3,1,""],from_array:[9,3,1,""],get_intra_similarity:[9,3,1,""],get_representative_vectors:[9,3,1,""],recalculate_centroid:[9,3,1,""],similarity:[9,3,1,""],size:[9,3,1,""],to_array:[9,3,1,""],vectors:[9,3,1,""]},"vsm.vector":{Vector:[9,1,1,""],VectorSpace:[9,1,1,""]},"vsm.vector.Vector":{__init__:[9,3,1,""],copy:[9,3,1,""],dimensions:[9,3,1,""],from_array:[9,3,1,""],normalize:[9,3,1,""],to_array:[9,3,1,""]},"vsm.vector.VectorSpace":{__getitem__:[9,3,1,""],__weakref__:[9,2,1,""]},"vsm.vector_math":{augmented_normalize:[9,5,1,""],concatenate:[9,5,1,""],cosine:[9,5,1,""],cosine_distance:[9,5,1,""],euclidean:[9,5,1,""],magnitude:[9,5,1,""],manhattan:[9,5,1,""],normalize:[9,5,1,""]},"wikinterface.info":{ArticleType:[10,1,1,""],is_person:[10,5,1,""],types:[10,5,1,""]},"wikinterface.links":{_get_all_links:[10,5,1,""],_get_intro_links:[10,5,1,""],collect:[10,5,1,""],collect_recursive:[10,5,1,""]},"wikinterface.search":{collect:[10,5,1,""]},"wikinterface.text":{collect:[10,5,1,""]},apd:{ner_participant_detector:[0,0,0,"-"],participant_detector:[0,0,0,"-"]},logger:{logger:[4,0,0,"-"]},nlp:{document:[3,0,0,"-"],term_weighting:[3,0,0,"-"],tokenizer:[3,0,0,"-"]},objects:{attributable:[4,0,0,"-"],exportable:[4,0,0,"-"]},summarization:{summary:[6,0,0,"-"]},tools:{collect:[8,0,0,"-"]},vsm:{vector:[9,0,0,"-"],vector_math:[9,0,0,"-"]},wikinterface:{API_ENDPOINT:[10,4,1,""],construct_url:[10,5,1,""],info:[10,0,0,"-"],is_error_response:[10,5,1,""],links:[10,0,0,"-"],revert_redirects:[10,5,1,""],search:[10,0,0,"-"],text:[10,0,0,"-"]}},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","attribute","Python attribute"],"3":["py","method","Python method"],"4":["py","data","Python data"],"5":["py","function","Python function"]},objtypes:{"0":"py:module","1":"py:class","2":"py:attribute","3":"py:method","4":"py:data","5":"py:function"},terms:{"abstract":[0,3,4,6,7,9],"boolean":[0,3,9,10],"break":7,"case":[0,3,7],"class":[0,2,3,5,6,7,9,10],"default":[0,6,7,8,9],"export":[3,4,6,9],"float":[0,6,7,9],"function":[0,3,4,5,6,7,9,10],"import":[3,4,7],"int":[0,1,3,5,7,8,9,10],"long":9,"new":[0,3,4,5,6,9,10],"return":[0,3,4,5,6,7,8,9,10],"static":[3,4,6,9],"true":[0,3,10],"try":[0,7],Aging:7,For:[0,3,7],Its:0,The:[0,1,3,4,5,6,7,8,9,10],Their:10,Then:[0,3,7],There:0,These:[0,3,6,7,10],Use:6,__getitem__:9,__init__:[0,3,4,5,6,7,9],__repr__:[],__str__:[3,6],__weakref__:[0,3,4,5,6,7,9],_add_to_graph:0,_closest_clust:9,_combine_adjacent_ent:0,_compute_burst:7,_compute_burst_drop:7,_compute_coeffici:7,_compute_decai:7,_compute_queri:6,_compute_scor:[0,6],_compute_similarity_matrix:6,_construct_inverted_index:0,_dimens:[],_disambigu:0,_extract_ent:0,_filter_docu:6,_freez:9,_frozen_clust:[],_get_all_link:10,_get_bursty_term:7,_get_critical_drop_index:7,_get_first_sent:0,_get_intro_link:10,_get_next_docu:6,_get_surnam:0,_has_year:0,_how_:7,_link_frequ:0,_minimize_inverted_index:0,_most_central_edg:0,_normal:0,_process_hashtag:[],_remove_acc:0,_remove_bracket:0,_reset_ag:9,_resolve_unambiguous_candid:0,_split_hashtag:3,_sum:0,_to_freez:9,_update_ag:9,_what_:7,about:[0,3,8,9,10],accent:[0,3],accept:[0,3,6,7,8],access:10,access_token:1,access_token_secret:1,accord:[0,3,7,10],account:[1,8],account_:[],accumul:[7,9],across:0,activ:9,actual:[0,3,6],add:[0,3,4,5,6,7],add_vector:[],added:[0,5,6,9,10],adding:9,addit:[0,3,4,8,9,10],adopt:[3,7],after:[0,7],age:9,aim:[0,9],algorithm:[0,2],all:[0,3,5,6,7,8,9],allow:[],almost:0,alon:7,alreadi:[6,10],also:[0,3,6,7,9],alt:3,altern:0,although:6,altogeth:10,alwai:6,ambigu:0,among:7,amount:9,analog:0,anew:0,ani:[0,3,5,6,7,8,9,10],anoth:[0,6,7],anymor:9,apd:2,api:[0,1,8,10],api_endpoint:10,appear:[0,3,7,10],appli:0,applic:4,approach:[3,6,7],arg:[0,3,5,6,7,8,9,10],argument:[3,5,7,8,9,10],around:[0,6],arrai:[3,4,6,9],arriv:9,arsen:8,arswat:8,articl:[0,10],articletyp:10,assign:[0,3,6],associ:[0,3,9],assum:[0,3,6,9,10],assumpt:3,attribut:[3,4,6,9],augment:9,augmented_norm:9,auth:8,automat:2,avail:[3,6,7,8,9],averag:[7,9],avoid:[],azzopardi:9,back:4,barcelona:0,base:[0,2,3,5,6,7,9],baselin:0,basi:[3,9],basic:[0,10],becaus:[7,9],becom:0,been:[9,10],befor:[1,3,7,9],begin:[3,7],being:[0,6,7,9],below:0,between:[0,3,5,6,7,9],beyond:0,bias:0,bigger:7,binari:0,bind:7,birth:10,block:9,bool:[0,3,7,9,10],bool_:3,borrow:7,both:7,bound:[0,7],bracket:0,broad:7,broader:7,broadli:7,build:[3,6,9],built:6,burst:7,burst_k:7,bursti:7,calcul:[7,9],call:[0,7,9],came:7,camel:3,can:[0,3,4,5,6,7,9,10],candid:[0,6],cannot:6,capabl:[],care:0,case_fold:[0,3],cataldi:[],cdot:[3,7,9],central:0,centroid:[6,9],certain:[0,9],chain:0,chang:[0,3,7,9],charact:[3,6],character:3,character_normalization_count:3,check:[0,3,9,10],checkpoint:7,chronolog:[],chunk:0,clear:7,clear_dimens:[],closest:9,cls:4,cluster:[2,7],clusteringalgorithm:9,code:3,collect:[2,5,9,10],collect_recurs:10,collected_link:10,collector:10,colloqui:0,combin:[0,3,7],come:8,command:8,common:0,commonli:[0,3],commun:0,compar:[0,6,7,9],complet:3,compon:[0,3,7],comput:[0,3,6,7,9],concaten:[3,6,9],concept:[0,7],conclud:0,conf:1,config:1,configur:[2,8],conjunct:[0,3],connect:8,consid:[0,6,7],consist:9,constraint:0,construct:[0,3,6,10],construct_url:10,constructor:[0,3,8],consum:5,consumer_kei:1,consumer_secret:1,contain:[0,3,6,7,9,10],content:[2,10],context:7,continu:10,contrain:7,contrast:0,control:3,convert:3,copi:[1,9],corpora:8,corpu:[0,8],correspond:[0,3,7],cos_:9,cosd_:9,cosin:9,cosine_dist:9,could:[0,10],count:0,creat:[0,3,4,5,6,7,8,9],creation:[],credenti:1,credibl:0,critic:7,critical_drop_index:7,current:[7,9,10],cut:0,data:[2,5,6,7],databas:7,dataset:8,date:10,decai:7,decay_r:7,decreas:0,deem:0,defin:[0,3,4,5,6,7,9],definit:0,degre:7,denomin:7,depend:[0,3],dequeu:5,dequeue_al:5,descend:[0,7],describ:[0,8,9],design:7,desir:10,detail:1,detect:[2,6],detector:0,develop:7,df_scorer:[],dfscorer:0,dict:[0,1,3,4,6,7,8,9,10],dictionari:[0,3,4,6,7,9,10],differ:[0,1,3,8,9],dimens:[0,3,9],directli:3,directori:8,disambigu:[0,10],discard:0,discuss:7,disproportion:0,distanc:9,distinguish:[0,3],divers:6,document:[0,6,7,9],documentsc:0,doe:[0,6,9],domain:0,draw:7,drop:7,due:0,each:[0,3,6,7,8,9,10],earlier:0,easi:10,easier:[3,10],edg:0,effici:7,either:10,eixst:[],eld:7,element:5,elsewher:0,emerg:7,emoji:3,empti:[0,4,5,9],emul:0,enabl:0,encapsul:[6,7],end:[0,3,5,7],endpoint:10,english:8,enough:[0,9],enqueu:5,enter:5,entir:7,entiti:[0,3],entity_extractor:[],entityextractor:0,equal:[3,6],equat:7,equival:[3,6,9],error:[4,10],essenti:6,euclidean:9,event:[0,7,8],event_:[],eventdt:[1,3,4,5,7,8,9],exampl:[0,1,7],exce:9,except:0,exclud:[0,10],exclus:7,exist:[0,7,9,10],expans:0,expect:[0,7,9,10],expens:10,explain:6,exploit:0,exponenti:[7,10],express:3,extend:0,extern:[],extract:[0,10],extractor:2,extrapol:2,f_i:9,f_j:[],factor:[0,7],fail:10,fals:[0,3,7,9,10],far:[6,7],featur:[3,7,9],fetch:[0,9,10],field:[3,9],fifo:5,fifth:0,file:8,filenam:8,fill:1,fill_:3,filler:3,filter:2,find:[0,3,7],fire:7,first:[0,3,5,7,8,9],first_level_link:0,first_level_similar:0,fold:[0,3],follow:[3,6,7],form:[0,7,10],formal:0,format:0,former:[3,7],formula:[7,9],found:[0,10],fourth:0,frac:[3,7,9],freez:9,freeze_period:9,frequenc:[0,3],from:[0,3,4,6,7,8,9,10],from_arrai:[3,4,6,9],from_docu:3,frozen:9,frozen_clust:9,full:[0,4],func:9,furthermor:[],gain:7,game:7,gener:[0,6,7,9],get:[0,3,4,5,6,7,8,9,10],get_class:4,get_dimens:[],get_intra_similar:9,get_modul:4,get_representative_vector:9,girvan:0,give:[0,3,7],given:[0,3,4,5,6,7,8,9,10],global:[],global_schem:3,goal:6,goe:0,graph:0,greatli:[6,7],greedi:6,group:9,grow:10,half:7,halv:7,handl:[0,7],handler:8,happen:[3,7],has:[0,6,7,8,9,10],hash:3,hashtag:3,have:[0,3,4,6,7,9,10],head:5,heart:7,help:[4,8,9,10],here:0,high:9,higher:[0,3,4],highest:[0,7,9],histor:7,hog:9,hour:8,how:7,howev:[0,3,6,7],http:10,human:[6,7],ideal:6,ident:0,identifi:[0,7],idf:[0,3],idf_:3,implement:[0,4,5,6,7,8],inact:9,includ:[0,3,4,5,6,7,9],inclus:[6,7,9],incom:9,increas:7,increment:9,index:[0,2,7,8],indexerror:9,indic:[0,3,7,9,10],individu:[0,7],info:[2,4],inform:[0,3,4,6,10],inherit:0,initi:[3,4,9],initialize_dimens:[],inner:[0,7],input:[0,7],instanc:[0,3,4,6,9],instanti:[3,9],instead:[0,4,5,9],integ:[7,9,10],interfac:[4,7,10],interpret:7,intersect:9,intra:9,introduc:[5,7],introduct:10,introduction_onli:10,invalid:[0,4],invers:3,invert:0,inverted_index:0,is_error_respons:10,is_person:10,isol:7,its:[0,3,8,9],itself:6,job:0,json:[4,8],just:[7,9],keep:[3,7,8,9],keep_redirect:[],kei:[0,3,4,6,7,9,10],keyerror:[],keyword:[0,3,8,9,10],kind:5,knowledg:0,known:0,kwarg:[0,3,6,7,8,9,10],lambda:6,lang:8,languag:[2,8,9],larg:0,larger:7,last:[0,5,7,9],later:[3,7],latest:10,latter:[3,7],leak:[],learn:[3,8,9],least:[3,6,9],length:[3,5,6,8],less:[0,7],level:[0,1,4,10],lies:7,likeli:9,limit:10,line:8,link:[0,2],list:[0,1,3,4,5,6,7,8,9,10],listen:8,littl:7,load:4,local:7,local_schem:3,log:[0,1,3,4,7],log_df_scor:[],log_level:1,log_tf_scor:[],log_tim:4,logarithm:[0,7],logdfscor:0,logger:[1,2],loglevel:[1,4],logtfscor:0,longer:9,look:[0,6,10],loop:8,lose:7,low:0,lower:0,lowercas:3,machin:6,made:[0,3,6,10],magnitud:9,mai:[0,3,6,9],main:[0,3,8],maintain:9,make:[0,3,6,9,10],mamo:[],manhattan:9,mani:0,map:0,margin:6,mark:7,match:0,math:2,mathemat:9,matrix:6,maxim:[6,9],maximum:[0,6],mean:[0,9],meant:9,measur:7,mechan:7,memori:[7,9],memorynutritionstor:7,mention:[3,10],messag:4,meta:8,metadata:8,method:[0,6,7,9],metric:[7,9],might:0,min_burst:7,min_length:3,minim:[0,9],minimum:[0,3,7,9],minut:[0,8],miss:10,mmr:6,mode:8,model:[2,3,7],modifi:0,modul:[2,4,7,10],more:[0,3,6,8,9,10],most:[0,3,7,9],much:7,multipl:[0,3],multipli:3,must:[3,6,7,8],n_t:3,name:[0,4,9,10],natur:[2,7,8,9],necessari:6,necessit:7,need:[3,7,10],neg:[0,3,7],ner:0,ner_participant_detector:[],nerparticipantdetector:0,nest:0,networkx:0,newest:5,newman:0,next:[0,6],nlp:[0,2,9],nltk:[0,3],node:0,nokmean:9,non:[6,7,9],none:[0,3,4,5,6,7,8,9,10],normal:[0,3,4,5,9,10],normalize_scor:0,normalize_special_charact:3,normalize_word:3,notat:3,note:[0,3],noth:5,notion:7,number:[0,3,7,8,9,10],nutr_:7,nutr_k:7,nutrit:2,nutritionstor:7,oauth:8,oauthhandl:8,object:[0,3,4,5,6,7,9],obtain:10,occur:9,off:[0,7],offer:4,often:[0,3,10],old:7,older:7,oldest:5,onc:10,one:[0,3,6,8,9],onli:[0,4,6,7,9,10],onward:7,oper:[0,8,10],option:[3,8],order:[0,5,7],ordered_enum:[],orderedenum:4,org:10,origin:[0,3],other:[0,2,3,5,6,7,10],otherwis:[0,3,9,10],out:[0,3,5,6,9],outer:0,outgo:[0,10],outgoing_link:0,outlin:7,output:[0,6,8],output_:[],outsid:3,over:[0,9],overcom:0,overhead:7,overli:0,overload:10,overwrit:7,own:8,p_i:9,page:[0,2,10],pair:[0,9],paper:[],param:[],paramat:0,paramet:[0,3,4,6,7,8,9,10],particip:[2,7],participant_detector:[],participantdetector:0,particular:[0,7,10],pass:[3,8,9,10],past:7,path:[0,4],penal:3,perform:0,period:[7,8,9],person:[0,7,10],php:10,physic:7,pivot:7,plain:[3,10],point:0,popular:[3,7],porter:3,porterstemm:3,posit:[6,7,10],possibl:0,post_rat:7,postproces:0,postprocess:0,postprocessor:2,potenti:0,praticip:0,predominantli:[7,10],present:[6,7],previou:[0,7],problem:0,process:[0,2,5,9],produc:6,product:[0,9],program:8,progress:7,promot:3,proper:0,properti:[3,6,9],proport:0,provid:[0,3,5,9,10],publish:9,punctuat:3,python:[0,1,3,4,5,6,7,8,9,10],q_i:9,queri:6,queue:2,rac:[],radic:0,rais:[0,3,4,5,6,7,9,10],rank:0,rare:3,rate:7,ratio:7,read:[3,8,9],real:[0,7,9],reason:[0,3],recalcul:9,recalculate_centroid:9,receiv:[0,3,5,7,9],recent:[7,9],recognit:0,recurs:10,redirect:10,reduc:[0,3],redund:6,refer:[0,3,4,5,6,7,9],relat:[8,9],relev:[0,6],relevan:0,remain:0,remov:[0,3,5,7,9],remove_acc:0,remove_alt_cod:3,remove_bracket:0,remove_hashtag:3,remove_ment:3,remove_numb:3,remove_punctu:3,remove_unicode_ent:3,remove_url:3,remove_vector:[],reorder:6,repeat:3,replac:[0,3],repres:[0,3,7,9,10],represent:[0,3,6,9],request:[9,10],requir:[0,3,4,8],rerank:6,rescal:[0,7],research:9,reset:9,resolut:0,resolv:[2,10],respect:[0,4,6,7],respons:[0,7,10],result:[0,7,10],retain:[0,3,9],retir:9,retorn:10,retriev:[0,7],retrospect:7,revert:10,revert_redirect:10,revis:10,revolv:0,routin:7,rtpye:9,rtype:[],run:[7,8],runtimeerror:10,said:0,same:[0,3,4,5,9],save:8,save_meta:8,scheme:0,schemescor:3,score:[0,3,6,9],scorer:[2,3],script:8,search:[0,2],second:[0,3,7,8,9],second_level_link:0,second_level_similar:0,secondli:0,seed:10,seek:0,seen:7,select:[6,7],send:10,sensor:7,sentenc:[0,6],separ:[0,7,10],set:[0,1,3,4,7,8,9,10],set_dimens:[],set_logging_level:4,setup_arg:8,sfrac:[],share:0,shorter:6,shortest:0,should:[0,3,7,8,9,10],show:4,signific:7,similar:[0,6,9],similarity_measur:9,similarli:0,simpl:[0,3,7],simplest:[0,3],simpli:[0,3],simplic:0,simultan:[6,9],sinc:[3,7,9],singl:[0,9,10],six:0,sixth:0,size:9,slide:7,slow:0,smallest:9,social:7,some:4,someth:7,sort:[0,7],sought:9,sourc:0,space:[2,3],special:5,specif:[5,6],specifi:0,spend:8,spike:7,split:[3,7],split_hashtag:3,sport:7,sqrt:[7,9],sqrt_:[],start:[4,7,10],state:[6,7,9],stem:[0,3],stemmer:3,step:[0,3],still:0,stopword:3,storag:7,store:[2,3,4,6,8,9],store_frozen:9,str:[0,3,4,6,7,8,9,10],stream:7,string:[0,3,4,6,10],structur:[5,7],studi:7,subject:[0,9],subtract:9,succe:7,suitabl:7,sum:[],sum_:[7,9],summar:2,summari:6,summarizationalgorithm:6,summat:0,suppli:3,surnam:0,surname_onli:0,synchron:8,system:7,tabl:[0,3],tag:3,tail:5,take:[0,3,5,6,9,10],taken:[0,7],target:0,task:[3,9],tdt:[0,2,3,4,5,6,8,9],tdtalgorithm:7,techniqu:7,tempor:9,temporalnokmean:9,term:[0,2,7,10],term_weight:[],terminolog:7,termweight:3,termweightingschem:[0,3],text:[0,2,3,6],tf_:3,tf_scorer:[],tfidf:[0,3],tfidf_:3,tfidf_scor:[],tfidfscor:0,tfscorer:0,than:[0,3,6,7,9],thei:[0,3,6,7,9,10],them:[0,3,5,6,7,8,9],themselv:6,therefor:[0,6,7],thet:7,thi:[0,3,5,6,7,8,9,10],thing:9,third:0,those:[0,3,7,10],three:0,threshold:[0,9],threshold_filt:[],thresholdfilt:0,through:[0,10],thu:[0,6,7],tightli:0,time:[0,3,4,7,8,9],time_attribut:[],timelin:[7,8],timestamp:[7,9],timestmap:7,titl:[0,10],to_arrai:[3,4,6,9],todo:[],togeth:[0,8,9],token:[0,2],token_extractor:[],token_resolv:[],tokenextractor:0,tokenresolv:0,too:[],tool:2,top:0,topic:[2,6],topmost:0,total:3,toward:0,track:[2,6,8],track_:[],tradition:3,transform:[0,3],tree:0,tri:0,tupl:[0,7,9],turn:[],tweepi:8,tweet:[5,8],tweetlisten:8,twevent:8,twice:0,twitter:[1,4,7,8],two:[0,3,7],type:[0,3,4,5,6,7,8,9,10],typeerror:9,unambigu:0,unchang:7,uncommon:3,understand:[6,8],understanding_:[],unicod:3,union:9,uniqu:6,unlik:[0,5],unresolv:0,unset:[],until:7,updat:9,upon:9,url:[3,10],use:[0,3,6,7,8,9,10],used:[0,3,6,7,9,10],useless:6,uses:[0,3,7,10],using:[0,1,3,7,9,10],usual:0,v_1:[],v_2:[],v_n:9,valid:[4,10],valu:[0,3,4,6,7,9,10],valueerror:[0,3,4,5,6,7,9,10],vari:[6,7],variabl:[0,1,3,4,5,6,7,9,10],variant:9,variou:[],vector:[2,3,6],vector_math:[],vectorspac:9,veri:[0,3,10],volum:7,vsm:[2,3,6],w_i:[],wai:[0,3,5],warn:4,watford:8,weak:[0,3,4,5,6,7,9],weigh:3,weight:[0,2,6,7,9],well:[0,6,7],were:0,what:6,whatsoev:0,when:[0,3,4,5,6,7,9,10],where:[0,3,7,8,9,10],whether:[0,3,9,10],which:[0,3,4,6,7,9,10],whole:0,whose:[0,7,9,10],why:0,wikimedia:10,wikinterfac:2,wikipedia:[0,10],wikipedia_extrapol:[],wikipedia_name_resolv:[],wikipedia_postprocessor:[],wikipedia_search_resolv:[],wikipediaextrapol:0,wikipedianameresolv:0,wikipediapostprocessor:0,wikipediasearchresolv:0,window:7,within:0,without:[0,5,9,10],word:[0,3,7],work:[0,3,7,9],worth:7,would:7,write:8,written:8,wrong:7,x_j:[],xxxxxxxxxxxxxxxxxxxxxxxxx:1,xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx:1,xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx:1,year:0,you:[4,8,9],zero:[7,9],zhao:[]},titles:["5. Automatic Participant Detection (APD)","0. Configuration","Welcome to EvenTDT\u2019s documentation!","3. Natural Language Processing (NLP)","9. Other","8. Queues","7. Summarization","6. Topic Detection and Tracking (TDT)","1. Tools","2. Vector Space Model (VSM)","4. Wikinterface"],titleterms:{"class":4,algorithm:[6,7,9],apd:0,automat:0,base:4,carbonel:6,cataldi:7,cluster:9,collect:8,common:3,configur:1,data:8,detect:[0,7],document:[2,3],eventdt:2,extern:0,extractor:0,extrapol:0,filter:0,global:3,goldstein:6,indic:2,info:10,languag:3,link:10,local:[0,3],logger:4,mamo:7,math:9,model:9,natur:3,nlp:3,nutrit:7,other:4,particip:0,postprocessor:0,process:3,queue:5,resolv:0,scheme:3,scorer:0,search:10,space:9,store:7,summar:6,tabl:2,tdt:7,term:3,text:10,token:3,tool:8,topic:7,track:7,vector:9,vsm:9,weight:3,welcom:2,wikinterfac:10,zhao:7}})