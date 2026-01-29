# Adaptaki Frontend (React SPA)

## Назначение

Frontend — это **тонкий клиент** платформы Adaptaki.
Он:

-   отображает данные,
-   отправляет действия пользователя,
-   не содержит бизнес-логики обучения.

Основной источник истины — backend API.

---

## Текущий статус (зафиксировано)

На данный момент реализовано:

### ✅ Инфраструктура

-   React + TypeScript
-   Vite (стандартный, без experimental режимов)
-   Axios для работы с API

### ✅ Авторизация

-   JWT хранится в `localStorage`
-   Автоматическое добавление токена к запросам
-   AuthContext:
    -   `login`
    -   `register`
    -   `logout`
    -   `user`

### ✅ Связь с backend

-   Backend: `http://127.0.0.1:8000`
-   API base URL: `/api`
-   CORS настроен на backend стороне

---

## Структура проекта

frontend/spa/
├─ src/
│ ├─ api.ts # Axios-клиент
│ ├─ auth.tsx # AuthContext и логика JWT
│ ├─ App.tsx # Минимальный UI
│ ├─ main.tsx # Точка входа
│ └─ index.html
├─ package.json
└─ vite.config.ts

---

## Важные правила (НЕ НАРУШАТЬ)

-   ❌ Не дублировать бизнес-логику backend
-   ❌ Не хранить состояние обучения на клиенте
-   ✔ Все защищённые запросы идут с JWT
-   ✔ Frontend — replaceable (можно переписать без изменения backend)

---

## Что делать дальше (следующие шаги)

Ближайшие логичные шаги frontend-разработки:

1. Protected routes (закрытые страницы)
2. Улучшение UX авторизации:
    - ошибки
    - загрузка
3. Первый бизнес-сценарий:
    - кнопка действия
    - запрос к backend
4. Адаптация под Telegram Mini App (WebApp)
