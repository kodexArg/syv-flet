---
name: assets-manager
description: Asset management strategy for SyV-Flet. Covers default assets inventory, caching, loading patterns, naming conventions, and best practices for working with Kenney.nl resources.
allowed-tools: Read, Grep
---

# Asset Management Strategy

This document defines the complete asset pipeline for SyV-Flet, including inventory, storage conventions, caching mechanisms, loading patterns, and best practices.

## 1. Default Assets Inventory (From Kenney.nl)

### Summary
- **Total PNG Files:** 584
- **Hexagon Tiles:** 74 files
- **Board Game Icons:** 510 files
- **Typography:** Kenney Fonts suite (Open-source, included separately)

### 1.1 Hexagon Tiles (assets/hexagons/)

#### Previews/ (73 files)
Terrain and structure tiles in 64×64 pixel format (finalized 2D previews from Kenney Hexagon Kit).

**Categories:**
- **Base Terrain** (4): grass, water, sand, stone, dirt
- **Terrain Variants** (8): grass-forest, grass-hill, sand-desert, sand-rocks, stone-hill, stone-mountain, stone-rocks, water-island, water-rocks
- **Structures** (18): building-archery, building-cabin, building-castle, building-dock, building-farm, building-house, building-market, building-mill, building-mine, building-port, building-sheep, building-smelter, building-tower, building-village, building-wall, building-walls, building-watermill, building-wizard-tower
- **Units** (8): unit-house, unit-mansion, unit-mill, unit-ship, unit-ship-large, unit-tower, unit-tree, unit-wall-tower
- **Paths** (14): path-corner, path-corner-sharp, path-crossing, path-end, path-intersectionA through H, path-square, path-square-end, path-start, path-straight
- **Rivers** (14): river-corner, river-corner-sharp, river-crossing, river-end, river-intersectionA through H, river-start, river-straight
- **Infrastructure** (1): bridge

#### Textures/ (1 file)
- Variation overlays for detail and visual consistency (variation-a.png, variation-b.png)

### 1.2 Board Game Icons (assets/icons/PNG/)

#### Default (64px) — 292 files
Primary icon set at 64×64 pixels. Recommended size for overlay UI elements.

**Categories:**
- **Arrows**: clockwise, counterclockwise, cross (divided, basic), diagonal, horizontal, right, reserve, rotate, curve
- **Cards**: base, add, diagonal, down, flip, lift, place, remove, rotate, subtract, tap, target
- **Card Collections**: collection, diagonal, fan, flip, order, return, seek, shift, shuffle, stack
- **Characters**: base, lift, place, remove
- **Chess**: bishop, king, knight, pawn, queen, rook
- **Crowns**: crown-a, crown-b
- **Dice**: d2-d20 (with number variants and outlines)
- **Dice States**: 3D, 3D detailed, detailed, close, empty, out, question, shield, skull, sword
- **Directions**: n, s, e, w
- **Economy**: dollar
- **Effects**: exploding, exploding-6, fire
- **Flags**: square, triangle
- **Flasks**: empty, full, half
- **Flip Coins**: empty, full, half, head, tails
- **Hands**: base, card, cross, cube, hexagon, token (open)
- **Hexagons**: base, in, out, outline, question, switch, tile
- **Hourglasses**: base, bottom, top
- **Locks**: closed, open
- **Notes**: notepad, notepad-write
- **Pawns**: base, clockwise, counterclockwise, down, flip, left, reverse, right, skip, table, up
- **Shapes**: pentagon, pentagon-outline, rhombus, rhombus-outline
- **Pouches**: base, add, remove
- **Puzzle**: base
- **Resources**: apple, iron, lumber, planks, wheat, wood
- **Shields**: base
- **Skull**: base
- **Spinners**: base, segment
- **Structures**: church, farm, gate, house, tower, wall, watchtower
- **Suits**: clubs, diamonds, hearts, spades (with broken-hearts variant)
- **Sword**: base
- **Tags**: 1-10, d6 variants, empty, infinite, shield variants
- **Timers**: 0, 100, CW/CCW variants (25/50/75 percent)
- **Tokens**: base, add, give, in, out, remove, subtract
- **Token Collections**: base, shadow, stack

