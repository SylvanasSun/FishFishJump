# -*- coding: utf-8 -*-
# Created by SylvanasSun in 2017.10.17
from hashlib import md5

import jieba
from jieba import analyse


def _default_hashfunc(content):
    """
    Default hash function which by MD5 algorithms then return a decimal number
    :param data: data that needs to hash
    :return: return a decimal number that after MD5 algorithms encode
    """
    return int(md5(content).hexdigest(), 16)


def _default_tokenizer_func(content, keyword_weight_pair):
    """
    Default tokenizer function that uses jieba tokenizer.
    :param feature_weight_pair: maximum pair of the keyword-weight list
    :return: return keyword-weight list. Example: [('Example',0.4511233019962264),('Hello',0.25548051420382073),...]
    """
    seg_list = jieba.lcut_for_search(content)
    # Extract keyword-weight list by TF-IDF algorithms and by sorted maximum weight
    jieba.analyse.set_stop_words("stop_words.txt")
    return jieba.analyse.extract_tags("".join(seg_list), topK=keyword_weight_pair, withWeight=True)


class Simhash(object):
    """
        Class Simhash implements simhash algorithms of the Google for filter duplicate content.
        Simhash algorithms idea is will reduce the dimension of content and compares the
        difference of the "Hamming Distance" implements filter duplicate content.
        About simhash algorithms the more introduction: https://en.wikipedia.org/wiki/SimHash
        Simhash default tokenizer is jieba (https://github.com/fxsjy/jieba).
    """

    def __init__(self, content, keyword_weight_pair=20, hashfunc=None, tokenizer_func=None):
        if hashfunc is None:
            self.hashfunc = _default_hashfunc
        else:
            self.hashfunc = hashfunc

        if tokenizer_func is None:
            self.tokenizer_func = _default_tokenizer_func
        else:
            self.tokenizer_func = tokenizer_func

        self.simhash = self._simhash(content, keyword_weight_pair)

    def __str__(self):
        return str(self.simhash)

    def _simhash(self, content, keyword_weight_pair):
        pass
