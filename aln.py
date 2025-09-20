import argparse
import re
import sys
import time
from pathlib import Path
from typing import List, Tuple, Dict


# ---------- CLUSTAL (pairwise) ----------

def parse_clustal_pair(path: Path) -> List[Tuple[str, str]]:
    seqs: Dict[str, List[str]] = {}
    order: List[str] = []
    with open(path) as f:
        lines = f.readlines()

    i = 0
    # Skip headers like "CLUSTAL ..." or "MUSCLE ..."
    while i < len(lines) and (not lines[i].strip() or lines[i].upper().startswith("CLUSTAL") or lines[i].startswith("MUSCLE")):
        i += 1

    name_chunk_re = re.compile(r'^(\S+)\s+([A-Za-z\-\.\*]+)')

    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue
        while i < len(lines) and lines[i].strip():
            m = name_chunk_re.match(lines[i])
            if m:
                name, chunk = m.group(1), m.group(2)
                if name not in seqs:
                    seqs[name] = []
                    order.append(name)
                seqs[name].append(chunk)
            i += 1
        while i < len(lines) and not lines[i].strip():
            i += 1

    if len(order) < 2:
        raise ValueError(f"Expected ≥2 sequences in CLUSTAL file: {path}")
    out = [(nm, "".join(seqs[nm])) for nm in order]
    return out[:2]


