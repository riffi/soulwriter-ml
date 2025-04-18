# Функция для извлечения слов из текста
from typing import List

from analyzers.repeats.types import WordInfoType


def extract_words(text):
  words_info: List[WordInfoType] = []
  original_word: str = ''  # Оригинальное слово с регистром
  start_pos: int = 0       # Начальная позиция слова
  current_word: str = ''   # Нормализованное слово (в нижнем регистре)

  for i, char in enumerate(text):
    if char.isalpha() or char == '-':
      if not current_word:
        start_pos = i
        original_word = char
      else:
        original_word += char
      current_word += char.lower()
    else:
      if current_word:
        # Добавление информации о слове в список
        words_info.append({
          'word': current_word,
          'original': original_word,
          'start': start_pos,
          'end': i - 1
        })
        current_word = ''
        original_word = ''

  # Добавление последнего слова, если текст заканчивается на букву
  if current_word:
    words_info.append({
      'word': current_word,
      'original': original_word,
      'start': start_pos,
      'end': len(text) - 1
    })
  return words_info
