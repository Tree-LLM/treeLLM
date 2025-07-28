"""
각 단계(run 함수)들을 한 번에 가져오기 위한 허브.
"""
from .split import run as split          # Step 1
from .build import run as build          # Step 2
from .fuse import run as fuse            # Step 3
from .audit import run as audit          # Step 4
from .edit_pass1 import run as edit_pass1  # Step 5
from .summarize import run as summarize    # Step 5-b
from .review import run as review        # Step 6
from .edit_pass2 import run as edit_pass2  # Step 7
from .finalize import run as finalize    # Step 8

__all__ = [
    "split", "build", "fuse", "audit",
    "edit_pass1", "summarize", "review",
    "edit_pass2", "finalize",
]
