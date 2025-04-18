import re
import os

script_dir = os.path.dirname(__file__)

def pattern_to_regex(pattern_str):
  tokens = pattern_str.split()
  regex_parts = []
  for token in tokens:
    if token.startswith('(') and token.endswith(')'):
      regex_parts.append(token)
    elif token == '?':
      regex_parts.append(r'(\w+)')  # Слово, игнорируя пунктуацию
    else:
      # Разрешаем знаки препинания до/после слова
      regex_parts.append(
          rf"\b{re.escape(token)}[\w']*\b"  # Учитывает апострофы и окончания
      )
  # Между токенами разрешаем пробелы и пунктуацию
  return r'[\s\W]*'.join(regex_parts)

def load_patterns():
  """Загружает паттерны из файла clishes.txt"""
  patterns = []
  file_path = os.path.join(script_dir, './clishes/clishes.txt')
  try:
    with open(file_path, 'r', encoding='utf-8') as f:
      clishes = [line.strip() for line in f if line.strip()]
  except FileNotFoundError:
    print(f"Файл {file_path} не найден!")
    return patterns
  except Exception as e:
    print(f"Ошибка чтения файла: {e}")
    return patterns
  if not clishes:
    print("Файл с клише пуст!")
    return patterns
  for clishe in clishes:
    patterns.append(re.compile(pattern_to_regex(clishe), flags=re.IGNORECASE))
  return patterns

def find_matches(text, regex_patterns):
  """Ищет совпадения в исходном тексте."""
  matches = []
  for regex in regex_patterns:
    for match in regex.finditer(text):
      matches.append({
        'pattern': regex.pattern,
        'text': match.group(),
        'start': match.start(),
        'end': match.end()
      })
  return matches

def get_cliched_matches(text):
  patterns = load_patterns()
  return find_matches(text, patterns)
