# Tree Presets

## RR_SummerAppleTree_Seed13001_Leaf3_BigApple_v1

Status: selected scene prototype for the outdoor reference reconstruction.

Blend artifact:
`tree_seed13001_leaf3_bigapple_study.blend`

Core generation:

```json
{
  "factory_class": "AppleCoverageLeaf3SummerTreeFactory",
  "base_factory": "infinigen.assets.objects.trees.generate.TreeFactory",
  "seed": 13001,
  "season": "summer",
  "fruit_type": "apple",
  "fruit_chance": 1.0,
  "realize": false,
  "distance": 4,
  "min_face_size": 0.01
}
```

Branch and foliage controls:

```json
{
  "branch_params": {
    "resolution": 160,
    "twig density_min": 10.0,
    "leaf density": 3.0,
    "leaf scale": 0.48,
    "fruit density": 0.8,
    "fruit scale": 0.30
  },
  "tree_child_placement": {
    "Density": 0.85,
    "Multi inst_min": 2,
    "Min scale": 1.15,
    "Max scale": 1.35
  },
  "twig_child_placement": {
    "Density": 1.0,
    "Multi inst_min": 3,
    "Min scale": 0.34,
    "Max scale": 0.48
  },
  "decimate_rate": {
    "leaf_min": 0.985,
    "apple_min": 0.90
  }
}
```

Validation notes:

- Created 2 new `BranchFactory(13001)` branch prototypes for this variant.
- Created 5 apple prototypes and 5 leaf prototypes.
- Verified branch `Set Material` nodes use `TREE_Branch_Bark_Fallback`.
- Verified branch anchor densities: fruit `0.8`, leaf `3.0`.
- Kept live Geometry Nodes and dependency collections; instances were not baked.
