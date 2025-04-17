import pymorphy3
morph = pymorphy3.MorphAnalyzer()


def generate_phrase_cases(phrase):
  words = phrase.split()
  # Список всех падежей
  cases = ['nomn', 'gent', 'datv', 'accs', 'ablt', 'loct']
  result = {}
  # Генерация форм для каждого падежа
  for case in cases:
    case_forms = []
    for word in words:
      parsed = morph.parse(word)[0]
      # Пытаемся просклонять слово
      form = parsed.inflect({case})
      case_forms.append(form.word if form else word)
    result[case] = ' '.join(case_forms)
  # Множественное число в именительном падеже
  plural_forms = []
  for word in words:
    parsed = morph.parse(word)[0]
    form = parsed.inflect({'plur', 'nomn'}) or parsed.inflect({'plur'})
    plural_forms.append(form.word if form else word)
  result['plural_nomn'] = ' '.join(plural_forms)
  return result
