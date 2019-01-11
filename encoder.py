from math import log2
from io import BytesIO
from heap import MinHeap

from utils import DataIsNotBytesError, TreeNode, MAGIC_NUMBER, bytes_to_int, File

class Compressor:
    def __init__(self, data_file, word_len = 1, is_open_stream = False):
        """ Initializes the compressor object and sets up everything,
        for compressing the file.
        The data_file is the path to the file, except if is_open_stream is True,
        in which case it is treated as a readable binary stream."""
        
        self.file = File(data_file, word_len, is_open_stream)
        self.data_length = len(self.file)
        self.initialize()
        self.word_len = word_len

    def initialize(self):
        """ Makes the frequency dict, list and encoding tree."""
        self.freq_dict = self._mk_freq_dict()
        self.freq_list = list()
        for word in self.freq_dict:
            self.freq_list.append(TreeNode(self.freq_dict[word], content = word))
        self.encode_tree = self._mk_encode_tree()
        self.encode_dict = self._mk_encode_dict()


    def compress(self, write_obj, data_only = False):
        """write_obj is a binary writable object.
        If data_only is set to True then only the compressed data will be written.
        Otherwise it will also write meta information at the start of the stream."""
        
        if not data_only:
            self.write_meta(write_obj)

        temp_byte = int(0) # cannot bit shift a bytes object directly
        temp_bits_written = 0

        for word in self.file:
            word_compressed = self.encode_dict[bytes_to_int(word)]
            word_compressed_length = len(word_compressed)
            comp_word_index = 0

            for comp_word_index in range(word_compressed_length):
            #while comp_word_index < word_compressed_length:
                if word_compressed[comp_word_index] == "1":
                    temp_byte += 1
                temp_bits_written += 1

                if temp_bits_written == 8:
                    write_obj.write(temp_byte.to_bytes(1, "big", signed = False))
                    temp_byte = 0
                    temp_bits_written = 0
                else:
                    temp_byte = temp_byte << 1

        if temp_bits_written != 0:
            temp_byte = temp_byte << (8 - temp_bits_written - 1)
            write_obj.write(temp_byte.to_bytes(1, "big", signed = False))

        write_obj.seek(0)

    def write_meta(self, file_object):
        """Writes meta information to file_object."""
        meta = self._gen_meta()
        file_object.write(meta["magic_number"].encode("UTF-8"))
        file_object.write(meta["data_length"].to_bytes(8, "big", signed = False))
        file_object.write(meta["word_length"].to_bytes(8, "big", signed = False))
        file_object.write("DICT_START".encode("utf-8"))
        file_object.write(str(meta["encode_dict"]).encode("utf-8"))
        file_object.write("DICT_END".encode("utf-8"))

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
        """Constructs the encoding tree form the heap containing _Node objects.
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
        #recurssively
        def transverse(node, encode_dict, collected):
            if node.content is not None:
                encode_dict[bytes_to_int(node.content)] = collected
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
        Returns a dictionary."""
        meta = {"encode_dict"  : self.encode_dict,
                "word_length"  : self.word_len,
                "data_length"  : self.data_length,
                "magic_number" : MAGIC_NUMBER}
        return meta

if __name__ == "__main__":
    word_length = 4
    compressor = Compressor("test", word_len= word_length)
    with open("compressed", "wb") as f:
        compressor.compress(f)