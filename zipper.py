#!/usr/bin/env python

import argparse
import sys
from encoder import Compressor
from decoder import Decompressor



def arg_parser():
    parser = argparse.ArgumentParser(prog = "zipper",
                                    description = "Simple program for compressing\
                                                    and decompressing files")
    parser.add_argument("file", action = "store", help = "Specifies the input file", metavar = "FILE")
    
    output = parser.add_mutually_exclusive_group()
    output.add_argument("-o", "--output", action = "store", help = "The name of the output file (optional)")
    output.add_argument("--to-stdout", action = "store_true", dest = "to_stdout", help = "Prints to stdout")

    mode = parser.add_mutually_exclusive_group(required = True)
    mode.add_argument("-c", "--compress", action = "store_const", dest = "mode", const = "c", help = "Compress the input file")
    mode.add_argument("-d", "--decompress", action = "store_const", dest = "mode", const = "d", help = "Decompress the input file")
    
    parser.add_argument("-b", "--bytes", dest = "word_length", type = int, default = 4, choices = [1,2,4,8], help = "The word length in bytes used for compression. Default: 4")
    parser.add_argument("-v", "--verbose", action = "store_true", help = "Be verbose")
    return parser

def main():
    parser = arg_parser()
    args = parser.parse_args()

    data_handler = Compressor if args.mode == "c" else Decompressor

    #figure out where the output goes
    if args.to_stdout:
        sys.stdout.close()
        output_file = open(1, "bw")
    else:
        if args.output is not None:
            out_name = args.output
        else:
            if args.mode == "c":
                out_name = args.file + ".compressed"
            else:
                if args.file.endswith(".compressed"):
                    out_name = args.file[:args.file.rindex(".")]
                else:
                    out_name = args.file + ".decompressed"
        try:
            output_file = open(out_name, "wb")
        except PermissionError:
            exit("Permission to write to file '{}' denied".format(out_name))

    handler = data_handler(args.file, word_len = args.word_length)
    if args.mode == "c":
        handler.compress(output_file)
    else:
        handler.decompress(output_file)
    output_file.close()

    if args.verbose:
        print("File '{}' {}compressed.".format(args.file, "de" if args.mode == "d" else ""),
            file = sys.stderr)
        print("Output written to '{}'".format("stdout" if args.to_stdout else out_name),
            file = sys.stderr)        

if __name__ == "__main__":
    main()
