"""
FUEGO (codename that means absolutely nothing) is a feature-pivot consumer built on the :class:`~queues.consumers.algorithms.eld_consumer.ELDConsumer`'s own feature-pivot method.
Differently from the :class:`~queues.consumers.algorithms.eld_consumer.ELDConsumer`, FUEGO uses a sliding time-window instead of checkpoints.
This allows for more accurate results in real-time.

.. note::

    Since FUEGO uses only a feature-pivot method, it is not very granular on its own.
    Therefore this consumer can only extract granular developments when combined with a :class:`~queues.consumers.token_split_consumer.TokenSplitConsumer`.
    For a combination of document-pivot and feature-pivot approaches, see the :class:`~queues.consumers.algorithms.eld_consumer.ELDConsumer`.
"""

import math
import os
import statistics
import sys

from nltk.corpus import stopwords

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from datetime import datetime
from logger import logger
from nlp import Document, Tokenizer
from nlp.cleaners import TweetCleaner
from nlp.weighting import TF, TFIDF
from nlp.weighting.global_schemes import IDF
from queues.consumers import Consumer
from summarization import Summary
from summarization.algorithms import DGS
from summarization.timeline import Timeline
from summarization.timeline.nodes import DocumentNode
from tdt.algorithms import SlidingELD
from tdt.nutrition import MemoryNutritionStore
import twitter

