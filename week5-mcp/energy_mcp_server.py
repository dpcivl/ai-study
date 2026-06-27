"""
에너지 관리 MCP 서버 (FEMS 워밍업)
가짜 데이터로 FEMS 도메인 도구들 구현
"""
import random
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("energy-management-server")


# ===== 가짜 데이터베이스 =====
# 실제로는 FEMS DB나 API에서 가져옴

FAKE_LINES = {
    "line_1": {"name": "조립 라인 1", "rated_power_kw": 150},
    "line_2": {"name": "조립 라인 2", "rated_power_kw": 200},
    "line 3": {"name": "포장 라인", "rated_power_kw": 80},
    "line_4": {"name": "도장 라인", "rated_power_kw": 250},
}


def generate_fake_consumption(line_id: str, hours: int = 24) -> list:
    """가짜 전력 사용량 생성"""
    if line_id not in FAKE_LINES:
        return []
    
    rated = FAKE_LINES[line_id]["rated_power_kw"]
    now = datetime.now()

    data = []
    for i in range(hours):
        timestamp = now - timedelta(hours=hours - i - 1)
        # 70 ~ 100% 사용률 랜덤
        usage = rated * random.uniform(0.7, 1.0)
        data.append({
            "timestamp": timestamp.strftime("%Y-%m-%d %H:00"),
            "power_kw": round(usage, 1)
        })

    return data


FAKE_ALARMS = [
    {
        "alarm_id": "A001", 
        "timestamp": "2026-06-25 14:23",
        "line_id": "line_4",
        "severity": "high",
        "message": "도장 라인 전력 사용량 정격 초과 (110%)"
    },
    {
        "alarm_id": "A002",
        "timestamp": "2026-06-25 16:45",
        "line_id": "line_2",
        "severity": "medium",
        "message": "조립 라인 2 전력 효율 저하 감지"
    },
    {
        "alarm_id": "A003",
        "timestamp": "2026-06-25 18:12",
        "line_id": "line_1",
        "severity": "low",
        "message": "조립 라인 1 야간 대기 전력 평소보다 높음"
    },
]


# ===== 도구 1: 라인 목록 =====
@mcp.tool()
def list_production_lines() -> str:
    """
    공장의 모든 생산 라인 목록을 반환합니다. 
    각 라인의 ID, 이름, 정격 전력을 포함합니다. 

    Returns:
        라인 목록 문자열
    """
    lines = []
    for line_id, info in FAKE_LINES.items():
        lines.append(
            f"- {line_id}: {info['name']} (정격: {info['rated_power_kw']}kW)"
        )
    return "생산 라인 목록:\n" + "\n".join(lines)


# ===== 도구 2: 전력 사용량 조회 =====
@mcp.tool()
def get_energy_consumption(line_id: str, hours: int = 24) -> str:
    """
    특정 라인의 최근 전력 사용량을 조회합니다. 
    
    Args:
        line_id: 라인 ID (예: line_1, line_2, line_3, line_4)
        hours: 조회할 과거 시간 범위 (기본 24시간)
        
    Returns:
        시간별 전력 사용량
    """
    if line_id not in FAKE_LINES:
        return f"오류: 알 수 없는 라인 '{line_id}'. list_production_lines로 확인하세요."
    
    line_info = FAKE_LINES[line_id]
    data = generate_fake_consumption(line_id, hours)

    if not data:
        return f"{line_info['name']}: 데이터 없음"
    
    # 통계
    powers = [d['power_kw'] for d in data]
    avg = sum(powers) / len(powers)
    max_power = max(powers)
    min_power = min(powers)

    result = f"{line_info['name']} ({line_id}) - 최근 {hours}시간 \n"
    result += f"정격 전력: {line_info['rated_power_kw']}kW\n"
    result += f"평균: {avg:.1f}kW, 최대: {max_power:.1f}kW, 최소: {min_power:.1f}kW\n\n"

    # 최근 5시간만 상세 표시 (전부면 길어짐)
    result += "최근 5시간 상세:\n"
    for d in data[-5:]:
        result += f"  {d['timestamp']}: {d['power_kw']}kW\n"

    return result



# ===== 도구 3: 알람 조회 =====
@mcp.tool()
def list_alarms(severity: str = "all") -> str:
    """
    현재 발생한 알람 목록을 조회합니다. 
    
    Args:
        severity: 알람 등급 필터 ("high", "medium", "low", "all" 중 하나)
    
    Returns:
        알람 목록
    """
    if severity not in ["high", "medium", "low", "all"]:
        return "오류: severity는 'high', 'medium', 'low', 'all' 중 하나여야 함"
    
    # 필터링
    if severity == "all":
        filtered = FAKE_ALARMS
    else:
        filtered = [a for a in FAKE_ALARMS if a['severity'] == severity]

    if not filtered:
        return f"등급 '{severity}'에 해당하는 알람 없음"
    
    result = f"알람 {len(filtered)}건:\n"
    for alarm in filtered:
        result += (
            f"\n[{alarm['alarm_id']}] {alarm['severity'].upper()}\n"
            f"  시각: {alarm['timestamp']}\n"
            f"  라인: {alarm['line_id']}\n"
            f"  메시지: {alarm['message']}\n"
        )
    
    return result


