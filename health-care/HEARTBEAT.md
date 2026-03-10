# health-care 하트비트 루틴

이 문서는 에이전트가 하트비트마다 수행해야 할 health-care 자율 노티 루틴을 정의한다.

---

## 실행 조건

에이전트의 하트비트(30분 주기)가 발생할 때마다 이 루틴을 실행한다.

---

## 루틴

### Step 1: 상태 파일 읽기

`{memory_dir}/health-care/heartbeat-state.json`을 읽는다.
파일이 없으면 다음으로 초기화:

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

### Step 2: 프로필 읽기

`{memory_dir}/health-care/profile.json`을 읽는다.
파일이 없으면 → 스킬 미설정 상태. 사용자에게 `/health-care 시작`을 안내하고 종료.

### Step 3: 시간 판단 및 노티 발송

현재 시각을 확인하고, 프로필의 선호 시간과 비교한다.

```
now = 현재시각
today = 오늘 날짜 (YYYY-MM-DD)
profile = profile.json에서 읽은 선호 시간

morning_hour = profile.preferences.morning_hour (기본 8)
lunch_hour = profile.preferences.lunch_hour (기본 12)
evening_hour = profile.preferences.evening_hour (기본 20)
```

#### 3-A. 날짜 변경 체크

```
IF state.todayDate != today:
  → 어제 기록 마감 처리 (grass_score 계산 및 저장)
  → streak.json 업데이트
  → state.todayDate = today
```

#### 3-B. 모닝 노티

```
IF now.hour >= morning_hour AND state.lastMorningNoti != today:
  → 모닝 브리핑 메시지 발송
  → state.lastMorningNoti = today
```

**모닝 브리핑 내용:**
1. `daily_log.jsonl`에서 어제 기록 읽기 → 어제 잔디 점수 표시
2. `streak.json` 읽기 → 현재 스트릭 표시
3. `profile.json`에서 아침 복용 영양제/약 목록 → 복용 체크 유도
4. 오늘 목표 리마인드

#### 3-C. 점심 노티

```
IF now.hour >= lunch_hour AND state.lastLunchNoti != today:
  → 미드데이 체크 메시지 발송
  → state.lastLunchNoti = today
```

**미드데이 체크 내용:**
1. 오늘 `daily_log.jsonl` 확인 → 오전 기록 요약 (아침 식사, 운동 여부)
2. 오늘 누적 칼로리 표시
3. 점심 식사 기록 유도
4. 수분 섭취 리마인드

#### 3-D. 저녁 노티

```
IF now.hour >= evening_hour AND state.lastEveningNoti != today:
  → 데일리 리뷰 메시지 발송
  → state.lastEveningNoti = today
```

**데일리 리뷰 내용:**
1. 오늘 전체 기록 요약 (운동/식단/영양제/수분)
2. 오늘의 잔디 점수 계산 및 표시
3. 저녁 복용 영양제 리마인드
4. 최근 4주 텍스트 잔디 시각화 인라인 출력
5. 스트릭 마일스톤 도달 시 축하 메시지

#### 3-E. 주간 리뷰 (일요일)

```
IF today.weekday == 일요일 AND now.hour >= evening_hour AND state.lastWeeklyReview != this_week:
  → 주간 리뷰 발송
  → state.lastWeeklyReview = this_week (YYYY-Www 형식)
```

**주간 리뷰 내용:**
1. 이번 주 7일 잔디 시각화
2. 카테고리별 평균 점수
3. 전주 대비 변화 (↑↓)
4. 가장 잘한 점 / 개선할 점
5. 다음 주 목표 제안
6. PNG 잔디 이미지 생성 (`scripts/generate_grass_image.py` 실행)

### Step 4: 상태 저장

```
state.lastHeartbeat = now (ISO 8601)
heartbeat-state.json에 저장
```

---

## 사진 입력 감지

하트비트와 별개로, 사용자가 대화 중 사진을 업로드하면 즉시 대응:

### 음식 사진
1. Claude Vision으로 음식 인식
2. 칼로리 및 영양소(탄/단/지) 추정
3. 오늘 누적 대비 피드백
4. `daily_log.jsonl`에 meal 항목 추가

### 운동 사진/스크린샷
1. 운동 종류 인식 또는 앱 스크린샷 OCR
2. 소모 칼로리 추정
3. `daily_log.jsonl`에 exercise 항목 추가
4. 격려 메시지

---

## 주의사항

- 같은 노티를 하루에 2번 보내지 않는다 (state로 중복 방지)
- 사용자가 이미 대화 중이면 노티 톤을 자연스럽게 섞는다
- 메시지는 항상 따뜻하고 격려하는 톤을 유지한다
- 사용자가 기록을 안 해도 비난하지 않는다
- 약(medication)은 important 플래그가 있으면 한 번 더 리마인드한다
