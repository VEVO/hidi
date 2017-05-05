import warnings
import numpy as np
import collections
from numpy.random import permutation
from sklearn.decomposition import TruncatedSVD
from hidi.transform import Transform

# Catch annoying warnings from nimfa
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import nimfa as nf


class W2VStringTransform(Transform):
    """
    Takes a pandas Dataframe and transforms it into a
    string

    :param n_shuffles: The number of suffles for the
    `item_id`.
    :type n_shuffles: int
    """
    def __init__(self, n_shuffles=3, **w2v_kwargs):
        self.w2v_kwargs = w2v_kwargs
        self.n_shuffles = n_shuffles

    def transform(self, df_temp, **kwargs):
        """
        :param df: a pandas Dataframe with two columns:
        :code:`link_id`, :code:`item_id`
        :type df: pandas.Dataframe
        :rtype: a string of shuffled item_id
        """
        df = df_temp
        if ('link_id' in df.index) | ('item_id' in df.index):
            df.reset_index(inplace=True)

        df.set_index('link_id', inplace=True)
        words = ''
        for index in df.index.unique():
            temp_item_id_list = df.loc[index].item_id
            item_id_list = temp_item_id_list
            for i in range(self.n_shuffles - 1):
                item_id_list = np.append(item_id_list,
                                         permutation(temp_item_id_list))
            joined_shuffled_list = ' '.join(str(x) for x in item_id_list)
            words = ' '.join([words, joined_shuffled_list]).strip()
        return words, kwargs


class W2VGenismTransform(Transform):
    """
    Generalized transform for gensim.models.Word2Vec
    Takes an uninitialized gensim.models.Word2Vec and here is more details
    about it:
    https://radimrehurek.com/gensim/models/word2vec.html
    Note that the uninitialized gensim.model.Word2Vec model can be created
    without sentences.

    :param gensim_w2v_model: an uninitialized gensim.model.Word2Vec model
    :type gensim_w2v_model: gensim.model.Word2Vec model
    """
    def __init__(self, gensim_w2v_model, **gensim_w2v_kwargs):
        self.gensim_w2v_kwargs = gensim_w2v_kwargs
        self.gensim_w2v_model = gensim_w2v_model

    def transform(self, words, **kwargs):
        """
        Takes a string of items

        :param words: a list of items
        :type words: str
        """
        self.gensim_w2v_model.build_vocab(words, **self.gensim_w2v_kwargs)
        return self.gensim_w2v_model, kwargs


class W2VBuildDatasetTransform(Transform):
    """
    Takes a string of list of items(words) and tokenize it.
    :param vocabulary_size: top n most frequent items(words)
    :type vocabulary_size: int
    """
    def __init__(self, vocabulary_size=5000, **w2v_kwargs):
        self.vocabulary_size = vocabulary_size
        self.w2v_kwargs = w2v_kwargs

    def transform(self, words, **kwargs):
        """
        :param words: a list or a string of items
        :type words: list or str
        :rtype: a tuple of `data`, `count`, `dictionary` and
            `reverse_dictionary` `data` is the tokenized words, `count` is a
            list of tuple which consists of `(item, count)`, `dictionary`
            stores tokens of each items as its keys and items as its values
            and `reverse_dictionary` is the reversed of `dictionary`
        """
        if isinstance(words, str):
            words = words.split()
        count = [['UNK', -1]]
        count_words = collections.Counter(words)
        count.extend(count_words.most_common((self.vocabulary_size-1)))
        dictionary = dict()
        for word, _ in count:
            dictionary[word] = len(dictionary)
        data = list()
        unk_count = 0
        for word in words:
            if word in dictionary:
                index = dictionary[word]
            else:
                index = 0  # dictionary['UNK']
                unk_count += 1
            data.append(index)
        count[0][1] = unk_count
        reverse_dictionary = dict(zip(dictionary.values(), dictionary.keys()))
        return (data, count, dictionary, reverse_dictionary), kwargs


class SkLearnTransform(Transform):
    """
    Generalized transform for SciKit Learn algorithms.

    This transform takes a SciKit Learn algorithm, and its
    keyword arguments upon initialization. It applies the
    algorithm to the input when :code:`transform` is called.

    The algorithm to be applied is likely, but not necessarily
    a :code:`sklearn.decomposition` algorithm.
    """
    def __init__(self, SkLearnAlg, **sklearn_args):
        self.SkLearnAlg = SkLearnAlg
        self.sklearn_args = sklearn_args

    def transform(self, M, **kwargs):
        """
        Takes a numpy ndarray-like object and applies a SkLearn
        algorithm to it.
        """
        sklearn_alg = self.SkLearnAlg(**self.sklearn_args)
        transformed = sklearn_alg.fit_transform(M)
        kwargs['sklearn_fit'] = sklearn_alg

        return transformed, kwargs


class SVDTransform(SkLearnTransform):
    """
    Perform Truncated SVD on the matrix.

    This uses SciKit Learn's Tuncated SVD implementation, which
    is documented here:
    http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.TruncatedSVD.html

    All kwargs given to :code:`SVDTransform`'s initialization
    function will be given to :code:`sklearn.decomposition.TruncatedSVD`.

    Please reference the `sklearn docs
    <http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.TruncatedSVD.html>`_
    when using this transform.
    """
    def __init__(self, **svd_kwargs):
        super(SVDTransform, self).__init__(TruncatedSVD, **svd_kwargs)


class NimfaTransform(Transform):
    """
    Generalized Nimfa transform.

    This transform takes a nimfa algorithm, and its keyword
    arguments upon initialization. It applies the algorithm
    to the input when :code:`transform` is called.
    """
    def __init__(self, NimfaAlg, **nimfa_kwargs):
        self.NimfaAlg = NimfaAlg
        self.nimfa_kwargs = nimfa_kwargs

    def transform(self, M, **kwargs):
        nimfa_alg = self.NimfaAlg(M, **self.nimfa_kwargs)
        nimfa_fit = nimfa_alg()
        kwargs['nimfa_fit'] = nimfa_fit

        return nimfa_fit.basis(), kwargs


class SNMFTransform(NimfaTransform):
    """
    Perform Sparse Nonnegative Matrix Factorization.

    This wraps nimfa's snmf function, which is documented here:
    http://nimfa.biolab.si/nimfa.methods.factorization.snmf.html

    All kwargs given to :code:`SNFMTransform`'s initialization
    function will be given to :code:`nimfa.Snmf`.

    Please reference the `nimfa docs
    <http://nimfa.biolab.si/nimfa.methods.factorization.snmf.html>`_
    when using this transform.
    """

    def __init__(self, **snmf_kwargs):
        super(SNMFTransform, self).__init__(nf.Snmf, **snmf_kwargs)
