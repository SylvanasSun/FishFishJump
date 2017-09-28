from hashlib import md5


class SimpleHash(object):
    """
        SimpleHash class to implement hash function of bloom filter.
    """

    def __init__(self, capacity, seed):
        """
            Parameters:
            -----------
            capacity: integer
                the maximum bit digits.
            seed: integer
                the seed is different param in the each hash function.
        """
        self.capacity = capacity
        self.seed = seed

    def hash(self, value):
        """
            function hash() implement to acquire hash value that use simply method that weighted sum.

            Parameters:
            -----------
            value: string
                the value is param of need acquire hash
            Returns:
            --------
            result
                hash code for value
        """
        result = 0
        for i in range(len(value)):
            result += self.seed * result + ord(value[i])
        return (self.capacity - 1) % result


class RedisBloomFilter(object):
    """
        RedisBloomFilter class to implement url filter by bloom filter in the string of redis.
    """

    def __init__(self, server, key, block_num=1):
        """
            Parameters:
            -----------
            server
                Redis client instance
            key
                Redis key name
            blocK_num
                block number
        """
        self.seeds = [5, 7, 11, 13, 31, 37, 61, 79, 97]  # the seeds for number of hash function
        self.bit_size = 1 << 31  # use 256MB because the string of redis maximum size is 512MB
        self.server = server
        self.key = key
        self.block_num = block_num
        self.hash_function = []
        for seed in self.seeds:
            self.hash_function.append(SimpleHash(self.bit_size, seed))

    def is_contains(self, data):
        """
            Judge the data whether is already exist if each bit of hash code is 1 then data exist.
        """
        if not data:
            return False
        data = self._compress_by_md5(data)
        result = True
        # cut the first two place,route to different block by block_num
        name = self.key + str(int(data[0:2], 16) % self.block_num)
        for h in self.hash_function:
            local_hash = h.hash(data)
            result = result & self.server.getbit(name, local_hash)
        return result

    def insert(self, data):
        """
            Insert 1 into each bit
        """
        if not data:
            return
        data = self._compress_by_md5(data)
        # cut the first two place,route to different block by block_num
        name = self.key + str(int(data[0:2], 16) % self.block_num)
        for h in self.hash_function:
            local_hash = h.hash(data)
            self.server.setbit(name, local_hash, 1)

    def _compress_by_md5(self, data):
        md_5 = md5()
        md_5.update(data)
        return md_5.hexdigest()
