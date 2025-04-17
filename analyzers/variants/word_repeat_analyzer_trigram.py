import pymorphy3
from typing import List, Dict, TypedDict, Any
from nltk import ngrams
from analyzers.types import RepeatDataType, LemmaDataType, WordInfoType, RepeatItemType
from analyzers.words_extractor import extract_words

morph = pymorphy3.MorphAnalyzer()

def get_trigrams(word: str) -> set:
  return set(ngrams(word.lower(), 3))

def calculate_similarity(a: set, b: set) -> float:
  common = a & b
  return len(common) / max(len(a), len(b)) if max(len(a), len(b)) > 0 else 0

def get_word_repeats_by_trigram(text: str, window_size: int) -> List[RepeatDataType]:
  words_info = extract_words(text)

  # Добавляем индексы слов, если их нет
  for idx, word_info in enumerate(words_info):
    word_info['word_index'] = idx

  clusters = cluster_similar_words(words_info)
  return find_repeats_in_clusters(clusters, window_size)


def cluster_similar_words(words: List[WordInfoType]) -> List[List[WordInfoType]]:
  clusters = []
  trigram_cache = {}

  for word_info in words:
    word = word_info['word']
    if len(word) < 4:
      continue

    trigrams = trigram_cache.get(word)
    if not trigrams:
      trigrams = get_trigrams(word)
      trigram_cache[word] = trigrams

    found_cluster = False
    for cluster in clusters:
      cluster_trigrams = trigram_cache[cluster[0]['word']]
      similarity = calculate_similarity(trigrams, cluster_trigrams)
      if similarity >= 0.5:
        cluster.append(word_info)
        found_cluster = True
        break

    if not found_cluster:
      clusters.append([word_info])

  return clusters

def find_repeats_in_clusters(clusters: List[List[WordInfoType]], window_size: int) -> List[RepeatDataType]:
  result = []

  for cluster in clusters:
    sorted_words = sorted(cluster, key=lambda x: x['word_index'])
    repeats = []

    for i in range(len(sorted_words)):
      for j in range(i+1, len(sorted_words)):
        # Проверяем разницу в количестве слов между позициями
        if sorted_words[j]['word_index'] - sorted_words[i]['word_index'] <= window_size:
          if sorted_words[i] not in repeats:
            repeats.append(sorted_words[i])
          if sorted_words[j] not in repeats:
            repeats.append(sorted_words[j])

    if len(repeats) >= 2:
      parsed = morph.parse(repeats[0]['word'])[0]
      result.append({
        'isFunctionWord': 'PREP' in parsed.tag or 'CONJ' in parsed.tag or 'PRCL' in parsed.tag,
        'analyzerName': 'trigram',
        'repeats': [{
          'startPosition': w['start'],
          'endPosition': w['end'],
          'word': w['original']
        } for w in sorted(repeats, key=lambda x: x['word_index'])]
      })

  result.sort(key=lambda x: x['repeats'][0]['startPosition'])
  return result
