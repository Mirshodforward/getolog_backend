# Getolog Admin Backend API

Backend API сервер для веб-админ-панели менеджера системы Getolog.

## Технологии

- **Node.js** - JavaScript runtime
- **Express.js** - Web framework
- **PostgreSQL** - База данных (используется существующая БД)
- **ExcelJS** - Экспорт данных в Excel
- **Helmet** - Security middleware
- **CORS** - Cross-origin resource sharing

## Структура проекта

```
backend/
├── config/
│   └── database.js         # Конфигурация PostgreSQL
├── middleware/
│   └── auth.js             # Middleware для аутентификации
├── routes/
│   ├── stats.js            # Маршруты статистики
│   ├── clients.js          # Управление клиентами
│   ├── bots.js             # Управление ботами
│   ├── users.js            # Управление пользователями
│   ├── transactions.js     # Управление транзакциями
│   └── export.js           # Экспорт в Excel
├── .env                    # Переменные окружения
├── server.js               # Главный файл сервера
└── package.json            # Зависимости проекта
```

## Установка

1. Перейдите в папку backend:
```bash
cd backend
```

2. Установите зависимости:
```bash
npm install
```

3. Убедитесь, что `.env` файл настроен правильно:
```env
PORT=5000
NODE_ENV=development
DB_HOST=localhost
DB_PORT=5433
DB_USER=postgres
DB_PASSWORD=123456
DB_NAME=getelog_db
ADMIN_ID=7547827275
FRONTEND_URL=http://localhost:5173
```

4. Запустите сервер:

**Development mode** (с автоперезагрузкой):
```bash
npm run dev
```

**Production mode**:
```bash
npm start
```

## API Endpoints

### Общие

- `GET /` - Информация о API
- `GET /api/health` - Проверка работоспособности

### Статистика

- `GET /api/stats/global` - Глобальная статистика системы
- `GET /api/stats/activity` - Последние активности

### Клиенты

- `GET /api/clients` - Список всех клиентов (с пагинацией)
- `GET /api/clients/search?query=...` - Поиск клиента по ID или username
- `GET /api/clients/:userId` - Детали клиента
- `GET /api/clients/:userId/bots` - Боты клиента
- `GET /api/clients/:userId/users` - Пользователи клиента
- `PATCH /api/clients/:userId/balance` - Изменить баланс клиента

### Боты

- `GET /api/bots` - Список всех ботов (с пагинацией)
- `GET /api/bots/:botId` - Детали бота
- `GET /api/bots/:botId/users` - Пользователи бота
- `PATCH /api/bots/:botId/status` - Изменить статус бота

### Пользователи

- `GET /api/users` - Список всех пользователей (с пагинацией)
- `GET /api/users/:userId` - Детали пользователя
- `GET /api/users/search/:query` - Поиск пользователя
- `GET /api/users/by-owner/:ownerId` - Пользователи по владельцу
- `PATCH /api/users/:userId/status` - Изменить статус пользователя

### Транзакции

- `GET /api/transactions` - Список всех транзакций (с пагинацией)
- `GET /api/transactions/:id` - Детали транзакции
- `GET /api/transactions/filter/pending` - Ожидающие транзакции
- `GET /api/transactions/by-client/:clientId` - Транзакции клиента
- `GET /api/transactions/by-user/:userId` - Транзакции пользователя
- `PATCH /api/transactions/:id/status` - Изменить статус транзакции

### Экспорт

- `GET /api/export/all` - Экспорт всех данных (4 листа: Clients, Bots, Users, Transactions)
- `GET /api/export/clients` - Экспорт только клиентов
- `GET /api/export/transactions` - Экспорт только транзакций

## Примеры использования

### Получить глобальную статистику

```bash
curl http://localhost:5000/api/stats/global
```

### Поиск клиента

```bash
# По ID
curl "http://localhost:5000/api/clients/search?query=123456789"

# По username
curl "http://localhost:5000/api/clients/search?query=username"
```

### Изменить баланс клиента

```bash
# Добавить баланс
curl -X PATCH http://localhost:5000/api/clients/123456789/balance \
  -H "Content-Type: application/json" \
  -d '{"amount": 50000, "action": "add"}'

# Вычесть баланс
curl -X PATCH http://localhost:5000/api/clients/123456789/balance \
  -H "Content-Type: application/json" \
  -d '{"amount": 20000, "action": "subtract"}'
```

### Экспорт данных

```bash
# Скачать все данные
curl -O http://localhost:5000/api/export/all

# Скачать только клиентов
curl -O http://localhost:5000/api/export/clients
```

## Аутентификация

В development режиме аутентификация отключена для удобства разработки.

Для production необходимо передавать `ADMIN_ID` в заголовке:
```
X-Admin-ID: 7547827275
```

## Безопасность

- Helmet для защиты заголовков
- CORS настроен для работы с frontend
- Rate limiting (100 запросов в 15 минут)
- Валидация входных данных

## База данных

Backend подключается к существующей PostgreSQL базе данных проекта Getolog.

Убедитесь, что PostgreSQL запущен на порту 5433 и база данных `getelog_db` доступна.

## Troubleshooting

**Ошибка подключения к БД:**
```
Убедитесь, что PostgreSQL запущен и настройки в .env корректны
```

**Port already in use:**
```
Измените PORT в .env файле на свободный порт
```

## Разработка

Для разработки рекомендуется использовать:
```bash
npm run dev
```

Это запустит сервер с автоматической перезагрузкой при изменении файлов (nodemon).

## Production

Для production окружения:
1. Установите `NODE_ENV=production` в `.env`
2. Включите аутентификацию (замените `devBypass` на `verifyManager` в `server.js`)
3. Настройте правильный `FRONTEND_URL`
4. Используйте process manager (PM2, systemd и т.д.)

```bash
# Пример с PM2
pm2 start server.js --name getolog-api
```
