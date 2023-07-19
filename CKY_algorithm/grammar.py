"""
COMS W4705 - Natural Language Processing - Spring 2023
Homework 2 - Parsing with Context Free Grammars 
Daniel Bauer
"""
import string
import sys
from collections import defaultdict
from math import fsum, isclose


class Pcfg(object): 
    """
    Represent a probabilistic context free grammar. 
    """

    def __init__(self, grammar_file): 
        self.rhs_to_rules = defaultdict(list)
        self.lhs_to_rules = defaultdict(list)
        self.startsymbol = None 
        self.read_rules(grammar_file)      
 
    def read_rules(self,grammar_file):
        
        for line in grammar_file: 
            line = line.strip()
            if line and not line.startswith("#"):
                if "->" in line: 
                    rule = self.parse_rule(line.strip())
                    lhs, rhs, prob = rule
                    self.rhs_to_rules[rhs].append(rule)
                    self.lhs_to_rules[lhs].append(rule)
                else: 
                    startsymbol, prob = line.rsplit(";")
                    self.startsymbol = startsymbol.strip()
                    
     
    def parse_rule(self,rule_s):
        lhs, other = rule_s.split("->")
        lhs = lhs.strip()
        rhs_s, prob_s = other.rsplit(";",1) 
        prob = float(prob_s)
        rhs = tuple(rhs_s.strip().split())
        return (lhs, rhs, prob)

    def verify_grammar(self):
        """
        Return True if the grammar is a valid PCFG in CNF.
        Otherwise return False.
        """
        # TODO, Part 1
        # helper method used to determine if the word is terminal or is non-terminal
        def is_terminal_word(word):
            # all the terminal words are lower case
            # check if the word is a lower case word
            terminal_word = word.islower()
            if terminal_word or (word in string.punctuation):
                #print("this word worked: " + word)
                return True
            else:
                #print("this word did not work: " + word)
                return False

        #helper method to check if the RHS is good
        def check_RHS(rhs):
            # arr_rhs should be of max length 2
            if len(rhs) > 2:
                #print("rhs greater 2")
                return False
            if len(rhs) == 1:
                #print("rhs equals 1")
                word = rhs[0]
                if is_terminal_word(word):
                    #print("word is terminal")
                    return True
            elif len(rhs) == 2:
                #print("rhs equals 2")
                #both must be non_terminal
                phrase_one = rhs[0]
                phrase_two = rhs[1]
                if not is_terminal_word(phrase_one) and not is_terminal_word(phrase_two):
                    #print("both non_terminal")
                    return True
            else:
                return False

        #check all probabilites of the lhs symbol add up to or are very close to 1.
        def check_lhs_probs(leftSymbol_prob_dictionary):
            #print(leftSymbol_prob_dictionary)
            for left_symbol, probability in leftSymbol_prob_dictionary.items():
                #print("ran lhs prob loop")
                if isclose(probability, 1):
                    #print("prob is 1")
                    return True
            return False

        #create a dictionary to add too for summation in next loop
        lhs_probs_dictionary = defaultdict(int)
        for key, rule in self.lhs_to_rules.items():
            #prints as follows TOMORROW [('TOMORROW', ('tomorrow',), 1.0)]
            #print(key, rule)
            #print(rule)
            # need to split by rule lhs, rhs, and prob
            left_side, right_side, probability = rule[0]
            #run the checks on these varaibles
            lhs_probs_dictionary[left_side] += probability
            rhs_bool = check_RHS(right_side)
            #print()
            #print(rhs_bool)
            if rhs_bool:
                continue
            else:
                #print("wrong RHS")
                return False

        #now since we have added everything to the lhs_probs we can check

        if check_lhs_probs(lhs_probs_dictionary) == False:
            #print("ran wrong value")
            return False
        else:
            return True



if __name__ == "__main__":
    with open(sys.argv[1],'r') as grammar_file:
        grammar = Pcfg(grammar_file)
        correct = grammar.verify_grammar()
        if correct:
            print("good prob context free grammer")
        else:
            print("bad prob context free grammar")
        
