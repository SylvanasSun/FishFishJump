# Created by SylvanasSun in 2017.10.17
# !/usr/bin/python
# -*- coding: utf-8 -*-
import collections

import jieba
from jieba import analyse


# TODO: Change default hash algorithms to the other algorithms of high-performance.
def _default_hashfunc(content, hashbits):
    """
    Default hash function is variable-length version of Python's builtin hash.

    :param content: data that needs to hash.
    :return: return a decimal number.
    """
    if content == "":
        return 0

    x = ord(content[0]) << 7
    m = 1000003
    mask = 2 ** hashbits - 1
    for c in content:
        x = ((x * m) ^ ord(c)) & mask
    x ^= len(content)
    if x == -1:
        x = -2
    return x


# TODO: Change default toknizer to the c/c++ version or other tokenizer of high-performance.
def _default_tokenizer_func(content, keyword_weight_pair):
    """
    Default tokenizer function that uses jieba tokenizer.

    :param keyword_weight_pair: maximum pair number of the keyword-weight list.
    :return: return keyword-weight list. Example: [('Example',0.4511233019962264),('Hello',0.25548051420382073),...].
    """
    seg_list = jieba.lcut_for_search(content)
    # Extract keyword-weight list by TF-IDF algorithms and by sorted maximum weight
    return jieba.analyse.extract_tags("".join(seg_list), topK=keyword_weight_pair, withWeight=True)


class Simhash(object):
    """
    Class Simhash implements simhash algorithms of the Google for filter duplicate content.
    Simhash algorithms idea is will reduce the dimension of content and compares the
    difference of the "Hamming Distance" implements filter duplicate content.
    About simhash algorithms the more introduction: https://en.wikipedia.org/wiki/SimHash
    Simhash default tokenizer is jieba (https://github.com/fxsjy/jieba).
    """

    def __init__(self, data, keyword_weight_pair=20, hash_bit_number=64, hashfunc=None, tokenizer_func=None):
        """
        :param data: data that needs to be encode.
        :param keyword_weight_pair: maximum pair number of the keyword-weight list.
        :param hash_bit_number: maximum bit number for hashcode.
        :param hashfunc: hash function,its first parameter must be data that needs to be encode
                         and the second parameter must be hash bit number.

        :param tokenizer_func: tokenizer function,its first parameter must be content that
                               needs to be tokenizer and the second parameter must be
                               keyword_weight_pair.
        """
        if hashfunc is None:
            self.hashfunc = _default_hashfunc
        else:
            self.hashfunc = hashfunc

        if tokenizer_func is None:
            self.tokenizer_func = _default_tokenizer_func
        else:
            self.tokenizer_func = tokenizer_func

        self.hash_bit_number = hash_bit_number
        self.keyword_weight_pari = keyword_weight_pair
        if isinstance(data, Simhash):
            self.hash = data.hash
        elif isinstance(data, int):
            self.hash = data
        else:
            self.simhash(data)

    def __str__(self):
        return str(self.hash)

    def simhash(self, content):
        """
        Select policies for simhash on the different types of content.
        """
        if content is None:
            self.hash = -1
            return

        if isinstance(content, str):
            features = self.tokenizer_func(content, self.keyword_weight_pari)
            self.hash = self.build_from_features(features)
        elif isinstance(content, collections.Iterable):
            self.hash = self.build_from_features(content)
        elif isinstance(content, int):
            self.hash = content
        else:
            raise Exception("Unsupported parameter type %s" % type(content))

    def build_from_features(self, features):
        """
        :param features: a list of (token,weight) tuples or a token -> weight dict,
                        if is a string so it need compute weight (a weight of 1 will be assumed).

        :return: a decimal digit for the accumulative result of each after handled features-weight pair.
        """
        v = [0] * self.hash_bit_number
        if isinstance(features, dict):
            features = features.items()

        # Starting longitudinal accumulation of bits, current bit add current weight
        # when the current bits equal 1 and else current bit minus the current weight.
        for f in features:
            if isinstance(f, str):
                h = self.hashfunc(f, self.hash_bit_number)
                w = 1
            else:
                assert isinstance(f, collections.Iterable)
                h = self.hashfunc(f[0], self.hash_bit_number)
                w = f[1]
            for i in range(self.hash_bit_number):
                bitmask = 1 << i
                v[i] += w if h & bitmask else -w

        # Just record weight of the non-negative
        fingerprint = 0
        for i in range(self.hash_bit_number):
            if v[i] >= 0:
                fingerprint += 1 << i

        return fingerprint

    def is_equal(self, another, limit=0.8):
        """
        Determine two simhash are similar or not similar.

        :param another: another simhash.
        :param limit: a limit of the similarity.
        :return: if similarity greater than limit return true and else return false.
        """
        if another is None:
            raise Exception("Parameter another is null")

        if isinstance(another, int):
            distance = self.hamming_distance(another)
        elif isinstance(another, Simhash):
            assert self.hash_bit_number == another.hash_bit_number
            distance = self.hamming_distance(another.hash)
        else:
            raise Exception("Unsupported parameter type %s" % type(another))

        similarity = float(self.hash_bit_number - distance) / self.hash_bit_number
        if similarity > limit:
            return True
        return False

    def hamming_distance(self, another):
        """
        Compute hamming distance,hamming distance is a total number of different bits of two binary numbers.

        :param another: another simhash value.
        :return: a hamming distance that current simhash and another simhash.
        """
        x = (self.hash ^ another) & ((1 << self.hash_bit_number) - 1)
        result = 0
        while x:
            result += 1
            x &= x - 1
        return result


if __name__ == "__main__":
    sentence_A = """
                 明朝军制建立在军户制度上，军户即为中国古代世代从军、充当军差的人户。
                 东晋南北朝时，士兵及家属的户籍隶于军府称为军户。军户子弟世袭为兵未经准许不得脱离军籍。
                 北魏军户亦有用俘虏充当的。元朝实行军户制度，军户必须出成年男子到军队服役，父死子替，兄亡弟代，世代相袭。
                 """
    sentence_B = """
                 明朝的军制是在元朝基础上改进，而没有采用唐宋时期的募兵制。
                 元朝的军制是建立在游牧民族制度上发展而来，游牧民族在战争是全民征兵，实际上是军户制度。
                 建立元朝以后，蒙古族还是全部军户，对于占领区招降的军队，也实行军户制度。
                 """
    sentence_C = "You know nothing Jon Snow!"
    sentence_D = "Jon Snow: I konw nothing."

    simhash_A = Simhash(sentence_A)
    simhash_B = Simhash(sentence_B)
    simhash_C = Simhash(sentence_C)
    simhash_D = Simhash(sentence_D)

    print(simhash_A)
    print(simhash_B)
    print(simhash_C)
    print(simhash_D)

    assert simhash_A.is_equal(simhash_B) is True
    assert simhash_B.is_equal(simhash_C) is False
    assert simhash_C.is_equal(simhash_D) is True
