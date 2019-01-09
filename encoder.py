from math import log2
from io import BytesIO
from heap import MinHeap

from utils import DataIsNotBytesError, TreeNode, MAGIC_NUMBER, bytes_to_int, File

class Compressor:
    def __init__(self, data_file, word_len = 1, use_arg = False):
        """ Initialize the compressor object and set up everything,
        for compressing the file. The data needs to be of type bytes. """
        if type(data) is not bytes:
            raise DataIsNotBytesError("The data supplied to the compressor\
            is excpected to be of type 'bytes' and not {}.".format(type(data)))
        
        self.file = File(data_file, word_len, use_arg)
        self.data = data
        self.initialize()
        self.data_length = len(self.file) # will be given a value by _mk_freq_dict
        self.compressed_data = None
        self.word_len = word_len

    def initialize(self):
        """ Makes the frequency dict, list and encoding tree."""
        self.freq_dict = self._mk_freq_dict()
        self.freq_list = list()
        for word in self.freq_dict:
            self.freq_list.append(TreeNode(self.freq_dict[word], content = word))
        self.encode_tree = self._mk_encode_tree()
        self.encode_dict = self._mk_encode_dict()

    @classmethod
    def from_file(cls, fname):
        """ Returns a new Compressor object. fname stands for file name. """
        with open(fname, "br") as f:
            data = f.read()

        return cls(data)

    def compress_data(self, write_obj = None):
        """write_obj is a writable object"""
        if write_obj == None:
            self.compressed_data = BytesIO()
            write_obj = self.compress_data

        temp_byte = int(0) # cannot bit shift a bytes object directly
        temp_bits_written = 0

        for byte in self.file:
            word_compressed = self.encode_dict[byte]
            word_compressed_length = len(word_compressed)
            comp_word_index = 0

            for comp_word_index in range(word_compressed_length):
            #while comp_word_index < word_compressed_length:
                if word_compressed[comp_word_index] == "1":
                    temp_byte += 1
                temp_bits_written += 1

                if temp_bits_written == 8:
                    self.compressed_data.write(temp_byte.to_bytes(1, "big", signed = False))
                    temp_byte = 0
                    temp_bits_written = 0
                else:
                    temp_byte = temp_byte << 1

        if temp_bits_written != 0:
            temp_byte = temp_byte << (8 - temp_bits_written - 1)
            self.compressed_data.write(temp_byte.to_bytes(1, "big", signed = False))

        self.compressed_data.seek(0)

    def get_compressed_data(self):
        if self.compressed_data is None:
            self.compress_data()
        self.compressed_data.seek(0)
        return self.compressed_data.read()

    def write_to_file(self, file_object):
        meta = self._gen_meta()
        file_object.write(meta["magic_number"].encode("UTF-8"))
        file_object.write(meta["data_length"].to_bytes(8, "big", signed = False))
        file_object.write("DICT_START".encode("utf-8"))
        file_object.write(str(meta["encode_dict"]).encode("utf-8"))
        file_object.write("DICT_END".encode("utf-8"))
        file_object.write(self.get_compressed_data())

    def _mk_freq_dict(self):
        """ Constructs and returns a dict with the bytes as keys, and
        the total number of times that byte appears in data as
        the value. """

        freq_dict = dict()
        for word in self.file:
            if word not in freq_dict:
                freq_dict[word] = 1
            else:
                freq_dict[word] += 1
        return freq_dict

    def _mk_encode_tree(self):
        """Constructs the encoding tree form a list containing _Node objects.
        Assumes that freq_list is sorted in ascending order.
        Returns the first node of the tree."""
        
        freq_heap = MinHeap.from_iterable(self.freq_list)
        while len(freq_heap) > 1:
            # get the nodes with the smallest frequency
            a = freq_heap.remove()
            b = freq_heap.remove()

            # make the new node and add it in it's proper position
            new_node = TreeNode(a.freq + b.freq, content = None)
            new_node.lchild = a
            new_node.rchild = b
            freq_heap.insert(new_node)

        return freq_heap.remove()

    def _mk_encode_dict(self):
        def transverse(node, encode_dict, collected):
            if node.content is not None:
                encode_dict[node.content] = collected
            else:
                if node.rchild is not None:
                    transverse(node.rchild, encode_dict, collected + "1")
                if node.lchild is not None:
                    transverse(node.lchild, encode_dict, collected + "0")

        encode_dict = dict()
        transverse(self.encode_tree, encode_dict, "")
        return encode_dict

    def _gen_meta(self):
        """ Generates meta data to be used during decompression.
        Return type is a dictionary."""
        meta = {"encode_dict" : self.encode_dict,
                "data_length" : self.data_length,
                "magic_number" : MAGIC_NUMBER}
        return meta

if __name__ == "__main__":
    with open("text.txt", "br") as f:
        data = f.read()
    compressor = Compressor(data)
    compressor.compress_data()
    with open("compressed", "bw") as f:
        compressor.write_to_file(f)
    print(compressor.get_compressed_data())