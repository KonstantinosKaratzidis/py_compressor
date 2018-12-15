from io import BytesIO

from utils import TreeNode, DataIsNotBytesError, MAGIC_NUMBER,\
                        NotCorrectMagicNumber, bytes_to_encode_dict

class CompressedData:
    def __init__(self, data):
        if type(data) is not bytes:
            raise DataIsNotBytesError
        if self._check_magic_number(data):
            data = data[len(MAGIC_NUMBER):]
        meta = self._get_meta(data)

        self.encode_dict = meta["encode_dict"]
        self.orig_length = meta["orig_length"]
        self.data = meta["data"]

    def _get_meta(self, data):
        """Returns a dict containing original data length,
        the encode table and the compressed data"""
        meta = dict()
        orig_length = int.from_bytes(data[:8], "big")
        encode_dict_tmp = data[8 + len("DICT_START"): data.index("DICT_END".encode("utf-8"))] 
        encode_dict = bytes_to_encode_dict(encode_dict_tmp)
        comp_data = data[data.index("DICT_END".encode("utf-8")) + 8: ]

        meta["orig_length"] = orig_length
        meta["encode_dict"] = encode_dict
        meta["data"] = comp_data
        return meta

    def _check_magic_number(self, data):
        """ Checks the magic number and if found to be correct,
        it removes it from the compressed, so that data does not contain it"""
        if not data.startswith(MAGIC_NUMBER.encode("utf-8")):
            raise NotCorrectMagicNumber("Compressed file should start with\
                                        {}".format(MAGIC_NUMBER))
        return True

class Decompressor:
    def __init__(self, raw_data):
        """ Initializes the object. raw_data is the data just like
        read from the file. It needs to be of type bytes."""
        #the init method of CompressedData does the checks
        compressed_data = CompressedData(raw_data)
        self.orig_length = compressed_data.orig_length
        self.encode_dict = compressed_data.encode_dict
        self.data = compressed_data.data
        # starting node, not contain any information
        self.encode_tree = TreeNode(0)

        self._mk_encode_tree()
        self.uncompressed_data = None

    @classmethod
    def from_file(cls, fname):
        with open(fname, "br") as f:
            return cls(f.read())

    def uncompress(self):
        if self.uncompressed_data is not None:
            return

        def bit_generator(data):
            if type(data) is not bytes:
                raise DataIsNotBytesError
            for byte in data:
                mask = 256
                for i in range(8):
                    mask = mask >> 1
                    bit = (byte & mask) >> (7 - i)
                    yield bit

        uncompressed_data = BytesIO()
        decoded_chars = 0
        tree_start = self.encode_tree
        curr_node = tree_start
        for bit in bit_generator(self.data):
            if decoded_chars == self.orig_length:
                break
            child_attr = "lchild" if bit == 0 else "rchild"
            curr_node = curr_node.__getattribute__(child_attr)
            
            if curr_node.content is not None:
                uncompressed_data.write(curr_node.content)
                curr_node = tree_start
                decoded_chars += 1
        self.uncompressed_data = uncompressed_data

    def get_uncmpressed_data(self):
        if self.uncompressed_data is None:
            self.uncompress()
        self.uncompressed_data.seek(0)
        return self.uncompressed_data.read()

    def _mk_encode_tree(self):
        """Reconstructs the encoding tree from the encoding dict"""
        # the TreeNode's attribute freq is of no interest here
        tree_start = self.encode_tree
        for byte in self.encode_dict:
            encoding = self.encode_dict[byte]
            cur_node = tree_start
            for bit in encoding:
                child_attr = "lchild" if bit == "0" else "rchild"
                if cur_node.__getattribute__(child_attr) is None:
                    cur_node.__setattr__(child_attr, TreeNode(0))
                cur_node = cur_node.__getattribute__(child_attr)
            cur_node.content = byte.to_bytes(1, "big", signed = False)

    def write_to_file(self, file_object):
        file_object.write(self.get_uncmpressed_data())

if __name__ == "__main__":
    
    decoder = Decompressor.from_file("compressed")
    print(decoder.get_uncmpressed_data().decode(), end = "")