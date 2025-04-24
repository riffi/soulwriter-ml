import pymorphy3
from typing import List, Dict

from analyzers.repeats.types import RepeatDataType, LemmaDataType, WordInfoType
from analyzers.repeats.words_extractor import extract_words

morph = pymorphy3.MorphAnalyzer()

def get_word_repeats_by_lemm(
    text: str,
    window_size: int,              # Максимальное расстояние между повторениями обычных слов (в количестве слов)
    window_size_tech_words: int    # Максимальное расстояние между повторениями служебных слов (в количестве слов)
) -> List[RepeatDataType]:
  lemmas_dict: Dict[str, LemmaDataType] = {}
  words_info: List[WordInfoType] = extract_words(text)

  # Добавляем индексы слов, если их нет
  for idx, word_info in enumerate(words_info):
    word_info['word_index'] = idx

  extract_lemmas(lemmas_dict, words_info)

  repeat_data: List[RepeatDataType] = []
  fill_repeat_data(lemmas_dict, repeat_data, window_size, window_size_tech_words)

  repeat_data.sort(key=lambda x: x['repeats'][0]['startPosition'])
  return repeat_data

def fill_repeat_data(
    lemmas_dict: Dict[str, LemmaDataType],
    repeat_data: List[RepeatDataType],
    window_size: int,
    window_size_tech_words: int
) -> None:
  for lemma, data in lemmas_dict.items():
    words_list: List[WordInfoType] = data['words']
    is_function_word: bool = data['is_function_word']
    current_window: int = window_size_tech_words if is_function_word else window_size

    # Сортируем слова по их позициям
    sorted_words = sorted(words_list, key=lambda x: x['word_index'])
    n = len(sorted_words)
    groups = []
    start = 0

    # Формируем группы через sliding window
    while start < n:
      max_end = start
      # Расширяем окно, пока разница между первым и последним элементом <= current_window
      while (max_end + 1 < n) and (sorted_words[max_end + 1]['word_index'] - sorted_words[start]['word_index'] <= current_window):
        max_end += 1
      # Если группа содержит хотя бы два слова
      if max_end > start:
        current_group = sorted_words[start:max_end + 1]
        groups.append(current_group)
      start = max_end + 1

    # Добавляем группы в результат
    for group in groups:
      unique_group = []
      seen_indices = set()
      # Удаляем дубликаты (на случай, если слова имеют одинаковый индекс)
      for word in group:
        idx = word['word_index']
        if idx not in seen_indices:
          seen_indices.add(idx)
          unique_group.append(word)
      if len(unique_group) >= 2:
        repeat_data.append({
          'isFunctionWord': is_function_word,
          'analyzerName': 'lemm',
          'repeats': [{
            'startPosition': w['start'],
            'endPosition': w['end'],
            'word': w['original']
          } for w in unique_group]
        })

def extract_lemmas(lemmas_dict: Dict[str, LemmaDataType], words_info: List[WordInfoType]) -> None:
  for word_data in words_info:
    word: str = word_data['word']
    if not any(1072 <= ord(c) <= 1103 for c in word):
      continue

    parsed = morph.parse(word)[0]
    lemma: str = parsed.normal_form
    is_function_word: bool = 'PREP' in parsed.tag or 'CONJ' in parsed.tag or 'PRCL' in parsed.tag

    if lemma not in lemmas_dict:
      lemmas_dict[lemma] = {
        'words': [],
        'is_function_word': is_function_word
      }
    lemmas_dict[lemma]['words'].append(word_data)
