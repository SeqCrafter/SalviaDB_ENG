"""Synchronous sequence-identification helpers for the Reflex background task."""

import os
import re
import subprocess
import tempfile
import time
from pathlib import Path
from typing import TypedDict


class MatchResult(TypedDict):
    rank: int
    species_name: str
    identity: float
    bit_score: float
    evalue: str
    its_genbank_id: str
    d1_genbank_id: str


class IdentificationResult(MatchResult):
    matches: list[MatchResult]


# Subject identifiers mirror the format stored by the internal reference
# database: <species key>_<orientation>_<ITS GenBank ID>_<D1 GenBank ID>.
# Orientation may be ++, +-, -+, or --.
_SIMULATED_MATCHES = [
    ("S.miltiorrhiza3_++_MW469062_MW493523", 100.00, 1613.0, "0.00e+00"),
    ("S.plectranthoides6_++_MW469098_MW493559", 99.66, 1600.0, "0.00e+00"),
    ("S.sinitica2_++_MW469143_MW493604", 99.54, 1596.0, "0.00e+00"),
    ("S.sinitica1_++_MW469142_MW493603", 99.54, 1596.0, "0.00e+00"),
    ("S.plectranthoides7_++_MW469099_MW493560", 99.54, 1594.0, "0.00e+00"),
]

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_DB_PATH = _PROJECT_ROOT / "database" / "salvia_db"
_TASKS = {"megablast", "blastn", "dc-megablast", "blastn-short"}
_MODES = {"direct", "all"}
_COMPLEMENT_TRANS = str.maketrans(
    "ACGTURYMKSWBDHVNacgturymkswbdhvn",
    "TGCAAYRKMWSVHDBNtgcaayrkmwsvhdbn",
)


def _parse_subject_id(subject_id: str) -> tuple[str, str, str]:
    """Extract the species name and both GenBank accessions from a subject ID."""
    try:
        species_key, accession_text = re.split(
            r"_[+-]{2}_", subject_id, maxsplit=1
        )
        its_genbank_id, d1_genbank_id = accession_text.split("_", maxsplit=1)
    except ValueError as exc:
        raise ValueError(f"Invalid internal subject ID: {subject_id}") from exc

    species_name = re.sub(r"\d+$", "", species_key)
    if species_name.startswith("S."):
        species_name = f"Salvia {species_name[2:]}"
    return species_name, its_genbank_id, d1_genbank_id


def simulate_salvia_sequence(
    its_sequence: str,
    d1_sequence: str,
    evalue: str,
    task: str,
    mode: str,
) -> IdentificationResult:
    """Simulate the synchronous sequence-identification pipeline.

    The sequence and algorithm arguments are accepted now so this function can
    later be replaced by the real BLAST implementation without changing the
    State event or the frontend contract.
    """
    # Materialize the inputs to mirror the validation/use performed by the real
    # pipeline and make the function's dependency on all five arguments clear.
    request = {
        "its_sequence": its_sequence.strip(),
        "d1_sequence": d1_sequence.strip(),
        "evalue": evalue.strip(),
        "task": task,
        "mode": mode,
    }
    if not request["its_sequence"] or not request["d1_sequence"]:
        raise ValueError("ITS and D1 sequences are required")

    time.sleep(10)

    matches: list[MatchResult] = []
    for rank, (subject_id, identity, bit_score, result_evalue) in enumerate(
        _SIMULATED_MATCHES, start=1
    ):
        species_name, its_genbank_id, d1_genbank_id = _parse_subject_id(subject_id)
        matches.append(
            {
                "rank": rank,
                "species_name": species_name,
                "identity": identity,
                "bit_score": bit_score,
                "evalue": result_evalue,
                "its_genbank_id": its_genbank_id,
                "d1_genbank_id": d1_genbank_id,
            }
        )

    best_match = matches[0]
    return {**best_match, "matches": matches}


def _parse_sequence(sequence_input: str) -> str:
    """Normalize pasted sequence text or FASTA content to a nucleotide string."""
    sequence_lines = [
        line.strip()
        for line in sequence_input.strip().splitlines()
        if line.strip() and not line.lstrip().startswith(">")
    ]
    sequence = "".join("".join(sequence_lines).split()).upper()
    if not sequence:
        raise ValueError("No valid nucleotide sequence could be parsed")
    return sequence


def _reverse_complement(sequence: str) -> str:
    return sequence.translate(_COMPLEMENT_TRANS)[::-1]


def _build_queries(its_sequence: str, d1_sequence: str, mode: str) -> list[tuple[str, str]]:
    if mode == "direct":
        return [("query_ITS_D1", its_sequence + d1_sequence)]
    return [
        ("query_ITS_D1_++", its_sequence + d1_sequence),
        ("query_ITS_D1_+-", its_sequence + _reverse_complement(d1_sequence)),
        ("query_ITS_D1_-+", _reverse_complement(its_sequence) + d1_sequence),
        ("query_ITS_D1_--", _reverse_complement(its_sequence) + _reverse_complement(d1_sequence)),
    ]


