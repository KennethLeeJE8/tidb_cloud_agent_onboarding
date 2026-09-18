#!/usr/bin/env python3
"""Classify TiDB Cloud project/cluster-list JSON without calling the network."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _items(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        for key in ("items", "projects", "clusters", "data", "result"):
            if key in value:
                return _items(value[key])
    return []


def project_ids(projects: Any) -> list[str]:
    ids = []
    for project in _items(projects):
        value = project.get("id", project.get("project_id", project.get("projectId")))
        if value is not None:
            ids.append(str(value))
    return ids


def is_starter_or_essential(cluster: dict[str, Any]) -> bool:
    """Treat unlabelled serverless-list rows as qualifying cloud clusters."""
    tier = next(
        (cluster[key] for key in ("tier", "cluster_type", "clusterType", "type") if key in cluster),
        None,
    )
    return tier is None or str(tier).strip().lower() in {"starter", "essential"}


def classify(projects: Any, cluster_results: dict[str, Any]) -> dict[str, Any]:
    ids = project_ids(projects)
    inaccessible = [project_id for project_id in ids if project_id not in cluster_results]
    qualifying: list[dict[str, str]] = []
    for project_id, document in cluster_results.items():
        for cluster in _items(document):
            if is_starter_or_essential(cluster):
                cluster_id = cluster.get("id", cluster.get("cluster_id", cluster.get("clusterId", "unknown")))
                qualifying.append({"project_id": project_id, "cluster_id": str(cluster_id)})
    return {
        "projects": ids,
        "inaccessible_projects": inaccessible,
        "qualifying_clusters": qualifying,
        "empty": bool(ids) and not inaccessible and not qualifying,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--projects", required=True, type=Path)
    parser.add_argument("--clusters", action="append", default=[], metavar="PROJECT_ID:FILE")
    args = parser.parse_args()
    results: dict[str, Any] = {}
    for value in args.clusters:
        project_id, separator, filename = value.partition(":")
        if not separator or not project_id or not filename:
            raise SystemExit("--clusters must be PROJECT_ID:FILE")
        results[project_id] = json.loads(Path(filename).read_text(encoding="utf-8"))
    projects = json.loads(args.projects.read_text(encoding="utf-8"))
    print(json.dumps(classify(projects, results), sort_keys=True))


if __name__ == "__main__":
    main()
