#!/usr/bin/env python3
"""Render a deterministic, looping 3D ASCII Christmas tree. Requires Pillow."""
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

WIDTH, HEIGHT = 672, 720
CELL_X, CELL_Y = 5, 7
FPS, SECONDS = 20, 12
BACKGROUND = (3, 9, 19)
SEED = 1717
TAU = math.tau


def font_path():
    for path in ["/System/Library/Fonts/Menlo.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", "C:/Windows/Fonts/consola.ttf"]:
        if Path(path).exists():
            return path
    raise FileNotFoundError("Set font_path() to a local monospace font.")


def scene():
    rng = random.Random(SEED)
    points = []

    def add(x, y, z, char, color, shine=0.0):
        points.append((x, y, z, char, color, shine, rng.random() * TAU))

    def radius(y):
        # Layered branch tips soften the cone without losing its silhouette.
        h = max(0, 1 - y / 6)
        return 2.05 * h * (0.93 + 0.07 * math.cos(y * TAU * 2.6))

    # Evergreen needles. Each character is a point on a rotating 3D surface.
    for row in range(135):
        y = row / 134 * 5.97
        r = radius(y)
        count = max(8, int(r * 97))
        for j in range(count):
            angle = j / count * TAU + rng.uniform(-0.012, 0.012)
            rr = r * rng.uniform(0.9, 1.035)
            v = rng.random()
            color = (int(42 + v * 62), int(142 + v * 95), int(82 + v * 77))
            add(rr * math.cos(angle), y + rng.uniform(-0.014, 0.014), rr * math.sin(angle), rng.choice(".,:;+=x*"), color, 0.25)
        # A scattering of frosty branch tips.
        for j in range(max(1, count // 22)):
            a = rng.random() * TAU
            add(r * 1.045 * math.cos(a), y, r * 1.045 * math.sin(a), rng.choice("+*x"), (207, 255, 231), 0.75)

    # A warm gold beaded garland winds six times around the tree.
    for i in range(1500):
        y = 0.22 + i / 1499 * 5.55
        a = y / 5.55 * TAU * 6
        r = radius(y) + 0.045
        add(r * math.cos(a), y, r * math.sin(a), rng.choice("o.:*"), (255, 222, 110), 0.55)

    # Round red and gold ornaments, modeled as small spheres.
    for i in range(25):
        y = 0.4 + (i + 0.35) / 25 * 4.9
        a = i * 2.39996
        r = radius(y) + 0.025
        cx, cz = r * math.cos(a), r * math.sin(a)
        size = 0.105 + (1 - y / 6) * 0.035
        red = i % 4 != 0
        for lat in range(8):
            phi = (lat + 0.5) / 8 * math.pi
            for lon in range(14):
                theta = lon / 14 * TAU
                dx, dy, dz = size * math.sin(phi) * math.cos(theta), size * math.cos(phi), size * math.sin(phi) * math.sin(theta)
                normal_light = max(0, (-dx + dy + dz) / (size * 1.73))
                lit = 0.8 + 0.2 * normal_light
                base = (255, 82, 94) if red else (255, 221, 117)
                specular = 0.8 * normal_light ** 10
                color = tuple(min(255, int(c * lit + (255 - c) * specular)) for c in base)
                add(cx + dx, y + dy, cz + dz, rng.choice("oO@*"), color, 0.25)

    # A short trunk, mostly visible between the lowest branches and the ground.
    for i in range(200):
        a, y = rng.random() * TAU, -0.35 + rng.random() * 0.5
        add(0.17 * math.cos(a), y, 0.17 * math.sin(a), "|", (112, 78, 54))

    # Presents on the ground rotate with the tree, as in the reference.
    for cx, cz, w, h, d, color in [(-2.0, 0.1, 0.63, 0.58, 0.58, (181, 39, 56)), (1.75, 0.6, 0.75, 0.43, 0.6, (43, 80, 173)), (1.1, -1.8, 0.55, 0.74, 0.58, (192, 43, 57)), (-0.45, 2.0, 0.58, 0.38, 0.58, (39, 133, 110))]:
        for axis in range(3):
            for side in [-1, 1]:
                for u in range(15):
                    for v in range(12):
                        a, b = u / 14 - 0.5, v / 11 - 0.5
                        if axis == 0:
                            x, y, z = side * w / 2, (a + 0.5) * h, b * d
                            ribbon = abs(b) < 0.065
                        elif axis == 1:
                            x, y, z = a * w, (side + 1) / 2 * h, b * d
                            ribbon = abs(a) < 0.065 or abs(b) < 0.065
                        else:
                            x, y, z = a * w, (b + 0.5) * h, side * d / 2
                            ribbon = abs(a) < 0.065
                        add(cx + x, -0.35 + y, cz + z, "+" if ribbon else rng.choice("#x="), (238, 202, 122) if ribbon else color)
        for i in range(60):
            a = i / 60 * TAU
            add(cx + 0.18 * math.sin(a), h - 0.3 + 0.09 * (1 - math.cos(a * 2)), cz + 0.09 * math.sin(a * 2), "o", (238, 202, 122))

    ground = []
    for row in range(33):
        z = -5 + row * 0.3
        for col in range(73):
            x = -6.5 + col * 0.18
            if (x / 6.6) ** 2 + (z / 5.2) ** 2 < 1:
                ground.append((x, -0.37, z, rng.choice("...,:")))
    snow = [(rng.random(), rng.random(), rng.choice([1, 1, 2, 3]), rng.random() * TAU) for _ in range(190)]
    return points, ground, snow


def renderer():
    points, ground, snow = scene()
    font = ImageFont.truetype(font_path(), 8)
    cols, rows = WIDTH // CELL_X, HEIGHT // CELL_Y
    glyphs = {}

    def stamp(char, color):
        # Quantize before rendering: stable colors prevent GIF palette flicker.
        color = tuple(min(255, round(c / 8) * 8) for c in color)
        key = char, color
        if key not in glyphs:
            tile = Image.new("RGB", (CELL_X, CELL_Y), BACKGROUND)
            ImageDraw.Draw(tile).text((0, -1), char, font=font, fill=color, stroke_width=0)
            glyphs[key] = tile
        return glyphs[key]

    def render(frame, count):
        t = frame / count
        angle = TAU * t
        ca, sa = math.cos(angle), math.sin(angle)
        cells = {}

        def project(x, y, z, char, color, rotating=True, priority=0):
            if rotating:
                x, z = ca * x + sa * z, -sa * x + ca * z
            yy = (y - 3) * 0.988 - z * 0.156
            zz = z * 0.988 + (y - 3) * 0.156
            depth = 12 - zz
            px = int((WIDTH / 2 + x * 920 / depth) / CELL_X)
            py = int((HEIGHT / 2 - yy * 920 / depth) / CELL_Y)
            if 0 <= px < cols and 0 <= py < rows:
                key = px, py
                score = depth - priority
                if key not in cells or score < cells[key][0]:
                    cells[key] = (score, char, color)

        for x, y, z, ch in ground:
            # Perspective dot grid fades toward its boundary.
            fade = max(0.12, 1 - (x / 6.8) ** 2 - (z / 6) ** 2)
            color = tuple(int(c * fade) for c in (112, 131, 150))
            project(x, y, z, ch, color, rotating=False)

        for x, y, z, ch, rgb, shine, phase in points:
            front = -sa * x + ca * z
            shade = 0.74 + 0.26 * (front / max(0.15, math.hypot(x, z)) + 1) / 2
            shimmer = 1 + shine * (0.5 + 0.5 * math.sin(angle * 3 + phase))
            color = tuple(min(255, int(c * shade * shimmer)) for c in rgb)
            project(x, y, z, ch, color)

        # A five-point gold star faces the viewer throughout the rotation.
        star = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            r = 1 if i % 2 == 0 else 0.45
            star.append((math.cos(a) * r, math.sin(a) * r))

        def inside(x, y):
            hit = False
            j = len(star) - 1
            for i in range(len(star)):
                ax, ay = star[i]
                bx, by = star[j]
                if (ay > y) != (by > y) and x < (bx - ax) * (y - ay) / (by - ay) + ax:
                    hit = not hit
                j = i
            return hit

        star_y = 6.34
        for iy in range(-5, 6):
            for ix in range(-7, 8):
                if inside(ix / 7, iy / 5):
                    project(ix * 0.061, star_y - iy * 0.085, 0.1, "*" if abs(ix) + abs(iy) > 4 else "@", (255, 238 + int(17 * math.sin(angle) ** 2), 157), rotating=False, priority=5)
        for i in [-1, 1]:
            for j in range(8, 15):
                project(i * j * 0.06, star_y, 0.1, "." if j > 11 else "-", (202, 177, 98), rotating=False)
            for j in range(6, 10):
                project(0, star_y + i * j * 0.085, 0.1, ":", (215, 186, 104), rotating=False)

        # All snowflakes travel an integer number of screen heights per loop.
        # Wrapping offscreen makes the last-to-first frame a normal time step.
        for x, y, speed, phase in snow:
            px = int(((x + 0.012 * math.sin(angle + phase)) % 1) * (cols - 2)) + 1
            py = int(((y + t * speed) % 1) * rows)
            brightness = 0.65 + 0.35 * math.sin(angle * 2 + phase) ** 2
            rgb = tuple(int(c * brightness) for c in (151, 181, 202))
            key = px, py
            # Some flakes pass behind the tree, others pass in front.
            if speed == 3 or key not in cells:
                cells[key] = (0, "+" if speed == 3 else ".", rgb)

        image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
        for (x, y), (_, char, color) in cells.items():
            image.paste(stamp(char, color), (x * CELL_X, y * CELL_Y))

        # Brief, staggered glints on visible branch tips and garland beads.
        # Periodic phases preserve the seamless rotation and snowfall loop.
        glints = Image.new("RGB", (WIDTH, HEIGHT))
        pen = ImageDraw.Draw(glints)
        for (x, y), (depth, char, color) in cells.items():
            if not (15 < y < 90 and 25 < x < cols - 25 and depth > 0):
                continue
            if char not in "+*xo" or (x * 19 + y * 31) % 37:
                continue
            phase = ((x * 17 + y * 43) % 101) / 101 * TAU
            pulse = max(0, math.sin(angle * 3 + phase)) ** 18
            if pulse < 0.2:
                continue
            cx, cy = x * CELL_X + 2, y * CELL_Y + 3
            glow_color = tuple(int(c * pulse) for c in (255, 248, 201))
            pen.line((cx - 3, cy, cx + 3, cy), fill=glow_color)
            pen.line((cx, cy - 4, cx, cy + 4), fill=glow_color)

        from PIL import ImageChops
        image = ImageChops.add(image, glints)
        # Two soft halos make the lights shine while keeping crisp ASCII cores.
        highlights = image.point(lambda v: max(0, v - 85))
        glow = highlights.filter(ImageFilter.GaussianBlur(1.5)).point(lambda v: v * 0.95)
        halo = highlights.filter(ImageFilter.GaussianBlur(4)).point(lambda v: v * 0.65)
        return ImageChops.add(ImageChops.add(image, glow), halo)

    return render


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--preview-only", action="store_true")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    render = renderer()
    count = FPS * SECONDS
    preview = render(0, count)
    preview.save(args.output_dir / "christmas-tree.png")
    if args.preview_only:
        return
    # A palette derived from several views includes every ornament color.
    samples = [render(i, count) for i in [0, count // 4, count // 2, 3 * count // 4]]
    sheet = Image.new("RGB", (WIDTH * 2, HEIGHT * 2))
    for i, sample in enumerate(samples):
        sheet.paste(sample, ((i % 2) * WIDTH, (i // 2) * HEIGHT))
    palette = sheet.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    frames = []
    for i in range(count):
        frames.append(render(i, count).quantize(palette=palette, dither=Image.Dither.NONE))
        if i % FPS == 0:
            print(f"Rendered {i}/{count}", flush=True)
    path = args.output_dir / "christmas-tree.gif"
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=1000 // FPS, loop=0, optimize=False, disposal=1)
    print(f"Saved {path} ({path.stat().st_size / 1024 / 1024:.2f} MiB)")


if __name__ == "__main__":
    main()
