Search.setIndex({docnames:["consumers","index","nlp","other","summarization","tdt","tools","vsm","wikinterface"],envversion:{"sphinx.domains.c":1,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":1,"sphinx.domains.javascript":1,"sphinx.domains.math":2,"sphinx.domains.python":1,"sphinx.domains.rst":1,"sphinx.domains.std":1,sphinx:56},filenames:["consumers.rst","index.rst","nlp.rst","other.rst","summarization.rst","tdt.rst","tools.rst","vsm.rst","wikinterface.rst"],objects:{"":{logger:[3,0,0,"-"],nlp:[2,0,0,"-"],objects:[3,0,0,"-"],summarization:[4,0,0,"-"],tdt:[5,0,0,"-"],tools:[6,0,0,"-"],vsm:[7,0,0,"-"],wikinterface:[8,0,0,"-"]},"logger.logger":{LogLevel:[3,1,1,""],error:[3,2,1,""],info:[3,2,1,""],log_time:[3,2,1,""],set_logging_level:[3,2,1,""],warning:[3,2,1,""]},"nlp.cleaners":{Cleaner:[2,1,1,""],tweet_cleaner:[2,0,0,"-"]},"nlp.cleaners.Cleaner":{__init__:[2,3,1,""],__weakref__:[2,4,1,""],clean:[2,3,1,""]},"nlp.cleaners.tweet_cleaner":{TweetCleaner:[2,1,1,""]},"nlp.cleaners.tweet_cleaner.TweetCleaner":{__init__:[2,3,1,""],clean:[2,3,1,""]},"nlp.document":{Document:[2,1,1,""]},"nlp.document.Document":{__init__:[2,3,1,""],__str__:[2,3,1,""],concatenate:[2,3,1,""],copy:[2,3,1,""],from_array:[2,3,1,""],to_array:[2,3,1,""]},"nlp.tokenizer":{Tokenizer:[2,1,1,""]},"nlp.tokenizer.Tokenizer":{__init__:[2,3,1,""],__weakref__:[2,4,1,""],pos:[2,4,1,""],tokenize:[2,3,1,""]},"nlp.weighting":{SchemeScorer:[2,1,1,""],TermWeightingScheme:[2,1,1,""],global_schemes:[2,0,0,"-"],local_schemes:[2,0,0,"-"],tf:[2,0,0,"-"],tfidf:[2,0,0,"-"]},"nlp.weighting.SchemeScorer":{__weakref__:[2,4,1,""],score:[2,3,1,""]},"nlp.weighting.TermWeightingScheme":{__init__:[2,3,1,""],__weakref__:[2,4,1,""],create:[2,3,1,""]},"nlp.weighting.global_schemes":{filler:[2,0,0,"-"],idf:[2,0,0,"-"]},"nlp.weighting.global_schemes.filler":{Filler:[2,1,1,""]},"nlp.weighting.global_schemes.filler.Filler":{score:[2,3,1,""]},"nlp.weighting.global_schemes.idf":{IDF:[2,1,1,""]},"nlp.weighting.global_schemes.idf.IDF":{__init__:[2,3,1,""],from_array:[2,3,1,""],from_documents:[2,3,1,""],score:[2,3,1,""],to_array:[2,3,1,""]},"nlp.weighting.local_schemes":{"boolean":[2,0,0,"-"],tf:[2,0,0,"-"]},"nlp.weighting.local_schemes.boolean":{Boolean:[2,1,1,""]},"nlp.weighting.local_schemes.boolean.Boolean":{score:[2,3,1,""]},"nlp.weighting.local_schemes.tf":{TF:[2,1,1,""]},"nlp.weighting.local_schemes.tf.TF":{score:[2,3,1,""]},"nlp.weighting.tf":{TF:[2,1,1,""]},"nlp.weighting.tf.TF":{__init__:[2,3,1,""]},"nlp.weighting.tfidf":{TFIDF:[2,1,1,""]},"nlp.weighting.tfidf.TFIDF":{__init__:[2,3,1,""],from_array:[2,3,1,""],to_array:[2,3,1,""]},"objects.attributable":{Attributable:[3,1,1,""]},"objects.attributable.Attributable":{__init__:[3,3,1,""],__weakref__:[3,4,1,""]},"objects.exportable":{Exportable:[3,1,1,""]},"objects.exportable.Exportable":{__weakref__:[3,4,1,""],decode:[3,3,1,""],encode:[3,3,1,""],from_array:[3,3,1,""],get_class:[3,3,1,""],get_module:[3,3,1,""],to_array:[3,3,1,""]},"queues.consumers":{buffered_consumer:[0,0,0,"-"],consumer:[0,0,0,"-"],eld_consumer:[0,0,0,"-"],fire_consumer:[0,0,0,"-"],print_consumer:[0,0,0,"-"],stat_consumer:[0,0,0,"-"],zhao_consumer:[0,0,0,"-"]},"queues.consumers.buffered_consumer":{BufferedConsumer:[0,1,1,""],SimulatedBufferedConsumer:[0,1,1,""]},"queues.consumers.buffered_consumer.BufferedConsumer":{__init__:[0,3,1,""],_consume:[0,3,1,""],_process:[0,3,1,""],_sleep:[0,3,1,""],run:[0,3,1,""]},"queues.consumers.buffered_consumer.SimulatedBufferedConsumer":{__init__:[0,3,1,""],_sleep:[0,3,1,""]},"queues.consumers.consumer":{Consumer:[0,1,1,""]},"queues.consumers.consumer.Consumer":{__init__:[0,3,1,""],__weakref__:[0,4,1,""],_consume:[0,3,1,""],_started:[0,3,1,""],_stopped:[0,3,1,""],_wait_for_input:[0,3,1,""],run:[0,3,1,""],stop:[0,3,1,""]},"queues.consumers.eld_consumer":{ELDConsumer:[0,1,1,""]},"queues.consumers.eld_consumer.ELDConsumer":{__init__:[0,3,1,""],_brevity_score:[0,3,1,""],_cluster:[0,3,1,""],_construct_idf:[0,3,1,""],_consume:[0,3,1,""],_create_checkpoint:[0,3,1,""],_detect_participants:[0,3,1,""],_detect_topics:[0,3,1,""],_emotion_score:[0,3,1,""],_filter_clusters:[0,3,1,""],_filter_tweets:[0,3,1,""],_latest_timestamp:[0,3,1,""],_remove_old_checkpoints:[0,3,1,""],_score_documents:[0,3,1,""],_to_documents:[0,3,1,""],buffer:[0,4,1,""],min_burst:[0,4,1,""],understand:[0,3,1,""]},"queues.consumers.fire_consumer":{FIREConsumer:[0,1,1,""]},"queues.consumers.fire_consumer.FIREConsumer":{__init__:[0,3,1,""],_cluster:[0,3,1,""],_create_checkpoint:[0,3,1,""],_detect_topics:[0,3,1,""],_filter_clusters:[0,3,1,""],_filter_documents:[0,3,1,""],_filter_tweets:[0,3,1,""],_latest_timestamp:[0,3,1,""],_process:[0,3,1,""],_remove_old_checkpoints:[0,3,1,""],_to_documents:[0,3,1,""]},"queues.consumers.print_consumer":{PrintConsumer:[0,1,1,""]},"queues.consumers.print_consumer.PrintConsumer":{_consume:[0,3,1,""]},"queues.consumers.stat_consumer":{StatConsumer:[0,1,1,""]},"queues.consumers.stat_consumer.StatConsumer":{_process:[0,3,1,""]},"queues.consumers.zhao_consumer":{ZhaoConsumer:[0,1,1,""]},"queues.consumers.zhao_consumer.ZhaoConsumer":{__init__:[0,3,1,""],_add_documents:[0,3,1,""],_create_checkpoint:[0,3,1,""],_detect_topics:[0,3,1,""],_documents_since:[0,3,1,""],_latest_timestamp:[0,3,1,""],_process:[0,3,1,""],_remove_documents_before:[0,3,1,""],_to_documents:[0,3,1,""]},"queues.queue":{Queue:[0,1,1,""]},"queues.queue.Queue":{__init__:[0,3,1,""],__weakref__:[0,4,1,""],dequeue:[0,3,1,""],dequeue_all:[0,3,1,""],empty:[0,3,1,""],enqueue:[0,3,1,""],head:[0,3,1,""],length:[0,3,1,""],tail:[0,3,1,""]},"summarization.algorithms":{SummarizationAlgorithm:[4,1,1,""],dgs:[4,0,0,"-"],mmr:[4,0,0,"-"]},"summarization.algorithms.SummarizationAlgorithm":{__weakref__:[4,4,1,""],summarize:[4,3,1,""]},"summarization.algorithms.dgs":{DGS:[4,1,1,""]},"summarization.algorithms.dgs.DGS":{__init__:[4,3,1,""],summarize:[4,3,1,""]},"summarization.algorithms.mmr":{MMR:[4,1,1,""]},"summarization.algorithms.mmr.MMR":{__init__:[4,3,1,""],summarize:[4,3,1,""]},"summarization.summary":{Summary:[4,1,1,""]},"summarization.summary.Summary":{__init__:[4,3,1,""],__str__:[4,3,1,""],documents:[4,3,1,""],from_array:[4,3,1,""],to_array:[4,3,1,""]},"summarization.timeline":{timeline:[4,0,0,"-"]},"summarization.timeline.nodes":{cluster_node:[4,0,0,"-"],document_node:[4,0,0,"-"],node:[4,0,0,"-"],topical_cluster_node:[4,0,0,"-"]},"summarization.timeline.nodes.cluster_node":{ClusterNode:[4,1,1,""]},"summarization.timeline.nodes.cluster_node.ClusterNode":{__init__:[4,3,1,""],add:[4,3,1,""],from_array:[4,3,1,""],get_all_documents:[4,3,1,""],similarity:[4,3,1,""],to_array:[4,3,1,""]},"summarization.timeline.nodes.document_node":{DocumentNode:[4,1,1,""]},"summarization.timeline.nodes.document_node.DocumentNode":{__init__:[4,3,1,""],add:[4,3,1,""],from_array:[4,3,1,""],get_all_documents:[4,3,1,""],similarity:[4,3,1,""],to_array:[4,3,1,""]},"summarization.timeline.nodes.node":{Node:[4,1,1,""]},"summarization.timeline.nodes.node.Node":{__init__:[4,3,1,""],add:[4,3,1,""],expired:[4,3,1,""],get_all_documents:[4,3,1,""],similarity:[4,3,1,""]},"summarization.timeline.nodes.topical_cluster_node":{TopicalClusterNode:[4,1,1,""]},"summarization.timeline.nodes.topical_cluster_node.TopicalClusterNode":{__init__:[4,3,1,""],add:[4,3,1,""],from_array:[4,3,1,""],similarity:[4,3,1,""],to_array:[4,3,1,""]},"summarization.timeline.timeline":{Timeline:[4,1,1,""]},"summarization.timeline.timeline.Timeline":{__init__:[4,3,1,""],add:[4,3,1,""],from_array:[4,3,1,""],to_array:[4,3,1,""]},"tdt.algorithms":{TDTAlgorithm:[5,1,1,""],cataldi:[5,0,0,"-"],eld:[5,0,0,"-"],zhao:[5,0,0,"-"]},"tdt.algorithms.TDTAlgorithm":{__weakref__:[5,4,1,""],detect:[5,3,1,""]},"tdt.algorithms.cataldi":{Cataldi:[5,1,1,""]},"tdt.algorithms.cataldi.Cataldi":{__init__:[5,3,1,""],detect:[5,3,1,""]},"tdt.algorithms.eld":{ELD:[5,1,1,""]},"tdt.algorithms.eld.ELD":{__init__:[5,3,1,""],detect:[5,3,1,""]},"tdt.algorithms.zhao":{Zhao:[5,1,1,""]},"tdt.algorithms.zhao.Zhao":{__init__:[5,3,1,""],detect:[5,3,1,""]},"tdt.nutrition":{NutritionStore:[5,1,1,""],memory:[5,0,0,"-"]},"tdt.nutrition.NutritionStore":{__init__:[5,3,1,""],__weakref__:[5,4,1,""],add:[5,3,1,""],all:[5,3,1,""],between:[5,3,1,""],copy:[5,3,1,""],get:[5,3,1,""],remove:[5,3,1,""],since:[5,3,1,""],until:[5,3,1,""]},"tdt.nutrition.memory":{MemoryNutritionStore:[5,1,1,""]},"tdt.nutrition.memory.MemoryNutritionStore":{__init__:[5,3,1,""],add:[5,3,1,""],all:[5,3,1,""],between:[5,3,1,""],copy:[5,3,1,""],get:[5,3,1,""],remove:[5,3,1,""]},"tools.bootstrap":{bootstrap:[6,2,1,""],filter_candidates:[6,2,1,""],generate_candidates:[6,2,1,""],load_candidates:[6,2,1,""],load_seed:[6,2,1,""],main:[6,2,1,""],method:[6,2,1,""],setup_args:[6,2,1,""],update_scores:[6,2,1,""]},"tools.collect":{collect:[6,2,1,""],main:[6,2,1,""],save_meta:[6,2,1,""],setup_args:[6,2,1,""]},"tools.consume":{consume:[6,2,1,""],consume_process:[6,2,1,""],consumer:[6,2,1,""],main:[6,2,1,""],scheme:[6,2,1,""],setup_args:[6,2,1,""],stream_process:[6,2,1,""],understand:[6,2,1,""],understand_process:[6,2,1,""]},"tools.idf":{construct:[6,2,1,""],main:[6,2,1,""],save:[6,2,1,""],setup_args:[6,2,1,""],tokenize:[6,2,1,""],update:[6,2,1,""]},"tools.tokenizer":{get_tags:[6,2,1,""],get_text:[6,2,1,""],main:[6,2,1,""],prepare_output:[6,2,1,""],setup_args:[6,2,1,""],tokenize_corpus:[6,2,1,""]},"vsm.clustering":{algorithms:[7,0,0,"-"],cluster:[7,0,0,"-"]},"vsm.clustering.algorithms":{ClusteringAlgorithm:[7,1,1,""],no_k_means:[7,0,0,"-"],temporal_no_k_means:[7,0,0,"-"]},"vsm.clustering.algorithms.ClusteringAlgorithm":{__init__:[7,3,1,""],__weakref__:[7,4,1,""],cluster:[7,3,1,""]},"vsm.clustering.algorithms.no_k_means":{NoKMeans:[7,1,1,""]},"vsm.clustering.algorithms.no_k_means.NoKMeans":{__init__:[7,3,1,""],cluster:[7,3,1,""]},"vsm.clustering.algorithms.temporal_no_k_means":{TemporalNoKMeans:[7,1,1,""]},"vsm.clustering.algorithms.temporal_no_k_means.TemporalNoKMeans":{__init__:[7,3,1,""],cluster:[7,3,1,""]},"vsm.clustering.cluster":{Cluster:[7,1,1,""]},"vsm.clustering.cluster.Cluster":{__init__:[7,3,1,""],centroid:[7,3,1,""],from_array:[7,3,1,""],get_intra_similarity:[7,3,1,""],get_representative_vectors:[7,3,1,""],recalculate_centroid:[7,3,1,""],similarity:[7,3,1,""],size:[7,3,1,""],to_array:[7,3,1,""],vectors:[7,3,1,""]},"vsm.vector":{Vector:[7,1,1,""],VectorSpace:[7,1,1,""]},"vsm.vector.Vector":{__init__:[7,3,1,""],copy:[7,3,1,""],dimensions:[7,3,1,""],from_array:[7,3,1,""],normalize:[7,3,1,""],to_array:[7,3,1,""]},"vsm.vector.VectorSpace":{__getitem__:[7,3,1,""],__weakref__:[7,4,1,""]},"vsm.vector_math":{augmented_normalize:[7,2,1,""],concatenate:[7,2,1,""],cosine:[7,2,1,""],cosine_distance:[7,2,1,""],euclidean:[7,2,1,""],magnitude:[7,2,1,""],manhattan:[7,2,1,""],normalize:[7,2,1,""]},"wikinterface.info":{ArticleType:[8,1,1,""],is_person:[8,2,1,""],types:[8,2,1,""]},"wikinterface.links":{collect:[8,2,1,""],collect_recursive:[8,2,1,""]},"wikinterface.search":{collect:[8,2,1,""]},"wikinterface.text":{collect:[8,2,1,""]},logger:{logger:[3,0,0,"-"]},nlp:{cleaners:[2,0,0,"-"],document:[2,0,0,"-"],tokenizer:[2,0,0,"-"],weighting:[2,0,0,"-"]},objects:{attributable:[3,0,0,"-"],exportable:[3,0,0,"-"]},queues:{queue:[0,0,0,"-"]},summarization:{algorithms:[4,0,0,"-"],summary:[4,0,0,"-"]},tdt:{algorithms:[5,0,0,"-"],nutrition:[5,0,0,"-"]},tools:{bootstrap:[6,0,0,"-"],cache_exists:[6,2,1,""],collect:[6,0,0,"-"],consume:[6,0,0,"-"],idf:[6,0,0,"-"],is_file:[6,2,1,""],is_json:[6,2,1,""],load:[6,2,1,""],meta:[6,2,1,""],save:[6,2,1,""],tokenizer:[6,0,0,"-"]},vsm:{vector:[7,0,0,"-"],vector_math:[7,0,0,"-"]},wikinterface:{API_ENDPOINT:[8,5,1,""],construct_url:[8,2,1,""],info:[8,0,0,"-"],is_error_response:[8,2,1,""],links:[8,0,0,"-"],revert_redirects:[8,2,1,""],search:[8,0,0,"-"],text:[8,0,0,"-"]}},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","function","Python function"],"3":["py","method","Python method"],"4":["py","attribute","Python attribute"],"5":["py","data","Python data"]},objtypes:{"0":"py:module","1":"py:class","2":"py:function","3":"py:method","4":"py:attribute","5":"py:data"},terms:{"abstract":[0,2,3,4,5,7],"boolean":[0,6,7,8],"break":[0,5,7],"case":[0,2,4,5,8],"class":[0,1,2,4,5,6,7,8],"default":[0,2,4,5,6,7,8],"enum":8,"export":[2,3,4,6,7],"final":[2,5],"float":[0,4,5,6,7],"function":[0,2,3,4,5,6,7,8],"import":[0,2,3,5,7],"int":[0,2,5,6,7,8],"long":[0,7],"new":[0,2,3,4,5,6,7,8],"public":0,"return":[0,2,3,4,5,6,7,8],"static":[2,3,4,7],"true":[0,2,7,8],"try":[3,5],"while":[0,4],ATE:1,Aging:5,DGS:[0,4],For:[2,4,5,7,8],Not:2,That:[0,2,7],The:[0,1,2,3,5,6,7,8],Their:8,Then:[2,5],There:0,These:[0,2,5,8],Use:4,Used:[0,6],With:[],__getitem__:7,__init__:[0,2,3,4,5,6,7],__str__:[2,4],__weakref__:[0,2,3,4,5,7],_add_docu:0,_all_:7,_brevity_scor:0,_cluster:0,_compute_queri:[],_compute_scor:[],_compute_similarity_matrix:[],_construct_idf:0,_consum:0,_creat:[],_create_checkpoint:0,_detect_particip:0,_detect_top:0,_documents_sinc:0,_emotion_scor:0,_extract_commun:[],_filter_clust:0,_filter_docu:0,_filter_tweet:0,_get_next_docu:[],_how_:[],_largest_commun:[],_latest_timestamp:0,_most_central_edg:[],_process:0,_remove_documents_befor:0,_remove_old_checkpoint:0,_score_docu:0,_sleep:0,_start:0,_stop:0,_summarization_bas:[],_to_docu:0,_to_graph:[],_unixselectoreventloop:6,_wait_for_input:0,_what_:[],about:[0,2,4,5,6,7,8],absolut:0,absorb:4,accent:2,accept:[0,2,4,5,6,7],access:[4,7,8],accompani:[2,4],accord:[2,4,5,8],account:6,accumul:0,accuraci:5,achiev:[5,7],acm:0,across:[2,5,7,8],action:8,activ:[0,4,7],actual:2,add:[0,2,3,4,5,6,7],added:[0,4,7,8],adding:7,addit:[0,2,3,4,5,6,7,8],adject:6,adopt:[2,5],advantag:7,adverb:6,affect:[0,5],after:[0,2,5,6,7],again:[2,7],ago:0,akin:0,algorithm:1,all:[0,2,4,5,6,7,8],allow:[0,7],almost:0,alon:[],along:7,alongsid:2,alreadi:[0,4,6,8],also:[0,2,4,5,7],alt:2,alt_code_pattern:2,altern:[4,6],although:[5,7,8],altogeth:8,alwai:[0,2,4,5,6,7,8],among:[0,5],amount:6,ani:[0,2,4,5,6,7,8],anoth:[4,5],anyth:3,apart:[0,2,5],apd:[0,1],api:[6,8],api_endpoint:8,appear:[2,5],appli:5,applic:[1,2,3,4,5],approach:[0,2,4,5,7],appropri:2,arg:[0,2,4,5,6,7,8],argpars:6,argument:[0,2,4,5,6,7,8],argumenttypeerror:6,around:[0,4],arrai:[2,3,4,6,7],arriv:[0,6,7],arsen:6,arswat:6,articl:8,articletyp:8,asid:7,ask:0,assign:[2,4,7],assignedd:2,associ:[1,2,4,7],assum:[0,2,4,5,6,8],assumpt:[2,5,6],async:0,asynchron:6,asyncio:6,attent:[2,5],attribut:[0,2,3,4,6,7],augment:7,augmented_norm:7,auth:6,author:0,automat:[0,1,2,4,5,6,7,8],autoproxi:6,avail:[0,2,5,6,8],averag:[0,7],awak:0,awar:2,azzopardi:[0,7],back:[2,3,4,6,7],backlog:0,base:[0,1,2,4,5,6,7],basi:7,basic:[1,2,4,7,8],batch:0,becaus:[0,2,4,5,7,8],becom:[0,2,5,7],been:[0,6,7,8],befor:[0,2,4,5,6,7],begin:[2,5,6],behavior:[5,7],being:[4,5,7],belong:4,between:[0,2,4,5,6,7],big:[0,2],biographi:0,birth:8,bit:0,bleu:0,block:7,blueprint:5,bool:[0,2,5,6,7,8],bool_:2,bootstrap:[1,6],borrow:5,bot:0,both:[0,6],bound:[0,5,7],breviti:[0,4],broad:5,broader:[],broadli:5,bucklei:2,buffer:0,bufferedconsum:0,build:[0,2,4,7],built:4,bundl:8,burst:[0,5],burst_k:5,bursti:0,c_f:7,cach:[2,3,6],cache_dir:6,cache_exist:6,calcul:[0,2,4,5,7],call:[0,2,5,7],came:5,camel:2,camel_case_pattern:2,can:[0,2,3,4,5,6,7,8],candid:[0,6],candidate_fil:6,cannot:[0,2,3,4,5,6,7],capabl:2,capit:[0,2],capitalize_first:2,captur:4,case_fold:2,cataldi:0,cdot:[2,5,7],central:[],centroid:[0,4,7],certain:[2,4,7],chang:[0,2,4,5,7],chapter:7,charact:[0,2,4,6],character:2,character_normalization_count:2,check:[0,2,3,4,5,6,7,8],checkpoint:[0,5],chi:6,chibootstrapp:6,chosen:2,chronolog:[0,4],clean:2,cleaner:[0,1,4],clear:[0,5],close:5,closest:7,cls:3,cluster:[0,1,4,5,6],clusteringalgorithm:7,clusternod:4,code:2,collaps:2,collapse_new_lin:2,collapse_whitespac:2,collecct:8,collect:[0,1,7,8],collect_recurs:8,collected_link:8,collector:8,com:[],combin:[2,5],come:6,comm:6,command:6,common:[0,5,6,7],commonli:2,commun:[0,4,6],compar:[5,7],comparison:4,compat:5,complement:0,complet:[2,5],complete_sent:2,complex:[7,8],compon:[0,2,4],comput:[0,2,4,5,7],concaten:[2,4,7],concept:[5,7,8],configur:[1,2,6],conjunct:[0,2],connect:[5,6,8],consecut:[0,2,5],consid:[0,4,5,6],constant:2,construct:[0,2,4,6,7,8],construct_url:8,constructor:[0,2,6],consum:[1,6],consume_process:6,consumpt:[0,6],contain:[0,2,4,5,6,7,8],content:[0,1,2,8],context:5,contigu:2,continu:[0,8],contrain:5,contrari:0,contribut:2,control:2,convers:[0,8],convert:[0,2,3,4,6],cooldown:0,copi:[0,2,5,7],corpora:[2,6],corpu:[2,6],correspond:[2,4,5,6,7],cos_:7,cosd_:7,cosin:7,cosine_dist:7,could:[0,8],count:[0,2,6],cover:[0,5],creat:[0,2,3,4,5,6,7],created_at:4,critic:5,current:[0,4,5],custom:0,d_u:0,data:[0,1,3,4,5],databas:5,dataset:6,date:8,decai:[0,5],decay_r:5,decid:4,decis:5,decod:3,decreas:8,deem:0,deep:5,defin:[0,2,3,4,5,7],degre:5,delai:0,delin:5,denomin:[2,7],depend:[0,2,5,6,7],deploi:5,dequeu:0,dequeue_al:0,deriv:[5,7],descend:[0,5],design:[2,5],desir:0,detail:2,detect:[0,1,4],detector:1,develop:0,develpo:0,dict:[0,2,3,4,5,6,7,8],dictat:4,dictionari:[0,2,3,4,5,6,7,8],dictproxi:6,did:[],differ:[0,2,4,5,6,7,8],difficult:5,dimens:[0,2,7],direct:7,directli:2,directori:6,disabl:[0,2],disambigu:8,discard:0,discuss:[0,5],displai:2,disregard:0,distanc:7,distinguish:2,divers:4,document:[0,4,5,6,7],documentnod:4,documet:0,docunet:4,doe:[2,4,5,6,7],doesn:4,doi:0,don:2,done:[0,3,6],down:[5,7],download:2,drop:5,duplic:6,dure:[5,7],dynam:[0,4,5],each:[0,2,4,5,6,7,8],easi:[],easier:[2,5,8],easili:2,edg:[],effect:5,effici:[5,7,8],either:[3,4,5,6,8],elaps:[0,7],eld:[0,4],eldconsum:[0,5,6,7],element:0,els:3,elsewher:7,emerg:[0,5],emoji:2,emot:0,empti:[0,2,3,4,7],enabl:2,encapsul:[4,5],encod:[3,6],encount:2,end:[0,2,5,6,7],endpoint:8,enforc:5,english:[0,6],enough:5,enqueu:0,ensur:[0,2],enter:0,entir:[0,5],entiti:[0,2,6],entityextractor:0,environ:0,equal:[0,2,4,5],equival:[2,4,7],error:[2,3,8],essenti:[2,4],euclidean:7,evalu:0,even:[0,4,5,7],event:[0,4,5,6],eventdt:[0,2,3,5,6,7,8],ever:4,everi:[0,6,7],exactli:0,examin:0,exampl:[2,4,5,7,8],exce:7,except:5,exclud:[5,6,8],exclus:[0,5],exist:[0,5,6,7],expect:[3,5,6,7,8],expens:8,expir:[0,4],expiri:4,explain:[4,5],exponenti:8,express:[2,8],extract:[1,2,6,8],extractin:0,extractor:1,extrapol:1,f_i:7,facet:4,facilit:4,fact:[2,7],fail:[],fals:[0,2,5,6,7,8],far:[0,5,7],fast:5,faster:2,favorit:0,featur:[2,5,7],fetch:[7,8],fewer:[5,6],field:0,fifo:0,file:[0,6],filenam:6,filter:[0,1,6],filter_candid:6,find:[0,4,5,7,8],finish:0,fire:[0,5],fireconsum:[0,6],first:[0,2,4,5,6,7],flag:[0,6],fold:2,follow:[0,2,4],foreign:8,form:[0,4,5,8],former:2,formula:7,found:[0,6,8],frac:[0,2,5,7],fraction:0,fragment:2,free:5,freez:[0,7],freeze_period:[0,7],frequenc:[5,6],from:[0,2,3,4,5,6,7,8],from_arrai:[2,3,4,7],from_docu:2,frozen:7,frozen_clust:7,fuel:5,full:[3,5,6],funaction:[],func:7,gain:[],game:[0,5],gener:[0,2,4,5,6,7,8],generate_candid:6,get:[0,2,3,4,5,6,7,8],get_all_docu:4,get_class:3,get_intra_similar:7,get_modul:3,get_representative_vector:7,get_tag:6,get_text:6,give:[2,5],given:[0,2,3,4,5,6,7,8],global:5,global_schem:2,goal:[2,4,7],goe:4,gomez:8,gone:5,good:7,goooaaaal:2,graph:[4,8],greater:[0,5],greatli:[4,5],greedi:4,group:[4,7],grow:8,half:[0,5],halv:5,hand:2,handl:[],handler:6,happen:[0,4,5,8],has:[0,2,4,5,6,7,8],hash:2,hashtag:[0,2],hashtag_pattern:2,have:[0,2,3,4,5,6,7,8],head:0,hello:2,help:[2,3,5,6,8],helper:8,here:[2,5,7],high:[2,7],higher:[0,2,3,5],highest:7,histor:[0,5],hog:7,hood:8,hour:6,how:[0,2,4,5,7],howev:[0,2,4,5,7],http:[0,8],human:[0,4,5],ideal:[0,4],ident:0,identifi:[0,2,4,5],idf:[0,6],idf_:2,idl:0,idli:0,ignor:0,immedi:[0,4],implement:[0,2,3,4,5,6,7],importantli:4,impos:5,improv:[2,7],inact:[0,6,7],includ:[0,2,3,4,5,6,7,8],inclus:[0,4,5,7],incom:[0,4,6,7],incomplet:2,increas:[0,5],increment:[0,7],indefinit:6,index:[1,5,6],indic:[0,2,5,6,7,8],individu:[0,5,7],inequ:7,influenc:2,info:[1,3],inform:[2,3,4,7,8],inherit:[2,3,6,7],initi:[0,2,3,4,5,7],inner:[],input:[0,4,5,6],instal:2,instanc:[0,2,3,4,5,7],instanti:[2,5],instead:[0,3,4,6,7],integ:[5,7,8],interfac:[3,5,7,8],intern:8,interpret:5,intersect:7,intra:[6,7],introduc:[0,5],introduct:8,introduction_onli:8,invalid:[3,6],invok:[0,7],involv:2,is_error_respons:8,is_fil:6,is_json:6,is_person:8,isn:4,item:0,iter:[6,7],its:[0,2,4,5,6,7],itself:6,join:4,json:[3,6,8],just:[2,5,7],keep:[0,2,5,6,8],kei:[0,2,3,5,6,7,8],kept:6,keyword:[0,2,4,6,7,8],kind:[0,2],kleinberg:5,know:[0,7],knowledg:[],kwarg:[0,2,4,5,6,7,8],lambda:4,lang:6,languag:[1,6],laplac:2,larg:[2,5],larger:5,largest:4,last:[0,2,7],later:[0,5],latest:[0,4,7],latter:2,leagu:8,learn:[1,6],least:[0,2,4,7],left:0,len:2,length:[0,2,4,5,6],less:[0,5,6],let:8,letter:2,level:[3,8],librari:7,lies:5,lifetim:4,like:[0,2,5,6,7,8],likeli:7,limit:8,line:[2,6],linguist:1,link:[0,1],lionel:8,list:[0,2,3,4,5,6,7,8],listen:[0,1,6],listo:4,littl:5,load:[3,6],load_candid:6,load_se:6,local:5,local_schem:2,log:[2,3,5,6],log_tim:3,logarithm:5,logger:1,loglevel:3,longer:0,look:[2,4,5,6,7,8],loop:6,lose:5,lost:5,lot:[0,2,5,7],low:2,lower:7,lowercas:2,machin:[0,1,4],made:[0,2,4,7],magnitud:7,mai:[0,2,4,5,7],main:[2,4,6,7],maintain:[5,7],make:[0,2,4,5,7,8],mamo:[0,2],manag:[4,6],manchest:2,manchesterunit:2,manhattan:7,mani:[0,2,7,8],manifest:7,manipul:[4,7],map:2,margin:[0,4],mark:5,mathemat:7,matrix:[],max:[0,6],max_candid:6,max_inact:[0,6],max_intra_similar:[0,6],max_se:6,max_tim:[4,6],maxim:[4,5],maximum:[0,4,5,6],mean:[0,2,3,4,5],meant:[2,5],measur:[4,5,7],mechan:5,media:0,memori:7,memorynutritionstor:5,mention:[2,8],mention_pattern:2,mere:0,messag:[0,3],messi:8,meta:6,metadata:6,method:[0,4,5,6,7],metric:7,metrid:5,middl:2,might:0,min:6,min_burst:[0,5],min_length:2,min_similar:4,min_siz:[0,6],mine:[1,2],minim:4,minimum:[0,2,4,5,6,7],minut:6,miss:[2,8],mistak:2,mitig:2,mmr:[0,4],mode:6,model:[1,5],modul:[1,3,4,5,8],more:[0,2,4,5,6,7,8],moreov:4,most:[0,2,5,6,7],much:0,multipl:2,multipli:2,multiprocess:6,must:[0,2,4,5,6,7],n_t:2,name:[0,2,3,6,7,8],namespac:6,natur:[1,5,6],navig:8,necessari:[0,3,4],necessit:4,need:[2,5,7,8],needless:2,neg:[0,2,4,5],neither:6,networkx:[],newer:0,newest:0,next:0,nichola:2,nicholasmamo:2,nlp:[1,7],nltk:2,node:0,node_typ:4,noisi:2,nokmean:7,non:[4,5],none:[0,2,3,4,5,6,7,8],normal:[0,2,3,4,6,7,8],normalize_special_charact:2,normalize_word:2,note:[0,2,5],noth:0,notion:5,noun:6,number:[0,2,4,5,6,7,8],number_pattern:2,nutr_:5,nutr_k:5,nutrit:[0,1],nutritionnutrit:[],nutritionstor:[0,5],nyphoon:[],oauth:6,oauthhandl:6,object:[0,1,2,3,5,6,7],observ:[5,7],obtain:8,occur:0,off:5,offer:[3,4],often:[0,2,5,7],old:[0,2,5],older:0,oldest:0,onc:[2,7,8],one:[0,2,4,5,6,7,8],ones:[0,5],onli:[0,2,3,4,5,6,7,8],onlin:7,onward:5,oper:[0,2,6,8],option:[2,6],order:[0,2,4,5],orderedenum:3,org:[0,8],origin:[0,2,4,5,6,7],other:[0,1,2,4,5,6,7,8],otherwis:[2,7,8],out:[0,5,6],outer:[],outgo:8,outlin:[0,5,7],output:[0,2,4,5,6],outsid:2,over:[0,5,6,7],overal:[2,5],overhead:5,overload:[],overwrit:5,overwritten:6,own:[2,7],p_i:7,packag:[2,4,5,8],page:8,pai:[2,5],paper:[5,7],papineni:0,paramet:[0,2,3,4,5,6,7,8],parent:2,paritit:[],pars:8,part:[0,2,5,6],particip:[0,1,4,5],particular:[5,8],partit:[],pass:[0,2,4,6,7,8],past:5,path:[3,6],pattern:[2,5,8],peak:5,penal:[2,5],penalti:0,peopl:[0,5,8],per:0,perform:[2,4,7,8],period:[0,2,4,5,6,7],person:[5,8],php:8,physic:[0,5],pick:4,piec:2,pip:2,pivot:5,plain:[2,8],plan:0,player:8,pmi:6,pmibootstrapp:6,point:[0,4,5],popul:0,popular:[0,2,5],porter:2,porterstemm:2,pos:2,posit:[4,5,8],possibl:[2,3,7],post:1,post_rat:5,practic:5,pre:[0,1,2],precis:[0,4],predominantli:5,prefix:2,premedit:0,premier:8,prepar:0,prepare_output:6,present:[0,2,4,5],previou:5,print:0,printconsum:[0,6],problem:5,process:[0,1,4],processor:1,produc:[4,7],product:[0,2],program:6,progress:5,project:8,promot:2,proper:6,proper_noun:6,properti:[4,7],provid:[0,2,4,5,6,7,8],pseudo:0,publish:0,punctuat:2,purpos:[2,5,7],python:[0,2,3,4,5,6,7,8],q_i:7,quasi:0,queri:[4,8],queue:[1,6],quick:2,rais:[0,2,3,4,5,6,7,8],rank:0,rare:2,rate:[0,5],ratio:5,read:[0,2,5,6,7],reader:1,readili:[2,8],real:[0,5,7],realiti:[2,5],realli:5,reason:[2,5],recalcul:7,recalculate_centroid:7,receiv:[0,2,4,5,6,7],recent:[0,5],reconaiss:0,record:[2,8],recurs:[3,8],redirect:8,reduc:2,redund:4,ref:[],refer:[0,2,3,4,5,7,8],regular:[2,8],rel:[5,6],relat:[4,6,7,8],relev:4,reliabl:5,remov:[0,2,4,5,6,7],remove_alt_cod:2,remove_hashtag:2,remove_ment:2,remove_numb:2,remove_punctu:2,remove_retweet:6,remove_retweet_prefix:2,remove_unicode_ent:2,remove_url:2,reorder:4,repeat:[2,6],replac:[0,2],replace_ment:2,repli:0,report:[0,5],repres:[0,2,4,5,6,7,8],represent:[2,4,7],representind:[],request:[7,8],requir:[2,3,5,6],rerank:4,resid:2,resolv:[1,8],resourc:[2,4],respect:[0,2,3,5],respons:[2,8],rest:2,restrict:5,result:[0,2,5,8],retain:[0,2,4,6,7],retir:7,retorn:[],retriev:[2,5,7,8],retrospect:[5,6],retweet:[0,2,6],revers:[4,8],revert:8,revert_redirect:8,revolv:0,root:5,routin:5,rtpye:7,rule:[0,1],run:[0,2,5,6],runtimeerror:8,s_d:0,safe:0,said:[4,5,8],salton:2,same:[0,2,3,4,6,7],sampl:6,save:[0,2,6],save_meta:6,scheme:[0,6],schemescor:2,score:[0,2,4,6],scorer:[1,2],scratch:7,screen:2,script:[6,7],search:1,second:[0,4,5,6,7],see:7,seed:[6,8],seed_fil:6,seen:5,select:[4,7],send:8,sensor:[0,5],sent:8,sentenc:[2,4],separ:[5,8],serial:6,serializ:[3,6],set:[0,2,3,4,5,6,7,8],set_logging_level:3,setup_arg:6,sever:[5,8],share:[5,6],sharp:5,shorter:[],shortest:[],should:[0,2,4,5,6,7,8],show:3,side:8,signific:5,similar:[0,2,4,5,6,7],similarity_measur:7,simpl:[2,4,5,8],simpli:[2,7,8],simul:0,simulatedbufferedconsum:0,simultan:[0,4],sinc:[0,2,5,7,8],singl:[2,7],siplit:0,size:[0,5,6,7],skip:[0,6,7],skip_tim:6,sleep:0,slew:0,slide:5,slow:5,small:[0,7],smaller:5,smallest:0,smooth:2,snapshot:0,social:[0,5],some:[0,2,3,7],someon:0,someth:[0,4,5],sometim:8,sort:[4,5],sought:[6,7],sourc:[],space:[1,2],spam:0,span:0,special:[0,4,7],specif:[0,2,4,5],specifi:[2,5,6,7],sped:6,speech:[2,6],speed:[2,6],spend:[0,6],spike:5,split:[0,2,4,5,6],split_hashtag:2,sport:[0,5],sqrt:[5,7],squar:5,stage:[0,5],standard:[2,5,8],start:[0,2,3,5,8],statconsum:[0,6],state:[0,4,5,7],statist:[0,1],stem:[2,6],stem_cach:2,stemmer:2,step:[0,2,5],still:[0,4],stop:[0,6],stopword:[2,6],storag:5,store:[0,1,2,3,4,6,7],store_frozen:7,str:[0,2,3,4,5,6,7,8],stream:[5,6],stream_process:6,string:[0,2,3,4,6,8],strip:2,structur:[0,5],studi:[0,5],succe:5,success:4,suffix:6,suggest:2,suitabl:5,sum:7,sum_:[5,7],summar:[0,1,2,5],summari:[0,1],summarization_bas:[],summarizationalgorithm:[4,5],summat:7,suppli:2,support:[5,6,8],surnam:8,synchron:6,syntax:2,system:[0,5],tab:2,tabl:[0,2,6],tackl:5,tag:[2,6],tail:0,take:[0,2,4,7],taken:5,talk:[0,5],task:[0,2,4,6],tdt:[0,1,2,3,4,6,7],tdtalgorithm:5,techniqu:[4,5,7],tell:4,temporalnokmean:[0,7],term:[0,1,5,6,7,8],terminolog:5,termweight:2,termweightingschem:[0,2,6],text:[0,1,2,4,6,7],textual:4,tf_:2,tfidf:[0,2,6],tfidf_:2,than:[0,2,5,6,8],thei:[0,2,4,5,7,8],them:[0,2,4,5,6,7,8],theme:5,themselv:[0,7],therefor:[0,2,4,5,7],thet:5,thi:[0,2,3,4,5,6,7,8],thing:5,those:[0,2,5],thought:5,thousand:0,three:[5,7],threshold:[0,6,7],through:[0,3,4,6,7,8],thu:[4,7],time:[0,2,3,4,5,6,7,8],time_window:0,timeli:7,timelin:[0,1,5,6],timestamp:[0,4,5,7],timestmap:5,titl:8,to_arrai:[2,3,4,6,7],togeth:[2,4,5,6,7],tokan:0,token:[0,1,4,6],tokenize_corpu:6,tokenize_pattern:2,tokenized_corpu:6,tokenizezr:[],too:[0,8],tool:[1,5],topic:[0,1,4,6,7],topicalclusternod:4,total:2,track:[0,1,4,6,8],transform:2,translat:0,tri:[4,5,6],triangl:7,trivial:2,tupl:[0,5,6],turn:0,tweepi:6,tweet:[0,4,5,6],tweetclean:[0,2],tweetlisten:6,twevent:6,twice:0,twitter:[0,1,2,3,5,6],two:[0,2,5,6,7],txt:6,type:[0,2,3,4,5,6,7,8],unchang:5,uncommon:2,undefin:7,under:8,underli:2,understand:[0,4,6],understand_process:6,undesir:2,unequ:4,unicod:[2,6],uniform:[2,5,7],union:7,uniqu:[0,2,4],unit:2,unix_ev:6,unless:4,unlik:[0,5],unpopular:5,unspecifi:7,until:[0,5],unus:7,updat:[6,7],update_scor:6,upenn_tagset:2,url:[0,2,8],url_pattern:2,use:[0,2,5,6,7,8],used:[0,2,4,5,6,7,8],useful:8,useless:[],user:2,usernam:2,uses:[0,2,5,6,7,8],using:[0,2,4,5,6,7,8],usual:[0,2],v_f:7,v_n:7,valid:[0,3,8],valu:[0,2,3,4,5,6,7,8],valueerror:[0,2,3,4,5,6,7,8],vari:[4,5],variabl:[0,2,3,4,5,7,8],variant:7,variou:0,vastli:5,vector:[1,2,4],vectori:4,vectorspac:[2,7],verb:6,veri:[0,2,5,7,8],version:2,vocabulari:6,volum:[0,5],vsm:[1,2],wai:[0,2,4,5],wait:[0,6],want:2,warn:3,watford:6,weak:[0,2,3,4,5,7],weigh:2,weight:[0,1,4,6,7],well:[2,5],were:[6,8],what:[4,5,8],whatsoev:[],when:[0,2,3,4,5,6,7,8],where:[0,2,3,5,6,7,8],wherea:[2,4],whether:[0,2,4,5,6,7,8],which:[0,2,3,4,5,6,7,8],white:2,whitespac:2,whose:[5,6,7,8],why:[5,7],wikimedia:8,wikinterfac:1,wikipedia:8,window:[0,5],without:[0,2,5,6,7,8],word:[2,5,6,7],word_normalization_pattern:2,work:[2,5],workflow:0,world:2,worth:[],would:[0,2,8],wouldn:7,wrap:7,write:[0,6],written:6,xclude:6,yet:[0,7],you:[2,3,5,6,7,8],your:2,yourself:7,zero:[5,6],zhao:0,zhaoconsum:[0,6]},titles:["9. Consumers","Welcome to EvenTDT\u2019s documentation!","3. Natural Language Processing (NLP)","12. Other","7. Summarization","6. Topic Detection and Tracking (TDT)","1. Tools","2. Vector Space Model (VSM)","4. Wikinterface"],titleterms:{"boolean":2,"class":3,The:4,algorithm:[0,4,5,6,7],base:3,carbonel:4,cataldi:5,cleaner:2,cluster:7,collect:6,common:2,consum:0,data:6,detect:5,document:[1,2],eld:5,eventdt:1,filler:2,frequenc:2,global:2,goldstein:4,idf:2,indic:1,info:8,invers:2,languag:2,link:8,local:2,logger:3,mamo:[4,5],math:7,mean:7,memori:5,model:7,natur:2,nlp:2,node:4,nutrit:5,object:4,other:3,pre:6,process:[2,6],queue:0,scheme:2,search:8,simpl:0,space:7,store:5,summar:4,summari:4,tabl:1,tdt:5,tempor:7,term:2,text:8,timelin:4,token:2,tool:6,topic:5,track:5,tweet:2,vector:7,vsm:7,weight:2,welcom:1,wikinterfac:8,zhao:5}})