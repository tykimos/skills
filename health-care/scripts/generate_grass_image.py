"""
health-care 건강 잔디 시각화 스크립트
GitHub contribution graph 스타일의 건강 실천도 히트맵 생성
"""
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


# GitHub 스타일 색상 팔레트
COLORS = {
    "exercise": {
        -1: "#161b22",   # 미기록
        0: "#161b22",
        1: "#0e4429",
        2: "#006d32",
        3: "#26a641",
        4: "#39d353",
    },
    "diet": {
        -1: "#161b22",
        0: "#161b22",
        1: "#5e1914",    # 과식 (붉은 톤)
        2: "#0e4429",
        3: "#26a641",
        4: "#39d353",
    },
    "supplements": {
        -1: "#161b22",
        0: "#161b22",
        1: "#0e4429",
        2: "#006d32",
        3: "#26a641",
        4: "#39d353",
    },
    "overall": {
        -1: "#161b22",
        0: "#161b22",
        1: "#0e4429",
        2: "#006d32",
        3: "#26a641",
        4: "#39d353",
    },
}

CATEGORY_LABELS = {
    "exercise": "운동",
    "diet": "식단",
    "supplements": "영양제/약",
    "overall": "종합",
}


def generate_sample_data(days=84):
    """최근 N일간 샘플 데이터 생성"""
    data = []
    today = datetime(2026, 3, 10)

    random.seed(42)
    for i in range(days - 1, -1, -1):
        date = today - timedelta(days=i)

        # 주말에는 운동 확률 낮게, 평일엔 높게
        is_weekend = date.weekday() >= 5

        # 시간이 갈수록 점수가 높아지는 트렌드
        trend = min(1.0, (days - i) / days + 0.3)

        exercise = random.choices(
            [0, 1, 2, 3, 4],
            weights=[0.1, 0.1, 0.15, 0.3 * trend, 0.35 * trend] if not is_weekend
            else [0.25, 0.15, 0.2, 0.2, 0.2],
        )[0]

        diet = random.choices(
            [1, 2, 3, 4],
            weights=[0.1, 0.2, 0.35 * trend, 0.35 * trend],
        )[0]

        supplements = random.choices(
            [0, 1, 2, 3, 4],
            weights=[0.05, 0.05, 0.1, 0.3, 0.5 * trend],
        )[0]

        overall = round(exercise * 0.4 + diet * 0.35 + supplements * 0.25)
        overall = max(0, min(4, overall))

        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "grass_score": {
                "exercise": exercise,
                "diet": diet,
                "supplements": supplements,
                "overall": overall,
            }
        })

    return data


def create_grass_image(data, category="overall", weeks=12, output_path=None):
    """GitHub 스타일 잔디 히트맵 이미지 생성"""

    colors = COLORS[category]
    label = CATEGORY_LABELS[category]

    # 날짜-점수 매핑
    score_map = {}
    for entry in data:
        score_map[entry["date"]] = entry["grass_score"].get(category, -1)

    # 최근 weeks주 범위 계산
    last_date = datetime.strptime(data[-1]["date"], "%Y-%m-%d")

    # 마지막 날짜가 속한 주의 토요일까지
    days_to_sat = (5 - last_date.weekday()) % 7
    end_date = last_date + timedelta(days=days_to_sat)
    start_date = end_date - timedelta(weeks=weeks) + timedelta(days=1)

    # 7행(요일) x weeks열 그리드
    grid = np.full((7, weeks), -1, dtype=int)
    date_labels = [[None] * weeks for _ in range(7)]

    current = start_date
    for week in range(weeks):
        for day in range(7):
            d = start_date + timedelta(weeks=week, days=day)
            date_str = d.strftime("%Y-%m-%d")
            if date_str in score_map:
                grid[day, week] = score_map[date_str]
            date_labels[day][week] = date_str

    # 그리기
    fig, ax = plt.subplots(figsize=(max(10, weeks * 0.75), 3.5))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")

    cell_size = 0.85
    gap = 0.15

    for week in range(weeks):
        for day in range(7):
            score = grid[day, week]
            color = colors.get(score, colors[-1])

            rect = mpatches.FancyBboxPatch(
                (week * (cell_size + gap), (6 - day) * (cell_size + gap)),
                cell_size, cell_size,
                boxstyle="round,pad=0.02,rounding_size=0.08",
                facecolor=color,
                edgecolor="none",
            )
            ax.add_patch(rect)

    # 요일 라벨
    day_names = ["월", "화", "수", "목", "금", "토", "일"]
    for i, name in enumerate(day_names):
        if i % 2 == 0:  # 월, 수, 금만 표시
            ax.text(
                -0.6, (6 - i) * (cell_size + gap) + cell_size / 2,
                name, ha="center", va="center",
                fontsize=9, color="#8b949e",
                fontfamily="AppleGothic",
            )

    # 월 라벨
    month_labels = {}
    for week in range(weeks):
        d = start_date + timedelta(weeks=week)
        month_key = d.strftime("%Y-%m")
        if month_key not in month_labels:
            month_labels[month_key] = week

    month_names = ["1월", "2월", "3월", "4월", "5월", "6월",
                   "7월", "8월", "9월", "10월", "11월", "12월"]
    for month_key, week_idx in month_labels.items():
        month_num = int(month_key.split("-")[1])
        ax.text(
            week_idx * (cell_size + gap), 7.2 * (cell_size + gap),
            month_names[month_num - 1],
            ha="left", va="center",
            fontsize=9, color="#8b949e",
            fontfamily="AppleGothic",
        )

    # 제목
    total_days = sum(1 for entry in data if entry["grass_score"].get(category, 0) >= 3)
    streak = 0
    for entry in reversed(data):
        if entry["grass_score"].get(category, 0) >= 3:
            streak += 1
        else:
            break

    title = f"health-care  {label} 잔디  |  최근 {weeks}주  |  달성일 {total_days}일  |  연속 {streak}일"
    ax.set_title(
        title,
        fontsize=13, color="#e6edf3", pad=20,
        fontfamily="AppleGothic", fontweight="bold",
    )

    # 범례
    legend_x = weeks * (cell_size + gap) - 6.5
    legend_y = -1.2
    ax.text(legend_x, legend_y, "Less", fontsize=8, color="#8b949e",
            ha="center", va="center", fontfamily="AppleGothic")
    for i, score in enumerate([0, 1, 2, 3, 4]):
        rect = mpatches.FancyBboxPatch(
            (legend_x + 1.0 + i * (cell_size + 0.05), legend_y - cell_size / 2),
            cell_size * 0.7, cell_size * 0.7,
            boxstyle="round,pad=0.02,rounding_size=0.05",
            facecolor=colors[score],
            edgecolor="none",
        )
        ax.add_patch(rect)
    ax.text(legend_x + 1.0 + 5 * (cell_size + 0.05), legend_y, "More",
            fontsize=8, color="#8b949e", ha="center", va="center",
            fontfamily="AppleGothic")

    ax.set_xlim(-1.5, weeks * (cell_size + gap) + 0.5)
    ax.set_ylim(-2.5, 8.5 * (cell_size + gap))
    ax.set_aspect("equal")
    ax.axis("off")

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches="tight",
                    facecolor="#0d1117", edgecolor="none")
        print(f"저장: {output_path}")

    plt.close()
    return fig


