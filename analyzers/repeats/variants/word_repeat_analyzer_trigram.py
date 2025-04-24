import pymorphy3
from typing import List
from nltk import ngrams
from analyzers.repeats.types import RepeatDataType, WordInfoType
from analyzers.repeats.words_extractor import extract_words

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
  morph = pymorphy3.MorphAnalyzer()

  for cluster in clusters:
    sorted_words = sorted(cluster, key=lambda x: x['word_index'])
    n = len(sorted_words)
    groups = []
    start = 0

    # Формируем группы через sliding window
    while start < n:
      max_end = start
      while (max_end + 1 < n) and (sorted_words[max_end + 1]['word_index'] - sorted_words[start]['word_index'] <= window_size):
        max_end += 1
      if max_end > start:
        current_group = sorted_words[start:max_end + 1]
        groups.append(current_group)
      start = max_end + 1

    # Обрабатываем найденные группы
    for group in groups:
      unique_group = []
      seen_indices = set()
      for word in group:
        idx = word['word_index']
        if idx not in seen_indices:
          seen_indices.add(idx)
          unique_group.append(word)
      if len(unique_group) >= 2:
        # Определяем, является ли слово служебным (по первому слову в группе)
        parsed = morph.parse(unique_group[0]['word'])[0]
        is_function_word = 'PREP' in parsed.tag or 'CONJ' in parsed.tag or 'PRCL' in parsed.tag
        result.append({
          'isFunctionWord': is_function_word,
          'analyzerName': 'trigram',
          'repeats': [{
            'startPosition': w['start'],
            'endPosition': w['end'],
            'word': w['original']
          } for w in sorted(unique_group, key=lambda x: x['word_index'])]
        })

  # Сортируем результат по позициям
  result.sort(key=lambda x: x['repeats'][0]['startPosition'])
  return result
