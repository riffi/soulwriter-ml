import pymorphy3
from typing import List, Dict, TypedDict, Callable, Any

from analyzers.types import RepeatDataType, LemmaDataType, WordInfoType, RepeatItemType
from analyzers.words_extractor import extract_words

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
    current_window: int = window_size_tech_words + 1 if is_function_word else window_size + 1

    # Сортируем слова по их позициям в тексте
    words_list.sort(key=lambda x: x['start'])

    repeats: List[WordInfoType] = []
    for i in range(len(words_list)):
      for j in range(i + 1, len(words_list)):
        distance = words_list[j]['word_index'] - words_list[i]['word_index']  # type: ignore
        if distance <= current_window:
          if words_list[i] not in repeats:
            repeats.append(words_list[i])
          if words_list[j] not in repeats:
            repeats.append(words_list[j])

    if len(repeats) >= 2:
      repeats.sort(key=lambda x: x['start'])
      repeat_data.append({
        'isFunctionWord': is_function_word,
        'analyzerName': 'lemm',
        'repeats': [{
          'startPosition': w['start'],
          'endPosition': w['end'],
          'word': w['original']
        } for w in repeats]
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
