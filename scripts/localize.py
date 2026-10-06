#!/usr/bin/env python3
"""產生 niio 繁中技能，涵蓋 Markdown、JSON 與程式顯示文字，檢查後才發布。"""
import argparse
import hashlib
import json
import os
import re
import shutil
import tempfile
import unicodedata
from pathlib import Path
from urllib.parse import unquote

import yaml
import opencc
from markdown_it import MarkdownIt
from opencc import OpenCC
from tree_sitter import Language, Parser
import tree_sitter_bash
import tree_sitter_javascript
import tree_sitter_python

MD = MarkdownIt("commonmark")
CC = OpenCC("s2twp")
HAN = re.compile(r"[\u3400-\u9fff]")
PARSERS = {
    "javascript": Parser(Language(tree_sitter_javascript.language())),
    "bash": Parser(Language(tree_sitter_bash.language())),
    "python": Parser(Language(tree_sitter_python.language())),
}
AUDIT = {"changedFiles": [], "preservedTechnicalText": [], "issues": []}
CURRENT_FILE = ""

# 排除「台、后、里」等繁簡共用字，以免把正確的台灣文字當成簡體。
character_pairs = [line.split('\t', 1) for line in
                   (Path(opencc.__file__).parent / 'dictionary' / 'STCharacters.txt')
                   .read_text(encoding='utf-8').splitlines() if '\t' in line]
traditional_characters = set(''.join(value.replace(' ', '') for _, value in character_pairs))
SIMPLIFIED_ONLY = {key for key, _ in character_pairs
                   if len(key) == 1 and key not in traditional_characters and CC.convert(key) != key}
CODE = re.compile(r"(?<!`)(`+)(?!`)[\s\S]*?(?<!`)\1(?!`)")
TECH = re.compile(
    r"https?://[^\s<>\"']+|"
    r"</?[A-Za-z][A-Za-z0-9:-]*(?:\s+[A-Za-z_:][A-Za-z0-9_:.-]*\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+))*/?>|"
    r"(?:\./|\.\./)[^\s<>\"'`,，；;|)]+|"
    r"(?<![\w])/[A-Za-z0-9_.-]+(?:/[^\s<>\"'`,，；;|)]+)+|"
    r"(?<![A-Za-z0-9_-])[A-Za-z][A-Za-z0-9_]*(?:[-_./][A-Za-z0-9_]+)+|"
    r"(?<![A-Za-z0-9_-])[A-Za-z0-9_-]+\.(?:md|json|js|py|sh|template|png|jpg|svg)\b"
)
DISPLAY_LABELS = {"hap-cli": "niio CLI"}
PUBLIC_POLICY = (
    "> **對外表達規範**：對使用者的說明、提示與成果摘要，統一使用 niio 品牌及台灣繁體中文。"
    "執行所需的技術名稱、套件、命令、API 參數與路徑請保留；"
    "只在操作或除錯所需的程式碼中呈現，勿將它們用作產品標題或品牌名稱。\n\n"
)


def make_converter(config):
    rules = {
        "hap": "niio CLI",
        "Hap": "niio",
        "hap-cli skills": "niio CLI 技能",
        **DISPLAY_LABELS,
        **config.get("brandReplacements", {}),
        **config.get("termReplacements", {})
    }
    for key, value in list(rules.items()):
        rules.setdefault(CC.convert(key), value)

    patterns = []
    for key in sorted(rules, key=len, reverse=True):
        if not key or not isinstance(rules[key], str):
            raise ValueError("轉換字典必須使用非空字詞及文字值")
        escaped = re.escape(key)
        if key.isascii():
            escaped = (
                r"(?<![A-Za-z0-9_-])"
                + escaped
                + r"(?![A-Za-z0-9_-])"
            )
        patterns.append(escaped)

    pattern = re.compile("|".join(patterns)) if patterns else None

    def convert(text):
        if pattern:
            text = pattern.sub(lambda m: rules[m.group()], text)
        text = CC.convert(text)
        text = (
            pattern.sub(lambda m: rules[m.group()], text)
            if pattern else text
        )
        # 品牌替換完成後才合併重複字詞；不跨行、不修改技術識別字。
        return re.sub(
            r'(?<![A-Za-z0-9_./-])niio(?:[^\S\r\n]+niio)+(?![A-Za-z0-9_./-])',
            'niio', text
        )

    return convert


def inline(text, convert, references=(), link=lambda value: value):
    # 只調整一般說明；完整命令與程式碼區塊仍使用真正的執行檔名稱。
    text = re.sub(r'`hap`(?=\s*命令(?:列|行))', 'niio CLI', text)
    text = re.sub(r'`hap-cli`(?=\s*(?:主\s*[Ss]kill|及其))', '`niio-cli`', text)
    saved = []

    def keep(value):
        saved.append(value)
        return f"\ue000{len(saved) - 1}\ue001"

    text = CODE.sub(lambda m: keep(localized_inline_code(m, convert)), text)

    # 連結目的地可能包含括號；逐字尋找配對，不翻譯路徑。
    chunks, start, pos = [], 0, 0
    while pos < len(text) - 1:
        if text[pos:pos + 2] != "](":
            pos += 1
            continue

        end, depth = pos + 2, 1
        while end < len(text) and depth:
            if text[end] == "\\":
                end += 2
                continue
            depth += (text[end] == "(") - (text[end] == ")")
            end += 1

        if depth:
            pos += 2
            continue

        chunks.append(text[start:pos + 2])
        chunks.append(keep(link(text[pos + 2:end - 1])))
        chunks.append(")")
        start = pos = end

    text = "".join(chunks) + text[start:]

    text = re.sub(
        r"(?<=\])\[[^\]\n]*\]",
        lambda m: keep(m.group()),
        text
    )
    text = re.sub(
        r"\[([^\]\n]+)\]",
        lambda m: (
            keep(m.group())
            if " ".join(m[1].upper().split()) in references
            else m.group()
        ),
        text
    )
    def protect_technical(match):
        value = match.group()
        before = text[match.start() - 1:match.start()]
        after = text[match.end():match.end() + 1]
        if (
            value in DISPLAY_LABELS
            and before not in {"/", "\\"}
            and after not in {"/", "\\", "."}
        ):
            return value
        return keep(value)

    text = TECH.sub(protect_technical, text)
    text = convert(text)

    for index in reversed(range(len(saved))):
        text = text.replace(
            f"\ue000{index}\ue001",
            saved[index]
        )

    return text