# ===== 도구 4: 라인 상태 =====
@mcp.tool()
def get_line_status(line_id: str) -> str:
    """
    특정 라인의 현재 운영 상태를 조회합니다. 
    
    Args:
        line_id: 라인 ID
        
    Returns:
        라인 상태 정보
    """
    if line_id not in FAKE_LINES:
        return f"오류: 알 수 없는 라인 '{line_id}"
    
    line_info = FAKE_LINES[line_id]
    rated = line_info['rated_power_kw']

    # 가짜 현재 상태 생성
    current_power = rated * random.uniform(0.6, 1.05)
    is_running = random.random() > 0.1      # 90% 가동 중
    efficiency = random.uniform(0.75, 0.95)

    # 알람 체크
    line_alarms = [a for a in FAKE_ALARMS if a['line_id'] == line_id]

    result = f"{line_info['name']} ({line_id}) 현재 상태\n"
    result += f"  가동 여부: {'운영 중' if is_running else '중단'}\n"
    result += f"  현재 전력: {current_power:.1f}kW (정격 대비 {current_power/rated*100:.1f}%\n)"
    result += f"  효율: {efficiency*100:.1f}%\n"
    result += f"  관련 알람: {len(line_alarms)}건"

    if line_alarms:
        result += "  (list_alarm로 상세 확인)"

    return result


# ===== 도구 5: 일별 요약 =====
@mcp.tool()
def get_daily_summary(date: str = "today") -> str:
    """
    특정 날짜의 전체 공장 에너지 요약을 반환합니다. 
    
    Args:
        date: 날짜 (예: "today", "yesterday", "2026-06-26")
    
    Returns:
        일별 요약 정보
    """
    # 가짜 요약 생성
    total_power = sum(FAKE_LINES[lid]["rated_power_kw"] for lid in FAKE_LINES) * 0.85

    return (
        f"공장 일별 요약 ({date}):\n"
        f"- 총 라인 수: {len(FAKE_LINES)}\n"
        f"- 총 사용 전력: {total_power:.1f}kW\n"
        f"- 평균 가동률: 85%\n"
        f"- 알람 발생: {len(FAKE_ALARMS)}건\n"
    )


# ===== 도구 6: 라인 비교 =====
@mcp.tool()
def compare_lines(line_id_1: str, line_id_2: str) -> str:
    """
    두 라인의 전력 사용 효율을 비교합니다. 
    
    Args:
        line_id_1: 첫 번째 라인 ID
        line_id_2: 두 번째 라인 ID
        
    Returns:
        비교 분석 결과
    """
    if line_id_1 not in FAKE_LINES or line_id_2 not in FAKE_LINES:
        return "오류: 알 수 없는 라인 ID"
    
    info1 = FAKE_LINES[line_id_1]
    info2 = FAKE_LINES[line_id_2]

    return (
        f"라인 비교: {info1['name']} vs {info2['name']}\n"
        f"\n{line_id_1}:\n"
        f"  - 정격 전력: {info1['rated_power_kw']}kW\n"
        f"\n{line_id_2}:\n"
        f"  - 정격 전력: {info2['rated_power_kw']}kW\n"
        f"\n정격 차이: {abs(info1['rated_power_kw'] - info2['rated_power_kw'])}kW"
    )


# ===== 도구 7: 에너지 비용 계산
@mcp.tool()
def calculate_energy_cost(line_id: str, hours: int = 24, kwh_price: float = 100.0) -> str:
    """
    특정 라인의 에너지 비용을 계산합니다. 
    
    Args:
        line_id: 라인 ID
        hours: 계산할 시간 (기본 24시간)
        kwh_price: kWh당 원 (기본 100원)
    
    Returns:
        에너지 비용 계산 결과
    """
    if line_id not in FAKE_LINES:
        return f"오류: 알 수 없는 라인 '{line_id}'"
    
    data = generate_fake_consumption(line_id, hours)
    total_kwh = sum(d['power_kw'] for d in data)    # 시간당 kW x 시간 = kWh
    total_cost = total_kwh * kwh_price

    return (
        f"{FAKE_LINES[line_id]['name']} 에너지 비용:\n"
        f"- 기간: 최근 {hours}시간\n"
        f"- 사용량: {total_kwh:.1f}kWh\n"
        f"- 단가: {kwh_price}원/kWh\n"
        f"- 총 비용: {total_cost:,.0f}원"
    )

if __name__ == "__main__":
    mcp.run()