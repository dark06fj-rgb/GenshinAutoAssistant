#!/usr/bin/env python3
"""Train a small Genshin resource detector from the public xhu dataset.

Only resource-like classes are retained. This first-stage dataset is small,
so the resulting model is experimental and must be evaluated before app use.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

import yaml
from roboflow import Roboflow
from ultralytics import YOLO

WORKSPACE = "xhu"
PROJECT = "genshin-guivb"
VERSION = 2
KEEP = {
    "mushroom": "mushroom",
    "berry": "berry",
    "crystalfly": "crystalfly",
    "dandelion": "dandelion",
    "mint": "mint",
    "sweet_flower": "sweet_flower",
    "mushroomberry": "mushroom_berry",
}
OUTPUT = Path("runs/detect/genshin_resources")


def find_image_dir(root: Path, names: tuple[str, ...]) -> Path:
    for split in names:
        candidates = list(root.rglob("images"))
        for candidate in candidates:
            if candidate.parent.name.lower() == split:
                return candidate
    raise RuntimeError(f"Could not find image folder for split: {names}")


def main() -> None:
    api_key = os.environ.get("ROBOFLOW_API_KEY", "").strip()
    if not api_key:
        raise SystemExit(
            "Missing GitHub Actions secret ROBOFLOW_API_KEY. "
            "Add it in Settings > Secrets and variables > Actions, then run this workflow again."
        )

    print("Downloading public Genshin dataset xhu/genshin-guivb version 2...")
    rf = Roboflow(api_key=api_key)
    dataset = rf.workspace(WORKSPACE).project(PROJECT).version(VERSION).download("yolov8")
    source = Path(dataset.location).resolve()
    data_file = source / "data.yaml"
    if not data_file.exists():
        raise RuntimeError(f"Roboflow export did not contain data.yaml: {source}")

    source_cfg = yaml.safe_load(data_file.read_text(encoding="utf-8"))
    raw_names = source_cfg.get("names", [])
    if isinstance(raw_names, dict):
        class_names = [raw_names[k] for k in sorted(raw_names, key=lambda x: int(x))]
    else:
        class_names = list(raw_names)

    kept_old_ids: dict[int, int] = {}
    new_names: list[str] = []
    for old_id, raw_name in enumerate(class_names):
        normalized = str(raw_name).strip().lower().replace(" ", "_").replace("-", "_")
        if normalized in KEEP:
            kept_old_ids[old_id] = len(new_names)
            new_names.append(KEEP[normalized])

    if not kept_old_ids:
        raise RuntimeError(
            "No target resource classes were found in this dataset export. "
            f"Available classes: {class_names}"
        )

    print("Retained resource classes:", ", ".join(new_names))
    filtered = Path("resource_dataset_filtered").resolve()
    if filtered.exists():
        shutil.rmtree(filtered)
    shutil.copytree(source, filtered)

    # Keep only selected class annotations and remap class IDs.
    label_files = list(filtered.rglob("labels/*.txt"))
    counts = {name: 0 for name in new_names}
    for label_file in label_files:
        kept_lines: list[str] = []
        for line in label_file.read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) < 5:
                continue
            try:
                old_id = int(float(parts[0]))
            except ValueError:
                continue
            if old_id not in kept_old_ids:
                continue
            new_id = kept_old_ids[old_id]
            parts[0] = str(new_id)
            kept_lines.append(" ".join(parts))
            counts[new_names[new_id]] += 1
        label_file.write_text("\n".join(kept_lines) + ("\n" if kept_lines else ""), encoding="utf-8")

    if sum(counts.values()) == 0:
        raise RuntimeError("No bounding boxes remained after filtering resource classes.")
    print("Bounding boxes by class:", counts)

    train_images = find_image_dir(filtered, ("train",))
    val_images = find_image_dir(filtered, ("valid", "val"))
    try:
        test_images = find_image_dir(filtered, ("test",))
    except RuntimeError:
        test_images = None

    config = {
        "path": str(filtered),
        "train": str(train_images.relative_to(filtered)),
        "val": str(val_images.relative_to(filtered)),
        "names": new_names,
        "nc": len(new_names),
    }
    if test_images is not None:
        config["test"] = str(test_images.relative_to(filtered))
    filtered_yaml = filtered / "resource_data.yaml"
    filtered_yaml.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

    attribution = (
        "Dataset: Genshin Computer Vision Dataset (xhu/genshin-guivb), version 2\n"
        "Author: xhu\n"
        "License: Creative Commons Attribution 4.0 International (CC BY 4.0)\n"
        "Source: https://universe.roboflow.com/xhu/genshin-guivb/dataset/2\n"
        "This training run filters resource classes only; non-resource classes are excluded.\n"
    )
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "DATASET_ATTRIBUTION.txt").write_text(attribution, encoding="utf-8")
    (OUTPUT / "class_counts.txt").write_text(
        "\n".join(f"{name}: {count}" for name, count in counts.items()) + "\n",
        encoding="utf-8",
    )

    print("Starting CPU transfer-learning run with YOLO11n (60 epochs, 416px)...")
    model = YOLO("yolo11n.pt")
    model.train(
        data=str(filtered_yaml),
        epochs=60,
        imgsz=416,
        batch=8,
        patience=15,
        workers=2,
        device="cpu",
        pretrained=True,
        cache=False,
        seed=42,
        project="runs/detect",
        name="genshin_resources",
        exist_ok=True,
        plots=True,
        verbose=True,
    )

    best = OUTPUT / "weights" / "best.pt"
    if not best.exists():
        raise RuntimeError("Training finished without producing weights/best.pt")
    print(f"TRAINING_COMPLETE best_model={best}")
    print("This model is experimental; inspect validation metrics and test false positives before mobile integration.")


if __name__ == "__main__":
    main()