def create_all_categories(data, weeks=12, output_dir=None):
    """4개 카테고리 통합 이미지 생성"""

    categories = ["overall", "exercise", "diet", "supplements"]

    fig, axes = plt.subplots(4, 1, figsize=(max(10, weeks * 0.75), 12))
    fig.patch.set_facecolor("#0d1117")
    fig.suptitle(
        "health-care 건강 잔디 리포트",
        fontsize=16, color="#e6edf3", y=0.98,
        fontfamily="AppleGothic", fontweight="bold",
    )

    last_date_str = data[-1]["date"]

    # 날짜-점수 매핑
    score_map = {}
    for entry in data:
        for cat in categories:
            key = (entry["date"], cat)
            score_map[key] = entry["grass_score"].get(cat, -1)

    last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
    days_to_sat = (5 - last_date.weekday()) % 7
    end_date = last_date + timedelta(days=days_to_sat)
    start_date = end_date - timedelta(weeks=weeks) + timedelta(days=1)

    for idx, (cat, ax) in enumerate(zip(categories, axes)):
        colors = COLORS[cat]
        label = CATEGORY_LABELS[cat]

        ax.set_facecolor("#0d1117")

        cell_size = 0.85
        gap = 0.15

        for week in range(weeks):
            for day in range(7):
                d = start_date + timedelta(weeks=week, days=day)
                date_str = d.strftime("%Y-%m-%d")
                score = score_map.get((date_str, cat), -1)
                color = colors.get(score, colors[-1])

                rect = mpatches.FancyBboxPatch(
                    (week * (cell_size + gap), (6 - day) * (cell_size + gap)),
                    cell_size, cell_size,
                    boxstyle="round,pad=0.02,rounding_size=0.08",
                    facecolor=color,
                    edgecolor="none",
                )
                ax.add_patch(rect)

        # 요일 라벨
        day_names = ["월", "화", "수", "목", "금", "토", "일"]
        for i, name in enumerate(day_names):
            if i % 2 == 0:
                ax.text(
                    -0.6, (6 - i) * (cell_size + gap) + cell_size / 2,
                    name, ha="center", va="center",
                    fontsize=8, color="#8b949e",
                    fontfamily="AppleGothic",
                )

        # 카테고리 라벨
        total = sum(1 for e in data if e["grass_score"].get(cat, 0) >= 3)
        ax.set_title(
            f"{label}  ({total}일 달성)",
            fontsize=11, color="#e6edf3", loc="left", pad=8,
            fontfamily="AppleGothic",
        )

        ax.set_xlim(-1.5, weeks * (cell_size + gap) + 0.5)
        ax.set_ylim(-0.5, 7.5 * (cell_size + gap))
        ax.set_aspect("equal")
        ax.axis("off")

    plt.tight_layout(rect=[0, 0, 1, 0.96])

    if output_dir:
        path = Path(output_dir) / "health_care_grass_all.png"
        plt.savefig(path, dpi=150, bbox_inches="tight",
                    facecolor="#0d1117", edgecolor="none")
        print(f"저장: {path}")

    plt.close()
    return fig


if __name__ == "__main__":
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    # 샘플 데이터 생성
    data = generate_sample_data(days=84)

    # 샘플 데이터 저장
    sample_path = Path(__file__).parent.parent / "examples" / "sample_data.jsonl"
    with open(sample_path, "w", encoding="utf-8") as f:
        for entry in data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"샘플 데이터 저장: {sample_path}")

    # 개별 카테고리 잔디
    for cat in ["overall", "exercise", "diet", "supplements"]:
        create_grass_image(
            data, category=cat, weeks=12,
            output_path=output_dir / f"health_care_grass_{cat}.png"
        )

    # 통합 리포트
    create_all_categories(data, weeks=12, output_dir=output_dir)

    print("\n모든 잔디 시각화 생성 완료!")
