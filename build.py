#!/usr/bin/env python3
"""Собирает языковые версии сайта Max Clean.

Источник: src/page.html (русский текст, переводимые строки в [[...]])
и translations_ka.json / translations_en.json (ключ — русская строка, значение — перевод).
Результат: index.html (ru), ka/index.html, en/index.html и sitemap.xml.

Запуск из папки проекта:  python3 build.py
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = "https://zuko90-sys.github.io/maxclean/"
HERE = Path(__file__).resolve().parent

# порядок важен: первая — основная версия в корне сайта (она же x-default)
LANGS = {
    "ru": {"dir": "", "locale": "ru_RU", "og": "og-image.jpg", "name": "Русский"},
    "ka": {"dir": "ka/", "locale": "ka_GE", "og": "og-image-ka.jpg", "name": "ქართული"},
    "en": {"dir": "en/", "locale": "en_US", "og": "og-image-en.jpg", "name": "English"},
}
MONTSERRAT = "family=Montserrat:ital,wght@0,400;0,500;0,600;0,700;0,800;1,600"
FONTS = {
    "ru": MONTSERRAT,
    "en": MONTSERRAT,
    "ka": MONTSERRAT + "&family=Noto+Sans+Georgian:wght@400;500;600;700;800",
}
UI = {  # подписи переключателя языка
    "ru": "Язык сайта",
    "ka": "საიტის ენა",
    "en": "Site language",
}

MARK = re.compile(r"\[\[(.+?)\]\]")


def load_dict(lang):
    if lang == "ru":
        return None
    return json.loads((HERE / f"translations_{lang}.json").read_text(encoding="utf-8"))


def translate(html, lang, table):
    missing, used = [], set()

    def sub(m):
        key = m.group(1)
        if table is None:
            return key
        if key not in table:
            missing.append(key)
            return key
        used.add(key)
        return table[key]

    out = MARK.sub(sub, html)
    if missing:
        sys.exit(f"[{lang}] нет перевода для {len(set(missing))} строк:\n  " + "\n  ".join(sorted(set(missing))))
    if table is not None:
        for key in sorted(set(table) - used):
            print(f"[{lang}] предупреждение: перевод не используется: {key}")
    return out


def page_url(lang):
    return ROOT + LANGS[lang]["dir"]


def build_page(template, lang):
    conf = LANGS[lang]
    base = "../" if conf["dir"] else ""
    hreflang = "\n".join(
        f'  <link rel="alternate" hreflang="{l}" href="{page_url(l)}">' for l in LANGS
    ) + f'\n  <link rel="alternate" hreflang="x-default" href="{ROOT}">'
    alternates = "\n".join(
        f'  <meta property="og:locale:alternate" content="{c["locale"]}">'
        for l, c in LANGS.items() if l != lang
    )
    links = []
    for l, c in LANGS.items():
        href = (base + c["dir"]) or "./"
        current = ' aria-current="page"' if l == lang else ""
        links.append(f'<a href="{href}" hreflang="{l}" lang="{l}"{current}>{c["name"]}</a>')
    langs = f'    <nav class="langs" aria-label="{UI[lang]}">' + "".join(links) + "</nav>"

    html = template
    for key, value in {
        "hreflang": hreflang,
        "locale_alternates": alternates,
        "langs": langs,
        "lang": lang,
        "base": base,
        "url": page_url(lang),
        "root": ROOT,
        "locale": conf["locale"],
        "og_image": ROOT + conf["og"],
        "fonts": FONTS[lang],
    }.items():
        html = html.replace("{{" + key + "}}", value)
    html = translate(html, lang, load_dict(lang))
    leftover = re.findall(r"\{\{\w+\}\}", html)
    if leftover:
        sys.exit(f"[{lang}] не подставлены: {sorted(set(leftover))}")
    out = HERE / conf["dir"] / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"[{lang}] {out.relative_to(HERE)}")


def build_sitemap():
    today = date.today().isoformat()
    alt = "".join(
        f'<xhtml:link rel="alternate" hreflang="{l}" href="{page_url(l)}"/>' for l in LANGS
    ) + f'<xhtml:link rel="alternate" hreflang="x-default" href="{ROOT}"/>'
    urls = "\n".join(
        f"  <url><loc>{page_url(l)}</loc>{alt}<lastmod>{today}</lastmod></url>" for l in LANGS
    )
    (HERE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        f"{urls}\n</urlset>\n",
        encoding="utf-8",
    )
    print("sitemap.xml")


if __name__ == "__main__":
    template = (HERE / "src" / "page.html").read_text(encoding="utf-8")
    for lang in LANGS:
        build_page(template, lang)
    build_sitemap()
