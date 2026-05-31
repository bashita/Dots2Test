BRAILLE_MAP = {
    (1,):                    'a',
    (1, 2):                  'b',
    (1, 4):                  'c',
    (1, 4, 5):               'd',
    (1, 5):                  'e',
    (1, 2, 4):               'f',
    (1, 2, 4, 5):            'g',
    (1, 2, 5):               'h',
    (2, 4):                  'i',
    (2, 4, 5):               'j',
    (1, 3):                  'k',
    (1, 2, 3):               'l',
    (1, 3, 4):               'm',
    (1, 3, 4, 5):            'n',
    (1, 3, 5):               'o',
    (1, 2, 3, 4):            'p',
    (1, 2, 3, 4, 5):         'q',
    (1, 2, 3, 5):            'r',
    (2, 3, 4):               's',
    (2, 3, 4, 5):            't',
    (1, 3, 6):               'u',
    (1, 2, 3, 6):            'v',
    (2, 4, 5, 6):            'w',
    (1, 3, 4, 6):            'x',
    (1, 3, 4, 5, 6):         'y',
    (1, 3, 5, 6):            'z',
    (3, 4, 5, 6):            '#',
    (2,):                    ',',
    (2, 3):                  ';',
    (2, 5):                  ':',
    (2, 5, 6):               '.',
    (2, 3, 5, 6):            '!',
    (2, 3, 6):               '"',
    (2, 3, 5):               '?',
    (3, 6):                  '-',
    (6,):                    'capital_indicator',
    ():                      ' ',
}

NUMBER_MAP = {
    'a': '1', 'b': '2', 'c': '3', 'd': '4', 'e': '5',
    'f': '6', 'g': '7', 'h': '8', 'i': '9', 'j': '0',
}

def pattern_to_char(dot_tuple, number_mode=False, capital_mode=False):
    key = tuple(sorted(dot_tuple))
    char = BRAILLE_MAP.get(key, '?')
    if char == '#':
        return '#', True, False
    if char == 'capital_indicator':
        return '', False, True
    if number_mode and char in NUMBER_MAP:
        return NUMBER_MAP[char], True, False
    if capital_mode and char.isalpha():
        return char.upper(), False, False
    return char, False, False

def decode_braille_sequence(dot_patterns):
    result = []
    number_mode = False
    capital_mode = False
    for pattern in dot_patterns:
        char, number_mode, capital_mode = pattern_to_char(pattern, number_mode, capital_mode)
        if char and char != '#':
            result.append(char)
    return ''.join(result)