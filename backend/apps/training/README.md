# training

Приложение `training` отвечает за тестирование/тренажер:
- хранение заранее подготовленных тестов (цепочек заданий);
- хранение попыток прохождения тестов;
- хранение фактов решения заданий (попыток заданий).

Важно:
- `TaskAttempt` — атомарная сущность: один факт "пользователь отправил ответ на задание".
- `TestAttempt` — контейнер/сессия, объединяющий множество `TaskAttempt` в рамках одного теста.

## Модели

### Test
Заранее подготовленный тест (последовательность заданий).

Поля:
- `title` — название/описание
- `subject` — предмет (FK на `graph.Subject`)
- `mode` — режим (simple/exam)

Пример:
- `Test(title="Тренировка: квадратные уравнения", subject=Математика, mode="simple")`

### TestItem
Элемент теста: конкретное задание + его позиция и максимальный балл в рамках теста.

Зачем:
- задает порядок выдачи заданий;
- позволяет переиспользовать одно `Task` в разных тестах;
- позволяет задавать `max_score` в контексте теста.

Поля:
- `test` — FK на `Test`
- `task` — FK на `tasks.Task`
- `order` — порядок (1..N)
- `max_score` — максимальный балл за это задание в данном тесте

Пример:
- `TestItem(test=Тест, task=Задание#123, order=1, max_score=1)`

### TestAttempt
Попытка прохождения теста (контейнер).

Зачем:
- фиксировать старт/финиш теста, статус и итоговый балл;
- объединять ответы (`TaskAttempt`) в рамках одного прохождения.

Поля:
- `user` — кто проходит
- `test` — какой тест
- `status` — started/finished/abandoned
- `started_at` / `finished_at`
- `total_score` / `max_score` — итоговые значения (снапшот на момент завершения)

Пример:
- ученик начал тест → создается `TestAttempt(status="started")`
- завершил → выставляем `finished_at`, `status="finished"`, считаем totals

### TaskAttempt
Попытка решения задания (атомарный факт решения).

Зачем:
- хранить историю ответов ученика для образовательного графа;
- использовать как внутри тестов, так и в режиме свободной тренировки.

Поля:
- `user`, `task`
- `test_attempt` (nullable) — если решали в рамках теста
- `answer_payload` — JSON с ответом пользователя
- `score`, `is_correct`
- `submitted_at`, `duration_ms`
- `applied_scoring_policy`, `applied_max_score` — снапшот политики (важно для воспроизводимости)

Пример:
- пользователь отправил ответ на `Task` типа short_text:
  - `answer_payload={ "value": "масса" }`
  - проверка записала `score=1`, `is_correct=True`

## Рандомный режим (практика)

Добавлен сценарий случайной выдачи заданий для авторизованного пользователя:

1. Клиент запрашивает случайное задание.
2. Backend возвращает задание и `test_attempt_id` (идентификатор сессии).
3. Клиент отправляет ответ — backend проверяет, сохраняет `TaskAttempt` и возвращает результат.
4. Пользователь может запросить следующий вопрос, продолжая с той же сессией.
5. По нажатию "хватит" клиент завершает сессию.

### API

#### GET /api/training/random-task/
Возвращает случайное задание и id текущей сессии.

Параметры (query):
- `subject_id` (опционально)
- `task_type` (опционально)
- `test_attempt_id` (опционально, если сессия уже есть)

Пример ответа:
```
{
  "id": 123,
  "subject_id": 1,
  "task_type": "short_text",
  "prompt": "...",
  "type_payload": {},
  "test_attempt_id": 555
}
```

#### POST /api/training/submit-answer/
Принимает ответ пользователя, сохраняет попытку, возвращает результат, `solution_text` и `answer_key`.

Пример запроса:
```
{
  "task_id": 123,
  "answer_payload": { "value": "масса" },
  "test_attempt_id": 555,
  "duration_ms": 4200
}
```

Пример ответа:
```
{
  "attempt_id": 999,
  "task_id": 123,
  "is_correct": true,
  "score": "1",
  "max_score": "1",
  "submitted_at": "2026-01-30T12:34:56.789012",
  "solution_text": "...",
  "answer_key": { "correct": ["масса"], "case_sensitive": false }
}
```

#### POST /api/training/random-session/finish/
Завершает сессию (TestAttempt) по запросу клиента.

Пример запроса:
```
{ "test_attempt_id": 555, "status": "finished" }
```

Пример ответа:
```
{ "test_attempt_id": 555, "status": "finished", "finished_at": "..." }
```

#### GET /api/training/test-attempt/summary/
Возвращает сводку по попытке теста (универсально для любого `TestAttempt`).

Параметры (query):
- `test_attempt_id` (обязательно)

Пример ответа:
```
{
  "test_attempt_id": 555,
  "status": "finished",
  "started_at": "2026-01-30T12:00:00Z",
  "finished_at": "2026-01-30T12:10:00Z",
  "total_score": "3",
  "max_score": "5",
  "items": [
    {
      "attempt_id": 999,
      "task_id": 123,
      "task_type": "short_text",
      "prompt": "...",
      "answer_payload": { "value": "масса" },
      "is_correct": true,
      "score": "1",
      "max_score": "1",
      "submitted_at": "2026-01-30T12:05:00Z",
      "solution_text": "..."
    }
  ]
}
```

### Механика завершения

- Сессия создается автоматически при первом `random-task`, если `test_attempt_id` не передан.
- Сессия — это `TestAttempt` со статусом `started` и служебным тестом `Random practice — <Subject>`.
- Завершение — явный вызов `random-session/finish`.
- Если пользователь просто закрывает страницу, сессия остается в `started` (возможный будущий перевод в `abandoned`).
- Если пользователь снова вызывает `random-task` без `test_attempt_id`, последняя незавершенная рандомная сессия автоматически закрывается со статусом `abandoned`.
