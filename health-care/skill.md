---
name: health-care
version: 1.0.0
description: "건강 잔디 심기 - 운동, 식단, 영양제/약 복용을 GitHub 잔디처럼 추적하고 매일 3회 자율 노티로 동기부여하는 헬스케어 에이전트 스킬"
trigger: "health-care, 건강, 잔디, 식단, 운동, 영양제, 칼로리, 체중, 다이어트, 헬스"
metadata:
  emoji: "🌱"
  category: "health"
  heartbeat_interval_min: 30
  notifications_per_day: 3
---

# health-care 스킬

GitHub 잔디(contribution graph) 심기처럼 매일의 건강 습관을 시각화하고 장려하는 AI 헬스케어 에이전트.

## 핵심 파일

| 파일 | 역할 |
|------|------|
| `skill.md` | 이 문서 (메인 스킬 정의) |
| `HEARTBEAT.md` | 자율 노티 스케줄 및 하트비트 루틴 |
| `scripts/generate_grass_image.py` | 잔디 히트맵 시각화 |
| `prd.md` | 상세 기획 문서 |

---

## 1. 메모리 구조

모든 사용자 데이터는 메모리 디렉토리에 영속 저장된다.

```
{memory_dir}/health-care/
├── profile.json           # 사용자 프로필 및 목표
├── daily_log.jsonl        # 일별 건강 기록 (append-only)
├── supplements.json       # 영양제/약 목록 및 복용 스케줄
├── streak.json            # 스트릭 및 통계
└── heartbeat-state.json   # 하트비트 상태 (마지막 노티 시각 등)
```

### 1.1 heartbeat-state.json

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

### 1.2 profile.json

```json
{
  "name": "사용자명",
  "created_at": "2026-03-10",
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
    {"name": "종합비타민", "time": "morning", "dosage": "1정"},
    {"name": "오메가3", "time": "evening", "dosage": "1캡슐"}
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

### 1.3 daily_log.jsonl (한 줄 = 하루)

```json
{
  "date": "2026-03-10",
  "exercise": {"done": true, "type": "러닝", "duration_min": 40, "calories_burned": 350},
  "meals": [
    {"time": "08:30", "type": "breakfast", "description": "계란 2개, 통밀빵", "calories": 450}
  ],
  "supplements": {"morning": {"종합비타민": true, "혈압약": true}, "evening": {"오메가3": false}},
  "water_ml": 1800,
  "weight_kg": 77.5,
  "grass_score": {"exercise": 3, "diet": 4, "supplements": 3, "overall": 3}
}
```

---

## 2. 하트비트 (자율 노티 시스템)

**에이전트는 하트비트 시 반드시 `HEARTBEAT.md`를 읽고 따른다.**

하트비트가 발생할 때마다 다음을 수행:

1. `heartbeat-state.json`을 읽는다
2. 현재 시각과 비교하여 보낼 노티가 있는지 판단한다
3. 해당하는 노티를 사용자에게 전달한다
4. `heartbeat-state.json`을 업데이트한다

### 2.1 노티 판단 로직

```
현재시각 = now()
오늘날짜 = today()

IF todayDate != 오늘날짜:
  → 새로운 날: todayDate 갱신, 어제 기록 마감 처리

IF 현재시각.hour >= morning_hour AND lastMorningNoti != 오늘날짜:
  → 모닝 노티 발송

IF 현재시각.hour >= lunch_hour AND lastLunchNoti != 오늘날짜:
  → 점심 노티 발송

IF 현재시각.hour >= evening_hour AND lastEveningNoti != 오늘날짜:
  → 저녁 노티 발송

IF 오늘 == 일요일 AND lastWeeklyReview != 이번주:
  → 주간 리뷰 발송
```

### 2.2 노티 내용

#### 모닝 노티 (아침)
```
📋 [health-care 모닝 브리핑]

좋은 아침이에요! 오늘도 건강한 하루 시작해볼까요?

◾ 아침 영양제: 종합비타민, 혈압약 - 드셨나요?
◾ 어제 잔디: 🟩🟩🟨 (종합 3.2/4)
◾ 현재 스트릭: 12일 연속 달성 중
◾ 오늘 목표: 운동 30분 | 칼로리 2,000kcal 이내

