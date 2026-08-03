import json
import socket
import sys
from pathlib import Path
from typing import Callable


SUPPORTED_SUFFIXES = {".docx", ".pdf"}


def _apply_resource_limits(
    max_memory_mb: int,
    max_cpu_seconds: int,
) -> None:
    import resource

    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

    current_soft, current_hard = resource.getrlimit(
        resource.RLIMIT_NOFILE
    )
    del current_soft
    file_limit = (
        64
        if current_hard == resource.RLIM_INFINITY
        else min(64, current_hard)
    )
    resource.setrlimit(
        resource.RLIMIT_NOFILE,
        (file_limit, file_limit),
    )

    cpu_hard_limit = max_cpu_seconds + 1
    _current_cpu_soft, current_cpu_hard = resource.getrlimit(
        resource.RLIMIT_CPU
    )
    if current_cpu_hard != resource.RLIM_INFINITY:
        cpu_hard_limit = min(cpu_hard_limit, current_cpu_hard)
    cpu_soft_limit = min(max_cpu_seconds, cpu_hard_limit)
    resource.setrlimit(
        resource.RLIMIT_CPU,
        (cpu_soft_limit, cpu_hard_limit),
    )

    if sys.platform.startswith("linux"):
        memory_limit = max_memory_mb * 1024 * 1024
        _current_memory_soft, current_memory_hard = resource.getrlimit(
            resource.RLIMIT_AS
        )
        if current_memory_hard != resource.RLIM_INFINITY:
            memory_limit = min(memory_limit, current_memory_hard)
        resource.setrlimit(
            resource.RLIMIT_AS,
            (memory_limit, memory_limit),
        )


def _load_reader(suffix: str) -> Callable[..., str]:
    if suffix == ".pdf":
        from resume_reader import read_pdf_resume

        return read_pdf_resume
    if suffix == ".docx":
        from docx_reader import read_docx_resume

        return read_docx_resume
    raise ValueError("Unsupported resume type.")


def _disable_network_access() -> None:
    def blocked(*_args, **_kwargs):
        raise OSError("Network access is disabled in the parser worker.")

    socket.socket = blocked
    socket.create_connection = blocked
    socket.getaddrinfo = blocked


def parse_document(
    file_path: Path,
    suffix: str,
    max_input_bytes: int,
    max_text_characters: int,
) -> str:
    if (
        suffix not in SUPPORTED_SUFFIXES
        or not file_path.is_absolute()
        or file_path.suffix.casefold() != suffix
        or not file_path.is_file()
        or file_path.stat().st_size > max_input_bytes
    ):
        raise ValueError("Invalid parser input.")

    reader = _load_reader(suffix)
    _disable_network_access()
    text = reader(
        str(file_path),
        max_characters=max_text_characters,
    )
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Resume contains no readable text.")
    if len(text) > max_text_characters:
        raise ValueError("Resume text exceeds the processing limit.")
    return text


def _write_payload(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False))
    sys.stdout.flush()


def main(arguments: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if arguments is None else arguments)
    if len(arguments) != 6:
        _write_payload({"status": "unavailable"})
        return 3

    file_name, suffix, *raw_limits = arguments
    try:
        max_input_bytes, max_text_characters, max_memory_mb, max_cpu_seconds = (
            int(value) for value in raw_limits
        )
        if min(
            max_input_bytes,
            max_text_characters,
            max_memory_mb,
            max_cpu_seconds,
        ) < 1:
            raise ValueError("Limits must be positive.")
        _apply_resource_limits(max_memory_mb, max_cpu_seconds)
    except (ImportError, OSError, TypeError, ValueError):
        _write_payload({"status": "unavailable"})
        return 3

    try:
        text = parse_document(
            Path(file_name),
            suffix.casefold(),
            max_input_bytes,
            max_text_characters,
        )
    except MemoryError:
        _write_payload({"status": "unavailable"})
        return 3
    except Exception:
        _write_payload({"status": "invalid"})
        return 2

    _write_payload({"status": "ok", "text": text})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
