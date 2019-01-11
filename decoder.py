from io import BytesIO

from utils import TreeNode, DataIsNotBytesError, MAGIC_NUMBER,\
                        NotCorrectMagicNumber, bytes_to_encode_dict, File

class CompressedData:
    def __init__(self, data_file, is_open_stream = False):
        """Extracts meta data.
        If is_open_stream is True data_file is treated as a readable
        binary stream."""
        self.data_stream = File(data_file, is_open_stream)

        magic_number = self.data_stream.read(len(MAGIC_NUMBER))
        if magic_number != MAGIC_NUMBER.encode("utf-8"):
            raise NotCorrectMagicNumber("Compressed file should start with\
                                        {}".format(MAGIC_NUMBER))

        meta = self._get_meta(self.data_stream)
        self.orig_length = meta["orig_length"]
        self.word_length = meta["word_length"]
        self.encode_dict = meta["encode_dict"]
        self.data_index = meta["data_index"]

    def _get_meta(self, data_stream):
        """Returns a dict containing original data length,
        the encode table and the compressed data"""
        meta = dict()
        orig_length = int.from_bytes(self.data_stream.read(8), "big")
        word_length = int.from_bytes(self.data_stream.read(8), "big")

        encode_dict_temp = BytesIO()
        while True:
            c = self.data_stream.read(1)
            encode_dict_temp.write(c)
            if c == b"}":
                break
        data_start = self.data_stream.tell() + len("DICT_END")

        encode_dict_temp.seek(0)
        encode_dict = encode_dict_temp.read()
        encode_dict = encode_dict[encode_dict.index(b"{") + 1: encode_dict.index(b"}")]

        meta["orig_length"] = orig_length
        meta["word_length"] = word_length
        meta["encode_dict"] = encode_dict
        meta["data_index"] = data_start
        return meta

class Decompressor(CompressedData):
    def __init__(self, data_file, is_open_stream = False):
        """ Initializes the object.
        If is_open_stream is set to True, data_file is treated as a
        readable binary stream."""
        #the init method of CompressedData does the checks
        #we get orig_length, word_length, encode_dict, data_index
        super().__init__(data_file, is_open_stream)
        self.encode_dict = bytes_to_encode_dict(self.encode_dict)

        # starting node for encode tree, not contain any information
        self.encode_tree = TreeNode(0)

        self._mk_encode_tree()

    def decompress(self, write_obj):
        self.data_stream.seek(self.data_index)

        # generates all the bits in a stream one by one
        def bit_generator(data):
            byte = data.read(1)
            while len(byte) != 0:
                byte = int.from_bytes(byte, "big", signed = False)
                #print(byte)
                mask = 256
                for i in range(8):
                    mask = mask >> 1
                    bit = (byte & mask) >> (7 - i)
                    yield bit
                byte = data.read(1)

        decoded_chars = 0
        tree_start = self.encode_tree
        curr_node = tree_start
        for bit in bit_generator(self.data_stream):
            if decoded_chars >= self.orig_length:
                break
            child_attr = "lchild" if bit == 0 else "rchild"
            curr_node = curr_node.__getattribute__(child_attr)

            if curr_node.content is not None:
                #print(curr_node.content)
                decoded_chars += self.word_length
                if decoded_chars > self.orig_length:
                    diff = self.orig_length - decoded_chars
                    curr_node.content = curr_node.content[:-diff]
                write_obj.write(curr_node.content)
                curr_node = tree_start


    def _mk_encode_tree(self):
        """Reconstructs the encoding tree from the encoding dict"""
        # the TreeNode's attribute freq is of no interest here
        tree_start = self.encode_tree
        for word in self.encode_dict:
            encoding = self.encode_dict[word]
            cur_node = tree_start
            for bit in encoding:
                child_attr = "lchild" if bit == "0" else "rchild"
                if cur_node.__getattribute__(child_attr) is None:
                    cur_node.__setattr__(child_attr, TreeNode(0))
                cur_node = cur_node.__getattribute__(child_attr)
            cur_node.content = word.to_bytes(self.word_length, "big", signed = False)

