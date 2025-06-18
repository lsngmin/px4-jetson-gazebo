import logging
import re
import pytest
from logging_config import configure_logging

@pytest.fixture(autouse=True)
def restore_root_handlers():
    """
    테스트 전에 root.handlers 상태를 그대로 두고,
    테스트 후에 원상 복구만 수행합니다.
    configure_logging이 내부에서 clear()를 호출하므로, 미리 지우지 않아도 됩니다.
    """
    root = logging.getLogger()
    prev_handlers = list(root.handlers)
    prev_level = root.level
    try:
        yield
    finally:
        # 테스트 후 원상 복구
        root.handlers.clear()
        root.setLevel(prev_level)
        for h in prev_handlers:
            root.addHandler(h)

def __test_configure_logging_sets_level_and_handler():
    # 테스트: __test_configure_logging_sets_level_and_handler
    # 설명:
    #   - 루트 로거(root)의 레벨을 전달된 level로 설정하는지 확인.
    #   - 기존 핸들러가 있든 없든, 호출 후에는 StreamHandler가 하나만 남도록 초기화하는지 확인.
    # 검증 포인트:
    #   1) root.level == level
    #   2) len(root.handlers) == 1
    #   3) handler 타입이 logging.StreamHandler 인지
    #   4) handler.formatter._fmt == "[%(asctime)s][%(name)s][%(levelname)s] %(message)s"
    #      handler.formatter.datefmt == "%Y-%m-%d %H:%M:%S"
    # 실제 로그 출력 예시:
    #   >>> configure_logging(level=logging.DEBUG)
    #   >>> logging.getLogger().debug("디버그 메시지")
    #   [2025-06-13 23:45:01][root][DEBUG] 디버그 메시지

    #####################################################
    root = logging.getLogger()

    configure_logging(level=logging.DEBUG)
    assert root.level == logging.DEBUG

    assert len(root.handlers) == 1
    handler = root.handlers[0]
    assert isinstance(handler, logging.StreamHandler)

    fmt = handler.formatter._fmt
    datefmt = handler.formatter.datefmt
    assert fmt == "[%(asctime)s][%(name)s][%(levelname)s] %(message)s"
    assert datefmt == "%Y-%m-%d %H:%M:%S"
    #####################################################
def __test_configure_logging_replaces_existing_handlers():
    # 테스트: test_configure_logging_replaces_existing_handlers
    # 설명:
    #   - 기존에 root.handlers에 여러 핸들러(StreamHandler, FileHandler 등)가 붙어 있더라도,
    #     configure_logging 호출 시 기존 핸들러를 모두 제거하고 새 StreamHandler 하나만 남기는지 확인.
    # 검증 포인트:
    #   1) 호출 전 root.handlers에 dummy 핸들러가 여러 개 있을 수 있음.
    #   2) configure_logging 후 len(root.handlers) == 1
    #   3) root.level == 설정한 level

    #####################################################
    root = logging.getLogger()

    dummy = logging.StreamHandler()
    root.addHandler(dummy)
    assert root.handlers

    configure_logging(level=logging.WARNING)
    assert len(root.handlers) == 1
    handler = root.handlers[0]
    assert isinstance(handler, logging.StreamHandler)
    assert root.level == logging.WARNING
    #####################################################
def test_log_output_format_with_capsys(capsys):
    # 테스트: test_log_output_format_with_capsys
    # 설명:
    #   - configure_logging(level=logging.INFO) 호출 후, INFO 레벨 메시지를 출력했을 때
    #     콘솔(stderr)에 "[YYYY-MM-DD HH:MM:SS][로거이름][레벨] 메시지" 형태로 찍히는지 확인.
    # 검증 포인트:
    #   - 캡처된 stderr 내용이 정규식 패턴
    #     r"^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]\[root\]\[INFO\] unit test message$"
    #     에 매칭되는지
    # 실제 로그 출력 예시:
    #   >>> configure_logging(level=logging.INFO)
    #   >>> logging.getLogger().info("unit test message")
    #   [2025-06-13 23:45:01][root][INFO] unit test message

    #####################################################
    root = logging.getLogger()
    configure_logging(level=logging.INFO)

    root.info("unit test message")

    captured = capsys.readouterr()
    out = captured.err.strip()
    pattern = r"^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]\[root\]\[INFO\] unit test message$"
    assert re.match(pattern, out), f"로그 포맷이 예상과 다릅니다: {out}"
    #####################################################
@pytest.mark.parametrize("level,should_output", [
    (logging.ERROR, False),
    (logging.INFO, True),
    (logging.DEBUG, True),
])
    #####################################################
def test_log_level_filtering(capsys, level, should_output):
    # 테스트: test_log_level_filtering
    # 설명:
    #   - 설정한 level에 따라 INFO 메시지 출력 여부가 달라지는지 확인.
    #     예: level=ERROR면 INFO 메시지는 출력되지 않아야 함.
    # 검증 포인트:
    #   - level=logging.ERROR → INFO 메시지 출력 안 됨
    #   - level=logging.INFO  → INFO 메시지 출력 됨
    #   - level=logging.DEBUG → INFO 메시지 출력 됨
    # 실제 로그 출력 예시:
    #   >>> configure_logging(level=logging.ERROR)
    #   >>> logging.getLogger().info("filter test")
    #   # 출력 없음
    #   >>> configure_logging(level=logging.INFO)
    #   >>> logging.getLogger().info("filter test")
    #   [2025-06-13 23:45:01][root][INFO] filter test

    #####################################################
    root = logging.getLogger()
    configure_logging(level=level)
    root.info("filter test")

    captured = capsys.readouterr()
    text = captured.err.strip()
    if should_output:
        assert "filter test" in text
    else:
        assert text == ""
    #####################################################