def localized_inline_code(match, convert):
    raw, marker = match.group(), match[1]
    content = raw[len(marker):-len(marker)]
    if content == 'hap-cli':
        return 'niio CLI'
    content = re.sub(r'(安[裝装][並并]登[入录]\s*)hap-cli', r'\1niio CLI', content)
    if not HAN.search(content):
        return raw
    try:
        translated = json_text(content, convert, localize_keys=True)
    except json.JSONDecodeError:
        # 行內的中文範例名稱／說明要轉換，ASCII 命令與識別字保持原樣。
        kept = []
        def save(m):
            kept.append(m.group())
            return f"\ue010{len(kept)-1}\ue011"
        translated = TECH.sub(save, content)
        translated = re.sub(r'[A-Za-z_][A-Za-z0-9_-]*', save, translated)
        translated = convert(translated)
        for index in reversed(range(len(kept))):
            translated = translated.replace(f"\ue010{index}\ue011", kept[index])
    return marker + translated + marker


def frontmatter(text):
    match = re.match(
        r"\A---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)",
        text
    )
    if not match:
        return None, text

    data = yaml.safe_load(match[1])
    if not isinstance(data, dict):
        raise ValueError("技能前置資料必須是 YAML 物件")

    return data, text[match.end():]


def is_text_example(content, language):
    if language in {"text", "plaintext"}:
        return True
    if language:
        return False
    beginning = content.lstrip()
    return bool(
        re.match(r"[\u3400-\u9fff]", beginning)
        or re.search(r"[┌┐└┘├┤│─]", content)
    )


def record_issue(kind, text, line=1):
    AUDIT['issues'].append({'file': CURRENT_FILE, 'line': line,
                            'reason': kind, 'text': text[:180]})


def human(text, convert):
    """轉換顯示文字；網址、實際路徑與技術識別字保留。"""
    return inline(text, convert)


def json_text(text, convert, localize_keys=False):
    # 僅替換 JSON 字串值，保留原排版、所有鍵值名稱及資料型別。
    json.loads(text)
    token = re.compile(r'"(?:[^"\\]|\\.)*"')
    def replace(match):
        tail = text[match.end():].lstrip()
        value = json.loads(match.group())
        if tail.startswith(':') and not localize_keys:
            if HAN.search(value) and CC.convert(value) != value:
                AUDIT['preservedTechnicalText'].append({
                    'file': CURRENT_FILE, 'reason': 'JSON key', 'text': value})
            return match.group()
        if not HAN.search(value):
            return match.group()
        translated = human(value, convert)
        return json.dumps(translated, ensure_ascii=False) if translated != value else match.group()
    result = token.sub(replace, text)
    json.loads(result)
    return result


def ancestors(node):
    while node.parent:
        node = node.parent
        yield node


def technical_string(node, language):
    # API 物件鍵、索引、比較常數、正規表示式都屬於程式語意。
    for parent in ancestors(node):
        if parent.type in {'comment', 'string', 'template_string', 'concatenated_string'}:
            continue
        if parent.type in {'pair', 'pair_pattern'}:
            key = parent.child_by_field_name('key')
            if key and key.start_byte <= node.start_byte < key.end_byte:
                return True
        if parent.type in {'subscript', 'subscript_expression'}:
            key = parent.child_by_field_name('index') or parent.child_by_field_name('subscript')
            if key and key.start_byte <= node.start_byte < key.end_byte:
                return True
        if parent.type in {'regex', 'comparison_operator'}:
            return True
        if parent.type == 'binary_expression':
            operator = parent.child_by_field_name('operator')
            if operator and operator.text.decode('utf-8') in {'==','===','!=','!==','<','>','<=','>='}:
                return True
        break
    return False


