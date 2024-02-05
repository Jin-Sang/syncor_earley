import parso
from transformers import AutoTokenizer, AutoModelForCausalLM
# from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import os
import glob
import re
import csv
import pandas as pd

# def tokenize_for_bleu_eval(code):
#     code = re.sub(r'([^A-Za-z0-9_])', r' \1 ', code)
#     code = re.sub(r'([a-z])([A-Z])', r'\1 \2', code)
#     code = re.sub(r'\s+', ' ', code)
#     code = code.replace('"', '`')
#     code = code.replace('\'', '`')
#     tokens = [t for t in code.split(' ') if t]

#     return tokens

# text = "def largest(nums,n):\n\tlargest_nums = numbers.sort(reverse=True)\n\treturn largest_nums"
# ans = "def heap_queue_largest(nums,n):\n\tlargest_nums = hq.nlargest(n, nums)\n\treturn largest_nums"

# CodeBLEU
# Copyright (c) Microsoft Corporation. 
# Licensed under the MIT license.

import argparse
import codebleu.bleu as bleu
import codebleu.weighted_ngram_match as weighted_ngram_match
import codebleu.syntax_match as syntax_match
import codebleu.dataflow_match as dataflow_match

parser = argparse.ArgumentParser()

lang = 'python'
alpha,beta,gamma,theta = 0.25,0.25,0.25,0.25

def compute_codebleu(reference_corpus, translation_corpus):
    # preprocess inputs
    # ref: 각 벤치별 정답'들'
    # trans: 평가 대상
    pre_references = [reference_corpus]
    hypothesis = translation_corpus

    # pre_references = [reference_corpus]
    # hypothesis = [translation_corpus]
    # tokenized_refs = [reference_corpus]
    # tokenized_hyps = [translation_corpus]
    for i in range(len(pre_references)):
        print(len(hypothesis), len(pre_references[i]))
        assert len(hypothesis) == len(pre_references[i])

        references = []
    for i in range(len(hypothesis)):
        ref_for_instance = []
        for j in range(len(pre_references)):
            ref_for_instance.append(pre_references[j][i])
        references.append(ref_for_instance)
    assert len(references) == len(pre_references)*len(hypothesis)

    # calculate ngram match (BLEU)
    tokenized_hyps = [x.split() for x in hypothesis]
    tokenized_refs = [[x.split() for x in reference] for reference in references]

    # tokenized_hyps = [tokenize_for_bleu_eval(x) for x in hypothesis]
    # tokenized_refs = [[tokenize_for_bleu_eval(x) for x in reference] for reference in references]

    ngram_match_score = bleu.corpus_bleu(tokenized_refs,tokenized_hyps)

    # calculate weighted ngram match
    keywords = [x.strip() for x in open('codebleu_utils/'+lang+'.txt', 'r', encoding='utf-8').readlines()]
    def make_weights(reference_tokens, key_word_list):
        return {token:1 if token in key_word_list else 0.2 \
                for token in reference_tokens}
    tokenized_refs_with_weights = [[[reference_tokens, make_weights(reference_tokens, keywords)]\
                for reference_tokens in reference] for reference in tokenized_refs]

    weighted_ngram_match_score = weighted_ngram_match.corpus_bleu(tokenized_refs_with_weights,tokenized_hyps)

    # calculate syntax match
    syntax_match_score = syntax_match.corpus_syntax_match(references, hypothesis, lang, 'codebleu_utils/my-languages.so')

    # calculate dataflow match
    dataflow_match_score = dataflow_match.corpus_dataflow_match(references, hypothesis, lang, 'codebleu_utils/my-languages.so')

    # print('bleu: {0}, weighted ngram match: {1}, syntax_match: {2}, dataflow_match: {3}'.\
    #                     format(ngram_match_score, weighted_ngram_match_score, syntax_match_score, dataflow_match_score))

    code_bleu_score = alpha*ngram_match_score\
                    + beta*weighted_ngram_match_score\
                    + gamma*syntax_match_score\
                    + theta*dataflow_match_score

    return (ngram_match_score, code_bleu_score)

# bleu, codebleu = compute_codebleu([text],[ans])
# print('Blue: {0}'.format(bleu))
# print('CodeBlue: {0}'.format(codebleu))

def make_ref_data(file, succ_list):
    json_data = pd.read_json(file)
    
    data_set = []
    
    for index, row in json_data.iterrows():
        text = row["code"]
        if index in succ_list:
            data_set.append(text)
        
    return data_set

def extract_number(file_name):
    match = re.search(r'(\d+)', file_name)
    if match:
        return int(match.group(1))
    return 0


ref_data = "/home/jskim/syncor/sanitized-mbpp.json"

hyp_list = []
succ_list = []

# read csv
csv_file = "/home/jskim/syncor/csv/base_gen_1.csv"
f = open(csv_file, 'r')
rdr = csv.reader(f)

# Check Only No Syntax Error
for i in rdr:
    if i[2] == "No Syntax Error":
        
        succ_list.append(int(i[0]))
        hyp_list.append(i[3])


ref_list = make_ref_data(ref_data, succ_list)
print(len(ref_list))
sum_bleu, sum_codebleu = 0, 0
for _ in range(10):
    
    bleu_s, codebleu_s = compute_codebleu(ref_list, hyp_list)
    
    sum_bleu += bleu_s
    sum_codebleu += codebleu_s
    
final_bleu = sum_bleu / 10
final_codebleu = sum_codebleu / 10

print('BLEU : ' + str(final_bleu))
print('CodeBLEU : ' + str(final_codebleu))

