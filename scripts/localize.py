#!/usr/bin/env python3
"""產生繁中技能；程式碼與技術識別名稱保留原樣。"""
import argparse
import json
import re
import shutil
import tempfile
import unicodedata
from pathlib import Path
from urllib.parse import unquote

import yaml
from markdown_it import MarkdownIt
from opencc import OpenCC

MD = MarkdownIt("commonmark")
CC = OpenCC("s2twp")
CODE = re.compile(r"(?<!`)(`+)(?!`)[\s\S]*?(?<!`)\1(?!`)")
TECH = re.compile(
    r"https?://[^\s<>]+|<[^>\n]+>|"
    r"(?<![\w-])[A-Za-z][\w]*(?:[-_./][\w]+)+|"
    r"[\w./-]+\.(?:md|json|js|py|sh|template|png|jpg|svg)\b"
)


def make_converter(config):
    rules = {
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
        return (
            pattern.sub(lambda m: rules[m.group()], text)
            if pattern else text
        )

    return convert


def inline(text, convert, references=(), link=lambda value: value):
    saved = []

    def keep(value):
        saved.append(value)
        return f"\ue000{len(saved) - 1}\ue001"

    text = CODE.sub(lambda m: keep(m.group()), text)

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
    text = TECH.sub(lambda m: keep(m.group()), text)
    text = convert(text)

    for index in reversed(range(len(saved))):
        text = text.replace(
            f"\ue000{index}\ue001",
            saved[index]
        )

    return text


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
            language = token.info.strip().lower()
            opening = re.match(
                r"^ {0,3}(`{3,}|~{3,})",
                lines[start]
            )

            # Markdown 範例可能是直接顯示給使用者的提示。
            if language in {"markdown", "md"} and opening:
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
                    replacements[start] = (
                        end,
                        lines[start]
                        + map_body(content, convert, link)
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


def build(source, output, config):
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
        documents, anchors = {}, {}

        for path in sorted(stage.rglob("*.md")):
            if path.stem.upper() in {
                "LICENSE", "LICENCE", "COPYING", "NOTICE"
            }:
                continue

            old = path.read_bytes().decode("utf-8")
            new, mapping = translate(old, convert)

            if path.name == "SKILL.md":
                before, _ = frontmatter(old)
                after, _ = frontmatter(new)

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

            documents[path] = new
            anchors[path.resolve()] = mapping

        for path, text in documents.items():
            path.write_bytes(
                rewrite_links(
                    text,
                    path.resolve(),
                    anchors
                ).encode("utf-8")
            )

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
        "授權及其他檔案已保留。"
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