def code_text(text, language, convert, strict=False):
    aliases = {'js':'javascript', 'jsonc':'javascript', 'typescript':'javascript',
               'ts':'javascript', 'sh':'bash', 'shell':'bash', 'zsh':'bash',
               'py':'python'}
    language = aliases.get(language, language)
    parser = PARSERS.get(language)
    if not parser:
        if HAN.search(text):
            record_issue('尚未支援的程式語言：' + language, text)
        return text
    data = text.encode('utf-8')
    placeholders = [(len(text[:m.start()].encode('utf-8')), len(text[:m.end()].encode('utf-8')))
                    for m in re.finditer(r'<[^>\n]*[\u3400-\u9fff][^>\n]*>', text)]
    root = parser.parse(data).root_node
    if strict and root.has_error:
        record_issue('來源程式無法完整解析，停止自動修改', text)
        return text
    edits = []
    normalized = set()

    def visit(node):
        kind = node.type
        raw = data[node.start_byte:node.end_byte].decode('utf-8')
        comment = kind == 'comment'
        candidate = comment or kind in {'string_fragment', 'string_content', 'raw_string', 'jsx_text', 'heredoc_body'}
        if not strict and kind in {'identifier', 'property_identifier', 'word'}:
            if any(start <= node.start_byte < end for start, end in placeholders):
                candidate = True
            if language == 'javascript' and root.has_error:
                before = data[:node.start_byte].decode('utf-8')
                after = data[node.end_byte:].decode('utf-8')
                opening, closing = before.rfind('>'), after.find('<')
                if opening >= 0 and closing >= 0 and before.rfind('<') < opening:
                    region = before[opening + 1:] + raw + after[:closing]
                    if not any(marker in region for marker in '{}'):
                        candidate = True
        diagnostic = (language == 'bash' and not strict and kind == 'ERROR'
                      and raw.startswith("'\n")
                      and all(not line.strip() or line.lstrip().startswith('#')
                              or not HAN.search(line)
                              for line in raw.splitlines()[1:]))
        if diagnostic:
            candidate = True
        # Bash 沒有加引號的中文顯示參數。
        if language == 'bash' and kind == 'word' and HAN.search(raw):
            parent = node.parent
            if parent and parent.type == 'command' and parent.child_by_field_name('name'):
                command = parent.child_by_field_name('name').text.decode('utf-8')
                candidate = command in {'echo', 'printf'} or not strict
            if not strict and parent and parent.type != 'command_name':
                candidate = True
        if candidate:
            if strict and technical_string(node, language) and not comment:
                if HAN.search(raw):
                    AUDIT['preservedTechnicalText'].append({
                        'file': CURRENT_FILE, 'reason': '程式鍵值／索引／比較常數',
                        'text': raw[:180]})
                return
            if not (HAN.search(raw) or comment):
                return
            # 保留套件工具指示、被註解掉的完整命令。
            prefix = re.sub(r'^(?:#|//|/\*)', '', raw).lstrip()
            if comment and re.match(r'(?:[!@]|(?:hap|pip|pip3|python|python3|npm|node|curl|git)\b)', prefix):
                return
            translated = human(raw, convert)
            if diagnostic:
                translated = ''.join(human(line, convert) if line.lstrip().startswith('#') else line
                                     for line in raw.splitlines(keepends=True))
            # Shell 的單引號 JSON 命令參數也使用相同鍵值保護規則。
            if kind == 'heredoc_body':
                try:
                    translated = json_text(raw, convert, localize_keys=not strict)
                except json.JSONDecodeError:
                    record_issue('無法辨識的 heredoc 中文內容', raw, node.start_point.row + 1)
                    return
            if kind == 'raw_string' and raw[1:-1].lstrip().startswith(('{', '[')):
                try:
                    translated = raw[0] + json_text(raw[1:-1], convert, localize_keys=not strict) + raw[-1]
                except json.JSONDecodeError:
                    if '...' not in raw:
                        record_issue('單引號內的 JSON 不完整', raw, node.start_point.row + 1)
                        return
            if translated != raw:
                edits.append((node.start_byte, node.end_byte, translated.encode('utf-8')))
                normalized.add((node.start_byte, node.end_byte, node.type))
            return
        if not node.children and HAN.search(raw):
            # 機器識別字不翻譯；不明語法必須報錯。
            if kind in {'identifier', 'property_identifier', 'variable_name', 'regex_pattern', 'word'}:
                AUDIT['preservedTechnicalText'].append({
                    'file': CURRENT_FILE, 'reason': kind, 'text': raw[:180]})
            else:
                record_issue('中文出現在無法安全辨識的程式區段：' + kind,
                             raw, node.start_point.row + 1)
        for child in node.children:
            visit(child)
    visit(root)
    for start, end, replacement in reversed(edits):
        data = data[:start] + replacement + data[end:]
    new_root = parser.parse(data).root_node

    # 除明確選取的註解／文字節點外，整棵語法樹必須完全相同。
    old_nodes = []
    def signature(node, original, target):
        if original and (node.start_byte, node.end_byte, node.type) in normalized:
            target.append((node.type, '<localized>'))
            return
        if not original and node.type in {'comment', 'string_fragment', 'string_content', 'raw_string', 'word', 'jsx_text', 'heredoc_body', 'ERROR', 'identifier', 'property_identifier'}:
            old = old_nodes[len(target)] if len(target) < len(old_nodes) else None
            if old == (node.type, '<localized>'):
                target.append(old)
                return
        target.append((node.type, None if node.children else node.text))
        for child in node.children:
            signature(child, original, target)
    signature(root, True, old_nodes)
    new_nodes = []
    signature(new_root, False, new_nodes)
    if old_nodes != new_nodes:
        record_issue('轉換造成程式語法或非文字內容變動', text)
        return text
    if strict and new_root.has_error:
        record_issue('轉換後程式語法錯誤', text)
        return text
    return data.decode('utf-8')


def example_text(text, language, convert):
    if language in {'javascript', 'js'}:
        visible = [line.strip() for line in text.splitlines()
                   if line.strip() and not line.lstrip().startswith(('//', '/*', '*'))]
        if visible and all(re.match(r'(?:[\u3400-\u9fff]|Top\s+\d|\d+[.、]|\.{3})', line)
                           for line in visible):
            return ''.join(human(line, convert) for line in text.splitlines(keepends=True))
    if language == 'json':
        try:
            return json_text(text, convert, localize_keys=True)
        except json.JSONDecodeError:
            return code_text(text, 'jsonc', convert)
    if language in {'javascript','js','jsonc','typescript','ts','bash','sh','shell','zsh','python','py'}:
        return code_text(text, language, convert)
    if language == 'cmd':
        return ''.join(human(line, convert) if line.lstrip().startswith('#') else line
                       for line in text.splitlines(keepends=True))
    if language == 'mermaid':
        return re.sub(r'"[^"\n]*"', lambda m: human(m.group(), convert), text)
    if not language:
        # 無標記的流程、目錄示意仍沿用 Markdown 顯示文字轉換。
        return ''.join(human(line, convert) for line in text.splitlines(keepends=True))
    if HAN.search(text):
        record_issue('尚未支援的範例類型：' + language, text)
    return text


def resource_text(path, text, convert):
    name = path.name.lower()
    if path.suffix == '.json':
        return json_text(text, convert)
    if name.endswith(('.js', '.jsx', '.js.template', '.jsx.template')):
        return code_text(text, 'javascript', convert, strict=True)
    if path.suffix == '.py':
        return code_text(text, 'python', convert, strict=True)
    if path.suffix == '.sh':
        return code_text(text, 'bash', convert, strict=True)
    if HAN.search(text):
        record_issue('新文字檔格式尚未納入轉換', text)
    return text


def write_audit(output, file_count):
    AUDIT['checkedFiles'] = file_count
    AUDIT['changedFiles'] = sorted(set(AUDIT['changedFiles']))
    # 路徑、識別字等例外可查閱，不要求人工逐檔審核。
    for key in ('preservedTechnicalText', 'issues'):
        unique = {json.dumps(item, sort_keys=True, ensure_ascii=False): item for item in AUDIT[key]}
        AUDIT[key] = [unique[key] for key in sorted(unique)]
    directory = output / 'localization'
    directory.mkdir(exist_ok=True)
    (directory / 'localization-report.json').write_text(
        json.dumps(AUDIT, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    message = (f"檢查 {file_count} 個檔案；轉換 {len(AUDIT['changedFiles'])} 個檔案；"
               f"未處理問題 {len(AUDIT['issues'])} 項。")
    print(message)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as stream:
            stream.write(message + '\n')
    for item in AUDIT['issues']:
        print(f"{item['file']}:{item['line']}: {item['reason']}：{item['text']}")
    if AUDIT['issues']:
        raise ValueError('自動檢查未通過，保留上一版 skills，不發布不完整的結果。')


def audit_locale(stage):
    global CURRENT_FILE
    for path in sorted(stage.rglob('*')):
        if not path.is_file() or path.stem.upper() in {'LICENSE','LICENCE','COPYING','NOTICE'}:
            continue
        CURRENT_FILE = 'skills/' + path.relative_to(stage).as_posix()
        try:
            text = path.read_bytes().decode('utf-8')
        except UnicodeDecodeError:
            continue
        technical = [item['text'] for item in AUDIT['preservedTechnicalText']
                     if item['file'] == CURRENT_FILE]
        for number, line in enumerate(text.splitlines(), 1):
            rest = line
            for value in technical:
                rest = rest.replace(value, '')
            # 包含失效的來源錨點在內，連結目的地屬於技術路徑。
            rest = re.sub(r'(?<=\]\()[^)\n]+', '', rest)
            rest = TECH.sub('', rest)
            rest = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m[1], 16)), rest)
            remaining = set(rest) & SIMPLIFIED_ONLY
            if remaining:
                record_issue('殘留簡體字：' + ''.join(sorted(remaining)), line, number)


