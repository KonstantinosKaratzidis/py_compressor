import functools
from io import BytesIO
from os import stat

MAGIC_NUMBER = "ZIPPER_FUN_v_1.0"

class DataIsNotBytesError(BaseException):
    pass

class NotCorrectMagicNumber(BaseException):
    pass

@functools.total_ordering
class TreeNode:
    """A node that is used when constructing the encoding tree"""
    def __init__(self, freq, content = None):
        self.freq = freq
        self.content = content
        self.rchild = None
        self.lchild = None

    def __repr__(self):
        return "Node({}, {})".format(self.freq, self.content)

    def __eq__(self, other):
        if type(other) == TreeNode:
            return self.freq == other.freq
        return NotImplemented
    def __lt__(self, other):
        if type(other) == TreeNode:
            return self.freq < other.freq
        return NotImplemented

def bytes_to_encode_dict(dict_bytes):
    """Exracts the encode dict when it has been encoded to a file.
    dict_dict contains the bytes string that is between 'DICT_START'
    and 'DICT_END' in the file."""
    ret = dict()
    d = dict_bytes[1 : -1].decode("utf-8")
    pairs = d.split(",")
    for pair in pairs:
        key, value = pair.strip().split(": ")
        ret[int(key)] = value.replace("'", "")
    return ret

class File:
    """A class that provides a wrapper for the
    TextIOWrapper. """
    def __init__(self, fname, word_len = 1, is_open_stream = False):
        """is_open_stream means that fname is considered to be data
        and is wrapped in a bytes_io object.
        Word_len is how many bytes will be returned when requested."""
        if is_open_stream:
            if type(fname) != bytes or type(fname) != str:
                raise TypeError("Expected type to be passed as argument to the File class is either 'bytes' or 'str'")
            if type(fname) is str:
                fname = fname.encode("utf-8")
            self.size = len(fname)
            self.file_base = BytesIO(fname)
        else:
            self.file_base = open(fname, "br")
            self.size = stat(fname).st_size
        self.word_len = word_len

    def __len__(self):
        return self.size

    def __iter__(self):
        self.seek(0)
        return self
    
    def __next__(self):
        ret = self.read(self.word_len)
        if len(ret) == 0:
            raise StopIteration
        if len(ret) < self.word_len:
            ret = ret + (self.word_len - len(ret)) * bytes.fromhex("00")
        return ret

    def read(self, length = None):
        return self.file_base.read(length)

    def tell(self):
        return self.file_base.tell()

    def seek(self, offset, whence = 0):
        self.file_base.seek(offset, whence)

    def close(self):
        self.file_base.close()

def bytes_to_int(bytes_obj, byteorder = "big"):
    return int.from_bytes(bytes_obj, byteorder)
