"""Render the existing Lumi atlas without generating or changing artwork."""
from pathlib import Path
import argparse
import hashlib
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TIMINGS = {
    "idle": [280, 110, 110, 140, 140, 320],
    "running-right": [120] * 7 + [220],
    "running-left": [120] * 7 + [220],
    "waving": [140] * 3 + [280],
    "jumping": [140] * 4 + [280],
    "failed": [140] * 7 + [240],
    "waiting": [150] * 5 + [260],
    "running": [120] * 5 + [220],
    "review": [150] * 5 + [280],
}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--atlas", type=Path, default=ROOT / "pets/lumi/final/lumi-spritesheet.png")
    parser.add_argument("--output", type=Path, default=ROOT / "build")
    args = parser.parse_args()
    with Image.open(args.atlas) as opened:
        atlas = opened.convert("RGBA")
    if atlas.size != (1536, 2288):
        raise SystemExit(f"Expected a v2 atlas, got {atlas.size}")
    args.output.mkdir(parents=True, exist_ok=True)

    def cell(row, column):
        sprite = atlas.crop((column * 192, row * 208, (column + 1) * 192, (row + 1) * 208))
        background = Image.new("RGBA", sprite.size, (232, 237, 245, 255))
        background.alpha_composite(sprite)
        return background.convert("RGB")

    def save(name, frames, durations):
        frames[0].save(args.output / f"{name}.gif", save_all=True, append_images=frames[1:],
                       duration=durations, loop=0, disposal=2, optimize=False)

    for row, (state, durations) in enumerate(TIMINGS.items()):
        save(state, [cell(row, column) for column in range(len(durations))], durations)
    save("look-around", [cell(9 + i // 8, i % 8) for i in range(16)], [200] * 16)
    print(json.dumps({"output": str(args.output), "previews": 10,
                      "atlas_sha256": hashlib.sha256(args.atlas.read_bytes()).hexdigest()}, indent=2))

if __name__ == "__main__":
    main()
