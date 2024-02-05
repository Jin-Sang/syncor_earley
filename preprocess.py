import re
from tokenize import TokenError
from tokenize import tokenize, untokenize, COMMENT, STRING, NEWLINE, ENCODING, ENDMARKER, NL, INDENT, DEDENT, NUMBER
from io import BytesIO

NUM_LITERALS = [
    '0', '0.0', '0.', '0.1', '0.5', '1', '1.0', '1.', '2', '3', '4', '5', '6', '7', '8', '9', '10',
    '11', '12', '15', '16', '20', '30', '32', '50', '64', '100', '200', '255', '1000'
]

def process_string(token, special_chars={" ": "U+0020", ",": "U+002C"}):
    str_quote_options = ["'''", '"""', "'", '"']
    start_quote = ""
    end_quote = ""
    qualifier_regex = r"^[a-zA-Z]+"
    qualifier_match = re.search(qualifier_regex, token)
    qualifier = "" if not qualifier_match else qualifier_match[0]
    token_string = re.sub(qualifier_regex, "", token)
    str_lit = token_string
    for q in str_quote_options:
        if token_string.startswith(q):
            start_quote = q
            str_lit = str_lit[len(q):]
            if token_string.endswith(q):
                end_quote = q
                str_lit = str_lit[:-len(q)]
            break
    for sc in special_chars:
        str_lit = str_lit.replace(sc, special_chars[sc])
    return f"{qualifier}{start_quote}<STR_LIT>{end_quote}"


def preprocess(code):
    if not code.strip():
        return None
    token_gen = tokenize(BytesIO(bytes(code, "utf8")).readline)
    out_tokens = []
    prev_eol = False
    try:
        for toknum, tokval_raw, _, _, _ in token_gen:
            tokval = " ".join(tokval_raw.split())
            if toknum == STRING:
                add_token = process_string(tokval)
                out_tokens.append(add_token)
                prev_eol = False
            elif toknum == NUMBER:
                if tokval in NUM_LITERALS:
                    out_tokens.append(f"<NUM_LIT:{tokval}>")
                else:
                    out_tokens.append(f"<NUM_LIT>")
                prev_eol = False
            elif toknum in [NEWLINE, NL]:
                if not prev_eol:
                    out_tokens.append("<EOL>")
                    prev_eol = True
            elif toknum == INDENT:
                indent = tokval_raw.replace("\t", " " * 4)
                out_tokens.append(f"<INDENT:{len(indent)}>")
                prev_eol = False
            elif toknum == DEDENT:
                out_tokens.append("<DEDENT>")
                prev_eol = False
            elif toknum in [COMMENT, ENCODING, ENDMARKER] or len(tokval) == 0:
                continue
            else:
                out_tokens.append(tokval)
                prev_eol = False
    except TokenError:
        pass
    except Exception:
        out_tokens = []

    if len(out_tokens) > 0 and out_tokens[0] == "<EOL>":
        out_tokens = out_tokens[1:]
    if len(out_tokens) > 0 and out_tokens[-1] == "<EOL>":
        out_tokens = out_tokens[:-1]
    out_tokens = ["<s>"] + out_tokens + ["</s>"]
    return " ".join(out_tokens)
