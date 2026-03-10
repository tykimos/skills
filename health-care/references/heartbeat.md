# Heartbeat Routine

Autonomous notification routine executed on each heartbeat cycle.

## State File: `heartbeat-state.json`

```json
{
  "lastHeartbeat": null,
  "lastMorningNoti": null,
  "lastLunchNoti": null,
  "lastEveningNoti": null,
  "lastWeeklyReview": null,
  "todayDate": null
}
```

## Execution Steps

### 1. Read State

Read `{memory_dir}/health-care/heartbeat-state.json`. If missing, initialize with defaults above.

### 2. Read Profile

Read `{memory_dir}/health-care/profile.json`. If missing, prompt user to run `/health-care 시작`.

### 3. Determine Notifications

```
now = current time
today = YYYY-MM-DD
morning_hour = profile.preferences.morning_hour (default 8)
lunch_hour   = profile.preferences.lunch_hour (default 12)
evening_hour = profile.preferences.evening_hour (default 20)
```

**Date rollover**: If `state.todayDate != today`, finalize yesterday's record (calculate grass_score), update streak.json, set `state.todayDate = today`.

**Morning** (`now.hour >= morning_hour AND lastMorningNoti != today`):
- Yesterday's grass score summary
- Current streak count
- Morning supplements/medications checklist
- Today's goals reminder

**Lunch** (`now.hour >= lunch_hour AND lastLunchNoti != today`):
- Morning record summary (breakfast, exercise)
- Cumulative calorie count
- Lunch meal logging prompt
- Hydration reminder

**Evening** (`now.hour >= evening_hour AND lastEveningNoti != today`):
- Full day summary (exercise/diet/supplements/water)
- Today's grass score with inline 4-week visualization
- Evening supplement reminder
- Streak milestone celebration if applicable

**Weekly review** (Sunday, `now.hour >= evening_hour AND lastWeeklyReview != this_week`):
- 7-day grass visualization
- Category averages vs previous week
- Highlights and improvement suggestions
- Generate PNG via `scripts/generate_grass_image.py`

### 4. Save State

Update `lastHeartbeat` to current ISO 8601 timestamp and write `heartbeat-state.json`.

## Rules

- Never send the same notification type twice in one day (enforce via state timestamps).
- Merge notification naturally into ongoing conversation if user is active.
- Always use warm, encouraging tone. Never criticize missed days.
- Flag `important: true` medications with an extra reminder.
