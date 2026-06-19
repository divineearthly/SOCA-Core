"""
sutra_080: BM25 Retriever
Pramana: Anumana (Inference)
Rank knowledge by BM25 score
"""

import os
import json
import sys
import math
from collections import Counter
sys.path.append('runtime')
from response import success_response, failure_response

class BM25:
    def __init__(self, corpus, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.corpus = corpus
        self.doc_lengths = [len(doc.split()) for doc in corpus]
        self.avg_doc_len = sum(self.doc_lengths) / len(self.doc_lengths)
        
        # Term frequencies
        self.tf = []
        self.doc_freq = {}
        for doc in corpus:
            words = doc.lower().split()
            tf = Counter(words)
            self.tf.append(tf)
            for word in set(words):
                self.doc_freq[word] = self.doc_freq.get(word, 0) + 1
        
        self.N = len(corpus)
    
    def score(self, query):
        query_words = query.lower().split()
        scores = []
        
        for doc_idx, tf in enumerate(self.tf):
            score = 0
            doc_len = self.doc_lengths[doc_idx]
            for word in query_words:
                if word in self.doc_freq:
                    idf = math.log((self.N - self.doc_freq[word] + 0.5) / (self.doc_freq[word] + 0.5) + 1)
                    term_freq = tf.get(word, 0)
                    numerator = term_freq * (self.k1 + 1)
                    denominator = term_freq + self.k1 * (1 - self.b + self.b * doc_len / self.avg_doc_len)
                    score += idf * (numerator / denominator)
            scores.append(score)
        
        return scores

def execute(inputs: dict, context: dict = None) -> dict:
    query = inputs.get('query', '').lower()
    knowledge_results = inputs.get('knowledge_results', [])
    top_k = inputs.get('top_k', 5)
    
    if not query:
        return failure_response("Query required")
    
    if not knowledge_results:
        return success_response(
            outputs={
                'ranked_results': [],
                'count': 0,
                'note': 'No knowledge to rank'
            },
            confidence=0.5
        )
    
    # Build corpus from knowledge results
    corpus = []
    items = []
    for item in knowledge_results:
        data_str = json.dumps(item.get('data', {})).lower()
        corpus.append(data_str)
        items.append(item)
    
    # BM25 scoring
    bm25 = BM25(corpus)
    scores = bm25.score(query)
    
    # Combine with items
    ranked = []
    for i, item in enumerate(items):
        ranked.append({
            'source': item.get('source', 'unknown'),
            'data': item.get('data', {}),
            'bm25_score': round(scores[i], 4)
        })
    
    # Sort by BM25 score
    ranked.sort(key=lambda x: x['bm25_score'], reverse=True)
    
    return success_response(
        outputs={
            'ranked_results': ranked[:top_k],
            'count': len(ranked),
            'top_score': ranked[0]['bm25_score'] if ranked else 0
        },
        confidence=0.9,
        metadata={'sutra': 'sutra_080', 'version': '1.0.0'}
    )