영양제 드셨으면 "먹었어"라고 알려주세요!
```

#### 점심 노티 (점심)
```
📋 [health-care 미드데이 체크]

점심 맛있게 드셨나요?

◾ 오전 운동 여부: 아직 미기록
◾ 오늘 누적 칼로리: 450kcal (아침)
◾ 수분 섭취 리마인드: 물 한 잔 드세요!

뭐 드셨는지 알려주시거나 사진 올려주시면 기록해드릴게요 📸
```

#### 저녁 노티 (저녁)
```
📋 [health-care 데일리 리뷰]

오늘 하루 수고하셨어요! 오늘의 건강 리포트:

  🏃 운동: 러닝 40분 (350kcal)          🟩
  🍽️ 식단: 1,450 / 2,000 kcal          🟩
  💊 영양제: 2/3 복용                    🟨
  💧 수분: 1.8L / 2L

  오늘의 잔디: 🟩 (3.5/4)
  스트릭: 13일째!

잠들기 전 오메가3 잊지 마세요!

[최근 4주 잔디]
     월  화  수  목  금  토  일
W07  🟩 🟩 🟨 🟩 🟩 🟩 🟩
W08  🟩 🟩 🟩 🟨 🟩 ⬜ 🟩
W09  🟩 🟩 🟩 🟩 🟩 🟩 🟩
W10  🟩 🟩 🟩 ·  ·  ·  ·
```

---

## 3. 사용자 입력 처리

### 3.1 트리거 키워드

다음 키워드가 감지되면 이 스킬이 활성화된다:

- `/health-care` - 메인 대시보드
- `건강`, `잔디`, `운동`, `식단`, `영양제`, `칼로리`, `체중`, `다이어트`
- 음식/운동 사진 업로드

### 3.2 음식 사진 대응

사용자가 음식 사진을 업로드하면:

1. Claude Vision으로 음식 종류 인식
2. 예상 칼로리 및 영양소(탄/단/지) 추정
3. 오늘 누적 칼로리 대비 피드백
4. `daily_log.jsonl`에 기록 추가
5. 격려 또는 주의 메시지

**응답 예시:**
```
후라이드 치킨이네요! 🍗
  예상 칼로리: ~800kcal (반마리 기준)
  탄:단:지 = 30:35:35

  오늘 누적: 2,250 / 2,000 kcal (250kcal 초과)
  괜찮아요, 내일 조금 더 가볍게 먹으면 됩니다!
  기록에 반영했어요 ✅
