import argparse
import re
import sys
import time
from pathlib import Path
from typing import List, Tuple, Dict
from aln2axt import utils, aln, axt

def main():
    ap = argparse.ArgumentParser(
        description="Recursively convert pairwise alignments (.aln CLUSTAL or 2-seq FASTA) to AXT, "
                    "padding to codon length (multiple of 3). Records conversion time and concatenates all AXT."
    )
    ap.add_argument("--input", required=True, help="Alignment file OR directory (recursively scanned).")
    ap.add_argument("--out_dir", required=True, help="Where to write .axt, timing_summary.tsv, and all_pairs_combined.axt")
    ap.add_argument("--format", choices=["auto","clustal","fasta"], default="auto", help="Force input format (default: auto)")
    ap.add_argument("--exts", nargs="+", default=[".aln",".fa",".fna",".fasta"], help="Extensions to scan recursively if --input is a directory")
    args = ap.parse_args()

    in_path = Path(args.input)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Build list of inputs (recurse if directory)
    if in_path.is_dir():
        inputs: List[Path] = []
        for ext in args.exts:
            inputs.extend(sorted(in_path.rglob(f"*{ext}")))
        if not inputs:
            sys.exit(f"No input files with {args.exts} under {in_path}")
    else:
        inputs = [in_path]

    summary = out_dir / "timing_summary.tsv"
    with open(summary, "w") as sf:
        sf.write("input_file\taxt_file\tconvert_seconds\tstatus\tnote\n")

    total, n_ok = 0.0, 0
    generated_axts: List[Path] = []

    for aln in inputs:
        status, note = "OK", ""
        t0 = time.monotonic()
        try:
            recs = load_alignment(aln, forced=args.format)
            (nameA, sA), (nameB, sB) = recs[0], recs[1]
            sA2, sB2 = pad_both_to_multiple_of_three(sA, sB)

            if in_path.is_dir():
                rel = aln.relative_to(in_path)
                axt_path = (out_dir / rel).with_suffix(".axt")
            else:
                axt_path = (out_dir / aln.name).with_suffix(".axt")

            write_axt(axt_path, nameA, nameB, sA2, sB2)
            generated_axts.append(axt_path)

            dt = time.monotonic() - t0
            total += dt; n_ok += 1
            print(f"[OK] {aln} -> {axt_path} ({dt:.3f}s)")
            with open(summary, "a") as sf:
                sf.write(f"{aln}\t{axt_path}\t{dt:.6f}\t{status}\t{note}\n")
        except Exception as e:
            dt = time.monotonic() - t0
            status, note = "FAIL", str(e).replace("\n"," ")
            print(f"[FAIL] {aln}: {note}")
            with open(summary, "a") as sf:
                sf.write(f"{aln}\t\t\t{status}\t{note}\n")


