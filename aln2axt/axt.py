import argparse
import re
import sys
import time
from pathlib import Path
from typing import List, Tuple, Dict

# ---------- Core ----------

def load_alignment(path: Path, forced: str = "auto") -> List[Tuple[str, str]]:
    """Return [(label, aligned_seq)] for a pairwise alignment."""
    fmt = forced
    if fmt == "auto":
        if path.suffix.lower() == ".aln":
            fmt = "clustal"
        else:
            with open(path) as f:
                for line in f:
                    if line.strip():
                        fmt = "clustal" if (line.upper().startswith("CLUSTAL") or line.startswith("MUSCLE")) else "fasta"
                        break
    if fmt == "clustal":
        recs = parse_clustal_pair(path)
        return [(sanitize_label(n), s) for n, s in recs]
    elif fmt == "fasta":
        recs = read_fasta(path)
        if len(recs) < 2:
            raise ValueError(f"FASTA must contain at least 2 records: {path}")
        (h1, s1), (h2, s2) = recs[0], recs[1]
        return [(sanitize_label(h1), s1), (sanitize_label(h2), s2)]
    else:
        raise ValueError(f"Unknown format: {forced}")

def write_axt(axt_path: Path, nameA: str, nameB: str, seqA: str, seqB: str) -> None:
    axt_path.parent.mkdir(parents=True, exist_ok=True)
    with open(axt_path, "w") as out:
        out.write(f"{nameA}_vs_{nameB}\n{seqA}\n{seqB}\n\n")


