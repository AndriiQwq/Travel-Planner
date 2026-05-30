# Travel Planner API

FastAPI CRUD service for travel projects and places.

## Run locally

```bash
copy .env.example .env
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

API: `http://127.0.0.1:8000`

## API docs

- Swagger UI: `http://127.0.0.1:8000/docs`

## Docker

```bash
docker compose up --build
```

## Notes

- Max 10 places per project
- No duplicate `external_id` in one project
- Project cannot be deleted if any place is visited
- Places are validated via Art Institute API (`/artworks/{id}`)
