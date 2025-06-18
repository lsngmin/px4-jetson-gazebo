import logging
import pytest
import importlib

# Dummy MavlinkClientInterface 대체용 목 객체
class DummyMavClient:
    def __init__(self):
        self.subscribed_callback = None
    def subscribe_vtol_state(self, callback):
        # 구독 콜백을 저장
        self.subscribed_callback = callback

# 실제 테스트할 모듈 import
from monitor import vtol_state
from monitor.vtol_state import VtolStateMonitor

@pytest.fixture(autouse=True)
def caplog_setup(caplog):
    # INFO 레벨 로그 캡처
    caplog.set_level(logging.INFO)
    return caplog

def test_start_subscribes_and_logs(caplog):
    dummy = DummyMavClient()
    monitor = VtolStateMonitor(dummy)
    monitor.start()
    # subscribe_vtol_state가 _on_vtol_state로 등록됐는지 확인
    cb = dummy.subscribed_callback
    # Bound method identity 비교 대신 함수와 self 비교
    assert hasattr(cb, '__self__') and hasattr(cb, '__func__')
    assert cb.__self__ is monitor
    assert cb.__func__ is VtolStateMonitor._on_vtol_state
    # 로그 메시지 확인
    found = False
    for record in caplog.records:
        if record.name == "VtolStateMonitor" and "VTOL_STATE 구독 시작" in record.message:
            found = True
    assert found, f"Expected log 'VTOL_STATE 구독 시작' from VtolStateMonitor, got: {[r.message for r in caplog.records]}"

def test_on_vtol_state_updates_and_logs(caplog):
    dummy = DummyMavClient()
    monitor = VtolStateMonitor(dummy)
    # 직접 콜백 등록
    dummy.subscribe_vtol_state(monitor._on_vtol_state)
    # 초기 상태 None -> 5
    monitor._on_vtol_state(5)
    assert monitor.current_vtol_state == 5
    # 로그 확인
    found = False
    for record in caplog.records:
        if record.name == "VtolStateMonitor" and "VTOL_STATE 변경: None -> 5" in record.message:
            found = True
    assert found, f"Expected log 'VTOL_STATE 변경: None -> 5', got: {[r.message for r in caplog.records]}"
    # 로그 초기화 후 다음 상태 변경
    caplog.clear()
    monitor._on_vtol_state(7)
    assert monitor.current_vtol_state == 7
    found2 = False
    for record in caplog.records:
        if record.name == "VtolStateMonitor" and "VTOL_STATE 변경: 5 -> 7" in record.message:
            found2 = True
    assert found2, f"Expected log 'VTOL_STATE 변경: 5 -> 7', got: {[r.message for r in caplog.records]}"

def test_multiple_start_calls(caplog):
    dummy = DummyMavClient()
    monitor = VtolStateMonitor(dummy)
    monitor.start()
    caplog.clear()
    # 두 번째 start 호출
    monitor.start()
    cb = dummy.subscribed_callback
    assert hasattr(cb, '__self__') and hasattr(cb, '__func__')
    assert cb.__self__ is monitor
    assert cb.__func__ is VtolStateMonitor._on_vtol_state
    # 로그가 다시 찍혔는지 확인
    assert any("VTOL_STATE 구독 시작" in record.message for record in caplog.records)

def test_reload_module_no_side_effect(caplog):
    # 모듈 reload 시 import 시점 로그가 남지 않는지 확인 (side effect 최소화)
    caplog.clear()
    importlib.reload(vtol_state)
    # import 시점에 심각 오류 로그가 없는지 확인
    for record in caplog.records:
        assert record.levelno < logging.ERROR, f"Unexpected error log on import: {record.message}"
