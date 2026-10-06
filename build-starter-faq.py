"""Build the standalone FAQ from the maintained Markdown guide."""
from pathlib import Path
import hashlib
import html
import re
from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "codex-nextjs-site-starter-guide-ru.md"
OUTPUT = ROOT / "index.html"
md = MarkdownIt("commonmark", {"html": False}).enable("table")

GROUPS = [
    ("start", "Начало работы", "Выбор шаблона, материалы и первый сайт"),
    ("tools", "Claude и Codex", "Что общее, чем отличаются и как подготовить компьютер"),
    ("context", "Контекст и перенос", "Бриф, новый чат, SSD и другой компьютер"),
    ("system", "Дизайн-система", "Концепт, общие элементы и Storybook"),
    ("pages", "Страницы и правки", "Figma, сайт, клиентские правки и мобильная версия"),
    ("review", "Проверка и публикация", "Независимое ревью, аудит и исправления"),
    ("reference", "Правила и справка", "Состав пака, глобальные настройки и источники"),
]
ICON_NAMES = dict(zip([g[0] for g in GROUPS], ['flag', 'terminal', 'folder', 'grid', 'layout', 'check-circle', 'book-open']))
# Feather icons, MIT; original SVGs and license are retained in assets/feather.
ART = {group: (ROOT / 'assets' / 'feather' / (name + '.svg')).read_text(encoding='utf-8') for group, name in ICON_NAMES.items()}

# Old anchors of renamed topics keep working: the page script opens the topic by alias.
ALIASES = {"Как пользоваться стартером сайтов (Claude Code и Codex)": ["Как пользоваться codex-nextjs-site-starter"]}

def title_markup(title):
    match = re.match(r'^(Промпт \d+[а-я]?\.)\s+(.+)$', title)
    if not match:
        return html.escape(title)
    return f'<span class="prompt-number">{html.escape(match[1])} </span><span class="prompt-name">{html.escape(match[2])}</span>'

def group_for(title):
    if title in {"Claude и Codex: что общее и что отличается", "Подготовить компьютер один раз"}:
        return "tools"
    numbered = re.match(r"Промпт (\d+)([а-я]?)\.", title)
    if numbered:
        number, suffix = int(numbered[1]), numbered[2]
        if number == 4 and suffix == "а":
            return "start"
        if 13 <= number <= 18:
            return "context"
        return {1: "start", 2: "context", 3: "context", 4: "context",
                5: "system", 6: "pages", 7: "review", 8: "review",
                9: "review", 10: "review", 11: "reference",
                12: "reference"}.get(number, "start")
    if re.match(r"Промпт 2|Промпт 3|Промпт 4", title) or title in {"Куда попадает информация", "Разобрать бэкап", "Сохранить состояние и продолжить"}:
        return "context"
    if re.match(r"Промпт 5", title) or title in {"Создать или обновить систему", "Создать или обновить Storybook"}:
        return "system"
    if re.match(r"Промпт 6", title):
        return "pages"
    if re.match(r"Промпт (7|8|9|10)\.", title) or title == "Когда запускается независимая проверка":
        return "review"
    if title == "GitHub: рабочие сценарии":
        return "context"
    if title in {"Словарь для дизайнера", "Какие навыки входят в комплект", "Ежедневный короткий порядок", "Что важно помнить", "Глобальные сценарии и независимая проверка", "Что включено", "Что шаблон делает по умолчанию", "Источники"}:
        return "reference"
    return "start"

source = SOURCE.read_text(encoding="utf-8")
chunks = []
current = None
fenced = False
for line in source.splitlines():
    if line.startswith("```"):
        fenced = not fenced
    match = re.match(r"^(#{1,3}) (.+)$", line) if not fenced else None
    if match:
        if current is not None:
            chunks.append(current)
        current = {"title": match[2], "lines": [], "level": len(match[1])}
    elif current is not None:
        current["lines"].append(line)
if current is not None:
    chunks.append(current)

