import os
from collections import Counter, defaultdict, deque

import numpy as np
import matplotlib.pyplot as plt

sym_splitter = " "
ref_splitter = "_"
alphabet = "abcdefghijklmnopqrstuvwxyzåäö"
alphabet = alphabet + alphabet.upper()

if 1:
    enc_alphabet = "abcdefghijklmnopqrstuvwxyz"
    enc_alphabet = enc_alphabet + enc_alphabet.upper()
    enc_alphabet = enc_alphabet + ".:,;!%&/()=@${[]}^~'*<>|-`\\"
    enc_alphabet = "0123456789" + enc_alphabet
else:
    enc_alphabet = "0123456789"
b = len(enc_alphabet)

root = "0"
symbol_set = set([])

class WZ_Model:
    def __init__(self):
        self.S = {}
        self.G = defaultdict(dict)
        self.s = []
        self.rewind = 0
        self.top = 0
        self.symbol_set = set([]) #symbol_set
        self.prime_with_symbol_set()

    def prime_with_symbol_set(self):
        for a in self.symbol_set:
            self.update(root, a, sym_splitter)

    def get_s(self):
        return self.s[len(self.symbol_set):]

    def get(self, seq, a):
        return self.G[seq][a]

    def update(self, seq, a, splitter):
        self.top += 1
        top = alph(self.top)
        self.S[top] = (seq, a)
        self.G[seq][a] = top
        
        for _ in range(self.rewind):
            self.s.pop() # remove last elements
        self.rewind = 0

        s = list(self.climb_to_root(seq))
        if splitter == ref_splitter:
            self.rewind = self.get_rewind("".join(s))
        self.s.extend(s)
        self.s.append(a)

        return seq, a, splitter

    def climb_to_root(self, seq):
        stack = []
        while seq != root:
            seq, a = self.S[seq]
            stack.append(a)
        return reversed(stack)

    def get_rewind(self, s):
        if all([ch in alphabet for ch in s]):
            return 0

        m = s.rstrip(alphabet)
        return len(s) - len(m) + 1

    def can_be_stripped(self, seq):
        s = "".join(self.climb_to_root(seq))
        rewind = self.get_rewind(s)
        return rewind

    def longest_match(self, s):
        """Finds the longest match in the phrase tree
        of a string
        """
        match = []
        seq = root
        for a in s:
            try:
                seq = self.G[seq][a]
            except KeyError:
                break
            match.append(a)
        return "".join(match)

    def get_seq(self, s):
        """
        Get the phrase tree sequence ID that corresponds
        to a certain string
        Raises a KeyError if s is not in phrase tree
        """
        seq = root
        for a in s:
            seq = self.G[seq][a]
        return seq


def encode(reader):
    global symbol_set

    seq = root
    seq_old = root
    s = reader.read()
    symbol_set = set(s)
    model = WZ_Model()
    N = len(s)
    idx = 0
    match = []

    while idx < N:
        a = s[idx]
        seq_old = seq

        try:
            seq = model.get(seq, a)
            match.append(a)
        except KeyError:
            rewind = model.can_be_stripped(seq)
            if rewind > 0:
                splitter = ref_splitter
                idx -= rewind
                #print("match:", match)
                #print("match[:-rewind]:", match[:-rewind])
                seq_len = len(model.get_seq(match[:-rewind]))
            else:
                splitter = sym_splitter
                seq_len = len(seq)
            yield seq, a, splitter, seq_len
            model.update(seq, a, splitter)
            seq = root
            match = []

        idx += 1

    if seq != root:
        yield seq_old, a, sym_splitter, len(seq_old)
        model.update(seq_old, a, sym_splitter)

    #poll_phrase_tree(model)
    #print("end of encoding")
    #print("G encode:", model.G)
    #print("S encode:", model.S)
    #print(model.s)

def decode(reader):
    model = WZ_Model()
    reader = iter(reader.read())

    queue = deque(maxlen=100)

    while True:
        try:
            seq, splitter = get_id(reader)
        except StopIteration:
            break
        a = next(reader)
        model.update(seq, a, splitter)
        match = "".join(model.climb_to_root(seq)) + a
        queue.append(match)

    yield from model.get_s()

    #for m in queue:
    #    print(m)
    #print("G decode:", model.G)
    #print("S encode:", model.S)
    #print(model.s)


def get_id(reader):
    id_num = []
    while True:
        a = next(reader)
        #print("digit", a)
        if a not in enc_alphabet:
            return "".join(id_num), a
        else:
            id_num.append(a)


def alph(seq):
    """
    Convert an int in base-10 to
    base-whatever length the alphabet is
    Assumes 0 is the 0
    """
    if not seq:
        return root
    s = []
    quot = seq
    while quot:
        quot, rest = quot // b, quot % b
        s.append(enc_alphabet[rest])
    return "".join(reversed(s))


def test_alph():
    for seq in range(11):
        print("alph({}): {}".format(seq, alph(seq)))


default_dbg = False
def debug(*s, dbg=False):
    if default_dbg or dbg:
        print(*s)


def poll_phrase_tree(model):
    strings = ["Nils", "Holgersson", "Akka",
               "Yksi", "Kaksi", "Kolme",
               "Neljä", "Viisi", "Kuusi",
               "vildgåsflock"]

    for s in strings:
        match = model.longest_match(s)
        print()
        print("s:", s)
        print("m:", match)


def main():
    fn = "/home/jdw/garageofcode/data/compression/big.txt"
    #fn = "/home/jdw/garageofcode/data/compression/words.txt"
    #fn = "/home/jdw/garageofcode/data/compression/nilsholg2.txt"
    #fn = "/home/jdw/garageofcode/data/compression/nilsholg.txt"
    #fn = "/home/jdw/garageofcode/data/compression/medium.txt"
    #fn = "short.txt"
    #fn = "veryshort.txt"
    fn_compressed = fn.split(".")[0] + ".wzip"
    fn_reconstructed = fn.split(".")[0] + "_rec.txt"
    fn_zip = fn.split(".")[0] + ".zip"
    # encoding step
    reduced_len = 0
    with open(fn, "r") as r:
        with open(fn_compressed, "w") as f:
            for idx, (seq, a, spl, seq_len) in enumerate(encode(r)):
                f.write("{}{}{}".format(seq, spl, a))
                reduced_len += (seq_len + 1)
    
    num_seqs = idx
    print("Before ", os.stat(fn).st_size)
    print("After  ", os.stat(fn_compressed).st_size)
    print("LZW opt  ", os.stat(fn_compressed).st_size - num_seqs)
    print("Impl. opt  ", reduced_len)
    print(".zip ", os.stat(fn_zip).st_size)

    #  exit()

    with open(fn_compressed, "r") as r:
        with open(fn_reconstructed, "w") as f:
            for a in decode(r):
                #if a == "\\n":
                #    f.write("\n")
                #else:
                f.write(a)

    #exit()
    res = os.system("diff {} {}".format(fn, fn_reconstructed))
    if res:
        print("Reconstruction: failed")
    else:
        print("Reconstruction: OK")

if __name__ == '__main__':
    main()

    #test_alph()
