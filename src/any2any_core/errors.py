"""Error taxonomy (docs/06 §6). Every failure maps to one of these codes."""

from __future__ import annotations


class Any2AnyError(Exception):
    code = "E_INTERNAL"
    title = "Internal error"

    def __init__(self, detail: str = "", *, hint: str | None = None, cause: str | None = None):
        self.detail = detail
        self.hint = hint
        self.cause = cause
        super().__init__(f"{self.code}: {detail}" if detail else self.code)

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "title": self.title,
            "detail": self.detail,
            "hint": self.hint,
            "cause": self.cause,
        }


class UsageError(Any2AnyError):
    code = "E_USAGE"
    title = "Bad usage"


class UnsupportedInput(Any2AnyError):
    code = "E_UNSUPPORTED_INPUT"
    title = "Unsupported input type"


class UnsupportedPair(Any2AnyError):
    code = "E_UNSUPPORTED_PAIR"
    title = "No conversion path"


class UnsupportedDirection(Any2AnyError):
    code = "E_UNSUPPORTED_DIRECTION"
    title = "Format not writable"


class EmptyFile(Any2AnyError):
    code = "E_EMPTY_FILE"
    title = "Empty file"


class ExtensionMismatch(Any2AnyError):
    code = "E_EXTENSION_MISMATCH"
    title = "Extension does not match content"


class ParseError(Any2AnyError):
    code = "E_PARSE"
    title = "Malformed input"


class ConflictOutput(Any2AnyError):
    code = "E_CONFLICT_OUTPUT"
    title = "Output exists"


class PermissionDenied(Any2AnyError):
    code = "E_PERMISSION"
    title = "Permission denied"


class DiskFull(Any2AnyError):
    code = "E_DISK_FULL"
    title = "Disk full"


class MissingEngine(Any2AnyError):
    code = "E_MISSING_ENGINE"
    title = "Missing requirement"


class EngineFailed(Any2AnyError):
    code = "E_ENGINE_FAILED"
    title = "Conversion step failed"


class TimeoutError_(Any2AnyError):
    code = "E_TIMEOUT"
    title = "Step timed out"


class Cancelled(Any2AnyError):
    code = "E_CANCELLED"
    title = "Cancelled"


class PlanFailed(Any2AnyError):
    code = "E_PLAN_FAILED"
    title = "All routes failed"


class InternalError(Any2AnyError):
    code = "E_INTERNAL"
    title = "Unexpected error"


class Warning_:
    def __init__(self, code: str, message: str, data: dict | None = None):
        self.code = code
        self.message = message
        self.data = data or {}

    def to_dict(self) -> dict:
        return {"code": self.code, "message": self.message, "data": self.data}


class Error_:
    """Serializable error payload for Result/Plan (no exception instance)."""

    def __init__(self, code: str, title: str, detail: str = "", hint: str | None = None, cause: str | None = None):
        self.code = code
        self.title = title
        self.detail = detail
        self.hint = hint
        self.cause = cause

    @classmethod
    def from_exc(cls, exc: Exception) -> Error_:
        if isinstance(exc, Any2AnyError):
            return cls(exc.code, exc.title, exc.detail, exc.hint, exc.cause or type(exc).__name__)
        return cls("E_INTERNAL", "Unexpected error", str(exc), cause=type(exc).__name__)

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "title": self.title,
            "detail": self.detail,
            "hint": self.hint,
            "cause": self.cause,
        }


# Warning codes (docs/06 §6)
W_LOSSY = "W_LOSSY"
W_CHAINED = "W_CHAINED"
W_EXTENSION_MISMATCH_ACCEPTED = "W_EXTENSION_MISMATCH_ACCEPTED"
W_PARTIAL_METADATA = "W_PARTIAL_METADATA"
W_LARGE_FILE_MEMORY = "W_LARGE_FILE_MEMORY"
W_DEGRADED_OUTPUT = "W_DEGRADED_OUTPUT"
