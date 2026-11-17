"""Cut the character sheets into transparent per-pose PNGs (dev-time tool, not needed to play)."""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi

# (x0, y0, x1, y1) crop per pose, chosen to exclude the baked-in labels
CELLS = {
    'idle':   (40, 70, 250, 395),
    'aim':    (255, 70, 500, 395),
    'swing':  (500, 70, 770, 395),
    'finish': (20, 448, 340, 790),
    'win':    (420, 447, 720, 790),
}

def cut(src, name):
    im = Image.open(src).convert('RGB')
    a = np.asarray(im).astype(int)
    for pose, (x0, y0, x1, y1) in CELLS.items():
        c = a[y0:y1, x0:x1]
        bg = (np.abs(c - 75).max(axis=2) < 22)
        # background = gray regions connected to the crop border
        lab, _ = ndi.label(bg)
        edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
        bgmask = np.isin(lab, list(edge))
        fg = ~bgmask
        fg = ndi.binary_opening(fg, iterations=1)
        # keep real pieces (sprite, club, swoosh); drop specks and label fragments
        lab2, n = ndi.label(fg)
        sizes = ndi.sum(fg, lab2, range(1, n + 1))
        keep = np.isin(lab2, [i + 1 for i, s in enumerate(sizes) if s > 150])
        keep = ndi.binary_fill_holes(keep) | keep
        rgba = np.dstack([c, (keep * 255)]).astype(np.uint8)
        out = Image.fromarray(rgba, 'RGBA')
        out = out.crop(out.getbbox())
        out.save(f'assets/sprites/{name}_{pose}.png')
        print(name, pose, out.size)

for n in ('ron', 'david', 'ryan'):
    cut(f'assets/{n}.webp', n)
