from __future__ import annotations

from pathlib import Path

from deepagents.backends import CompositeBackend, FilesystemBackend, StateBackend
from deepagents.backends.protocol import (
    BackendProtocol,
    EditResult,
    GlobResult,
    GrepResult,
    LsResult,
    ReadResult,
    WriteResult,
)

from config import Settings, get_settings

NOTES_FILESYSTEM_ROOT = "/database_notes"
WRITE_NOT_ALLOWED_ERROR = "write not allowed"
EDIT_NOT_ALLOWED_ERROR = "edit not allowed"


class EmptyBackend(BackendProtocol):
    def ls(self, path: str) -> LsResult:
        del path
        return LsResult(entries=[])

    def read(self, file_path: str, offset: int = 0, limit: int = 2000) -> ReadResult:
        del file_path, offset, limit
        return ReadResult(error="file not found")

    def glob(self, pattern: str, path: str = "/") -> GlobResult:
        del pattern, path
        return GlobResult(matches=[])

    def grep(self, pattern: str, path: str | None = None, glob: str | None = None) -> GrepResult:
        del pattern, path, glob
        return GrepResult(matches=[])

    def write(self, file_path: str, content: str) -> WriteResult:
        del file_path, content
        return WriteResult(error=WRITE_NOT_ALLOWED_ERROR)

    def edit(
        self,
        file_path: str,
        old_string: str,
        new_string: str,
        replace_all: bool = False,
    ) -> EditResult:
        del file_path, old_string, new_string, replace_all
        return EditResult(error=EDIT_NOT_ALLOWED_ERROR)


class ReadOnlyFilesystemBackend(BackendProtocol):
    def __init__(self, *, notes_root: Path) -> None:
        self.notes_root = notes_root.resolve()
        self.backend = FilesystemBackend(
            root_dir=self.notes_root,
            virtual_mode=True,
        )

    def _normalize_path(self, path: str | None) -> str:
        if path in (None, "", "."):
            return NOTES_FILESYSTEM_ROOT
        return path if path.startswith("/") else f"/{path}"

    def ls(self, path: str) -> LsResult:
        try:
            return self.backend.ls(self._normalize_path(path))
        except ValueError as exc:
            return LsResult(error=str(exc), entries=[])

    def read(self, file_path: str, offset: int = 0, limit: int = 2000) -> ReadResult:
        try:
            return self.backend.read(
                self._normalize_path(file_path),
                offset=offset,
                limit=limit,
            )
        except ValueError as exc:
            return ReadResult(error=str(exc))

    def glob(self, pattern: str, path: str = NOTES_FILESYSTEM_ROOT) -> GlobResult:
        try:
            return self.backend.glob(
                pattern,
                path=self._normalize_path(path),
            )
        except ValueError as exc:
            return GlobResult(error=str(exc), matches=[])

    def grep(self, pattern: str, path: str | None = None, glob: str | None = None) -> GrepResult:
        try:
            return self.backend.grep(
                pattern,
                path=self._normalize_path(path),
                glob=glob,
            )
        except ValueError as exc:
            return GrepResult(error=str(exc), matches=[])

    def write(self, file_path: str, content: str) -> WriteResult:
        del file_path, content
        return WriteResult(error=WRITE_NOT_ALLOWED_ERROR)

    def edit(
        self,
        file_path: str,
        old_string: str,
        new_string: str,
        replace_all: bool = False,
    ) -> EditResult:
        del file_path, old_string, new_string, replace_all
        return EditResult(error=EDIT_NOT_ALLOWED_ERROR)


def build_notes_backend(
    *,
    settings: Settings | None = None,
) -> CompositeBackend:
    runtime_settings = settings or get_settings()
    repo_root = Path(__file__).resolve().parents[2]
    if Path(runtime_settings.database_notes_path).is_absolute():
        notes_root = Path(runtime_settings.database_notes_path).resolve()
    else:
        notes_root = (repo_root / runtime_settings.database_notes_path).resolve()

    return CompositeBackend(
        default=StateBackend(),
        routes={
            "/database_notes": ReadOnlyFilesystemBackend(
                notes_root=notes_root,
            ),
            "/database_notes/": ReadOnlyFilesystemBackend(
                notes_root=notes_root,
            ),
        },
    )