#### Double (128px) — 218 files
2× scaled versions (128×128 pixels) for HUD overlays or magnified displays. Mirrors the 64px set.

### 1.3 Typography (assets/fonts/)

**kenney_kenney-fonts/** — Complete Kenney Fonts suite
- Multiple weights and styles suitable for UI text rendering
- Licensed under open-source (check individual font files for specifics)

---

## 2. Directory Structure & Conventions

### Canonical Structure
```
assets/
├── hexagons/
│   ├── Previews/              ← Main terrain/structure tiles (64×64)
│   └── Textures/              ← Detail variations (overlays)
├── icons/
│   ├── PNG/
│   │   ├── Default (64px)/    ← Primary icon resolution
│   │   └── Double (128px)/    ← Scaled variants
│   └── Tilesheet/             ← (Future) optimized spritesheets
└── fonts/
    └── kenney_kenney-fonts/   ← Typography
```

### Naming Conventions

#### Hexagon Tiles
Format: `[category]-[descriptor].png` or `[category]_[variant].png`

Examples:
- Base terrain: `grass.png`, `water.png`
- Variants: `grass-forest.png`, `stone-mountain.png`
- Structures: `building-tower.png`, `unit-house.png`
- Features: `river-straight.png`, `path-intersection-D.png`

**Rules:**
- Lowercase with hyphens (kebab-case)
- No spaces or underscores except logical grouping
- Category prefix mandatory (building-, unit-, grass-, river-, etc.)

#### Board Game Icons
Format: `[category]_[name].png`

Examples:
- `card_tap.png`, `card_tap_outline.png`
- `dice_6.png`, `dice_6_number.png`
- `arrow_clockwise.png`, `direction_n.png`

**Rules:**
- Lowercase with underscores (snake_case)
- Suffix variants with descriptors: `_outline`, `_detailed`, `_number`, `_broken`

---

## 3. Asset Loading Strategy

### Loading Modes

#### 1. **Lazy Loading on Demand**
- Load PNGs only when needed (e.g., when rendering a specific hex or icon)
- Suitable for Desktop (sufficient RAM)
- Risk: Frame stutter on first render of new asset

#### 2. **Batch Preload at Startup**
- Load all default hexagon tiles (74 files) + frequently-used icons at game start
- Remaining icons loaded on-demand
- Balanced approach for Mobile (limited RAM)

#### 3. **Streaming/Progressive Load**
- Load visible region + adjacent hexagons
- Unload off-screen assets
- Complex but essential for very large maps on low-end Mobile

### Recommended Strategy for MVP
**Batch Preload:** Load all hexagon tiles + common icons (Start button, UI controls) at startup. Defer remaining icons to on-demand.

---

## 4. Caching & Memory Management

### In-Memory Cache

**Purpose:** Avoid re-decoding PNGs on every frame.

**Scope:**
- Maintain a dictionary mapping asset path → decoded Image (Flet Image object)
- Cache only loaded assets; lazy-evict unused assets after N frames

**Cache Invalidation:**
- Invalidate on theme change (e.g., dark mode toggle)
- Manual clear on memory pressure warnings

### File-System Cache
- PNG files are immutable (Kenney.nl assets)
- No cache files needed; rely on OS file-system cache
- Optional: Pre-convert PNG to a faster format (e.g., PNG → WebP) if performance is critical

### Memory Budget
| Platform | Hexagon Budget | Icon Budget | Total Estimate |
|----------|---|---|---|
| Desktop (Linux/Windows, 4GB+ RAM) | 74 tiles × 64KB = 4.7MB | 100+ icons × 32KB = 3.2MB | ~8-10MB |
| Mobile (Android, 512MB app limit) | 74 × 64KB = 4.7MB | 20-30 icons = 640KB-960KB | ~5-6MB |

---

## 5. Loading Patterns

### Pattern 1: Synchronous Load (Blocking)
- Suitable for startup/batch load
- Load all hexagon tiles before rendering first frame
- Block until complete; UI appears after

### Pattern 2: Asynchronous Load (Non-blocking)
- Load icon on first render request if not in cache
- Return placeholder/default image if not yet loaded
- Update UI when async load completes

### Pattern 3: Preload on Hover
- When mouse hovers over a hex or UI element, preload associated assets
- Smooth user experience for interactive exploration

### Fallback Strategy
- If asset load fails, render colored rectangle with error indication
- Log error; do not crash
- Allow graceful degradation

---

## 6. Best Practices

### DO
- Store all asset paths relative to `assets/` root (e.g., `hexagons/Previews/grass.png`)
- Use a centralized `AssetManager` class to handle all loading/caching
- Validate asset existence before rendering
- Log cache hits/misses for performance profiling
- Batch multiple asset requests into single async operation

### DON'T
- Load assets synchronously on every frame
- Decode PNG → raw pixels without caching
- Store hard-coded absolute paths (`/home/kodex/...`)
- Mix Kenney assets with custom art without versioning
- Resize/scale assets on-GPU without proper texture filtering (use Nearest for pixel art)

### Quality & Scaling
- **Pixel-Perfect Rendering:** Use nearest-neighbor scaling (not linear) for hexagon tiles to preserve retro aesthetic
- **Icon Scaling:** 64px icons → 48px (desktop tablets) or 40px (mobile) via scaling filters (can use linear for icons)
- **DPI Awareness:** Query device DPI; scale assets proportionally (e.g., 1× on 96 DPI, 1.5× on 144 DPI)

---

## 7. Asset Attribution & Licensing

### Source: Kenney.nl
- **License:** Creative Commons Zero (CC0) — Public Domain
- **Attribution (optional but recommended):**
  ```
  "Kenney.nl (2024). Hexagon Kit, Board Game Icons, Kenney Fonts.
   Retrieved from https://kenney.nl/assets"
  ```

### No Derivative Restrictions
- Modify, remix, combine freely
- No credit required (but appreciated)

---

## 8. Future Considerations

### Asset Variants
- **Dark Mode:** Inverted/desaturated versions of hexagon tiles (store in separate folder: `hexagons/Previews-Dark/`)
- **Custom Assets:** User-created terrains, structures (validate format before loading)

### Optimization: Spritesheets
- Combine 20-30 frequently-used icons into single tilesheet
- Reduce file I/O and GPU memory fragmentation
- Store in `icons/Tilesheet/`

### Localization Assets
- Locale-specific icons (future)
- Store in `assets/l10n/[locale]/`

### Version Pinning
- Document Kenney.nl asset versions used (currently: Latest as of 2024)
- If updating Kenney assets, version-tag in git commit message

---

## 9. Quick Reference: Default Assets Checklist

| Item | Count | Location | Type | Default? |
|------|-------|----------|------|----------|
| Hexagon Tiles | 74 | `hexagons/Previews/` | PNG 64×64 | ✓ |
| Board Icons (64px) | 292 | `icons/PNG/Default (64px)/` | PNG 64×64 | ✓ |
| Board Icons (128px) | 218 | `icons/PNG/Double (128px)/` | PNG 128×128 | ✓ |
| Fonts | ~10 | `fonts/kenney_kenney-fonts/` | TTF/OTF | ✓ |
| **Total** | **584+** | — | — | — |

---

## 10. Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Asset not found | Wrong path or typo in filename | Verify path against `assets/` structure; check naming convention |
| Slow loading | Lazy-loading too many at once | Implement batch preload or async loading with fallbacks |
| Blurry icons/tiles | Linear filtering on pixel art | Ensure scaling uses nearest-neighbor filter |
| Memory leak | Cache never evicted | Implement LRU cache eviction or explicit cache clearing |
| Different sizes in UI | Mixed 64px and 128px icons | Standardize icon size; scale consistently via UI layout (not asset size) |
