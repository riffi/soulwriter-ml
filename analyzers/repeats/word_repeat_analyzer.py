# Основная функция для поиска повторяющихся слов в тексте
from typing import List, Set

from analyzers.repeats.types import RepeatDataType
from analyzers.repeats.variants.word_repeat_analyzer_lemm import \
  get_word_repeats_by_lemm
from analyzers.repeats.variants.word_repeat_analyzer_trigram import \
  get_word_repeats_by_trigram


def get_word_repeats(
    text: str,
    window_size: int,              # Максимальное расстояние между повторениями обычных слов
    window_size_tech_words: int    # Максимальное расстояние между повторениями служебных слов
) -> List[RepeatDataType]:
  # Получаем результаты от обоих анализаторов
  lemm_results = get_word_repeats_by_lemm(text, window_size, window_size_tech_words)
  trigram_results = get_word_repeats_by_trigram(text, window_size)

  # Объединяем и сортируем результаты
  combined = lemm_results + trigram_results

  # Удаление дублей
  unique_entries: List[RepeatDataType] = []
  seen: Set[str] = set()

  for entry in combined:
    # Сортируем повторы по начальной позиции
    sorted_repeats = sorted(entry['repeats'], key=lambda x: x['startPosition'])
    # Генерируем уникальный ключ
    key_parts = [
      f"{r['startPosition']}_{r['endPosition']}_{r['word']}"
      for r in sorted_repeats
    ]
    key = "|".join(key_parts)

    if key not in seen:
      seen.add(key)
      # Обновляем запись с отсортированными повторами
      unique_entry = {**entry, 'repeats': sorted_repeats}
      unique_entries.append(unique_entry)

  # Сортировка по позиции первого повтора
  unique_entries.sort(key=lambda x: x['repeats'][0]['startPosition'])
  return unique_entries

  return combined
