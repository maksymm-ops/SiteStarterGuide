# Гайд Макса по Site Starter

Русская памятка по codex-nextjs-site-starter: сценарии работы и готовые промпты.

**Открыть гайд:** https://maksymm-ops.github.io/SiteStarterGuide/

## Как обновлять

1. Измени `codex-nextjs-site-starter-guide-ru.md` — это основной текст гайда.
2. Установи зависимости сборщика: `python -m pip install -r requirements.txt`.
3. Выполни `python build-starter-faq.py`. Он обновит `index.html`.
4. Проверь страницу, сохрани изменения коммитом и отправь в ветку `main`.
   GitHub Pages опубликует обновление по прежней ссылке.

Для просмотра готового гайда Python не нужен. Для локальной проверки можно
выполнить `python -m http.server 8767 --bind 127.0.0.1` и открыть
http://127.0.0.1:8767/.

## Файлы

- `index.html` — готовая главная страница со встроенными стилями и шрифтами.
- `codex-nextjs-site-starter-guide-ru.md` — исходный текст.
- `starter-faq-template.html` — оформление и поведение FAQ.
- `build-starter-faq.py` — сборщик страницы из текста и шаблона.
- `assets/feather/` — исходные иконки Feather и их лицензия MIT.

Основа гайда: https://github.com/maisjandesign/codex-nextjs-site-starter.
Это отдельная памятка, а не копия стартового проекта сайта.
