# ASCII Christmas tree

An original, procedural recreation inspired by your screen recording: a rotating evergreen, gold spiral garland, red and gold ornaments, a five-point star, presents, a perspective ground grid, and falling snow. Every visible shape is drawn with ASCII characters in a monospace font.

## GitHub profile

GitHub displays the root `README.md` from a public repository whose name matches your username. For your connected account, that is `Jeffreylirj/Jeffreylirj`.

1. Create that public repository if it does not exist.
2. Copy `README.md` and `christmas-tree.gif` into its root. If you already have a profile README, append the image block instead of replacing your existing content.
3. Commit the files to the default branch.

The GIF is embedded in the Markdown; it loops automatically without JavaScript or an external hosting service. Both files are needed: the `.md` references the `.gif` using a relative path. A still preview is included as `christmas-tree.png`.

Profile README requirements: [GitHub documentation](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme).

## Regenerate or customize

Requires Python 3.9+ and Pillow. No API keys or network calls are used by the generator.

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 generate_tree.py
```

On Windows, activate the environment using `.venv\Scripts\activate`.

The generator uses Menlo on macOS, DejaVu Sans Mono on Linux, or Consolas on Windows. If none is installed, update `font_path()` to point to your preferred monospace font. Font choice can slightly alter the appearance.

Edit `FPS`, `SECONDS`, `BACKGROUND`, and `SEED` near the top of `generate_tree.py` to change speed, duration, background, or the scene. `SECONDS` is the time for one complete rotation. To render just a still:

```sh
python3 generate_tree.py --preview-only
```

The default export is 672 × 720 pixels, 20 frames per second, and a 12-second seamless loop. A fixed GIF palette avoids frame-to-frame color shifts.
