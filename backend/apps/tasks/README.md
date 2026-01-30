# Tasks app plan (MVP → расширение)

Ниже план реализации базы заданий и проверки ответов с учетом MVP типов:
- single_choice (radio)
- multi_choice (checkbox)
- number (число с допуском)
- short_text (строка)
- match (сопоставление)

## 1. Архитектура и модель данных

1) Базовые сущности
- Task
  - общие поля: subject, grade, type, prompt, solution_text
  - поля для расширения:
    - type_payload (JSON): структура интерфейса задания
    - answer_key (JSON): правильный ответ
- Test
  - название/описание
- TestItem
  - связь Test → Task + order + points
- Attempt
  - пользователь, тест, статус, started_at/finished_at
- AttemptAnswer
  - attempt, task, answer_payload (JSON), score, is_correct, duration_ms, submitted_at

2) Медиа
- MediaAsset (для картинок/чертежей/графиков)
  - url, mime_type, width, height, size
- В prompt хранить ссылки вида `media:img_123` либо Markdown-изображения

## 2. Форматы type_payload и answer_key (MVP)

1) single_choice
- type_payload: options (id, text, media_id)
- answer_key: { "correct": "A" }

2) multi_choice
- type_payload: options (id, text, media_id)
- answer_key: { "correct": ["A","C"] }

3) number
- type_payload: { "format": "float", "unit": "м/с" }
- answer_key: { "value": 9.8, "tolerance": 0.05, "method": "abs" }

4) short_text
- type_payload: { "max_len": 50 }
- answer_key: { "correct": ["масса"], "case_sensitive": false }

5) match
- type_payload: left[] и right[] (id, text, media_id)
- answer_key: { "pairs": [["L1","R1"],["L2","R2"]] }

## 3. Сервисы проверки (без логики во views)

1) TaskAnswerChecker
- вход: task.type, task.answer_key, user.answer_payload
- выход: is_correct + score

2) Реализация по типам
- single_choice: сравнение id
- multi_choice: сравнение множеств
- number: допуск abs/rel
- short_text: нормализация + совпадение по списку
- match: сравнение пар

## 4. API (минимальный набор)

1) Управление заданиями (админка)
- POST /api/tasks/ (создать)
- GET /api/tasks/<id>/ (просмотр)
- PATCH /api/tasks/<id>/ (редактирование)

2) Прохождение тестов
- POST /api/tests/<id>/start
- GET /api/attempts/<id>/
- GET /api/attempts/<id>/tasks/<task_id>/
- POST /api/attempts/<id>/submit
- POST /api/attempts/<id>/finish

## 5. Рендеринг формул

- Храним Markdown с LaTeX ($...$, $$...$$)
- Web и Telegram Mini Apps: KaTeX
- React Native: WebView (KaTeX) или server-side SVG/PNG

## 6. Этапы реализации

1) Создать app `tasks` и базовые модели
2) Реализовать проверку short_text (первый тип)
3) Добавить API для выдачи/приема ответов
4) Добавить tests/test_items/attempts
5) Подключить media_assets
6) Реализовать остальные типы

## 7. Миграция SQLite → Postgres

- На MVP можно оставаться на SQLite
- Перед запуском в прод — перейти на Postgres
- Использовать JSONB для payload/answer_key
