# Fog of War — MTBank Hackathon

Гео-игра в мобильном банкинге MTBank. Карта Минска покрыта туманом войны, территории разблокируются за транзакции картой.

## Запуск

```bash
docker-compose up --build
```

Открыть: http://localhost:5173

## Без Docker

Terminal 1:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Terminal 2:
```bash
cd frontend
npm install
npm run dev
```

## Сценарий демо для жюри (2 минуты)

1. Открыть карту — Минск покрыт тёмным туманом, виден 1 открытый гекс в центре (Лидо).
2. Нажать **[🍕 Ресторан 25 BYN]** — туман рассеивается, анимация открытия территории.
3. Нажать ещё раз — квест обновляется, прогресс-бар растёт.
4. После 3 открытий — всплывает ачивка **«Первые шаги»** (+50 бонусных баллов).
5. Нажать на открытый гекс — popup с именем партнёра и размером кэшбэка.

## Стек

- **Frontend:** React 18 + Vite + Leaflet + react-leaflet
- **Backend:** FastAPI + SQLAlchemy 2.0 + SQLite
- **Тайлы:** OpenStreetMap

## API

- `GET  /api/hexes` — состояние карты для игрока `demo_player_001`
- `POST /api/transaction` — имитация транзакции, обновляет квест
- `GET  /api/player/{id}/profile` — профиль игрока