def map_body(body, convert, link=lambda value: value):
    env = {}
    tokens = MD.parse(body, env)
    lines = body.splitlines(keepends=True)
    protected = set()
    replacements = {}

    for token in tokens:
        if not token.map:
            continue

        start, end = token.map

        if token.type == "fence":
            language = token.info.strip().split(maxsplit=1)
            language = language[0].lower() if language else ""
            opening = re.match(
                r"^ {0,3}(`{3,}|~{3,})",
                lines[start]
            )

            if opening:
                marker = opening[1]
                closing = re.fullmatch(
                    r" {0,3}" + re.escape(marker[0])
                    + "{" + str(len(marker)) + r",}[ \t]*",
                    lines[end - 1].rstrip("\r\n")
                )

                if closing and end > start + 1:
                    content = "".join(
                        lines[start + 1:end - 1]
                    )
                    if language in {"markdown", "md"}:
                        translated = map_body(content, convert, link)
                    elif is_text_example(content, language):
                        translated = "".join(
                            code_text(line, 'bash', convert) if re.match(
                                r"\s*(?:hap|pip|pip3|python|python3|npm|node|curl|git)\b",
                                line
                            ) else inline(line, convert, (), link)
                            for line in content.splitlines(keepends=True)
                        )
                    else:
                        translated = example_text(content, language, convert)
                    replacements[start] = (
                        end,
                        lines[start]
                        + translated
                        + lines[end - 1]
                    )
                    continue

            protected.update(range(start, end))

        elif token.type in {"code_block", "html_block"}:
            protected.update(range(start, end))

    result = []
    index = 0

    while index < len(lines):
        if index in replacements:
            end, replacement = replacements[index]
            result.append(replacement)
            index = end
            continue

        line = lines[index]

        if (
            index in protected
            or re.match(r"^\s{0,3}\[[^\]]+\]:", line)
        ):
            result.append(line)
        else:
            result.append(
                inline(
                    line,
                    convert,
                    env.get("references", {}),
                    link
                )
            )

        index += 1

    return "".join(result)


def headings(body):
    counts, result = {}, []
    tokens = MD.parse(body)

    for index, token in enumerate(tokens):
        if token.type != "heading_open":
            continue

        title = "".join(
            t.content
            for t in tokens[index + 1].children or []
            if t.type in {"text", "code_inline"}
        )
        slug = "".join(
            c for c in title.lower()
            if (
                c in "_-"
                or c.isspace()
                or unicodedata.category(c)[0] in "LNM"
            )
        )
        slug = re.sub(r"\s", "-", slug)

        base, number = slug, counts.get(slug, 0)
        while slug in counts:
            number += 1
            slug = f"{base}-{number}"

        counts[base] = number
        counts[slug] = 0
        result.append(slug)

    return result


def translate(text, convert):
    data, body = frontmatter(text)
    new_body = map_body(body, convert)
    anchors = dict(zip(headings(body), headings(new_body)))

    if data is None:
        return new_body, anchors

    if isinstance(data.get("description"), str):
        data["description"] = inline(
            data["description"],
            convert
        )

    header = yaml.safe_dump(
        data,
        allow_unicode=True,
        sort_keys=False,
        width=1000
    )
    return "---\n" + header + "---\n" + new_body, anchors


def rewrite_links(text, current, anchors):
    def link(value):
        match = re.match(
            r"(<?)([^\s>]+)(>?)([\s\S]*)",
            value
        )
        if not match:
            return value

        url = match[2]
        if (
            "#" not in url
            or re.match(r"[A-Za-z][\w+.-]*:", url)
        ):
            return value

        path, fragment = url.split("#", 1)
        target = (
            (current.parent / unquote(path)).resolve()
            if path else current
        )
        replacement = anchors.get(target, {}).get(
            unquote(fragment)
        )
        if replacement is None:
            return value

        return (
            match[1]
            + path
            + "#"
            + replacement
            + match[3]
            + match[4]
        )

    data, body = frontmatter(text)
    new_body = map_body(body, lambda value: value, link)

    if data is None:
        return new_body

    # 第二遍只更新連結，保留第一遍產生的 YAML。
    return text[:len(text) - len(body)] + new_body


