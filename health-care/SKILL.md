---
name: health-care
description: "GitHub 잔디(contribution graph) 스타일로 매일의 건강 습관(운동, 식단, 영양제/약 복용)을 추적하고 시각화하는 헬스케어 에이전트 스킬. 하트비트 기반 자율 노티(하루 3회)와 음식/운동 사진 인식을 지원한다. Use when: (1) 사용자가 건강, 다이어트, 운동, 식단, 칼로리, 체중, 영양제, 잔디를 언급할 때 (2) 음식이나 운동 사진을 업로드할 때 (3) /health-care 커맨드를 실행할 때 (4) 하트비트 주기에 아침/점심/저녁 노티를 자율 발송할 때"
---

# health-care

GitHub 잔디처럼 운동/식단/영양제 실천도를 날짜별 히트맵으로 시각화하고, 하루 3회 자율 노티로 건강 습관을 장려하는 에이전트 스킬.

## Workflow

```
[하트비트 발생] → heartbeat-state.json 읽기 → 시간대 판단 → 노티 발송
[사용자 입력]   → 텍스트/사진 분류 → 기록 저장 → 피드백 응답
[커맨드 실행]   → 대시보드/잔디/리포트 출력
```

## Commands

| Command | Action |
|---------|--------|
| `/health-care` | 오늘 현황 대시보드 + 최근 4주 잔디 |
| `/health-care 시작` | 온보딩 (프로필 인터뷰 → 초기 파일 생성) |
| `/health-care 잔디` | 최근 4주 잔디 시각화 |
| `/health-care 잔디 6개월` | 6개월 잔디 |
| `/health-care 기록` | 오늘 기록 입력/수정 |
| `/health-care 리포트` | 주간/월간 리포트 |
| `/health-care 체중` | 체중 변화 그래프 |
| `/health-care 설정` | 프로필/목표 수정 |

## Onboarding (`/health-care 시작`)

Collect via interview:
1. 이름, 키/체중/목표체중
2. 하루 목표 칼로리, 운동 목표(분)
3. 복용 중인 영양제/약 (이름, 시간대, 용량, 중요도)
4. 노티 선호 시간 (아침/점심/저녁 시)

Create files in `{memory_dir}/health-care/`:
- `profile.json`, `streak.json` (initial), `heartbeat-state.json` (initial)

Output first empty grass visualization.

## Heartbeat (Autonomous Notifications)

On each heartbeat, read and follow [references/heartbeat.md](references/heartbeat.md).

Summary: check `heartbeat-state.json` timestamps against current time and `profile.preferences` hours. Send at most 3 notifications per day:

- **Morning**: yesterday's grass, streak, morning supplement check, today's goals
- **Lunch**: morning summary, cumulative calories, meal logging prompt, hydration
- **Evening**: full day report, grass score with inline 4-week chart, evening supplement reminder

Weekly review on Sundays with PNG grass image via `scripts/generate_grass_image.py`.

## User Input Handling

### Text Input

| Input pattern | Action |
|---------------|--------|
| "비타민 먹었어" / "약 먹었어" | Update supplements record, remind remaining |
| "5km 뛰었어" / "운동 30분" | Add exercise record, estimate calories |
| "점심에 샐러드" / "치킨 먹었어" | Add meal record, estimate calories |
| "체중 77kg" | Record weight, show trend vs target |
| "물 500ml" | Accumulate water intake |
| "잔디 보여줘" | Output 4-week inline grass |
| "리포트" | Weekly/monthly detailed report |

### Photo Input

**Food photo**: Recognize food via Claude Vision → estimate calories and macros (carb/protein/fat) → compare to daily goal → save to daily_log → feedback.

**Exercise photo/screenshot**: Recognize exercise type or OCR running app data → extract distance/time/calories → save to daily_log → encouragement.

## Grass Visualization

### Inline text (conversations/notifications)

```
     월  화  수  목  금  토  일
W07  🟩 🟩 🟨 🟩 🟩 🟩 🟩
W08  🟩 🟩 🟩 🟨 🟩 ⬜ 🟩
W09  🟩 🟩 🟩 🟩 🟩 🟩 🟩
W10  🟩 🟩 🟩 ·  ·  ·  ·

🔥 12일 연속 | 평균: 3.8/4
```

Legend: ⬜ none | 🟥 poor | 🟨 fair | 🟩 good

### PNG image

Run `scripts/generate_grass_image.py` with daily_log.jsonl data. Supports per-category (exercise/diet/supplements/overall) and combined report images.

## Motivation System

**Streak milestones**: 3d, 7d, 14d, 30d, 100d — celebrate with warm message.

**Levels** (by cumulative days): Lv.1 새싹🌱(0) → Lv.2 풀잎🌿(7) → Lv.3 나무🌲(30) → Lv.4 숲🌳(90) → Lv.5 정원사🏡(180) → Lv.6 마스터👑(365)

**Tone**: Always warm and encouraging. Never criticize. Overeating → "내일 가볍게 먹으면 돼요". Missed day → "다시 시작하면 됩니다!".

## Data Schema

See [references/data-schema.md](references/data-schema.md) for full file structures, grass score calculation, and field definitions.