```

### 3.3 운동 사진/스크린샷 대응

사용자가 운동 사진이나 러닝앱 스크린샷을 업로드하면:

1. 운동 종류 인식 (러닝, 헬스, 요가 등)
2. 스크린샷 OCR로 거리/시간/칼로리 추출
3. `daily_log.jsonl`에 기록 추가
4. 격려 메시지 + 잔디 업데이트

### 3.4 텍스트 입력 대응

| 사용자 입력 | 에이전트 동작 |
|------------|-------------|
| "비타민 먹었어" | supplements 기록 업데이트, 남은 약 리마인드 |
| "오늘 5km 뛰었어" | 운동 기록 추가, 칼로리 추정, 격려 |
| "점심에 샐러드 먹었어" | 식단 기록 추가, 칼로리 추정 |
| "체중 77kg" | 체중 기록, 목표 대비 변화 추이 표시 |
| "물 500ml" | 수분 섭취 기록 누적 |
| "잔디 보여줘" | 최근 4주 잔디 시각화 출력 |
| "리포트" | 주간/월간 상세 리포트 |

---

## 4. 잔디 점수 산정

### 0~4 스케일

| 점수 | 운동 | 식단 | 영양제/약 | 색상 |
|------|------|------|----------|------|
| 0 | 미기록 | 미기록 | 미기록 | ⬛ |
| 1 | 10분 미만 | 목표 150%+ | 25% 미만 | 🟫 |
| 2 | 10~20분 | 목표 120~150% | 25~50% | 🟩(연) |
| 3 | 20~30분 | 목표 100~120% | 50~75% | 🟩(중) |
| 4 | 30분+ | 목표 이내 | 75%+ | 🟩(진) |

**종합 = 운동×0.4 + 식단×0.35 + 영양제×0.25** (반올림)

---

## 5. 동기부여 시스템

### 5.1 스트릭 축하

| 스트릭 | 메시지 |
|--------|--------|
| 3일 | "3일 연속! 습관이 만들어지고 있어요 🌱" |
| 7일 | "일주일 달성! 첫 번째 마일스톤 🎉" |
| 14일 | "2주 연속! 몸이 변화를 느끼기 시작할 때에요 💪" |
| 30일 | "한 달 달성! 이제 완전한 습관이에요 🏆" |
| 100일 | "100일! 전설의 잔디밭 완성 🌳" |

### 5.2 레벨 시스템

| 레벨 | 누적 달성일 | 칭호 |
|------|-----------|------|
| Lv.1 | 0일 | 새싹 🌱 |
| Lv.2 | 7일 | 풀잎 🌿 |
| Lv.3 | 30일 | 나무 🌲 |
| Lv.4 | 90일 | 숲 🌳 |
| Lv.5 | 180일 | 정원사 🏡 |
| Lv.6 | 365일 | 마스터 👑 |

### 5.3 메시지 톤

- 강압적이지 않고 따뜻하게 격려
- 연속 달성 시 스트릭 축하
- 놓친 날이 있어도 비난하지 않고 다시 시작 응원
- 과식해도 "내일 가볍게 먹으면 돼요"식 긍정 피드백

---

## 6. 커맨드

| 커맨드 | 설명 |
|--------|------|
| `/health-care` | 메인 대시보드 (오늘 현황 + 잔디) |
| `/health-care 시작` | 최초 설정 (온보딩 인터뷰) |
| `/health-care 잔디` | 잔디 시각화 (기본: 최근 4주) |
| `/health-care 잔디 6개월` | 6개월 잔디 |
| `/health-care 기록` | 오늘 기록 입력/수정 |
| `/health-care 리포트` | 주간/월간 리포트 |
| `/health-care 체중` | 체중 변화 그래프 |
| `/health-care 설정` | 프로필/목표 수정 |

---

## 7. 온보딩 (최초 설정)

사용자가 처음 `/health-care 시작`을 실행하면:

1. **환영 메시지** 출력
2. **인터뷰 형식으로 기본 정보 수집:**
   - 이름
   - 키 / 현재 체중 / 목표 체중
   - 하루 목표 칼로리
   - 운동 목표 (분/일)
   - 복용 중인 영양제/약 목록 및 시간대
   - 노티 선호 시간 (아침/점심/저녁)
3. `profile.json` 생성
4. `supplements.json` 생성
5. `heartbeat-state.json` 초기화
6. `streak.json` 초기화
7. 첫 잔디 시각화 출력 (빈 잔디)

---

## 8. 잔디 시각화

### 8.1 터미널 텍스트 잔디 (인라인)

하트비트 노티나 대화 중 간이 표시:

```
     월  화  수  목  금  토  일
W07  🟩 🟩 🟨 🟩 🟩 🟩 🟩
W08  🟩 🟩 🟩 🟨 🟩 ⬜ 🟩
W09  🟩 🟩 🟩 🟩 🟩 🟩 🟩
W10  🟩 🟩 🟩 ·  ·  ·  ·

🔥 12일 연속 | 이번 주 평균: 3.8/4
```

범례: ⬜ 미기록 | 🟥 부족 | 🟨 보통 | 🟩 달성

### 8.2 이미지 잔디 (PNG)

`scripts/generate_grass_image.py` 실행하여 GitHub 스타일 히트맵 PNG 생성.
카테고리별(종합/운동/식단/영양제) 또는 통합 리포트 이미지 출력.

---

## 9. 하트비트 통합 가이드

이 스킬을 에이전트의 하트비트에 등록하려면 `HEARTBEAT.md`에 다음을 추가:

```markdown
## health-care 체크

If it's time for a health-care notification:
1. Read `{memory_dir}/health-care/heartbeat-state.json`
2. Read `{memory_dir}/health-care/HEARTBEAT.md` and follow it
3. Update heartbeat-state.json timestamps
```

자세한 하트비트 루틴은 `HEARTBEAT.md` 참조.
