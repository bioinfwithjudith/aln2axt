import argparse
import re
import sys
import time
from pathlib import Path
from typing import List, Tuple, Dict

# ---------- Small utils ----------

def sanitize_label(h: str) -> str:
    """Take first token of header, strip '>', keep safe chars for filenames."""
    token = h[1:].split()[0] if h.startswith('>') else h.split()[0]
    return re.sub(r'[^A-Za-z0-9._|\-]+', '_', token)

def pad_both_to_multiple_of_three(seqA: str, seqB: str) -> Tuple[str, str]:
    """Equalize lengths, then pad both so total length % 3 == 0."""
    if len(seqA) != len(seqB):
        if len(seqA) < len(seqB):
            seqA += "-" * (len(seqB) - len(seqA))
        else:
            seqB += "-" * (len(seqA) - len(seqB))
    r = len(seqA) % 3
    if r != 0:
        pad = 3 - r
        seqA += "-" * pad
        seqB += "-" * pad
    return seqA, seqB

# ---------- FASTA (2-seq) ----------

def read_fasta(path: Path) -> List[Tuple[str, str]]:
    recs: List[Tuple[str, str]] = []
    h, chunks = None, []
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            if line.startswith(">"):
                if h is not None:
                    recs.append((h, "".join(chunks)))
                h, chunks = line.strip(), []
            else:
                chunks.append(line.strip())
        if h is not None:
            recs.append((h, "".join(chunks)))
    return recs

    # ---- Concatenate all generated AXT files (sorted) ----
    combined_path = out_dir / "sequences.axt"
    if generated_axts:
        generated_axts = sorted(set(p.resolve() for p in generated_axts))
        with open(combined_path, "w") as out:
            for p in generated_axts:
                with open(p, "r") as inp:
                    out.write(inp.read())
        print(f"[OK] Concatenated {len(generated_axts)} AXT files -> {combined_path}")
    else:
        print("[WARN] No AXT files generated; skipping concatenation.")

    print("\n==== Conversion Timing ====")
    avg = (total / n_ok) if n_ok else 0.0
    print(f"Converted: {n_ok} files, total {total:.3f}s, avg {avg:.3f}s")
    print(f"Summary: {summary.resolve()}")