def prepare_names(stage):
    """來源目錄維持原樣；只在待發布副本更名，並同步所有本機引用。"""
    names = {}
    for path in stage.rglob('*'):
        if re.search('hap-', path.name, re.IGNORECASE):
            names[path.name] = re.sub('hap-', 'niio-', path.name, flags=re.IGNORECASE)
    # hap-cli 同時也是實際套件名稱，只能在技能名稱及目錄語境中修改。
    ordinary = {}
    for key, value in names.items():
        if key.casefold() == 'hap-cli':
            continue
        if key.casefold() in ordinary and ordinary[key.casefold()] != value:
            raise ValueError(f'來源名稱只有大小寫不同，無法安全對應：{key}')
        ordinary[key.casefold()] = value
    ordinary['hap_personal_mcp'] = 'niio_personal_mcp'
    ordinary['hap-builder'] = 'niio-builder'
    ordinary['hap-update'] = 'niio-update'
    pattern = re.compile(r'(?<![A-Za-z0-9_-])(?:' + '|'.join(
        re.escape(k) for k in sorted(ordinary, key=len, reverse=True)
    ) + r')(?![A-Za-z0-9_-])', re.IGNORECASE)

    def rewrite(text):
        # 遠端網址不是本機路徑；不可把上游網址改成不存在的網址。
        urls = []
        def keep_url(match):
            value = match.group()
            if value.startswith('https://github.com/apsm-niio/niio-skills/'):
                value = pattern.sub(lambda m: ordinary[m.group().casefold()], value)
                value = value.replace('/hap-cli/', '/niio-cli/')
            urls.append(value)
            return f'\ue020{len(urls)-1}\ue021'
        text = re.sub(r'https?://[^\s<>\"\'`]+', keep_url, text)
        text = pattern.sub(lambda m: ordinary[m.group().casefold()], text)
        text = re.sub(r'(?<![A-Za-z0-9_-])hap-mcp-(?!app-builder)', 'niio-mcp-', text)
        text = re.sub(r'(?m)^(name:\s*)hap-cli\s*$', r'\1niio-cli', text)
        text = re.sub(r'(?<=[/\\])hap-cli(?=[/\\]|[\s`\"\')]|$)', 'niio-cli', text)
        text = re.sub(r'(?<![A-Za-z0-9_-])hap-cli(?=/)', 'niio-cli', text)
        for i, url in enumerate(urls):
            text = text.replace(f'\ue020{i}\ue021', url)
        return text

    paths = sorted(stage.rglob('*'))
    targets = {}
    for path in paths:
        relative = path.relative_to(stage)
        target = Path(*(names.get(part, part) for part in relative.parts))
        if target in targets and targets[target] != relative:
            raise ValueError(f'更名後路徑衝突：{relative}、{targets[target]}')
        targets[target] = relative
    for path in paths:
        if not path.is_file() or path.stem.upper() in {'LICENSE','LICENCE','COPYING','NOTICE'}:
            continue
        try:
            text = path.read_bytes().decode('utf-8')
        except UnicodeDecodeError:
            continue
        new = rewrite(text)
        if new != text:
            path.write_bytes(new.encode('utf-8'))
            renamed = Path(*(names.get(part, part) for part in path.relative_to(stage).parts))
            AUDIT['changedFiles'].append('skills/' + renamed.as_posix())
    renamed_paths = []
    for path in sorted(paths, key=lambda p: len(p.parts), reverse=True):
        if path.name in names:
            old = path.relative_to(stage)
            new = Path(*(names.get(part, part) for part in old.parts))
            path.rename(path.with_name(names[path.name]))
            renamed_paths.append({'from': 'skills/' + old.as_posix(), 'to': 'skills/' + new.as_posix()})
    AUDIT['renamedPaths'] = sorted(renamed_paths, key=lambda item: item['from'])
    AUDIT['connectionNames'] = {'hap_personal_mcp': 'niio_personal_mcp'}
    return pattern


def audit_renamed_references(stage, pattern):
    """發布前攔截已更名項目的舊引用，包含不同大小寫寫法。"""
    global CURRENT_FILE
    for path in sorted(stage.rglob('*')):
        if not path.is_file() or path.stem.upper() in {'LICENSE','LICENCE','COPYING','NOTICE'}:
            continue
        CURRENT_FILE = 'skills/' + path.relative_to(stage).as_posix()
        try:
            text = path.read_bytes().decode('utf-8')
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(text.splitlines(), 1):
            def external_url(match):
                value = match.group()
                return value if value.startswith('https://github.com/apsm-niio/niio-skills/') else ''
            local = re.sub(r'https?://[^\s<>"\x27`]+', external_url, line)
            for match in pattern.finditer(local):
                record_issue('殘留已更名的舊引用：' + match.group(), line, number)


# 客戶可安裝的 skills 必須通過此政策；來源與轉換規則留在維護用目錄。
FORBIDDEN_BRAND = re.compile(
    r'mingdao[a-z]*|nocoly|mingo|明道[雲云]?|high[\s‐‑–-]*performance\s+application\s+platform',
    re.IGNORECASE
)
WRONG_TABLE_WORD = re.compile(r'工作錶|資料錶|子錶|父錶|主錶|流水錶|錶格|錶單|錶示')
DEPLOYMENT_NOTE = (
    '> **部署設定**：範例 API 使用 `https://niiodemo.apsm.com.tw`；其他部署須替換為該環境網址與憑證。API、MCP 與網站網址必須使用本次選定部署環境的已確認設定，'
    '三者可能不同，不得只依 MCP 網址推測 API 或網站位置。'
    '下方 `.example.invalid` 網址只是不可連線的佔位範例，執行前必須替換；'
    '未確認網址時先詢問，不得向佔位網址傳送憑證。'
    '圖片與附件只能使用使用者提供或已授權的素材網址。\n\n'
)


def replace_required(text, old, new, label):
    if text.count(old) != 1:
        raise ValueError(f'上游內容已變更，無法安全套用 {label}；保留上一版技能。')
    return text.replace(old, new, 1)


def configure_refresh_script(text):
    text = replace_required(text, 'from urllib.request import Request, urlopen',
                            'from urllib.request import Request, build_opener, HTTPRedirectHandler\n'
                            'from urllib.parse import urlsplit', 'API 請求匯入')
    old_base = 'API_BASE = "https://api2.mingdao.com"'
    helpers = '''def validate_api_base(value):
    value = value.strip().rstrip('/')
    parsed = urlsplit(value)
    if (parsed.scheme != 'https' or not parsed.hostname or parsed.username
            or parsed.password or parsed.query or parsed.fragment
            or parsed.hostname.endswith('.invalid')
            or parsed.path.rstrip('/').endswith(('/mcp', '/v3'))):
        raise argparse.ArgumentTypeError('請提供已確認的 HTTPS API 基底網址，不含 /mcp、/v3、帳密或查詢參數')
    return value


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise URLError('API 網址發生重新導向；請先確認正確網址，不自動轉送憑證')
'''
    text = replace_required(text, old_base, helpers, 'API 基底網址設定')
    text = replace_required(text, 'def fetch_worksheet_structure(worksheet_id, token, app_id):',
                            'def fetch_worksheet_structure(worksheet_id, token, app_id, api_base):', 'API 函式參數')
    text = replace_required(text, '{API_BASE}/v3/app/worksheets/', '{api_base}/v3/app/worksheets/', 'API URL 組合')
    text = replace_required(text, 'with urlopen(req, timeout=30) as resp:',
                            'with build_opener(NoRedirect()).open(req, timeout=30) as resp:', 'API 重新導向處理')
    text = replace_required(text, '    except HTTPError as e:',
                            '    except (json.JSONDecodeError, UnicodeDecodeError):\n'
                            '        print("  ❌ API 未回傳有效的 JSON", file=sys.stderr)\n'
                            '        return None\n'
                            '    except HTTPError as e:', 'API JSON 檢查')
    text = replace_required(text, '        body = e.read().decode("utf-8", errors="replace")\n'
                            '        print(f"  ❌ HTTP {e.code}: {body[:200]}", file=sys.stderr)',
                            '        print(f"  ❌ HTTP {e.code}，請檢查 API 網址與此環境的授權", file=sys.stderr)', 'API 錯誤輸出')
    text = replace_required(text, '    args = parser.parse_args()',
                            '    parser.add_argument("--api-base", default="https://niiodemo.apsm.com.tw", type=validate_api_base,\n'
                            '                        help="此部署環境已確認的 HTTPS API 基底網址")\n'
                            '    args = parser.parse_args()', 'API 必填參數')
    text = replace_required(text, 'fetch_worksheet_structure(ws_id, args.token, app_id)',
                            'fetch_worksheet_structure(ws_id, args.token, app_id, args.api_base)', 'API 呼叫參數')
    text = replace_required(text, '        fields = extract_fields(raw)',
                            '        fields = extract_fields(raw)\n'
                            '        if (not isinstance(raw, dict) or raw.get("success") is False\n'
                            '                or not isinstance(fields, list) or not fields\n'
                            '                or not all(isinstance(field, dict) for field in fields)):\n'
                            '            errors.append(ws_name)\n'
                            '            print(" ❌ 未取得有效欄位結構", file=sys.stderr)\n'
                            '            continue', '工作表回應檢查')
    text = replace_required(text, '    # 寫入輸出',
                            '    if errors:\n'
                            '        print("❌ 部分工作表讀取失敗，保留既有 worksheetContext.json", file=sys.stderr)\n'
                            '        sys.exit(1)\n\n'
                            '    # 寫入輸出', '避免不完整輸出')
    text = text.replace('python3 refresh_fields.py --token',
                        'python3 refresh_fields.py --api-base "https://niiodemo.apsm.com.tw" --token')
    compile(text, 'refresh_fields.py', 'exec')
    return text


