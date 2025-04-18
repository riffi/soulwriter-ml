from typing import List, Dict, TypedDict, Callable, Any


# Тип для хранения информации о слове в тексте
class WordInfoType(TypedDict):
  word: str          # Нормализованное слово (в нижнем регистре)
  original: str      # Оригинальное слово (с сохранением регистра)
  start: int         # Начальная позиция слова в тексте
  end: int           # Конечная позиция слова в тексте
  word_index: int


# Тип для хранения данных о лемме (нормальной форме слова)
class LemmaDataType(TypedDict):
  words: List[WordInfoType]  # Список всех вхождений слова
  is_function_word: bool     # Флаг, является ли слово служебным (предлог/союз)


# Тип для хранения информации о повторяющемся слове
class RepeatItemType(TypedDict):
  startPosition: int  # Начальная позиция повторения
  endPosition: int    # Конечная позиция повторения
  word: str           # Оригинальное слово


# Тип для хранения данных о повторениях
class RepeatDataType(TypedDict):
  isFunctionWord: bool       # Флаг, являются ли повторяющиеся слова служебными
  analyzerName: str          # Название анализатора, который обнаружил повторения
  repeats: List[RepeatItemType]  # Список повторений



