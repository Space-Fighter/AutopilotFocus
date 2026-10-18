"""Tiny Excalidraw drawing library for architecture sheets.

A Sheet holds frames laid out on one canvas (a "drawing sheet"). Inside a
frame, all coordinates are local to the frame's top-left corner. Every element
gets a deterministic id derived from its key, so regenerating keeps arrows
bound and keeps hand-drawn user additions attached to the right frame.

Elements created here carry customData.generated = True. On save, any element
in the existing file WITHOUT that flag (i.e. drawn by hand in Excalidraw) is
preserved and appended.
"""
import json
import math
import os
import re
import zlib
from contextlib import contextmanager

# stroke, fill — Excalidraw's own palette. Meaning is fixed across the sheet.
COLORS = {
    "blue": ("#1971c2", "#a5d8ff"),     # Chrome extension
    "cyan": ("#0c8599", "#99e9f2"),     # Go API / infra
    "yellow": ("#e67700", "#ffec99"),   # Python AI / LLM work
    "violet": ("#6741d9", "#d0bfff"),   # data stores
    "gray": ("#495057", "#e9ecef"),     # external / neutral
    "red": ("#c92a2a", "#ffc9c9"),      # block / security / errors
    "green": ("#2f9e44", "#b2f2bb"),    # allow / success
    "pink": ("#a61e4d", "#fcc2d7"),     # user-facing moments
    "ink": ("#1e1e1e", "transparent"),
}
HAND, NORMAL, MONO = 1, 2, 3
MUTED = "#495057"


def _rng(key):
    return zlib.crc32(key.encode("utf-8"))


def _measure(text, size, family):
    lines = text.split("\n")
    k = {HAND: 0.58, NORMAL: 0.55, MONO: 0.6}[family]
    return max(len(l) for l in lines) * size * k, len(lines) * size * 1.25