def apply_customer_policy(stage, output):
    base = stage / 'mcp/niio-mcp-app-builder'
    refresh = base / 'build/scripts/refresh_fields.py'
    if not refresh.is_file():
        raise ValueError('來源缺少欄位更新腳本，請檢查上游結構變動。')
    policy_changed = []
    for path in sorted(stage.rglob('*')):
        if not path.is_file() or path.stem.upper() in {'LICENSE','LICENCE','COPYING','NOTICE'}:
            continue
        try:
            old = path.read_bytes().decode('utf-8')
        except UnicodeDecodeError:
            continue
        text = old
        relative = path.relative_to(stage).as_posix()
        if path == refresh:
            text = configure_refresh_script(text)
        elif relative.endswith('/assets/config.js.template'):
            text = replace_required(text, "API_BASE_URL: 'https://api.mingdao.com',",
                                    "API_BASE_URL: 'https://niiodemo.apsm.com.tw', // 其他部署請改為該環境的 API 基底網址，不含 /v3", '網站 API 設定')
        elif relative.endswith('/assets/api.js.template'):
            text = replace_required(text, '        const url = `${CONFIG.API_BASE_URL}${endpoint}`;',
                                    '''        const base = CONFIG.API_BASE_URL;
        if (!base) throw new Error('請先設定此部署環境的 API_BASE_URL');
        const parsedBase = new URL(base);
        if (parsedBase.protocol !== 'https:' || parsedBase.username || parsedBase.password ||
            parsedBase.search || parsedBase.hash || parsedBase.hostname.endsWith('.invalid') ||
            /\\/(mcp|v3)\\/?$/.test(parsedBase.pathname)) {
            throw new Error('API_BASE_URL 必須是已確認的 HTTPS API 基底網址');
        }
        const url = `${base.replace(/\\/$/, '')}${endpoint}`;''', '網站 API 防呆')
            text = replace_required(text, '                ...options,',
                                    "                ...options,\n                redirect: 'error',", '網站 API 重新導向')
        elif relative.endswith('/build/steps/3_refresh_fields.md'):
            text = '''# Step 3：重新整理欄位結構

先確認本次使用的部署環境，再取得其 API 基底網址、應用 ID、工作表 ID 與認證資訊。
API、MCP 與網站網址可能不同；不得由 MCP 網址自行推測，也不得跨環境共用 Token。

1. 從使用者選定的 MCP 連線讀取 `headers.Authorization`；若實際設定使用 URL 的 `Authorization` 參數，解碼後取值。保留完整認證字串，不假設固定前綴，不顯示 Token。
2. niio demo 的 API 基底網址預設為 `https://niiodemo.apsm.com.tw`。其他部署必須以 `--api-base` 指定該環境網址；不得將其他環境的憑證傳往 demo。網址必須包含 HTTPS，不能包含 `/mcp`、`/v3` 或驗證參數。
3. 執行下列腳本，將變數替換為此環境已確認的設定。範例變數必須先設定，不能直接照抄執行。

```bash
python3 {SKILL_DIR}/build/scripts/refresh_fields.py \\
  --api-base "$NIIO_API_BASE" \\
  --token "$NIIO_AUTHORIZATION" \\
  {PROJECT_ROOT}/apps/{appName}/hap-context.json
```

腳本從 `hap-context.json` 讀取 `appId`、`worksheetIdByName`，以 GET 取得欄位結構並寫入 `worksheetContext.json`。
若網址、授權、回傳格式或任何工作表的欄位檢查失敗，停止本步驟並保留既有輸出，不得改用其他服務重試。

驗證：本次腳本成功結束；輸出的工作表數量等於已建立工作表數，每表的 `fields` 非空。
不寫 `progress`，由排程器統一管理。
'''
        elif relative.endswith('/build/steps/1_create_app.md'):
            start = text.find('根據目前使用的 MCP 服務地址，確定前端網域：')
            end = text.find('拼接應用連結', start)
            if start < 0 or end < 0:
                raise ValueError('上游應用連結章節已變更，停止套用部署規則。')
            text = text[:start] + ('使用本次環境已確認的 niio 網站根網址 `NIIO_WEB_BASE_URL`。'
                '此網址可以與 MCP 或 API 不同；若未提供，先詢問使用者，不自行推測。'
                '保留已確認的協定、連接埠與部署路徑；移除尾端斜線後接上 `/app/{appId}`。\n\n') + text[end:]
            text = text.replace('https://{前端域名}', '{NIIO_WEB_BASE_URL}')
        elif relative.endswith('/build/resources/sample_images.json'):
            catalog = json.loads(text)
            manifest_path = output / 'localization/image-catalog.json'
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            if manifest.get('version') != 1:
                raise ValueError('圖片對照表版本不支援。')
            lookup = {item['sourceUrlSha256']: item for item in manifest['images']}
            if len(lookup) != len(manifest['images']):
                raise ValueError('圖片對照表有重複來源。')
            count = 0
            repository = os.environ.get('GITHUB_REPOSITORY', 'apsm-niio/niio-skills')
            for category, entries in catalog.items():
                if not isinstance(entries, list):
                    raise ValueError('圖片目錄結構已變更，請檢查素材政策。')
                for entry in entries:
                    source_key = hashlib.sha256(entry['url'].encode('utf-8')).hexdigest()
                    asset = lookup.get(source_key)
                    if not asset or asset.get('reviewed') is not True:
                        raise ValueError(f'新圖片尚未審查：{category}/{entry.get("keyword", "")}，來源識別 {source_key}；保留上一版技能。')
                    filename = asset['file']
                    if not re.fullmatch(r'[a-z0-9-]+\.jpg', filename):
                        raise ValueError('圖片檔名格式錯誤。')
                    image_path = output / 'assets/sample-images' / filename
                    if image_path.is_symlink() or not image_path.is_file():
                        raise ValueError(f'圖片檔案不存在或不安全：{filename}')
                    if hashlib.sha256(image_path.read_bytes()).hexdigest() != asset['sha256']:
                        raise ValueError(f'圖片內容變更，需重新審查：{filename}')
                    entry['url'] = f'https://raw.githubusercontent.com/{repository}/main/assets/sample-images/{filename}'
                    count += 1
            AUDIT['mirroredSampleImages'] = count
            text = json.dumps(catalog, ensure_ascii=False, indent=2) + '\n'
        elif relative.endswith('/build/steps/6_create_sample_data.md'):
            heading = '## 4. 系統內建預設附件清單 (Attachment)'
            if text.count(heading) != 1:
                raise ValueError('上游範例素材章節已變更，停止套用素材政策。')
            start = text.index(heading)
            following = re.search(r'^## ', text[start + len(heading):], re.MULTILINE)
            end = start + len(heading) + following.start() if following else len(text)
            text = text[:start] + '''## 4. 圖片與附件素材 (Attachment)

只使用使用者提供、部署環境管理或已確認授權的素材網址。不得自行猜測下載網址。
優先讀取 `build/resources/sample_images.json`，使用其中本儲存庫已審查的圖片直接網址，按關鍵字挑選符合情境的素材。分類清單可能為空，不能對空清單隨機取值。
沒有合適素材時，非必填附件欄位可留空；必填欄位須先向使用者取得素材再繼續該筆資料。
不得為了填滿欄位而下載未知來源的圖片或使用範例佔位網址。
使用平台支援的附件結構 `[{"name": "檔名", "url": "使用者提供的實際素材網址"}]`。

''' + text[end:]
            text = text.replace('從內建預設附件清單中挑選契合場景的資源。', '使用已確認授權的素材；沒有素材時依下方附件規則處理。')
        elif relative == 'api/niio-apiv3-data/SKILL.md':
            old_selection = '''const hapMcpConfig = Object.entries(mcpServers).find(
  ([name, config]) => config.url && /api2?\\.mingdao\\.com\\/mcp/.test(config.url)
);'''
            new_selection = '''// selectedMcpName 必須由使用者選定，不能靠品牌網域猜測或任取第一筆。
const selectedMcpName = process.env.NIIO_MCP_SERVER_NAME;
if (!selectedMcpName || !mcpServers[selectedMcpName]?.url) {
  throw new Error('請先指定本次要使用的 MCP 連線名稱');
}
const hapMcpConfig = [selectedMcpName, mcpServers[selectedMcpName]];'''
            text = replace_required(text, old_selection, new_selection, 'MCP 連線選擇')
            text = re.sub(r'^.*(?:url|`url`) 指向 .*mingdao.*$',
                          lambda m: ('// 依使用者指定的連線名稱取得 MCP 設定'
                                     if m.group().lstrip().startswith('//') else
                                     '   - 使用已確認的 MCP 連線名稱與網址，不依品牌網域判斷。'), text, flags=re.MULTILINE)
            text = text.replace('連線名称', '連線名稱')
            text = text.replace('  console.log(auth);', "  console.log('已取得所選環境的認證設定'); // 不輸出憑證")

        if relative.endswith('/version.json'):
            metadata = json.loads(text)
            metadata['repository'] = 'https://github.com/' + os.environ.get('GITHUB_REPOSITORY', 'apsm-niio/niio-skills')
            metadata['branch'] = 'main'
            text = json.dumps(metadata, ensure_ascii=False, indent=2) + '\n'

        # 文件中的外部說明連結改成純文字；API/網站/素材範例使用明確的不可連線佔位網址。
        if path.suffix == '.md':
            had_brand = bool(FORBIDDEN_BRAND.search(text))
            text = re.sub(r'\[([^\]\n]+)\]\((https?://[^)\s]*(?:mingdao|nocoly|mingo)[^)\s]*)\)',
                          lambda m: m[1] + '（請參閱此技能隨附文件或部署管理者提供的說明）', text, flags=re.IGNORECASE)
            text = re.sub(r'https?://(?:apifox|developers|help|bbs)\.mingdao\.com[^\s<>"\x27`)\]}]*',
                          '（請參閱部署管理者提供的說明文件）', text, flags=re.IGNORECASE)
            text = re.sub(r'(?<![A-Za-z0-9_.-])(?:api2?\.mingdao\.com)', 'niiodemo.apsm.com.tw', text, flags=re.IGNORECASE)
            text = re.sub(r'(?<![A-Za-z0-9_.-])(?:p1|d1)\.mingdaoyun\.cn', 'niio-assets.example.invalid', text, flags=re.IGNORECASE)
            text = re.sub(r'(?<![A-Za-z0-9_.-])(?:www|xxx)\.mingdao\.com', 'niio-web.example.invalid', text, flags=re.IGNORECASE)
            text = re.sub(r'(?<![A-Za-z0-9_.-])avatars\.mingdao\.com', 'niio-assets.example.invalid', text, flags=re.IGNORECASE)
            text = re.sub(r'\s*[（(]High-performance Application Platform[）)]', '', text, flags=re.IGNORECASE)
            if had_brand:
                data, body = frontmatter(text)
                header = text[:len(text)-len(body)] if data is not None else ''
                text = header + DEPLOYMENT_NOTE + body

        if text != old:
            path.write_bytes(text.encode('utf-8'))
            policy_changed.append('skills/' + relative)
    AUDIT['deploymentPolicyChangedFiles'] = policy_changed
    AUDIT['changedFiles'].extend(policy_changed)


