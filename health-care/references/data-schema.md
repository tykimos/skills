# Data Schema

All user data persists in `{memory_dir}/health-care/`.

## profile.json

```json
{
  "name": "string",
  "created_at": "YYYY-MM-DD",
  "goals": {
    "daily_calories": 2000,
    "exercise_minutes": 30,
    "water_ml": 2000
  },
  "body": {
    "height_cm": 175,
    "weight_kg": 78,
    "target_weight_kg": 72
  },
  "supplements": [
    {"name": "종합비타민", "time": "morning", "dosage": "1정"}
  ],
  "medications": [
    {"name": "혈압약", "time": "morning", "dosage": "1정", "important": true}
  ],
  "preferences": {
    "morning_hour": 8,
    "lunch_hour": 12,
    "evening_hour": 20,
    "tone": "friendly"
  }
}
```

## daily_log.jsonl (append-only, one JSON object per line per day)

```json
{
  "date": "YYYY-MM-DD",
  "exercise": {"done": true, "type": "러닝", "duration_min": 40, "calories_burned": 350},
  "meals": [
    {"time": "HH:MM", "type": "breakfast|lunch|dinner|snack", "description": "string", "calories": 450, "photo": false}
  ],
  "supplements": {
    "morning": {"종합비타민": true, "혈압약": true},
    "evening": {"오메가3": false}
  },
  "water_ml": 1800,
  "weight_kg": 77.5,
  "grass_score": {"exercise": 3, "diet": 4, "supplements": 3, "overall": 3}
}
```

## streak.json

```json
{
  "current_streak": 12,
  "longest_streak": 30,
  "total_logged_days": 45,
  "milestones": [
    {"type": "streak", "value": 7, "date": "YYYY-MM-DD", "celebrated": true}
  ],
  "weekly_summary": {
    "YYYY-Www": {"avg_score": 3.5, "exercise_days": 5, "diet_score": 3.8}
  }
}
```

## heartbeat-state.json

See [heartbeat.md](heartbeat.md).

## Grass Score Calculation

| Score | Exercise | Diet | Supplements | Color |
|-------|----------|------|-------------|-------|
| 0 | not logged | not logged | not logged | ⬛ |
| 1 | <10 min | >150% goal | <25% taken | dark green |
| 2 | 10-20 min | 120-150% | 25-50% | medium green |
| 3 | 20-30 min | 100-120% | 50-75% | green |
| 4 | 30+ min | within goal | 75%+ | bright green |

**Overall = exercise×0.4 + diet×0.35 + supplements×0.25** (rounded)
