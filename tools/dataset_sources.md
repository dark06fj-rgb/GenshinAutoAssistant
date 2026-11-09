# Genshin resource dataset source register

This file separates sources suitable for object-detection training from metadata-only or unverified sources.

## Enabled training source

- `xhu/genshin-guivb/2`
- Roboflow Universe: https://universe.roboflow.com/xhu/genshin-guivb
- Reported dataset license: CC BY 4.0 (verify again on the exact version before redistribution).
- Resource labels retained by the training pipeline: mushroom, berry, crystalfly, dandelion, mint, sweet flower, mushroom berry.

## Enabled additional source

- `genshin-cczfg/genshinthingscollect/8`
- Roboflow Universe: https://universe.roboflow.com/genshin-cczfg/genshinthingscollect/dataset/8
- Version 8: 361 images; 253 train, 73 validation, 35 test; 24 classes total.
- The project page explicitly lists CC BY 4.0. Attribution is retained in the training artifact.
- Resource classes retained include CrystalChunk, SmallLampGrass, Sunsettia, WhiteIronChunk, iron, mint, pinecone, sweetFlower, valberry, and wolfhook. Non-resource classes are filtered out.

## Metadata-only / not training images

- https://github.com/kxxoling/genshin-map-data — snapshots of official web-map data; useful for resource names and map locations, not labeled in-world gameplay frames. Repository license metadata is absent.
- https://github.com/FlavioForci/GenshinMapOverlay — map overlay project; repository license metadata is absent. Do not copy its user-submitted images into training without explicit permission.
- Standalone map icons are not equivalent to screenshots of resource objects in the 3D game world.

## Training configuration

The default training configuration now includes both verified sources above. An optional GitHub Actions repository variable `ROBOFLOW_DATASETS` can override the sources, separated by semicolons, in this format:

`workspace/project/version;workspace2/project2/version`

The pipeline merges labeled images, normalizes supported resource class names, remaps YOLO class IDs, and removes exact duplicate images by SHA-256. It keeps train/validation/test splits separate. Only images with at least one retained resource annotation are included.
