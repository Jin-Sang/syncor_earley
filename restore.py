import re


def rm_l(text, token):
    t = text.lstrip()
    cnt = 0
    while t.startswith(token):
        t = t[len(token):].lstrip()
        cnt += 1
    return cnt, t


def rm_r(text, token):
    t = text.rstrip()
    cnt = 0
    while t.endswith(token):
        t = t[:-len(token)].rstrip()
        cnt += 1
    return cnt, t


def strip(text):
    _, t = rm_l(text, "<s>")
    _, t = rm_r(t, "</s>")
    return t


def restore_num(line):
    pattern = re.compile("<NUM_LIT:(?P<value>\d*[.]{0,1}\d*)>")
    res = line
    for m in pattern.finditer(line):
        matched_text = m.group()
        value = m.group('value')
        res = res.replace(matched_text, value)
    if "<NUM_LIT>" in res:
        res = res.replace("<NUM_LIT>", "0")
    return res

def restore_str(line):
    pattern = re.compile("<STR_LIT:(?P<value>\S*)>")
    res = line
    for m in pattern.finditer(line):
        matched_text = m.group()
        value = m.group('value')
        res = res.replace(matched_text, value)
    if "<STR_LIT>" in res:
        res = res.replace("<STR_LIT>", "")
    return res


def restore_indent(lines):

    def strip_indent(line):
        pattern = re.compile("<INDENT:(?P<size>\d+)>")
        m = pattern.match(line)
        if m:
            matched_text = m.group()
            size = int(m.group('size'))
            return size, 0, line.replace(matched_text, "", 1).strip()
        elif "<DEDENT>" in line:
            cnt, line = rm_l(line, "<DEDENT>")
            return 0, cnt, line.strip()
        else:
            return 0, 0, line.strip()

    prev_indent = []
    indented_lines = []
    for l in lines:
        line = l
        indent_size, dedent_cnt, line = strip_indent(line)
        if indent_size > 0:
            prev_indent.append(" " * indent_size)
        elif dedent_cnt > 0:
            cnt = min(dedent_cnt, len(prev_indent))
            for i in range(cnt):
                prev_indent.pop()

        if prev_indent:
            line = prev_indent[-1] + line
        dedent_cnt, line = rm_r(line, "<DEDENT>")
        cnt = min(dedent_cnt, len(prev_indent))
        for i in range(cnt):
            prev_indent.pop()
        indented_lines.append(line)
    return indented_lines


def restore(text):
    lines = []
    for l in strip(text).split("<EOL>"):
        res = l.strip()
        res = restore_num(res)
        res = restore_str(res)
        lines.append(res)
    lines = restore_indent(lines)
    return "\n".join(lines)