def _resolve_database_prefix(db_path: str | os.PathLike[str] | None) -> Path:
    configured_path = db_path or os.environ.get("SALVIADB_BLAST_DB") or _DEFAULT_DB_PATH
    database_prefix = Path(configured_path).expanduser().resolve()
    database_files = list(database_prefix.parent.glob(f"{database_prefix.name}.*"))
    if not database_files:
        raise FileNotFoundError(
            "BLAST database not found. Set SALVIADB_BLAST_DB to the makeblastdb database prefix."
        )
    return database_prefix


def _parse_blast_rows(tsv_path: Path) -> list[dict[str, str | float | int]]:
    rows: list[dict[str, str | float | int]] = []
    if not tsv_path.exists():
        return rows

    with tsv_path.open("r", encoding="utf-8") as result_file:
        for line in result_file:
            columns = line.rstrip("\n").split("\t")
            if len(columns) < 12:
                continue
            try:
                rows.append(
                    {
                        "qseqid": columns[0],
                        "sseqid": columns[1],
                        "pident": float(columns[2]),
                        "length": int(columns[3]),
                        "evalue": float(columns[10]),
                        "bitscore": float(columns[11]),
                    }
                )
            except ValueError:
                continue
    return rows


def identify_salvia_sequence(
    its_sequence: str,
    d1_sequence: str,
    evalue: str,
    task: str,
    mode: str,
    *,
    db_path: str | os.PathLike[str] | None = None,
    blastn_bin: str | None = None,
    threads: int = 4,
) -> IdentificationResult | None:
    """Run the real BLAST search and return up to five qualifying matches.

    A hit qualifies only when its aligned length covers at least 90% of the
    normalized ITS + D1 input length. Results are unique by subject and sorted
    by Bit-Score descending, E-value ascending, then Identity descending.
    """
    normalized_its = _parse_sequence(its_sequence)
    normalized_d1 = _parse_sequence(d1_sequence)
    query_length = len(normalized_its) + len(normalized_d1)

    if task not in _TASKS:
        raise ValueError(f"Unsupported BLAST task: {task}")
    if mode not in _MODES:
        raise ValueError(f"Unsupported concatenation mode: {mode}")
    try:
        evalue_number = float(evalue)
    except ValueError as exc:
        raise ValueError(f"Invalid E-value: {evalue}") from exc
    if evalue_number <= 0:
        raise ValueError("E-value must be greater than 0")

    database_prefix = _resolve_database_prefix(db_path)
    blastn_executable = blastn_bin or os.environ.get("SALVIADB_BLASTN_BIN", "blastn")
    query_records = _build_queries(normalized_its, normalized_d1, mode)

    with tempfile.TemporaryDirectory(prefix="salviadb_blast_") as temporary_dir:
        temporary_path = Path(temporary_dir)
        query_fasta = temporary_path / "query.fasta"
        output_tsv = temporary_path / "blast_results.tsv"

        with query_fasta.open("w", encoding="utf-8") as query_file:
            for query_id, query_sequence in query_records:
                query_file.write(f">{query_id}\n{query_sequence}\n")

        command = [
            blastn_executable,
            "-db",
            str(database_prefix),
            "-query",
            str(query_fasta),
            "-out",
            str(output_tsv),
            "-task",
            task,
            "-num_threads",
            str(threads),
            "-evalue",
            str(evalue_number),
            "-max_target_seqs",
            "100",
            "-outfmt",
            "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore",
        ]

        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"NCBI BLAST+ executable not found: {blastn_executable}"
            ) from exc
        if completed.returncode != 0:
            details = completed.stderr.strip() or "Unknown error"
            raise RuntimeError(f"blastn failed: {details}")

        blast_rows = _parse_blast_rows(output_tsv)

    minimum_alignment_length = query_length * 0.9
    qualified_rows = [
        row for row in blast_rows if int(row["length"]) >= minimum_alignment_length
    ]
    qualified_rows.sort(
        key=lambda row: (
            -float(row["bitscore"]),
            float(row["evalue"]),
            -float(row["pident"]),
        )
    )

    matches: list[MatchResult] = []
    seen_subjects: set[str] = set()
    for row in qualified_rows:
        subject_id = str(row["sseqid"])
        if subject_id in seen_subjects:
            continue
        seen_subjects.add(subject_id)
        try:
            species_name, its_genbank_id, d1_genbank_id = _parse_subject_id(subject_id)
        except ValueError:
            # A malformed internal subject cannot provide the required GenBank IDs.
            continue
        matches.append(
            {
                "rank": len(matches) + 1,
                "species_name": species_name,
                "identity": float(row["pident"]),
                "bit_score": float(row["bitscore"]),
                "evalue": f"{float(row['evalue']):.2e}",
                "its_genbank_id": its_genbank_id,
                "d1_genbank_id": d1_genbank_id,
            }
        )
        if len(matches) == 5:
            break

    if not matches:
        return None
    return {**matches[0], "matches": matches}
