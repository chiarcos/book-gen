import csv, sys
import numpy as np
from sklearn.preprocessing import *


#run e.g.
"""
python normalization.py -o=normalized_scores -s=tsv_with_scores/CathodeAnodeMaterialsLithiumIon.3-gram.vs.maxAbstractSentence.tsv
"""

def get_score_sent_pairs_from_tsv(tsv_filepath, encoding="ISO-8859-1"):
  """expects tokenized sentences in tsv file!"""
  with open(tsv_filepath, encoding=encoding) as tsvfile:
    reader = csv.reader(tsvfile, delimiter='\t')
    score_sent_pairs = [[float(row[0]), row[1]] for row in reader]
  return score_sent_pairs

def normalize_scores_division_sentlength(score_sent_pairs):
  return [[float(score)/len(sent.split()), sent] for [score, sent] in score_sent_pairs]

def normalize_scores_normalizer(score_sent_pairs, normalizer=None, multiply_score_with=1):
  """score_sent_pairs should be a list of tuples (score, sent) where the score values were already normalized by sentence length division
  result of function  normalize_scores_division_sentlength """
  print("Using normalizer: ", normalizer)
  scores = [score for [score, sent] in score_sent_pairs]
  print(scores[:10])
  if normalizer.__class__ == Normalizer:
    normalizer = normalizer.fit([scores])
    scores_norm = normalizer.transform([scores])[0]
  else:
    normalizer = normalizer.fit(scores)
    scores_norm = normalizer.transform(scores)
    scores_norm = [s[0] for s in scores_norm]
  print(scores_norm[:10])
  scores_norm = list(map(lambda x: x*multiply_score_with, scores_norm))
  return [(i,k) for (i,[j,k]) in zip(scores_norm, score_sent_pairs)]

def limit_to_interval(a,b,score_sent_pairs):
  """score sent pairs: list of tuples (score, sent)"""
  return list(filter(lambda x: a<x[0]<b, score_sent_pairs))


def quantile_trans(score_sent_pairs, output_distribution="uniform"):
  print("Doing quantile transformation")
  scores = [s for (s, sent) in score_sent_pairs]
  sents = [sent for (s, sent) in score_sent_pairs]
  scores_norm = quantile_transform([[i] for i in scores], output_distribution=output_distribution).squeeze() #requires linear activation in output layer as these nor$
  return list(zip(scores_norm, sents))


def write_result(score_sent_pairs, outputfile="normalized_scores.csv", encoding_outputfile="ISO-8859-1"):
  """writes the list of tuples (score, sent) to csv file """
  with open(outputfile,"w",encoding=encoding_outputfile) as tsvfile:
    writer = csv.writer(tsvfile)
    for s,sent in score_sent_pairs:
      writer.writerow([s,sent])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = '')
    parser.add_argument('--score_file_tsv', '-s', default='tsv_with_scores/CathodeAnodeMaterialsLithiumIon.3-gram.vs.maxAbstractSentence.tsv', type=str, \
                        help="Path to the tsv file containing each sentence with score - this tsv file is the output generated by ")
    parser.add_argument('--output_dir', '-o', default='normalized_scores', help="Directory to which the result files should be saved", type=str)
    args = parser.parse_args()
    scorefile=args.score_file_tsv
    ssp = get_score_sent_pairs_from_tsv(scorefile)
    normalize_sentlengt = normalize_scores_division_sentlength(ssp)

    if not os.path.exists(args.output_dir):
      os.mkdir(args.output_dir)

    write_result(normalize_sentlengt, outputfile=os.path.join(args.output_dir, "normalized_scores_sentlen.csv"), encoding_outputfile="ISO-8859-1")

    limit1 = limit_to_interval(-1,70, ssp) #0 values included
    print("len limit: ", len(limit1))
    write_result(limit1, outputfile=os.path.join(args.output_dir, "normalized_scores_sentlen_limit--1-70.csv"), encoding_outputfile="ISO-8859-1")

    ##different normlizers on all data
    normalizer=Normalizer()
    score_sent_pairs_norm = normalize_scores_normalizer(normalize_sentlengt, normalizer=normalizer, multiply_score_with=1)
    write_result(score_sent_pairs_norm, outputfile=os.path.join(args.output_dir, "normalized_scores_normalizer.csv"), encoding_outputfile="ISO-8859-1")

    normalizer=MinMaxScaler() #cauten, shape for this normalizer has to be [[],[],..]
    normalize_sentlengt_reshaped = [([i],j) for (i,j) in normalize_sentlengt]
    score_sent_pairs_norm = normalize_scores_normalizer(normalize_sentlengt_reshaped, normalizer=normalizer, multiply_score_with=1)
    write_result(score_sent_pairs_norm, outputfile=os.path.join(args.output_dir, "normalized_scores_minmaxscaler.csv"), encoding_outputfile="ISO-8859-1")

    ##different normalizers on limited data
    normalizer=Normalizer()
    score_sent_pairs_norm = normalize_scores_normalizer(limit1, normalizer=normalizer, multiply_score_with=1)
    write_result(score_sent_pairs_norm, outputfile=os.path.join(args.output_dir, "normalized_scores_limit_normalizer.csv"), encoding_outputfile="ISO-8859-1")

    normalizer=MinMaxScaler() #cauten, shape for this normalizer has to be [[],[],..]
    limit1_reshaped = [([i],j) for (i,j) in limit1]
    score_sent_pairs_norm = normalize_scores_normalizer(limit1_reshaped, normalizer=normalizer, multiply_score_with=1)
    write_result(score_sent_pairs_norm, outputfile=os.path.join(args.output_dir, "normalized_scores_limit_minmaxscaler.csv"), encoding_outputfile="ISO-8859-1")
