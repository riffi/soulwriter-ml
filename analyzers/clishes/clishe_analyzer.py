import re
import os
from pymorphy3 import MorphAnalyzer

morph = MorphAnalyzer()
script_dir = os.path.dirname(__file__)

def lemmatize_text_with_positions(text):
  # Разбиваем текст на токены с их позициями и леммами
  tokens = []
  for match in re.finditer(r'(\w+)|([^\w\s])', text):
    word, punct = match.groups()
    start, end = match.start(), match.end()
    if word:
      lemma = morph.parse(word)[0].normal_form
      tokens.append((lemma, start, end, 'WORD'))
    elif punct:
      tokens.append((punct, start, end, 'PUNCT'))
  return tokens

def lemmatize_word(word):
  return morph.parse(word)[0].normal_form
def pattern_to_regex(pattern_str):
  tokens = pattern_str.split()
  regex_parts = []

  for token in tokens:
    if token.startswith('(') and token.endswith(')'):
      # Заменяем двоеточия на | и разбиваем варианты
      inner = token[1:-1].replace(':', '|')
      options = [morph.parse(opt.strip())[0].normal_form for opt in inner.split('|')]
      escaped_options = [re.escape(opt) for opt in options]
      regex_parts.append(f"({'|'.join(escaped_options)})")  # Фикс: закрывающая скобка
    elif token == '?':
      regex_parts.append(r'\w+')
    else:
      lemma = morph.parse(token)[0].normal_form
      regex_parts.append(re.escape(lemma))

  return r'(?i)\b' + r'[\s\W]*'.join(regex_parts) + r'\b'

def load_patterns():
  """Загружает паттерны из файла clishes.txt"""
  patterns = []
  file_path = os.path.join(script_dir, './clishes/clishes.txt')

  try:
    with open(file_path, 'r', encoding='utf-8') as f:
      clishes = [line.strip() for line in f if line.strip()]
  except Exception as e:
    print(f"Ошибка: {e}")
    return patterns

  for clishe in clishes:
    try:
      patterns.append(re.compile(pattern_to_regex(clishe), flags=re.IGNORECASE))
    except Exception as e:
      print(f"Ошибка в паттерне '{clishe}': {e}")

  return patterns

def lemmatize_text(text):
  words = re.findall(r'\w+', text.lower())
  return ' '.join([lemmatize_word(w) for w in words])


def find_matches(text, regex_patterns):
  tokens = lemmatize_text_with_positions(text)
  lemmatized_text = ' '.join([lemma for lemma, _, _, type_ in tokens if type_ == 'WORD'])

  matches = []
  for regex in regex_patterns:
    for match in regex.finditer(lemmatized_text):
      # Находим границы в лемматизированном тексте
      match_start = match.start()
      match_end = match.end()

      # Сопоставляем с исходными позициями
      start_pos = None
      end_pos = None
      current_pos = 0
      for token in tokens:
        lemma, t_start, t_end, type_ = token
        if type_ == 'WORD':
          token_len = len(lemma) + 1  # +1 для пробела
          if current_pos <= match_start < current_pos + token_len:
            start_pos = t_start
          if current_pos < match_end <= current_pos + token_len:
            end_pos = t_end
            break
          current_pos += token_len
        else:
          continue

      if start_pos is not None and end_pos is not None:
        matches.append({
          'pattern': regex.pattern,
          'text': text[start_pos:end_pos],
          'start': start_pos,
          'end': end_pos
        })

  return matches

def get_cliched_matches(text):
  patterns = load_patterns()
  return find_matches(text, patterns)