def audit_customer_policy(stage):
    global CURRENT_FILE
    for path in sorted(stage.rglob('*')):
        CURRENT_FILE = 'skills/' + path.relative_to(stage).as_posix()
        if FORBIDDEN_BRAND.search(CURRENT_FILE):
            record_issue('檔名含禁用品牌字詞', CURRENT_FILE)
        if not path.is_file() or path.stem.upper() in {'LICENSE','LICENCE','COPYING','NOTICE'}:
            continue
        try:
            text = path.read_bytes().decode('utf-8')
        except UnicodeDecodeError:
            record_issue('新增非文字資源需確認品牌內容', CURRENT_FILE)
            continue
        for number, line in enumerate(text.splitlines(), 1):
            decoded = unquote(line)
            decoded = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m[1], 16)), decoded)
            if FORBIDDEN_BRAND.search(decoded):
                record_issue('殘留禁用品牌字詞', line, number)
            if WRONG_TABLE_WORD.search(decoded):
                record_issue('殘留資料表用語誤譯', line, number)


def build(source, output, config):
    global CURRENT_FILE
    for key in AUDIT:
        if isinstance(AUDIT[key], list):
            AUDIT[key].clear()
    source, output = source.resolve(), output.resolve()

    if source == output or not (source / "skills").is_dir():
        raise ValueError(
            "來源必須是另一個包含 skills 資料夾的目錄"
        )

    if (
        (output / "skills").is_relative_to(source)
        or source.is_relative_to(output / "skills")
    ):
        raise ValueError(
            "來源與輸出的 skills 目錄不可互相包含"
        )

    if not (source / "LICENSE").is_file():
        raise ValueError("來源缺少 LICENSE，停止轉換")

    if any(path.is_symlink() for path in source.rglob("*")):
        raise ValueError(
            "來源含符號連結，需先確認後才能轉換"
        )

    destination = output / "skills"
    license_target = output / "THIRD_PARTY_LICENSE.txt"

    if destination.is_symlink() or license_target.is_symlink():
        raise ValueError("輸出位置含符號連結，停止轉換")

    if destination.exists() and not destination.is_dir():
        raise ValueError("輸出的 skills 必須是資料夾")

    convert = make_converter(config)
    output.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(
        prefix=".niio-localize-",
        dir=output
    ) as tmp:
        stage = Path(tmp) / "skills"
        shutil.copytree(source / "skills", stage)
        renamed_pattern = prepare_names(stage)
        documents, anchors = {}, {}

        for path in sorted(stage.rglob("*.md")):
            CURRENT_FILE = "skills/" + path.relative_to(stage).as_posix()
            if path.stem.upper() in {
                "LICENSE", "LICENCE", "COPYING", "NOTICE"
            }:
                continue

            old = path.read_bytes().decode("utf-8")
            new, mapping = translate(old, convert)

            if path.name == "SKILL.md":
                before, _ = frontmatter(old)
                after, new_body = frontmatter(new)

                if (
                    not before
                    or not before.get("name")
                    or not before.get("description")
                ):
                    raise ValueError(
                        f"技能缺少 name 或 description：{path.name}"
                    )

                if after != {
                    **before,
                    "description": after["description"]
                }:
                    raise ValueError(
                        "轉換修改了技能識別資料，停止發布"
                    )

                prefix = new[:len(new) - len(new_body)]
                new = prefix + PUBLIC_POLICY + new_body
                if after['name'] == 'niio-cli':
                    note = ('> **執行相容性**：niio CLI 目前使用 `hap` 執行命令、'
                            '`pip install hap-cli` 安裝套件及 `python -m hap_cli` 呼叫模組；'
                            '下方可執行範例保留這些必要名稱。\n\n')
                    new = prefix + PUBLIC_POLICY + note + new_body

            documents[path] = new
            anchors[path.resolve()] = mapping

        for path, text in documents.items():
            CURRENT_FILE = "skills/" + path.relative_to(stage).as_posix()
            final = rewrite_links(
                    text,
                    path.resolve(),
                    anchors
            )
            if final != path.read_text(encoding="utf-8"):
                AUDIT['changedFiles'].append(CURRENT_FILE)
            path.write_bytes(final.encode("utf-8"))

        for path in sorted(stage.rglob("*")):
            if not path.is_file() or path in documents:
                continue
            CURRENT_FILE = "skills/" + path.relative_to(stage).as_posix()
            if path.stem.upper() in {"LICENSE", "LICENCE", "COPYING", "NOTICE"}:
                continue
            try:
                old = path.read_bytes().decode("utf-8")
            except UnicodeDecodeError:
                continue
            new = resource_text(path, old, convert)
            if new != old:
                AUDIT['changedFiles'].append(CURRENT_FILE)
                path.write_bytes(new.encode("utf-8"))

        apply_customer_policy(stage, output)
        audit_customer_policy(stage)
        audit_locale(stage)
        audit_renamed_references(stage, renamed_pattern)
        write_audit(output, sum(path.is_file() for path in stage.rglob("*")))

        license_stage = Path(tmp) / "THIRD_PARTY_LICENSE.txt"
        shutil.copy2(source / "LICENSE", license_stage)
        backup = Path(tmp) / "previous-skills"

        if destination.exists():
            destination.rename(backup)

        try:
            stage.rename(destination)
            license_stage.replace(license_target)
        except Exception:
            if destination.exists():
                shutil.rmtree(destination)
            if backup.exists():
                backup.rename(destination)
            raise

    print(
        f"完成：{len(documents)} 份 Markdown 文件；"
        "JSON 資源、程式顯示文字與註解已一併處理。"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        required=True,
        type=Path
    )
    parser.add_argument(
        "--output",
        default=Path("."),
        type=Path
    )
    parser.add_argument(
        "--terms",
        default=Path("localization/terms.json"),
        type=Path
    )
    args = parser.parse_args()

    config = json.loads(
        args.terms.read_text(encoding="utf-8")
    )
    if config.get("locale") != "zh-TW":
        raise ValueError("目前僅支援 zh-TW")

    build(args.source, args.output, config)


if __name__ == "__main__":
    main()