class FUEGOConsumer(Consumer):
    """
    The :class:`~queues.consumers.fuego_consumer.FUEGOConsumer` is a real-time consumer with a custom algorithm to detect topics.
    Unlike other :ref:`consumers <consumers>`, the consumer has both a :func:`~queues.consumers.Consumer.ELDConsumer.run` and a :func:`~queues.consumers.fuego_consumer.FUEGOConsumer.understand` functions.
    The former is the normal processing step, whereas the :func:`~queues.consumers.fuego_consumer.FUEGOConsumer.understand` function precedes the event and builds a TF-IDF scheme for the event.

    In additional to the :class:`~queues.Queue`, the consumer maintains in its state two objects to transform tweets into :class:`~nlp.document.Document` instances:

    - ``tokenizer``: used to tokenize the text in tweets.
    - ``scheme``: used to weight the tokens and create :class:`~nlp.document.Document` instances.

    As part of the TDT approach, the consumer maintaints in its state:

    - ``volume``: records the number of tweets (after filtering) received per second.
    - ``nutrition``: records the nutrition of terms at each second.
    - ``tdt``: the TDT algorithm used by the consumer to detect and track bursty terms.

    :ivar ~.tokenizer: The tokenizer used to tokenize tweets.
    :vartype tokenizer: :class:`~nlp.tokenizer.Tokenizer`
    :ivar scheme: The term-weighting scheme used to create documents from tweets.
    :vartype scheme: :class:`~nlp.weighting.TermWeightingScheme`
    :ivar volume: A nutrition store that contains the number of tweets (after filtering) received per second.
    :vartype volume: :class:`~tdt.nutrition.memory.MemoryNutritionStore`
    :ivar nutrition: A nutrition store that contains the nutrition of terms from tweets.
                     The nutrition is stored for each second.
    :vartype nutrition: :class:`~tdt.nutrition.memory.MemoryNutritionStore`
    :ivar tdt: The TDT algorithm used by the consumer to detect and track bursty terms.
    :vartype tdt: :class:`~tdt.algorithms.eld.SlidingELD`
    :ivar burst_start: The minimum burst value to consider a term to be bursty.
                       This value is applied to terms that are known to find new bursty terms during detection.
                       If the burst of a term is above this value, the consumer considers it to be bursty.
                       This value is exclusive.
    :vartype burst_start: float
    :ivar burst_end: The maximum burst value to consider a bursty term to still be bursty.
                     This value is applied to terms that are known to be bursty while tracking.
                     If the burst of a term goes below this value, the consumer stops considering it to be bursty.
                     This value is exclusive.
    :vartype burst_end: float
    :ivar min_volume: The minimum volume in the last window required to look for bursty terms.
                      This is not the raw number of tweets, but considers the damping factor of tweets.
                      If the volume drops below this value, the consumer does not look for bursty terms.
    :vartype min_volume: float
    :ivar summarization: The summarization algorithm to use.
    :vartype summarization: :class:`~summarization.algorithms.dgs.DGS`
    """

    def __init__(self, queue, scheme=None, damping=0.5,
                 window_size=60, windows=5, burst_start=0.5, burst_end=0.2, min_volume=15,
                 *args, **kwargs):
        """
        Create the consumer with a queue.

        :param queue: The queue that will be receiving tweets.
                      The consumer reads tweets from this queue and processes them.
        :type queue: :class:`~queues.Queue`
        :param scheme: The term-weighting scheme used to create documents from tweets.
        :type scheme: :class:`~nlp.weighting.TermWeightingScheme`
        :param damping: The damping factor to apply to reduce the importance of old retweets.
                        If the value is 0, the consumer never applies any damping.
                        The value should not be lower than 0.
        :type damping: float
        :param window_size: The length in seconds of the sliding time windows.
        :type window_size: int
        :param windows: The number of sliding time windows to use when detecting or tracking bursty terms.
        :type windows: int
        :param burst_start: The minimum burst value to consider a term to be bursty.
                            This value is applied to terms that are known to find new bursty terms during detection.
                            If the burst of a term is above this value, the consumer considers it to be bursty.
                            This value is exclusive.
        :type burst_start: float
        :param burst_end: The maximum burst value to consider a bursty term to still be bursty.
                          This value is applied to terms that are known to be bursty while tracking.
                          If the burst of a term goes below this value, the consumer stops considering it to be bursty.
                          This value is exclusive.
        :type burst_end: float
        :param min_volume: The minimum volume in the last window required to look for bursty terms.
                           This is not the raw number of tweets, but considers the damping factor of tweets.
                           If the volume drops below this value, the consumer does not look for bursty terms.
        :type min_volume: float

        :raises ValueError: When the damping factor is negative.
        :raises ValueError: When the burst start parameter is not between -1 and 1.
        :raises ValueError: When the burst end parameter is not between -1 and 1.
        """

        super(FUEGOConsumer, self).__init__(queue, *args, **kwargs)

        self.tokenizer = Tokenizer(stopwords=stopwords.words('english'),
                                   normalize_words=True, character_normalization_count=3,
                                   remove_unicode_entities=True)
        self.scheme = scheme or TF()

        if damping < 0:
            raise ValueError(f"The damping factor cannot be negative; received { damping }")

        if not -1 <= burst_start <= 1:
            raise ValueError(f"The burst start value must be between -1 and 1; received { burst_start }")

        if not -1 <= burst_end <= 1:
            raise ValueError(f"The burst end value must be between -1 and 1; received { burst_end }")

        self.damping = damping

        # TDT
        self.volume = MemoryNutritionStore()
        self.nutrition = MemoryNutritionStore()
        self.tdt = SlidingELD(self.nutrition, window_size=window_size, windows=windows)
        self.burst_start = burst_start
        self.burst_end = burst_end
        self.min_volume = min_volume

        # summarization
        self.summarization = DGS()

    async def understand(self, max_inactivity=-1, *args, **kwargs):
        """
        Understanding precedes the event and is tasked with generating knowledge automatically.

        During understanding, the :class:`~queues.consumers.fuego_consumer.FUEGOConsumer` creates a :class:`~nlp.weighting.TermWeightingScheme` with an :class:`~nlp.weighting.global_schemes.idf.IDF` table based on the pre-event discussion.
        The consumer uses the :class:`~nlp.weighting.TermWeightingScheme` while processing tweets in real-time.

        .. note::

            This function returns a dictionary so that it can be used as additional parameters in the :mod:`~tools.consume` tool.
            In fact, the parameter name of the :class:`~nlp.weighting.tfidf.TFIDF` scheme is ``scheme``, the same as the scheme's parameter name in the class' constructor.

        :param max_inactivity: The maximum time in seconds to wait idly without input before stopping.
                               If it is negative, it is ignored.
        :type max_inactivity: int

        :return: The :class:`~nlp.weighting.tfidf.TFIDF` scheme built from the documents from the pre-event tweets.
                 This is returned in a dictionary in the ``scheme`` key.
        :rtype: dict
        """

        self._started()
        tfidf = await self._construct_idf(max_inactivity=max_inactivity)
        logger.info(f"TF-IDF constructed with { tfidf.global_scheme.documents } documents", process=str(self))
        self._stopped()
        return { 'scheme': tfidf }

    async def _construct_idf(self, max_inactivity):
        """
        Construct the TF-IDF table from the pre-event discussion.

        :param max_inactivity: The maximum time in seconds to wait idly without input before stopping.
                               If it is negative, it is ignored.
        :type max_inactivity: int

        :return: The constructed TF-IDF scheme.
        :rtype: :class:`~nlp.weighting.tfidf.TFIDF`
        """

        idf = { }
        size = 0

        """
        Understanding keeps working until it is stopped.
        """
        while self.active:
            active = await self._wait_for_input(max_inactivity)
            if not active:
                break

            """
            After it is stopped, construct the IDF.
            Get all the tweets in the queue and convert them to documents.
            """
            tweets = self.queue.dequeue_all()
            documents = self._to_documents(tweets)
            size += len(documents)

            """
            If there are documents, update the IDF with the consumed documents.
            These documents are also added to the buffer so they can be used by the APD process.
            """
            if documents:
                subset = IDF.from_documents(documents)
                idf = { term: idf.get(term, 0) + subset.get(term, 0)
                        for term in subset.keys() | idf.keys() }

        return TFIDF(idf, size)

    async def _consume(self, max_inactivity, *args, **kwargs):
        """
        Consume and process the documents in the queue.

        :param max_inactivity: The maximum time in seconds to wait idly without input before stopping.
                               If it is negative, the consumer keeps waiting for input until the maximum time expires.
        :type max_inactivity: int

        :return: The constructed timeline.
        :rtype: :class:`~summarization.timeline.Timeline`
        """

        timeline = Timeline(DocumentNode, expiry=60*5, min_similarity=0.6, max_time=600)

        """
        The consumer keeps track of the keywords that are breaking at any given moment.
        """
        ongoing = [ ]

        """
        The consumer keeps working until it is stopped or it receives no more tweets for a long period of time.
        """
        while self.active:
            """
            If the queue is idle, stop and wait for input.
            """
            active = await self._wait_for_input(max_inactivity=max_inactivity)
            if not active:
                break

            if self.queue.length():
                """
                Get all the tweets in the queue and convert them to documents.
                """
                tweets = self.queue.dequeue_all()
                tweets = self._filter_tweets(tweets)
                documents = self._to_documents(tweets)
                if not documents:
                    continue
                time = self._time(documents)

                """
                The TDT process is as follows:

                1. Update the volume nutrition.
                2. Update the term nutrition values.
                3. Identify whether the currently-breaking terms are still bursty (tracking).
                4. If the stream is not dormant (receiving very few tweets), identify any new bursty terms.
                """
                self._update_volume(documents)
                self._update_nutrition(documents)
                ongoing = self._track(ongoing, time)
                if not self._dormant(time):
                    bursty = self._detect(time)
                    ongoing = list(set(ongoing + bursty))

                """
                The summarization process is as follows:

                1. Collect the tweets mentioning any of the currently bursty terms.
                2. Add them to the timeline.
                3. If the timeline creates a new node, summarize the last finished node.
                """
                for term in ongoing:
                    topic_documents = self._collect(term, documents)
                    if topic_documents:
                        timeline.add(time, topic_documents)

            if timeline.nodes:
                node = timeline.nodes[-1]
                if node.expired(timeline.expiry, time) and not node.attributes.get('printed'):
                    summary = self._summarize(node)
                    cleaner = TweetCleaner(collapse_new_lines=True, collapse_whitespaces=True, remove_unicode_entities=True)
                    logger.info(f"{datetime.fromtimestamp(node.created_at).ctime()}: { cleaner.clean(str(summary)) }", process=str(self))
                    node.attributes['printed'] = True

        return timeline

    def _filter_tweets(self, tweets):
        """
        Filter the given tweets.
        The rules are based on :class:`~queues.consumers.algorithms.fire_consumer.FIREConsumer`'s and :class:`~queues.consumers.algorithms.eld_consumer.ELDConsumer`'s filtering rules.

        :param tweets: A list of tweets to filter.
                       The tweets can either be tweet dictionaries or documents.
                       If they are documents, this function looks for the tweet in the ``tweet`` attribute.
        :type tweets: list of dict or list of :class:`~nlp.document.Document`

        :return: A list of filtered tweets.
        :type tweets: list of dict or list of :class:`~nlp.document.Document`
        """

        filtered = [ ]

        for item in tweets:
            tweet = item.attributes['tweet'] if type(item) is Document else item
            if self._validate_tweet(tweet):
                filtered.append(item)

        return filtered

    def _validate_tweet(self, tweet):
        """
        Filter the given tweet based on :class:`~.queues.consumers.fire_consumer.FIREConsumer`'s and :class:`~queues.consumers.algorithms.eld_consumer.ELDConsumer`'s filtering rules.

        FIRE's rules are:

            #. The tweet has to be in English,

            #. The tweet must contain no more than 2 hashtags,

            #. The tweet's author must have favorited at least one tweet, and

            #. The tweet's author must have at least one follower for every thousand tweets they've published.

        ELD's rule is:

            #. The biography of the tweet's author cannot be empty because that is indicative of bots.

        ELD also contained a rule that removed tweets with more than one URL.
        FUEGO's filtering is harsher and excludes all tweets with URLs.

        :param tweet: The tweet to validate.
        :type tweet: dict

        :return: A boolean indicating whether the tweet passed the filtering test.
        :rtype: str
        """

        while 'retweeted_status' in tweet:
            tweet = tweet['retweeted_status'] if 'retweeted_status' in tweet else tweet

        if not tweet['lang'] == 'en':
            return False

        if len(tweet['entities']['hashtags']) > 2:
            return False

        if tweet['user']['favourites_count'] == 0:
            return False

        if not tweet['user']['statuses_count'] or tweet['user']['followers_count'] / tweet['user']['statuses_count'] < 1e-3:
            return False

        if len(tweet['entities']['urls']):
            return False

        if not tweet['user']['description']:
            return False

        return True

    def _to_documents(self, tweets):
        """
        Convert the given tweets into documents.
        If the input is made up of documents, these are not changed, but the function adds additional attributes to them.

        :param tweets: A list of tweets.
        :type tweets: list of dict or list of :class:`~nlp.document.Document`

        :return: A list of documents created from the tweets in the same order as the given tweets.
                 Documents are normalized and contain the original tweet in the ``tweet`` attribute.
        :rtype: list of :class:`~nlp.document.Document`
        """

        documents = [ ]

        """
        The text used for the document depend on what kind of tweet it is.
        If the tweet is too long to fit in the tweet, the full text is used;

        Retain the comment of a quoted status.
        However, if the tweet is a plain retweet, get the full text.
        """
        for item in tweets:
            tweet = item.attributes['tweet'] if type(item) is Document else item
            text = twitter.full_text(tweet)

            """
            Create the document and save the tweet in it.
            """
            tokens = self.tokenizer.tokenize(text)
            document = item if type(item) is Document else self.scheme.create(tokens, text=text)
            document.attributes['id'] = tweet.get('id')
            document.attributes['timestamp'] = twitter.extract_timestamp(tweet)
            document.attributes['tweet'] = tweet
            document.normalize()
            documents.append(document)

        return documents

    def _time(self, documents):
        """
        Get the current time.
        The time is taken from the most recent :class:`~nlp.document.Document`.

        :param documents: The list of documents from where to get the timestamp.
        :type documents: list of :class:`~nlp.document.Document`

        :return: The current time, or the timestamp of the most recently-published :class:`~nlp.document.Document`..
        :rtype: float

        :raises ValueError: If the list of documents is empty.
        :raises ValueError: If the given documents are not presented as a list.
        """

        if not documents:
            raise ValueError(f"The given list of documents is empty")

        if type(documents) is not list:
            raise ValueError(f"Expected a list of documents; received { type(documents) }")

        timestamps = [ document.attributes['timestamp'] for document in documents ]
        return max(timestamps)

    def _update_volume(self, documents):
        """
        Update the volume based on the given documents.

        The function simply counts the number of documents published at each second and adds them to the nutrition store.

        :param documents: The list of documents from where to get the timestamp.
        :type documents: list of :class:`~nlp.document.Document`
        """

        for document in documents:
            damping = self._damp(document)
            timestamp = document.attributes['timestamp']
            volume = self.volume.get(timestamp) or 0
            self.volume.add(timestamp, volume + damping)

    def _update_nutrition(self, documents):
        """
        Update the nutrition based on the given documents.

        The function adds the term weights of the documents to the class' nutrition store.
        It separates the nutrition based on timestamp.
        For each second, it keeps track of the nutrition of each distinct term.

        :param documents: The list of documents from where to get the timestamp.
        :type documents: list of :class:`~nlp.document.Document`
        """

        for document in documents:
            damping = self._damp(document)
            timestamp = document.attributes['timestamp']
            nutrition = self.nutrition.get(timestamp) or { }
            for dimension, magnitude in document.dimensions.items():
                nutrition[dimension] = nutrition.get(dimension, 0) + magnitude * damping
            self.nutrition.add(timestamp, nutrition)

    def _damp(self, document):
        """
        Get the damping factor from the document.

        The damping factor is a constant, 1, if the tweet is original or quoted.
        If it is a retweet, the damping factor is calculated as:

        .. math::

            f = e^{-\\lambda \\frac{t_r - t_o}{60}}

        where :math:`t_r` is the time when the original tweet was retweeted, and :math:`t_o` is the time when the original tweet was published.
        :math:`\\lambda` is a parameter; the smaller it is, the less damping is applied, and the larger it is, the more damping is applied.

        When the damping factor is 1, it means that no damping should be applied to the tweet's value (whatever value means in the context).
        When the damping factor is less than 1, it means that the value should be reduced.

        :param document: The document for which to calculate the damping factor.
                         This function expects the document to have an attribute ``tweet`` with the tweet it represents.
        :type document: :class:`~nlp.document.Document`

        :return: The damping factor, bound between 0 and 1.
        :rtype: float
        """

        """
        If the tweet is not a retweet, apply no damping.
        """
        tweet = document.attributes['tweet']
        if 'retweeted_status' not in tweet:
            return 1

        """
        If the tweet is a retweet, apply damping proportional to the difference between the time it took to retweet it.
        """
        retweet = tweet['retweeted_status']
        diff = twitter.extract_timestamp(tweet) - twitter.extract_timestamp(retweet)
        return math.exp(- self.damping * diff / 60)

    def _track(self, topics, timestamp):
        """
        Check whether the given topics are still ongoing at the given time.
        Ongoing topics are those terms whose burst has not yet dipped below a specific value.

        :param topics: The list of topics to check whether they are still ongoing.
        :type topics: list of str
        :param timestamp: The timestamp at which to detect bursty terms.
        :type timestamp: float

        :return: The list of keywords that are still ongoing at the given timestamp.
        :rtype: list of str
        """

        bursty = self.tdt.detect(timestamp, min_burst=self.burst_end)
        ongoing = list(set(topics).intersection(set(bursty.keys())))
        return ongoing

    def _dormant(self, timestamp):
        """
        Check whether the stream is dormant.
        A dormant stream is one that has received very few tweets in the last time window.

        :param timestamp: The timestamp at which to detect bursty terms.
        :type timestamp: float

        :return: A boolean indicating whether the stream is dormant.
        :rtype: bool
        """

        current, historic = self._partition(timestamp)
        mean = statistics.mean(historic.values()) if historic else 0

        # to fix a weird bug in the statistics package
        stdev = 0
        if historic and len(historic) >= 2:
            _stdev = (sum([ (val - mean) ** 2 for val in historic.values() ]) / len(historic)) ** 0.5
            if _stdev > 0:
                stdev = statistics.stdev(historic.values())

        return current <= max(self.min_volume, mean + stdev * 2)

    def _partition(self, timestamp):
        """
        Partition the volume in the store into time windows.
        This function returns a tuple:

        1. The volume at the latest time window.
        2. The volume at the time windows preceding the latest one.

        The number of time windows, including the latest one, is at most equivalent to the number of time windows defined during instantiation.
        The historic volume is a dictionary, with the timestamps as keys and the volume data as the values.
        The timestamps indicate the end of the time window, not the start.
        Moreover, the end value is inclusive.

        :param timestamp: The timestamp at which to create the time windows.
        :type timestamp: float

        :return: A tuple, containing:

                  - The volume at the latest time window, and
                 - The volume at the previous time windows.
        :rtype: tuple of dict
        """

        # NOTE: In this function, the ``since`` is exclusive, and the ``until`` is inclusive.

        """
        Calculate the volume in the current time window.
        """
        volume = self.volume.between(timestamp - self.tdt.window_size + 1, timestamp + 1).values()
        current = sum(volume) if volume else 0

        """
        Calculate the historic volume.
        """
        historic = { }
        windows = math.ceil((timestamp + 1 - min(self.volume.all().keys()))/self.tdt.window_size) if self.volume.all() else 0
        for window in range(1, windows):
            since = max(timestamp - self.tdt.window_size * (window + 1) + 1, 0)
            until = timestamp - self.tdt.window_size * window
            if until > 0:
                data = self.volume.between(since, until + 1)
                historic[until] = sum(data.values())

        return (current, historic)

    def _detect(self, timestamp):
        """
        Detect bursty terms at the given time.

        :param timestamp: The timestamp at which to detect bursty terms.
        :type timestamp: float

        :return: A list of keywords that are bursty at the given timestamp.
        :rtype: list of str
        """

        return list(self.tdt.detect(timestamp, min_burst=self.burst_start).keys())

    def _collect(self, term, documents):
        """
        Collect all documents that contain the given term.
        The function looks for the term in the document's dimensions.

        :param term: The term to look for.
        :type term: str
        :param documents: The list of documents where to look for the term.
        :type documents: list of :class:`~nlp.document.Document`

        :return: A list of documents that contain the given term.
        :rtype: list of :class:`~nlp.document.Document`
        """

        return [ document for document in documents
                           if document.dimensions[term] > 0 ]

    def _summarize(self, node):
        """
        Summarize the given node.

        :param node: The node to summarize.
        :type node: :class:`~summarization.timeline.nodes.Node`

        :return: A summary of the given node.
        :rtype: :class:`~summarization.summary.Summary`
        """

        documents = node.get_all_documents()
        if not documents:
            return Summary()

        """
        Get the unique documents (in terms of text).
        Sort them in descending order of length and retain only the top ones.
        """
        summary_documents = { }
        for document in documents:
            if document.text in summary_documents:
                existing = summary_documents[document.text]
                summary_documents[document.text] = document if self._damp(document) > self._damp(existing) else existing
            else:
                summary_documents[document.text] = document
        summary_documents = { text: document for text, document in summary_documents.items()
                                              if len(text) <= 300 }
        summary_documents = sorted(summary_documents.items(), key=lambda document: len(document[0]) * self._damp(document[1]), reverse=True)
        summary_documents = [ document for _, document in summary_documents[:20] ]

        return self.summarization.summarize(summary_documents, 300)