class Sheet:
    def __init__(self, max_row_width=7600, gap=200):
        self.elements = []
        self.by_id = {}
        self.max_row_width = max_row_width
        self.gap = gap
        self._cx = 0          # layout cursor
        self._cy = 0
        self._row_h = 0
        self._frame = None    # current frame id
        self._fkey = "sheet"
        self.ox = 0           # current frame origin
        self.oy = 0
        self._auto = 0
        self.frame_index = 0

    # ------------------------------------------------------------ internals
    def _id(self, key):
        if key is None:
            self._auto += 1
            key = f"_{self._auto}"
        full = key if "." in key else f"{self._fkey}.{key}"
        return re.sub(r"[^A-Za-z0-9_.:-]", "_", full)

    def _base(self, kind, x, y, w, h, stroke, bg="transparent", key=None, **kw):
        eid = self._id(key)
        if eid in self.by_id:
            raise ValueError(f"duplicate element key: {eid}")
        seed = _rng(eid)
        el = {
            "id": eid, "type": kind,
            "x": x, "y": y, "width": w, "height": h, "angle": 0,
            "strokeColor": stroke, "backgroundColor": bg,
            "fillStyle": kw.pop("fill", "solid"),
            "strokeWidth": kw.pop("sw", 2),
            "strokeStyle": kw.pop("style", "solid"),
            "roughness": kw.pop("rough", 1),
            "opacity": kw.pop("opacity", 100),
            "groupIds": kw.pop("groups", []),
            "frameId": self._frame,
            "roundness": kw.pop("roundness", None),
            "seed": seed % (2**31 - 1) + 1,
            "version": 1,
            "versionNonce": (seed * 7) % (2**31 - 1) + 1,
            "isDeleted": False,
            "boundElements": [],
            "updated": 1, "link": None, "locked": False,
            "customData": {"generated": True},
        }
        el.update(kw)
        self.elements.append(el)
        self.by_id[eid] = el
        return el

    def _bind_text(self, container, s, size, family, align, color="#1e1e1e"):
        c = self.by_id[container]
        w, h = _measure(s, size, family)
        x = c["x"] + c["width"] / 2 - w / 2 if align == "center" else c["x"] + 14
        y = c["y"] + c["height"] / 2 - h / 2
        t = self._base("text", x, y, w, h, color, key=container + ":label",
                       text=s, originalText=s, fontSize=size, fontFamily=family,
                       textAlign=align, verticalAlign="middle", containerId=container,
                       lineHeight=1.25, autoResize=True)
        t["boundElements"] = None
        c["boundElements"].append({"type": "text", "id": t["id"]})
        return t

    # -------------------------------------------------------------- frames
    @contextmanager
    def frame(self, key, title, w, h, subtitle=None):
        """A titled frame. Frames flow left→right and wrap into rows."""
        if self._cx and self._cx + w > self.max_row_width:
            self._cx = 0
            self._cy += self._row_h + self.gap
            self._row_h = 0
        self.frame_index += 1
        self._fkey = key
        self._frame = None
        self.ox, self.oy = self._cx, self._cy
        name = f"{self.frame_index} · {title}"
        f = self._base("frame", self.ox, self.oy, w, h, "#bbbbbb", key=f"{key}.frame", name=name)
        f["boundElements"] = None
        self._frame = f["id"]
        self.text(40, 28, title, 34, key="title")
        if subtitle:
            self.text(40, 78, subtitle, 18, color=MUTED, key="subtitle")
        try:
            yield self
        finally:
            self._cx += w + self.gap
            self._row_h = max(self._row_h, h)
            self._frame = None
            self.ox = self.oy = 0

    # ---------------------------------------------------------- primitives
    def text(self, x, y, s, size=18, color="#1e1e1e", family=HAND, align="left", key=None):
        w, h = _measure(s, size, family)
        t = self._base("text", self.ox + x, self.oy + y, w, h, color, key=key,
                       text=s, originalText=s, fontSize=size, fontFamily=family,
                       textAlign=align, verticalAlign="top", containerId=None,
                       lineHeight=1.25, autoResize=True)
        t["boundElements"] = None
        return t["id"]

    def box(self, key, x, y, w, h, label="", color="blue", shape="rectangle", size=17,
            family=HAND, align="center", style="solid", bg=None, sw=2):
        """rectangle | ellipse | diamond with a centered label."""
        stroke, fill = COLORS[color]
        el = self._base(shape, self.ox + x, self.oy + y, w, h, stroke,
                        fill if bg is None else bg, key=key, style=style, sw=sw,
                        roundness={"type": 3} if shape == "rectangle" else {"type": 2})
        if label:
            self._bind_text(el["id"], label, size, family, align)
        return el["id"]

    def proposed(self, key, x, y, w, h, label, color="gray", **kw):
        """A box for a Proposed (not yet decided) component: dashed outline."""
        return self.box(key, x, y, w, h, label + "\n(proposed)", color, style="dashed", **kw)

    def zone(self, key, x, y, w, h, title, color="gray", style="dashed"):
        """A labelled grouping rectangle (not a container: arrows don't bind)."""
        stroke, _ = COLORS[color]
        self._base("rectangle", self.ox + x, self.oy + y, w, h, stroke, "transparent",
                   key=key, style=style, roundness={"type": 3})
        self.text(x + 14, y - 32, title, 21, color=stroke, key=key + ":title")

    def note(self, key, x, y, w, h, s, color="yellow", size=16):
        return self.box(key, x, y, w, h, s, color, align="left", size=size)

    def cylinder(self, key, x, y, w, h, label, color="violet", size=17):
        """Database / store shape. Arrows bind to the body (returned id)."""
        stroke, fill = COLORS[color]
        x, y = self.ox + x, self.oy + y
        g = [self._id(key) + ":g"]
        eh = h * 0.24
        self._base("ellipse", x, y + h - eh, w, eh, stroke, fill, key=key + ":bottom", groups=g,
                   roundness={"type": 2})
        body = self._base("rectangle", x, y + eh / 2, w, h - eh, "transparent", fill, key=key, groups=g)
        for i, lx in enumerate((x, x + w)):
            self._base("line", lx, y + eh / 2, 0, h - eh, stroke, key=f"{key}:side{i}", groups=g,
                       points=[[0, 0], [0, h - eh]], lastCommittedPoint=None, startBinding=None,
                       endBinding=None, startArrowhead=None, endArrowhead=None)
        self._base("ellipse", x, y, w, eh, stroke, fill, key=key + ":top", groups=g, roundness={"type": 2})
        t = self._bind_text(body["id"], label, size, HAND, "center")
        t["y"] += eh / 4
        return body["id"]

    def table(self, key, x, y, name, rows, color="violet", w=320):
        """SQL table: dark header + monospace column list. Arrows bind to body."""
        stroke, _ = COLORS[color]
        x, y = self.ox + x, self.oy + y
        g = [self._id(key) + ":g"]
        self._base("rectangle", x, y, w, 42, stroke, stroke, key=key + ":head", groups=g)
        hw, hh = _measure(name, 21, NORMAL)
        t = self._base("text", x + 14, y + 21 - hh / 2, hw, hh, "#ffffff", key=key + ":name", groups=g,
                       text=name, originalText=name, fontSize=21, fontFamily=NORMAL, textAlign="left",
                       verticalAlign="top", containerId=None, lineHeight=1.25, autoResize=True)
        t["boundElements"] = None
        body = self._base("rectangle", x, y + 42, w, len(rows) * 24 + 22, stroke, "#ffffff",
                          key=key, groups=g)
        self._bind_text(body["id"], "\n".join(rows), 15, MONO, "left")
        return body["id"]

    def lifeline(self, key, x, y, w, length, label, color="gray"):
        """Sequence-diagram participant: header box + dashed vertical line."""
        hid = self.box(key, x, y, w, 70, label, color, size=16)
        cx = x + w / 2
        self._base("line", self.ox + cx, self.oy + y + 70, 0, length, COLORS[color][0],
                   key=key + ":life", style="dashed", sw=1,
                   points=[[0, 0], [0, length]], lastCommittedPoint=None, startBinding=None,
                   endBinding=None, startArrowhead=None, endArrowhead=None)
        return cx

    def message(self, x1, x2, y, label, style="solid", color="ink", key=None, size=15):
        """Unbound horizontal arrow at local y (for sequence diagrams)."""
        stroke = COLORS[color][0]
        dx = x2 - x1
        el = self._base("arrow", self.ox + x1, self.oy + y, abs(dx), 0, stroke, key=key, style=style,
                        roundness=None, points=[[0, 0], [dx, 0]], lastCommittedPoint=None,
                        startBinding=None, endBinding=None, startArrowhead=None, endArrowhead="arrow")
        if label:
            w, h = _measure(label, size, HAND)
            lx = self.ox + min(x1, x2) + abs(dx) / 2 - w / 2
            self._base("text", lx, self.oy + y - h - 4, w, h, MUTED, key=el["id"] + ":label",
                       text=label, originalText=label, fontSize=size, fontFamily=HAND,
                       textAlign="center", verticalAlign="top", containerId=None,
                       lineHeight=1.25, autoResize=True)["boundElements"] = None
        return el["id"]

    # --------------------------------------------------------------- arrows
    def _edge(self, el, tx, ty):
        cx, cy = el["x"] + el["width"] / 2, el["y"] + el["height"] / 2
        dx, dy = tx - cx, ty - cy
        if dx == 0 and dy == 0:
            return cx, cy
        hw, hh = el["width"] / 2, el["height"] / 2
        if el["type"] == "diamond":
            t = 1 / (abs(dx) / hw + abs(dy) / hh)
        elif el["type"] == "ellipse":
            t = 1 / math.sqrt((dx / hw) ** 2 + (dy / hh) ** 2)
        else:
            t = min(hw / abs(dx) if dx else math.inf, hh / abs(dy) if dy else math.inf)
        return cx + dx * t, cy + dy * t

    def arrow(self, a, b, label="", style="solid", color="ink", both=False, offset=0,
              via=None, size=15, key=None, sw=2):
        """Bound arrow from element a to b. `offset` shifts it sideways (use ±
        for a pair of opposite arrows); `via` adds local-coordinate waypoints."""
        a, b = self._id(a), self._id(b)
        ea, eb = self.by_id[a], self.by_id[b]
        ca = (ea["x"] + ea["width"] / 2, ea["y"] + ea["height"] / 2)
        cb = (eb["x"] + eb["width"] / 2, eb["y"] + eb["height"] / 2)
        pts_via = [(self.ox + px, self.oy + py) for px, py in (via or [])]
        ox = oy = 0
        if offset:
            ln = math.hypot(cb[0] - ca[0], cb[1] - ca[1]) or 1
            ox, oy = -(cb[1] - ca[1]) / ln * offset, (cb[0] - ca[0]) / ln * offset
        first = pts_via[0] if pts_via else (cb[0] + ox, cb[1] + oy)
        last = pts_via[-1] if pts_via else (ca[0] + ox, ca[1] + oy)
        sx, sy = self._edge(ea, first[0] - ox, first[1] - oy)
        ex, ey = self._edge(eb, last[0] - ox, last[1] - oy)
        sx, sy, ex, ey = sx + ox, sy + oy, ex + ox, ey + oy
        pts = [(sx, sy)] + pts_via + [(ex, ey)]
        rel = [[px - sx, py - sy] for px, py in pts]
        xs, ys = [p[0] for p in rel], [p[1] for p in rel]
        el = self._base("arrow", sx, sy, max(xs) - min(xs), max(ys) - min(ys), COLORS[color][0],
                        key=key, style=style, sw=sw, roundness={"type": 2} if not via else None,
                        points=rel, lastCommittedPoint=None,
                        startBinding={"elementId": a, "focus": 0, "gap": 6},
                        endBinding={"elementId": b, "focus": 0, "gap": 6},
                        startArrowhead="arrow" if both else None, endArrowhead="arrow")
        ea["boundElements"].append({"type": "arrow", "id": el["id"]})
        eb["boundElements"].append({"type": "arrow", "id": el["id"]})
        if label:
            # label sits at the middle of the longest segment
            segs = list(zip(pts, pts[1:]))
            (p1, p2) = max(segs, key=lambda s: math.hypot(s[1][0] - s[0][0], s[1][1] - s[0][1]))
            w, h = _measure(label, size, HAND)
            t = self._base("text", (p1[0] + p2[0]) / 2 - w / 2, (p1[1] + p2[1]) / 2 - h / 2, w, h,
                           MUTED, key=el["id"] + ":label", text=label, originalText=label,
                           fontSize=size, fontFamily=HAND, textAlign="center", verticalAlign="middle",
                           containerId=el["id"], lineHeight=1.25, autoResize=True)
            t["boundElements"] = None
            el["boundElements"].append({"type": "text", "id": t["id"]})
        return el["id"]

    # ----------------------------------------------------------------- save
    def save(self, path, keep_user_elements=True):
        """Write the board. Hand-drawn elements already in the file are kept."""
        kept = []
        if keep_user_elements and os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                old = json.load(f)
            ids = set(self.by_id)
            for el in old.get("elements", []):
                if el.get("isDeleted") or (el.get("customData") or {}).get("generated"):
                    continue
                if el.get("id") in ids:
                    continue
                if el.get("frameId") and el["frameId"] not in ids:
                    el["frameId"] = None  # its frame was removed
                kept.append(el)
            files = old.get("files", {})
        else:
            files = {}
        doc = {
            "type": "excalidraw", "version": 2,
            "source": "excalidraw-architecture skill",
            "elements": self.elements + kept,
            "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None},
            "files": files,
        }
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=1, ensure_ascii=False)
        frames = sum(1 for e in self.elements if e["type"] == "frame")
        print(f"wrote {path}: {frames} frames, {len(self.elements)} generated + {len(kept)} hand-drawn elements")
