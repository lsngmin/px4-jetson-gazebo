import logging, os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def configure_logging(level=logging.DEBUG, log_dir = "./log", filename = None):
    ######################################
    #                                    #
    #                                    #
    ######################################
    format_msg  = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    format_date = "%Y-%m-%d %H:%M:%S"

    # StreamHandler: 콘솔 출력용
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(format_msg, format_date))

    root = logging.getLogger()
    root.setLevel(level)

    # 기존 핸들러 교체
    if not root.handlers:
        root.addHandler(handler)
    else:
        root.handlers.clear()
        root.addHandler(handler)

    # 로그 디렉토리 생성

    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        root.warning(f"로그 디렉토리 생성 실패: {log_dir}, 오류: {e}")

    # 파일명 생성: 파라미터 filename 없으면 timestamp 사용
    ts = datetime.utcnow().strftime("%m%dT%H%M")
    if filename:
        log_filename = f"{filename}_{ts}.log"
    else:
        log_filename = f"log_{ts}.log"
    filepath = os.path.join(log_dir, log_filename)

    # RotatingFileHandler 설정: 5MB, 백업 3개
    try:

        fh = logging.handlers.RotatingFileHandler(
            filepath, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
        )
        fh.setLevel(level)
        fh.setFormatter(logging.Formatter(format_msg, format_date))
        root.addHandler(fh)
    except Exception as e:
        root.error(f"파일 핸들러 설정 실패: {filepath}, 오류: {e}")