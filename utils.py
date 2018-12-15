import functools

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
