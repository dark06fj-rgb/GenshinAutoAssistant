#!/usr/bin/env python3
"""Build and train a merged Genshin resource detector dataset.

Datasets are supplied as semicolon-separated workspace/project/version entries
in ROBOFLOW_DATASETS. Only datasets whose reuse license has been verified should
be added. Map metadata and icon packs are intentionally not treated as gameplay
object-detection images.
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
from pathlib import Path

import yaml
from roboflow import Roboflow
from ultralytics import YOLO

DEFAULT_DATASETS = "xhu/genshin-guivb/2;genshin-cczfg/genshinthingscollect/8"
OUTPUT = Path("runs/detect/genshin_resources")
MERGED = Path("resource_dataset_merged")

# Canonical names and known spelling variants across community datasets.
KEEP = {
    "mushroom": "mushroom",
    "berry": "berry",
    "mushroomberry": "mushroom_berry",
    "crystalfly": "crystalfly",
    "dandelion": "dandelion",
    "mint": "mint",
    "sweet_flower": "sweet_flower",
    "sweetflower": "sweet_flower",
    "valberry": "valberry",
    "wolfhook": "wolfhook",
    "sweet_flowery": "sweet_flower",
    "crystalchunk": "crystal_chunk",
    "crystal_chunk": "crystal_chunk",
    "whiteironchunk": "white_iron_chunk",
    "white_iron_chunk": "white_iron_chunk",
    "smalllampgrass": "small_lamp_grass",
    "small_lamp_grass": "small_lamp_grass",
    "sunsettia": "sunsettia",
    "pinecone": "pinecone",
    "iron": "iron_ore",
    "iron_ore": "iron_ore",
}


def parse_sources() -> list[tuple[str, str, int]]:
    raw = os.environ.get("ROBOFLOW_DATASETS", "").strip() or DEFAULT_DATASETS
    sources = []
    for item in raw.split(";"):
        item = item.strip()
        if not item:
            continue
        parts = item.split("/")
        if len(parts) != 3 or not parts[2].isdigit():
            raise ValueError(
                "Each ROBOFLOW_DATASETS entry must be workspace/project/version, "
                f"got: {item!r}"
            )
        sources.append((parts[0], parts[1], int(parts[2])))
    if not sources:
        raise RuntimeError("No Roboflow datasets were configured.")
    return sources


def find_split_dir(root: Path, split_names: tuple[str, ...], folder: str) -> Path:
    for split in split_names:
        for candidate in root.rglob(folder):
            if candidate.parent.name.lower() == split:
                return candidate
    raise RuntimeError(f"Could not find {folder} folder for split {split_names}")


def class_list(data_file: Path) -> list[str]:
    cfg = yaml.safe_load(data_file.read_text(encoding="utf-8"))
    names = cfg.get("names", [])
    if isinstance(names, dict):
        return [str(names[k]) for k in sorted(names, key=lambda x: int(x))]
    return [str(name) for name in names]


def normalize_class(name: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")
    return KEEP.get(normalized, "")


def main() -> None:
    api_key = os.environ.get("ROBOFLOW_API_KEY", "").strip()
    if not api_key:
        raise SystemExit(
            "Missing GitHub Actions secret ROBOFLOW_API_KEY. "
            "Add it in Settings > Secrets and variables > Actions."
        )

    sources = parse_sources()
    print("Configured dataset sources:", ", ".join(f"{w}/{p}/{v}" for w, p, v in sources))
    rf = Roboflow(api_key=api_key)

    if MERGED.exists():
        shutil.rmtree(MERGED)
    for split in ("train", "valid", "test"):
        (MERGED / split / "images").mkdir(parents=True, exist_ok=True)
        (MERGED / split / "labels").mkdir(parents=True, exist_ok=True)

    class_names: list[str] = []
    counts: dict[str, int] = {}
    image_hashes: set[str] = set()
    source_notes: list[str] = []
    copied_images = 0

    for workspace, project_name, version_number in sources:
        source_id = f"{workspace}/{project_name}/v{version_number}"
        print(f"Downloading {source_id}...")
        dataset = (
            rf.workspace(workspace)
            .project(project_name)
            .version(version_number)
            .download("yolov8")
        )
        root = Path(dataset.location).resolve()
        data_file = root / "data.yaml"
        if not data_file.exists():
            raise RuntimeError(f"{source_id} export has no data.yaml")

        names = class_list(data_file)
        old_to_new: dict[int, int] = {}
        for old_id, name in enumerate(names):
            canonical = normalize_class(name)
            if not canonical:
                continue
            if canonical not in class_names:
                class_names.append(canonical)
                counts[canonical] = 0
            old_to_new[old_id] = class_names.index(canonical)

        if not old_to_new:
            print(f"Skipping {source_id}: no supported resource classes. Classes: {names}")
            continue

        source_notes.append(
            f"{source_id}: retained {', '.join(sorted(set(class_names[i] for i in old_to_new.values())))}"
        )

        split_specs = [
            (("train",), "train"),
            (("valid", "val"), "valid"),
            (("test",), "test"),
        ]
        for split_aliases, output_split in split_specs:
            try:
                images_dir = find_split_dir(root, split_aliases, "images")
            except RuntimeError:
                if output_split == "test":
                    continue
                raise
            labels_dir = images_dir.parent / "labels"
            if not labels_dir.exists():
                raise RuntimeError(f"{source_id} is missing labels for {images_dir.parent.name}")

            for label_path in sorted(labels_dir.glob("*.txt")):
                kept_lines = []
                for line in label_path.read_text(encoding="utf-8").splitlines():
                    parts = line.split()
                    if len(parts) < 5:
                        continue
                    try:
                        old_id = int(float(parts[0]))
                    except ValueError:
                        continue
                    if old_id not in old_to_new:
                        continue
                    parts[0] = str(old_to_new[old_id])
                    kept_lines.append(" ".join(parts))
                if not kept_lines:
                    continue

                image_path = next(
                    (p for p in images_dir.glob(label_path.stem + ".*")
                     if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}),
                    None,
                )
                if image_path is None:
                    continue

                digest = hashlib.sha256(image_path.read_bytes()).hexdigest()
                if digest in image_hashes:
                    continue
                image_hashes.add(digest)
                safe_source = re.sub(r"[^a-zA-Z0-9]+", "_", f"{workspace}_{project_name}")
                filename = f"{safe_source}_{digest[:12]}{image_path.suffix.lower()}"
                shutil.copy2(image_path, MERGED / output_split / "images" / filename)
                (MERGED / output_split / "labels" / f"{Path(filename).stem}.txt").write_text(
                    "\n".join(kept_lines) + "\n", encoding="utf-8"
                )
                copied_images += 1
                for line in kept_lines:
                    counts[class_names[int(line.split()[0])]] += 1

    if copied_images == 0 or not class_names:
        raise RuntimeError("No labeled resource images were merged from the configured datasets.")

    # Training requires train and validation images. Avoid silently using test data as validation.
    if not any((MERGED / "train" / "images").iterdir()):
        raise RuntimeError("Merged dataset has no training images.")
    if not any((MERGED / "valid" / "images").iterdir()):
        raise RuntimeError("Merged dataset has no validation images.")

    config = {
        "path": str(MERGED.resolve()),
        "train": "train/images",
        "val": "valid/images",
        "names": class_names,
        "nc": len(class_names),
    }
    if any((MERGED / "test" / "images").iterdir()):
        config["test"] = "test/images"
    filtered_yaml = MERGED / "resource_data.yaml"
    filtered_yaml.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "DATASET_ATTRIBUTION.txt").write_text(
        "Merged Genshin resource dataset sources:\n"
        + "\n".join(source_notes)
        + "\n\nOnly sources with verified reuse permission should be configured. "
          "Map-coordinate JSON and standalone icons are not used as gameplay training images.\n",
        encoding="utf-8",
    )
    (OUTPUT / "class_counts.txt").write_text(
        f"Unique labeled images: {copied_images}\n"
        + "\n".join(f"{name}: {counts.get(name, 0)} boxes" for name in class_names)
        + "\n",
        encoding="utf-8",
    )
    split_image_counts = {
        split: len(list((MERGED / split / "images").glob("*")))
        for split in ("train", "valid", "test")
    }
    split_report = [
        "Merged dataset split image counts:",
        *(f"{split}: {amount}" for split, amount in split_image_counts.items()),
        "",
        "Bounding boxes by class:",
        *(f"{name}: {counts.get(name, 0)}" for name in class_names),
    ]
    (OUTPUT / "dataset_quality_report.txt").write_text("\n".join(split_report) + "\n", encoding="utf-8")
    print(f"Merged {copied_images} unique labeled images across {len(class_names)} resource classes.")
    print("Split image counts:", split_image_counts)
    print("Bounding boxes by class:", counts, flush=True)
    rare = {name: amount for name, amount in counts.items() if amount < 10}
    if rare:
        print("DATASET_WARNING rare classes (<10 boxes):", rare, flush=True)

    # Higher resolution and longer transfer learning help small/distant targets,
    # but do not replace collecting more varied examples for rare classes.
    print("Starting accuracy-focused CPU training (80 epochs, 512px, YOLO11s, batch 4)...", flush=True)
    model = YOLO("yolo11s.pt")
    model.train(
        data=str(filtered_yaml),
        epochs=80,
        imgsz=512,
        batch=4,
        patience=20,
        workers=2,
        device="cpu",
        pretrained=True,
        cache=False,
        seed=42,
        cos_lr=True,
        close_mosaic=10,
        degrees=5.0,
        translate=0.10,
        scale=0.50,
        fliplr=0.5,
        hsv_h=0.015,
        hsv_s=0.65,
        hsv_v=0.40,
        mixup=0.05,
        project="runs/detect",
        name="genshin_resources",
        exist_ok=True,
        plots=True,
        verbose=True,
    )

    best = OUTPUT / "weights" / "best.pt"
    if not best.exists():
        raise RuntimeError("Training finished without producing weights/best.pt")

    # Evaluate on a held-out test split when the source datasets provide one.
    trained = YOLO(str(best))
    test_images = MERGED / "test" / "images"
    metrics_path = OUTPUT / "test_metrics.txt"
    if test_images.exists() and any(test_images.iterdir()) and "test" in config:
        print("Evaluating best.pt on the held-out test split...", flush=True)
        test_metrics = trained.val(
            data=str(filtered_yaml),
            split="test",
            imgsz=320,
            batch=4,
            device="cpu",
            plots=True,
            project="runs/detect",
            name="genshin_resources_test",
            exist_ok=True,
        )
        box = test_metrics.box
        metric_lines = [
            "Held-out test split metrics (not training/validation metrics):",
            f"test_images: {split_image_counts['test']}",
            f"mAP50: {float(box.map50):.6f}",
            f"mAP50-95: {float(box.map):.6f}",
            f"precision: {float(box.mp):.6f}",
            f"recall: {float(box.mr):.6f}",
            "",
            "Per-class AP50:",
        ]
        names_by_id = test_metrics.names
        ap50 = getattr(box, "ap50", [])
        ap = getattr(box, "ap", [])
        class_ids = getattr(box, "ap_class_index", [])
        for pos, class_id in enumerate(class_ids):
            class_name = names_by_id.get(int(class_id), str(class_id)) if isinstance(names_by_id, dict) else names_by_id[int(class_id)]
            ap50_value = float(ap50[pos]) if len(ap50) > pos else float("nan")
            ap_value = float(ap[pos].mean()) if len(ap) > pos else float("nan")
            metric_lines.append(f"{class_name}: AP50={ap50_value:.6f}, AP50-95={ap_value:.6f}")
        metrics_path.write_text("\n".join(metric_lines) + "\n", encoding="utf-8")

        quality_pass = float(box.map50) >= 0.60 and float(box.mr) >= 0.50 and split_image_counts["test"] >= 100
        quality_text = (
            "PASS: held-out accuracy and test coverage thresholds met.\n"
            if quality_pass else
            "NOT_READY: require mAP50 >= 0.60, recall >= 0.50, and at least 100 held-out test images.\n"
        )
        (OUTPUT / "quality_gate.txt").write_text(quality_text, encoding="utf-8")
        print("MODEL_QUALITY_GATE=" + ("PASS" if quality_pass else "NOT_READY"), flush=True)
    else:
        metrics_path.write_text(
            "No held-out test split was supplied by the configured datasets.\n",
            encoding="utf-8",
        )

    # Export is deliberately non-fatal: preserve best.pt and evaluation outputs
    # even when the optional ONNX toolchain is incompatible.
    export_status = OUTPUT / "onnx_export_status.txt"
    export_error = OUTPUT / "onnx_export_error.txt"
    print("Exporting experimental model to ONNX for a future Android test build...", flush=True)
    try:
        onnx_path = trained.export(format="onnx", imgsz=512, simplify=False)
        onnx_path = Path(onnx_path)
        if not onnx_path.exists():
            raise RuntimeError("ONNX export returned without creating a model file.")
        export_status.write_text(f"ONNX export succeeded: {onnx_path}\n", encoding="utf-8")
        if export_error.exists():
            export_error.unlink()
        print(f"ONNX_EXPORT_COMPLETE model={onnx_path}", flush=True)
    except Exception as exc:
        export_status.write_text("ONNX export failed; trained weights and evaluation files are preserved.\n", encoding="utf-8")
        export_error.write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
        print(f"ONNX_EXPORT_FAILED: {type(exc).__name__}: {exc}", flush=True)

    print(f"TRAINING_COMPLETE best_model={best}", flush=True)
    print(f"TEST_METRICS_FILE={metrics_path}", flush=True)
    print("Experimental model only; require quality_gate.txt PASS and real gameplay false-positive review before integration.", flush=True)


if __name__ == "__main__":
    main()
