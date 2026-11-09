# Genshin resource dataset source register

This file separates sources suitable for object-detection training from metadata-only or unverified sources.

## Enabled training source

- `xhu/genshin-guivb/2`
- Roboflow Universe: https://universe.roboflow.com/xhu/genshin-guivb
- Reported dataset license: CC BY 4.0 (verify again on the exact version before redistribution).
- Resource labels retained by the training pipeline: mushroom, berry, crystalfly, dandelion, mint, sweet flower, mushroom berry.

## Candidate source — not enabled yet

- `genshin-cczfg/genshinthingscollect`
- Roboflow Universe: https://universe.roboflow.com/genshin-cczfg/genshinthingscollect
- Search index reports 364 images and classes including CrystalChunk, SmallLampGrass, Sunsettia, WhiteIronChunk, iron, mint, and pinecone.
- Exact dataset version and reuse license were not independently verified during this review. Do not add it to `ROBOFLOW_DATASETS` until its owner/license and a downloadable version are confirmed.

## Metadata-only / not training images

- https://github.com/kxxoling/genshin-map-data — snapshots of official web-map data; useful for resource names and map locations, not labeled in-world gameplay frames. Repository license metadata is absent.
- https://github.com/FlavioForci/GenshinMapOverlay — map overlay project; repository license metadata is absent. Do not copy its user-submitted images into training without explicit permission.
- Standalone map icons are not equivalent to screenshots of resource objects in the 3D game world.

## Training configuration

Set the GitHub Actions repository variable `ROBOFLOW_DATASETS` only to verified sources, separated by semicolons, in this format:

`workspace/project/version;workspace2/project2/version`

The pipeline merges labeled images, normalizes supported resource class names, remaps YOLO class IDs, and removes exact duplicate images by SHA-256. It keeps train/validation/test splits separate. Only images with at least one retained resource annotation are included.