cards = []
prompt_count = 0
for chunk in chunks:
    body = "\n".join(chunk["lines"]).strip()
    if not body:
        continue
    title = chunk["title"]
    display = title
    ident = "topic-" + hashlib.sha256(title.encode()).hexdigest()[:10]
    tokens = md.parse(body)
    fences = [t for t in tokens if t.type == "fence"]
    has_prompt = any(t.info.strip() == "text" for t in fences)
    rendered = md.render(body)
    for token in fences:
        lang = token.info.strip()
        escaped = html.escape(token.content)
        class_attr = f' class="language-{html.escape(lang)}"' if lang else ""
        original = f"<pre><code{class_attr}>{escaped}</code></pre>\n"
        is_prompt = lang == "text"
        prompt_count += int(is_prompt)
        label = "Готовый промпт" if is_prompt else "Команда"
        button = "Копировать промпт" if is_prompt else "Копировать"
        replacement = f'<div class="copy-block {"prompt" if is_prompt else "command"}"><div class="copy-bar"><span>{label}</span><button type="button" class="copy-button" disabled aria-label="{button}: {html.escape(display)}">{button}</button></div><pre><code{class_attr}>{escaped}</code></pre></div>\n'
        if original not in rendered:
            raise ValueError(f"Unmatched fenced block in {title}")
        rendered = rendered.replace(original, replacement, 1)
    cards.append({"id": ident, "title": display, "original": title, "group": group_for(title), "prompt": has_prompt, "rendered": rendered})

nav = []
sections = []
tiles = []
for group_id, label, description in GROUPS:
    group_cards = [c for c in cards if c["group"] == group_id]
    opened = ''
    tiles.append(f'<a class="category-card" href="#group-{group_id}"><h3>{label}</h3><p>{description}</p><span class="category-art" aria-hidden="true">{ART[group_id]}</span></a>')
    nav.append(f'<details class="nav-group"{opened}><summary class="group-link"><span>{label}</span><span class="nav-chevron" aria-hidden="true"></span></summary><div class="topic-links"><a class="topic-link" href="#group-{group_id}">Обзор темы</a>' + "".join(f'<a class="topic-link" href="#{c["id"]}">{title_markup(c["title"])}</a>' for c in group_cards) + '</div></details>')
    articles = []
    for c in group_cards:
        alias = "".join(" " + "topic-" + hashlib.sha256(a.encode()).hexdigest()[:10] for a in ALIASES.get(c["original"], []))
        alias_attr = f' data-alias="{alias.strip()}"' if alias else ""
        articles.append(f'<details class="topic" id="{c["id"]}"{alias_attr} data-group="{group_id}" data-prompt="{str(c["prompt"]).lower()}"><summary><h3 class="topic-title">{title_markup(c["title"])}</h3><span class="chevron" aria-hidden="true"></span></summary><div class="topic-body">{c["rendered"]}</div></details>')
    sections.append(f'<section class="topic-group" id="group-{group_id}"><h2>{label}</h2>' + "".join(articles) + '</section>')

template = (ROOT / "starter-faq-template.html").read_text(encoding="utf-8")

for key, value in {"NAV": "".join(nav), "SECTIONS": "".join(sections), "TILES": "".join(tiles), "CARDS": str(len(cards)), "PROMPTS": str(prompt_count)}.items():
    template = template.replace("@@" + key + "@@", value)
if re.search(r"@@[A-Z]+@@", template):
    raise ValueError("Unfilled template token")
license_text = (ROOT / 'assets' / 'feather' / 'LICENSE').read_text(encoding='utf-8')
template = template.replace('</head>', '<!-- Feather icons: https://github.com/feathericons/feather\n' + license_text + '\n-->\n</head>')
OUTPUT.write_text(template, encoding="utf-8")
print(f"Built {OUTPUT.name}: {len(cards)} topics, {prompt_count} prompts, {len(template.encode('utf-8'))} bytes")
