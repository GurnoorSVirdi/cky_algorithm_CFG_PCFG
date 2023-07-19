"""
COMS W4705 - Natural Language Processing - Spring 2023
Homework 2 - Parsing with Probabilistic Context Free Grammars 
Daniel Bauer
"""
import math
import sys
from collections import defaultdict
import itertools
from grammar import Pcfg


### Use the following two functions to check the format of your data structures in part 3 ###
def check_table_format(table):
    """
    Return true if the backpointer table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict):
        sys.stderr.write("Backpointer table is not a dict.\n")
        return False
    for split in table:
        if not isinstance(split, tuple) and len(split) == 2 and \
                isinstance(split[0], int) and isinstance(split[1], int):
            sys.stderr.write("Keys of the backpointer table must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of backpointer table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str):
                sys.stderr.write(
                    "Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            bps = table[split][nt]
            if isinstance(bps, str):  # Leaf nodes may be strings
                continue
            if not isinstance(bps, tuple):
                sys.stderr.write(
                    "Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Incorrect type: {}\n".format(
                        bps))
                return False
            if len(bps) != 2:
                sys.stderr.write(
                    "Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Found more than two backpointers: {}\n".format(
                        bps))
                return False
            for bp in bps:
                if not isinstance(bp, tuple) or len(bp) != 3:
                    sys.stderr.write(
                        "Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has length != 3.\n".format(
                            bp))
                    return False
                if not (isinstance(bp[0], str) and isinstance(bp[1], int) and isinstance(bp[2], int)):
                    print(bp)
                    sys.stderr.write(
                        "Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has incorrect type.\n".format(
                            bp))
                    return False
    #print("true assert")
    return True


def check_probs_format(table):
    """
    Return true if the probability table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict):
        sys.stderr.write("Probability table is not a dict.\n")
        return False
    for split in table:
        if not isinstance(split, tuple) and len(split) == 2 and isinstance(split[0], int) and isinstance(split[1], int):
            sys.stderr.write("Keys of the probability must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of probability table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str):
                sys.stderr.write(
                    "Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            prob = table[split][nt]
            if not isinstance(prob, float):
                sys.stderr.write(
                    "Values of the inner dictionary (for each span and nonterminal) must be a float.{}\n".format(prob))
                return False
            if prob > 0:
                sys.stderr.write("Log probability may not be > 0.  {}\n".format(prob))
                return False
    #print("true assert")
    return True


class CkyParser(object):
    """
    A CKY parser.
    """

    def __init__(self, grammar):
        """
        Initialize a new parser instance from a grammar. 
        """
        self.grammar = grammar

    def is_in_language(self, tokens):
        """
        Membership checking. Parse the input tokens and return True if 
        the sentence is in the language described by the grammar. Otherwise
        return False
        """
        # TODO, part 2
        # print(tokens)#being passed in as an array

        n = len(tokens)
        Table = [[set() for len in range(n + 1)] for width in range(n + 1)]
        # print(Table)

        # do the first iteration, filling Table with rules for each token
        for i in range(n):
            for rule in self.grammar.rhs_to_rules[(tokens[i],)]:
                Table[i][i + 1].add(rule[0])
        # checking if table is getting diagonal properly
            # print(Table)
        for length in range(2, n + 1):
            for i in range(0, n - length + 1):
                j = i + length
                for mid in range(i + 1, j):
                    # check for midpoint non-temrinals A-> B C
                    for B in Table[i][mid]:
                        for C in Table[mid][j]:
                            rules = {rule[0] for rule in self.grammar.rhs_to_rules[(B, C)]}
                            #used W3 python code to find.union of adding to a set
                            Table[i][j] = Table[i][j].union(rules)

        if self.grammar.startsymbol in Table[0][n]:
            return True
        else:
            return False

    def parse_with_backpointers(self, tokens):
        """
        Parse the input tokens and return a parse table and a probability table.
        """
        # TODO, part 3
        table = defaultdict(dict)
        probs = defaultdict(dict)
        n = len(tokens)

        #first initilize with diagonals
        for i in range(n):
            for rule in self.grammar.rhs_to_rules[tuple([tokens[i]])]:
                left = rule[0]
                prob = rule[2]
                #print(rule[2])
                table[(i, i+1)][left] = tokens[i]
                probs[(i, i+1)][left] = math.log(prob)
            #print(table)
            #print(probs)

        #now run bottom up
        for length in range(2, n + 1):
            for i in range(0, n - length + 1):
                j = i + length
                for mid in range(i + 1, j):
                    # check for midpoint non-terminals A-> B C
                    for B in table[(i, mid)]:
                        for C in table[(mid, j)]:
                            for rule in self.grammar.rhs_to_rules[(B, C)]:
                                left, result, prob = rule
                                x = result[0]
                                y = result[1]
                                probabilites = math.log(prob) + probs[(i, mid)][x] + probs[(mid, j)][y]
                                if left not in probs[(i, j)]:
                                    curr = -float('inf')
                                else:
                                    curr = probs[(i, j)][left]

                                # check probabilites to see if its higher than the curr
                                if probabilites > curr:
                                    table[(i, j)][left] = tuple([(B, i, mid), (C, mid, j)])
                                    probs[(i, j)][left] = probabilites

        return table, probs


def get_tree(chart, i, j, nt):
    """
    Return the parse-tree rooted in non-terminal nt and covering span i,j.
    """
    #print(chart)
    val = chart[(i, j)][nt]
    if isinstance(val, tuple):
        B = val[0]
        C = val[1]
        tree1 = get_tree(chart, B[1], B[2], B[0])
        tree2 = get_tree(chart, C[1], C[2], C[0])
        return (nt, tree1 , tree2)
    else:
        return (nt, val)


if __name__ == "__main__":
    with open('atis3.pcfg', 'r') as grammar_file:
        grammar = Pcfg(grammar_file)
        parser = CkyParser(grammar)
        toks = ['flights', 'from', 'miami', 'to', 'cleveland', '.']
        print(parser.is_in_language(toks))
        table,probs = parser.parse_with_backpointers(toks)
        assert check_table_format(table)
        assert check_probs_format(probs)
