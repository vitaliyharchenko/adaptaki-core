# tasks

Приложение `tasks` — банк заданий.

Цели:
- хранить контент заданий (условие, решение, правильный ответ);
- поддерживать разные типы заданий через `task_type` + JSON-поля `type_payload`/`answer_key`;
- связывать задания с образовательным графом (`graph.Node`), чтобы результаты решения влияли на метрики;
- (опционально) привязывать задания к экзаменационному рубрикатору (`exams.ExamTaskType`) для экзамен-режима.

Архитектура:
- `domain/` — смыслы/enum'ы типов заданий (без Django)
- `application/` — use cases проверки/прохождения (позже)
- `infrastructure/` — Django ORM модели (без бизнес-логики)

## Модели

### Task
Задание (контент).

Зачем:
- единая сущность, которую можно переиспользовать в разных тестах (`training.Test`);
- один и тот же `Task` может решаться учеником много раз (это хранится в `training.TaskAttempt`).

Ключевые поля:
- `subject` — предмет (`graph.Subject`)
- `task_type` — тип задания (enum в `tasks.domain.enums.TaskType`)
- `prompt` — условие (Markdown + LaTeX)
- `solution_text` — решение (Markdown + LaTeX)
- `type_payload` — JSON для интерфейса (например, список вариантов)
- `answer_key` — JSON с правильным ответом (для автопроверки)
- `exam_task_type` (nullable) — привязка к рубрикатору экзамена

Пример (short_text):
- `task_type="short_text"`
- `type_payload={ "max_len": 50 }`
- `answer_key={ "correct": ["масса"], "case_sensitive": false }`

### TaskNode
Прослойка (through) для связи `Task` ↔ `graph.Node`.

Зачем:
- иметь явную таблицу связей (проще расширять: например, добавить вес связи или комментарий методиста);
- контролировать уникальность пары (task, node).

Пример:
- `TaskNode(task=Задание#1, node=Теорема Виета)`

## MVP-типы заданий (план)

Для MVP (первые реализации проверки):
- `short_text` — строка
- `number` — число (с допуском)
- `single_choice` — один вариант
- `multi_choice` — несколько вариантов
- `match` — сопоставление

## Проверка ответов (application/answer_check.py)

В `apps.tasks.application.answer_check` реализована базовая проверка ответов:
- все типы проверяются по схеме "правильно/неправильно" (binary);
- `answer_key.max_score` задает максимальный балл (по умолчанию 1);
- допустимы разные форматы `answer_payload` (например, `"value"` или `"values"`).

Примеры `answer_key`:
- short_text:
  - `{ "correct": ["масса"], "case_sensitive": false }`
- number:
  - `{ "correct": [3.14], "tolerance": 0.01 }`
- single_choice:
  - `{ "correct": "B" }`
- multi_choice:
  - `{ "correct": ["A", "C"] }`
- match:
  - `{ "correct": {"1": "A", "2": "B"} }`

## API

### GET /api/tasks/task-types/
Возвращает список типов заданий с человеко-понятными названиями.

Пример ответа:
```
{
  "task_types": [
    { "value": "short_text", "label": "Короткий ответ" },
    { "value": "number", "label": "Число" }
  ]
}
```

## Про формулы и картинки

- Формулы: храним LaTeX внутри Markdown (`$...$`, `$$...$$`), рендер на клиентах (KaTeX/MathJax).
- Картинки: хранить как отдельные media-assets (будущий app), в `prompt`/`type_payload` хранить ссылки/идентификаторы.
