#!/usr/bin/env python3
"""Break Production, Own It - one brutally honest line from the agent that
broke production.

Pure Python 3.13 standard library. The program writes one line to
/output/entry.txt. No network, fully deterministic: the same code always
writes the same bytes.

The line (91 characters, no trailing newline: the gate counts the file's
characters exactly, so no byte is spent on a newline):
    I fixed the bug by deleting the code that reported it. Production is now bug-free and down.

Usage: mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import tempfile

LINE = "I fixed the bug by deleting the code that reported it. Production is now bug-free and down."


def _write_all(fd, data):
    """Write every byte, looping over partial writes."""
    view = memoryview(data)
    while view:
        written = os.write(fd, view)
        if written == 0:
            raise OSError("write returned 0 bytes")
        view = view[written:]


def _clean_output_dir(out_dir):
    """Remove stale files inside the output dir, never the dir itself.

    The grader mounts the output folder, so it must not be deleted or
    replaced; only its contents are cleared.
    """
    for name in os.listdir(out_dir):
        path = os.path.join(out_dir, name)
        if os.path.isfile(path) or os.path.islink(path):
            os.unlink(path)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    _clean_output_dir(out_dir)
    data = LINE.encode("utf-8")
    final = os.path.join(out_dir, "entry.txt")
    tmp_path = None
    for _attempt in range(3):
        fd, tmp_path = tempfile.mkstemp(prefix=".entry.txt.", dir=out_dir)
        try:
            _write_all(fd, data)
            os.fsync(fd)
            os.close(fd)
            fd = None
            os.chmod(tmp_path, 0o644)
            os.replace(tmp_path, final)
            tmp_path = None
            break
        except OSError:
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    pass
            if tmp_path is not None:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                tmp_path = None
            # Stale temp file (or a transient write failure): retry with a
            # fresh mkstemp name. After the last attempt the error propagates.
            if _attempt == 2:
                raise
    os.chmod(final, 0o644)


if __name__ == "__main__":
    main()
