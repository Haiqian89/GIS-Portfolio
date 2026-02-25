from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime


PROJECT_DIR = Path(r"D:\Python_Projects\SchedulerDemo")

# 你要自动整理的“收件箱”目录（改成你自己的）
INBOX_DIR = Path(r"D:\python\inbox")

# 归档输出目录
ARCHIVE_DIR = Path(r"D:\python\archive")

# 日志目录（放在项目里更专业）
LOG_DIR = PROJECT_DIR / "logs"
LOG_FILE = LOG_DIR / "scheduler_demo.log"


EXT_MAP = {
    "pdf": "PDF",
    "png": "Images",
    "jpg": "Images",
    "jpeg": "Images",
    "gif": "Images",
    "xlsx": "Excel",
    "xls": "Excel",
    "csv": "CSV",
    "txt": "Text",
    "zip": "Zip",
}


def setup_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 防止 VS Code 多次运行重复添加 handler
    if logger.handlers:
        return

    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=1_000_000, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(fmt)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)
    console_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def ensure_dirs() -> None:
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)


def classify(file_path: Path) -> str:
    ext = file_path.suffix.lower().lstrip(".")
    return EXT_MAP.get(ext, "Other")


def move_file(src: Path, dst_dir: Path) -> Path:
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / src.name

    # 如果重名，就加时间戳避免覆盖
    if dst.exists():
        stem = src.stem
        suffix = src.suffix
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dst = dst_dir / f"{stem}_{ts}{suffix}"

    src.rename(dst)
    return dst


def run_job() -> int:
    ensure_dirs()
    logging.info("Job started. inbox=%s", INBOX_DIR)

    moved = 0
    failed = 0

    for p in INBOX_DIR.iterdir():
        if not p.is_file():
            continue

        category = classify(p)
        target_dir = ARCHIVE_DIR / category

        try:
            new_path = move_file(p, target_dir)
            moved += 1
            logging.info("Moved: %s -> %s", p.name, new_path)
        except Exception:
            failed += 1
            logging.exception("Failed to move: %s", p)

    logging.info("Job finished. moved=%d failed=%d", moved, failed)
    return 0 if failed == 0 else 1


def main() -> int:
    setup_logging()
    logging.info("Task started")
    try:
        code = run_job()
        logging.info("Task finished (exit_code=%d)", code)
        return code
    except Exception:
        logging.exception("Task crashed")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
