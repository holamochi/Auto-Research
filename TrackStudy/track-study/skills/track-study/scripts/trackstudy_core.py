#!/usr/bin/env python3
"""Shared TrackStudy loading, validation, and deterministic build helpers."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


STABLE_ID = re.compile(r"^[a-z0-9][a-z0-9._:-]*$")
SHA256 = re.compile(r"^[a-f0-9]{64}$")
STATUSES = {"planned", "in-progress", "done", "blocked", "registered"}
RELATION_TYPES = {"depends_on", "relates_to"}
RELATION_KINDS = {"evolution", "variant", "comparison", "evaluation", "transfer"}
CHANGE_KINDS = {
    "origin",
    "primary",
    "secondary",
    "comparison",
    "implementation-basis",
    "evaluation-input",
    "protocol",
}
EVIDENCE_TYPES = {"local", "manifest", "external", "remote-summary"}
CLAIM_POLICIES = {"citable", "context-only", "not-citable"}


class ContractError(ValueError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"{path} must contain a JSON object")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_id(value: Any, label: str) -> str:
    if not isinstance(value, str) or not STABLE_ID.fullmatch(value):
        raise ContractError(f"{label} must match {STABLE_ID.pattern!r}: {value!r}")
    return value


def require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{label} must be a non-empty string")
    return value.strip()


def resolve_inside(root: Path, relative: str, label: str) -> Path:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ContractError(f"{label} must be a non-empty relative path")
    target = (root / relative).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise ContractError(f"{label} leaves the study root: {relative}") from exc
    return target


def validate_evidence(item: Any, root: Path, label: str) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise ContractError(f"{label} must be an object")
    evidence_id = require_id(item.get("id"), f"{label}.id")
    evidence_type = item.get("type")
    if evidence_type not in EVIDENCE_TYPES:
        raise ContractError(f"{label}.type must be one of {sorted(EVIDENCE_TYPES)}")
    policy = item.get("claimPolicy")
    if policy not in CLAIM_POLICIES:
        raise ContractError(f"{label}.claimPolicy must be one of {sorted(CLAIM_POLICIES)}")
    normalized = {"id": evidence_id, "type": evidence_type, "claimPolicy": policy}
    if evidence_type in {"local", "manifest"}:
        path_value = item.get("path")
        path = resolve_inside(root, path_value, f"{label}.path")
        if not path.is_file():
            raise ContractError(f"{label}.path does not exist: {path_value}")
        lines = path.read_text(encoding="utf-8").splitlines()
        line_start = item.get("lineStart")
        line_end = item.get("lineEnd")
        if not isinstance(line_start, int) or not isinstance(line_end, int):
            raise ContractError(f"{label} requires integer lineStart and lineEnd")
        if line_start < 1 or line_end < line_start or line_end > len(lines):
            raise ContractError(
                f"{label} invalid line range {line_start}-{line_end} for {len(lines)} lines"
            )
        source_sha = item.get("sourceSha256")
        current_sha = sha256_file(path)
        if not isinstance(source_sha, str) or not SHA256.fullmatch(source_sha):
            raise ContractError(f"{label}.sourceSha256 must be 64 lowercase hexadecimal characters")
        if source_sha != current_sha:
            raise ContractError(f"{label}.sourceSha256 is stale for {path_value}")
        normalized.update(
            {
                "path": path_value,
                "lineStart": line_start,
                "lineEnd": line_end,
                "sourceSha256": source_sha,
            }
        )
    else:
        if policy == "citable":
            raise ContractError(f"{label}: external or remote-summary evidence cannot be citable")
        url = item.get("url")
        if url is not None:
            if not isinstance(url, str) or not url.startswith("https://"):
                raise ContractError(f"{label}.url must use HTTPS")
            normalized["url"] = url
        note = item.get("note")
        if note is not None:
            normalized["note"] = require_text(note, f"{label}.note")
    return normalized


def load_study(root: Path) -> tuple[dict[str, Any], list[Path]]:
    root = root.resolve()
    study_path = root / "study.json"
    study = read_json(study_path)
    if study.get("schemaVersion") != 1:
        raise ContractError("study.json schemaVersion must be 1")
    project = study.get("project")
    if not isinstance(project, dict):
        raise ContractError("study.json project must be an object")
    normalized_project = {
        "id": require_id(project.get("id"), "project.id"),
        "title": require_text(project.get("title"), "project.title"),
        "description": require_text(project.get("description"), "project.description"),
        "snapshotDate": require_text(project.get("snapshotDate"), "project.snapshotDate"),
    }
    tracks = study.get("tracks")
    if not isinstance(tracks, list) or not tracks:
        raise ContractError("study.json tracks must be a non-empty array")
    normalized_tracks = []
    track_ids: set[str] = set()
    for index, raw in enumerate(tracks):
        label = f"tracks[{index}]"
        if not isinstance(raw, dict):
            raise ContractError(f"{label} must be an object")
        track_id = require_id(raw.get("id"), f"{label}.id")
        if track_id in track_ids:
            raise ContractError(f"duplicate track ID: {track_id}")
        track_ids.add(track_id)
        color = raw.get("color", "#58a487")
        if not isinstance(color, str) or not re.fullmatch(r"#[a-fA-F0-9]{6}", color):
            raise ContractError(f"{label}.color must be a six-digit hex color")
        normalized_tracks.append(
            {"id": track_id, "label": require_text(raw.get("label"), f"{label}.label"), "color": color}
        )

    experiment_paths = sorted((root / "experiments").glob("*.json"))
    if not experiment_paths:
        raise ContractError("experiments/ must contain at least one JSON file")
    experiments: dict[str, dict[str, Any]] = {}
    evidence_by_id: dict[str, dict[str, Any]] = {}
    for path in experiment_paths:
        payload = read_json(path)
        if payload.get("schemaVersion") != 1:
            raise ContractError(f"{path}: schemaVersion must be 1")
        raw_experiments = payload.get("experiments")
        if not isinstance(raw_experiments, dict) or not raw_experiments:
            raise ContractError(f"{path}: experiments must be a non-empty object")
        for experiment_id, raw in raw_experiments.items():
            label = f"{path.name}:{experiment_id}"
            require_id(experiment_id, f"{label}.id")
            if experiment_id in experiments:
                raise ContractError(f"duplicate experiment ID: {experiment_id}")
            if not isinstance(raw, dict):
                raise ContractError(f"{label} must be an object")
            track = raw.get("track")
            if track not in track_ids:
                raise ContractError(f"{label}.track references unknown track {track!r}")
            status = raw.get("status")
            if status not in STATUSES:
                raise ContractError(f"{label}.status must be one of {sorted(STATUSES)}")
            brief = raw.get("brief")
            detail = raw.get("detail")
            if not isinstance(brief, dict) or not isinstance(detail, dict):
                raise ContractError(f"{label} requires brief and detail objects")
            changes = detail.get("changes")
            caveats = detail.get("caveats")
            if not isinstance(changes, list) or not changes:
                raise ContractError(f"{label}.detail.changes must be a non-empty array")
            if not isinstance(caveats, list) or not caveats:
                raise ContractError(f"{label}.detail.caveats must be a non-empty array")
            normalized_changes = []
            for change_index, change in enumerate(changes):
                change_label = f"{label}.detail.changes[{change_index}]"
                if not isinstance(change, dict):
                    raise ContractError(f"{change_label} must be an object")
                kind = change.get("kind")
                if kind not in CHANGE_KINDS:
                    raise ContractError(f"{change_label}.kind must be one of {sorted(CHANGE_KINDS)}")
                predecessor = change.get("from")
                if kind == "origin" and predecessor is not None:
                    raise ContractError(f"{change_label}: origin requires from=null")
                if kind != "origin" and not isinstance(predecessor, str):
                    raise ContractError(f"{change_label}: non-origin change requires a predecessor ID")
                normalized_changes.append(
                    {
                        "from": predecessor,
                        "kind": kind,
                        "summary": require_text(change.get("summary"), f"{change_label}.summary"),
                    }
                )
            raw_evidence = raw.get("evidence")
            if not isinstance(raw_evidence, list) or not raw_evidence:
                raise ContractError(f"{label}.evidence must be a non-empty array")
            normalized_evidence = []
            for evidence_index, item in enumerate(raw_evidence):
                evidence = validate_evidence(item, root, f"{label}.evidence[{evidence_index}]")
                if evidence["id"] in evidence_by_id:
                    raise ContractError(f"duplicate evidence ID: {evidence['id']}")
                evidence_by_id[evidence["id"]] = evidence
                normalized_evidence.append(evidence)
            experiments[experiment_id] = {
                "id": experiment_id,
                "number": require_text(raw.get("number"), f"{label}.number"),
                "title": require_text(raw.get("title"), f"{label}.title"),
                "track": track,
                "status": status,
                "brief": {
                    "experiment": require_text(brief.get("experiment"), f"{label}.brief.experiment"),
                    "change": require_text(brief.get("change"), f"{label}.brief.change"),
                    "conclusion": require_text(brief.get("conclusion"), f"{label}.brief.conclusion"),
                },
                "detail": {
                    "experiment": require_text(detail.get("experiment"), f"{label}.detail.experiment"),
                    "changes": normalized_changes,
                    "conclusion": require_text(detail.get("conclusion"), f"{label}.detail.conclusion"),
                    "caveats": [
                        require_text(value, f"{label}.detail.caveats[{index}]")
                        for index, value in enumerate(caveats)
                    ],
                },
                "evidence": normalized_evidence,
            }

    for experiment in experiments.values():
        for change in experiment["detail"]["changes"]:
            predecessor = change["from"]
            if predecessor is not None and predecessor not in experiments:
                raise ContractError(
                    f"experiment {experiment['id']} change references unknown predecessor {predecessor}"
                )
            if predecessor == experiment["id"]:
                raise ContractError(f"experiment {experiment['id']} cannot reference itself")

    relations = study.get("relations")
    if not isinstance(relations, list):
        raise ContractError("study.json relations must be an array")
    normalized_relations = []
    relation_ids: set[str] = set()
    primary_incoming: dict[str, str] = {}
    for index, raw in enumerate(relations):
        label = f"relations[{index}]"
        if not isinstance(raw, dict):
            raise ContractError(f"{label} must be an object")
        relation_id = require_id(raw.get("id"), f"{label}.id")
        if relation_id in relation_ids:
            raise ContractError(f"duplicate relation ID: {relation_id}")
        relation_ids.add(relation_id)
        predecessor = raw.get("from")
        successor = raw.get("to")
        if predecessor not in experiments or successor not in experiments:
            raise ContractError(f"{label} references an unknown experiment")
        if predecessor == successor:
            raise ContractError(f"{label} cannot be a self relation")
        relation_type = raw.get("type")
        kind = raw.get("kind")
        if relation_type not in RELATION_TYPES:
            raise ContractError(f"{label}.type must be one of {sorted(RELATION_TYPES)}")
        if kind not in RELATION_KINDS:
            raise ContractError(f"{label}.kind must be one of {sorted(RELATION_KINDS)}")
        primary = raw.get("primary", False)
        if not isinstance(primary, bool):
            raise ContractError(f"{label}.primary must be boolean")
        if primary and (relation_type != "depends_on" or kind != "evolution"):
            raise ContractError(f"{label}: only depends_on evolution relations may be primary")
        if primary:
            if successor in primary_incoming:
                raise ContractError(
                    f"experiment {successor} has multiple primary predecessors: "
                    f"{primary_incoming[successor]} and {predecessor}"
                )
            primary_incoming[successor] = predecessor
        evidence_ids = raw.get("evidence")
        if not isinstance(evidence_ids, list) or not evidence_ids:
            raise ContractError(f"{label}.evidence must be a non-empty array")
        for evidence_id in evidence_ids:
            if evidence_id not in evidence_by_id:
                raise ContractError(f"{label} references unknown evidence {evidence_id!r}")
        normalized_relations.append(
            {
                "id": relation_id,
                "from": predecessor,
                "to": successor,
                "type": relation_type,
                "kind": kind,
                "label": require_text(raw.get("label"), f"{label}.label"),
                "primary": primary,
                "evidence": evidence_ids,
            }
        )

    graph = {experiment_id: [] for experiment_id in experiments}
    for relation in normalized_relations:
        if relation["primary"]:
            graph[relation["from"]].append(relation["to"])
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            raise ContractError(f"primary evolution graph contains a cycle at {node}")
        if node in visited:
            return
        visiting.add(node)
        for child in graph[node]:
            visit(child)
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)

    sources = [study_path, *experiment_paths]
    return (
        {
            "schemaVersion": 1,
            "project": normalized_project,
            "tracks": normalized_tracks,
            "experiments": [experiments[key] for key in sorted(experiments)],
            "relations": sorted(normalized_relations, key=lambda item: item["id"]),
        },
        sources,
    )


def source_digest(payload: dict[str, Any], sources: list[Path]) -> str:
    digest = hashlib.sha256()
    digest.update(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8"))
    for path in sorted(sources):
        digest.update(path.name.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def build_payload(root: Path) -> dict[str, Any]:
    payload, sources = load_study(root)
    return {
        "meta": {
            "schemaVersion": 1,
            "sourceDigest": source_digest(payload, sources),
            "experimentCount": len(payload["experiments"]),
            "relationCount": len(payload["relations"]),
        },
        **payload,
    }


def render_javascript(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
    return f"window.TRACKSTUDY_DATA = {body};\n"
