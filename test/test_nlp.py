import spacy

def word_similarity_spacy():
    nlp = spacy.load('en_core_web_md')

    print("Enter two space-separated words")
    words = input()

    tokens = nlp(words)

    for token in tokens:
        # Printing the following attributes of each token.
        # text: the word string, has_vector: if it contains
        # a vector representation in the model,
        # vector_norm: the algebraic norm of the vector,
        # is_oov: if the word is out of vocabulary.
        print(token.text, token.has_vector, token.vector_norm, token.is_oov)

    token1, token2 = tokens[0], tokens[1]

    print("Similarity:", token1.similarity(token2))

import nltk

from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic
def word_similarity_wn():
    print("Enter two space-separated words")
    words = input().split(" ")
    words = [word+".n.01" for word in words]
    w1 = wn.synset(words[0])
    w2 = wn.synset(words[1])
    brown_ic = wordnet_ic.ic('ic-brown.dat')
    print(w1.jnc_similarity(w2, brown_ic))

if __name__ == "__main__":
    word_similarity_spacy()