"""Geo adapter: GPX / KML / GeoJSON core geometry+name only (docs M2 scope)."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from ..errors import ParseError
from ..models import PairSpec, Requirement
from ..registry import AdapterMeta, Registry

FORMATS = ("gpx", "kml", "geojson")


@dataclass
class Wpt:
    lat: float
    lon: float
    ele: float | None = None
    time: str | None = None
    name: str | None = None


class StepContext:
    def __init__(self, input_path, output_path, options, temp_dir, token=None, progress=None):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.options = options
        self.temp_dir = temp_dir
        self.token = token
        self.progress = progress

    def cancelled(self) -> bool:
        return bool(self.token is not None and getattr(self.token, "is_set", lambda: False)())


def _strip_ns(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def parse_gpx(path: Path) -> list[Wpt]:
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        raise ParseError(f"{path.name}: {e}") from e
    root = tree.getroot()
    if _strip_ns(root.tag) != "gpx":
        raise ParseError(f"{path.name}: not a GPX document")
    wpts: list[Wpt] = []
    for el in root.iter():
        tag = _strip_ns(el.tag)
        if tag not in ("wpt", "trkpt", "rtept"):
            continue
        try:
            lat = float(el.attrib["lat"])
            lon = float(el.attrib["lon"])
        except (KeyError, ValueError) as e:
            raise ParseError(f"{path.name}: bad point coordinates") from e
        ele = None
        time_ = None
        name = None
        for child in el:
            ct = _strip_ns(child.tag)
            if ct == "ele" and child.text:
                try:
                    ele = float(child.text)
                except ValueError:
                    pass
            elif ct == "time" and child.text:
                time_ = child.text.strip()
            elif ct == "name" and child.text:
                name = child.text.strip()
        wpts.append(Wpt(lat, lon, ele, time_, name))
    if not wpts:
        raise ParseError(f"{path.name}: no points")
    return wpts


def parse_kml(path: Path) -> list[Wpt]:
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        raise ParseError(f"{path.name}: {e}") from e
    root = tree.getroot()
    if _strip_ns(root.tag) != "kml":
        raise ParseError(f"{path.name}: not a KML document")
    wpts: list[Wpt] = []
    for placemark in root.iter():
        if _strip_ns(placemark.tag) != "Placemark":
            continue
        name = None
        coord_text = None
        for child in placemark:
            ct = _strip_ns(child.tag)
            if ct == "name" and child.text:
                name = child.text.strip()
            elif ct in ("Point", "LineString", "LinearRing"):
                for sub in child:
                    if _strip_ns(sub.tag) == "coordinates" and sub.text:
                        coord_text = sub.text.strip()
        if not coord_text:
            continue
        for tok in coord_text.split():
            parts = tok.split(",")
            if len(parts) < 2:
                continue
            try:
                lon, lat = float(parts[0]), float(parts[1])
            except ValueError:
                continue
            ele = float(parts[2]) if len(parts) > 2 and parts[2] else None
            wpts.append(Wpt(lat, lon, ele, None, name))
    if not wpts:
        raise ParseError(f"{path.name}: no points")
    return wpts


def parse_geojson(path: Path) -> list[Wpt]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as e:
        raise ParseError(f"{path.name}: line {e.lineno}: {e.msg}") from e
    wpts: list[Wpt] = []

    def walk(obj, name=None):
        if isinstance(obj, dict):
            t = obj.get("type")
            if t == "FeatureCollection":
                for f in obj.get("features", []):
                    walk(f)
            elif t == "Feature":
                walk(obj.get("geometry"), obj.get("properties", {}).get("name") if isinstance(obj.get("properties"), dict) else None)
            elif t == "Point":
                c = obj.get("coordinates", [])
                if len(c) >= 2:
                    wpts.append(Wpt(float(c[1]), float(c[0]), float(c[2]) if len(c) > 2 else None, None, name))
            elif t in ("LineString", "MultiPoint"):
                for c in obj.get("coordinates", []):
                    if len(c) >= 2:
                        wpts.append(Wpt(float(c[1]), float(c[0]), float(c[2]) if len(c) > 2 else None, None, name))
            elif t == "Polygon":
                for ring in obj.get("coordinates", []):
                    for c in ring:
                        if len(c) >= 2:
                            wpts.append(Wpt(float(c[1]), float(c[0]), float(c[2]) if len(c) > 2 else None, None, name))
            elif t == "MultiLineString":
                for line in obj.get("coordinates", []):
                    for c in line:
                        if len(c) >= 2:
                            wpts.append(Wpt(float(c[1]), float(c[0]), float(c[2]) if len(c) > 2 else None, None, name))
        elif isinstance(obj, list):
            for i in obj:
                walk(i, name)

    walk(data)
    if not wpts:
        raise ParseError(f"{path.name}: no points")
    return wpts


def write_gpx(wpts: list[Wpt], name: str | None = None) -> str:
    import gpxpy.gpx

    gpx = gpxpy.gpx.GPX()
    gpx.name = name or "Any2Any export"
    track = gpxpy.gpx.GPXTrack(name=gpx.name)
    gpx.tracks.append(track)
    seg = gpxpy.gpx.GPXTrackSegment()
    track.segments.append(seg)
    for w in wpts:
        seg.points.append(gpxpy.gpx.GPXTrackPoint(w.lat, w.lon, elevation=w.ele, time=_parse_time(w.time)))
    return gpx.to_xml()


def _parse_time(s: str | None):
    if not s:
        return None
    from datetime import datetime

    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(s.replace("+00:00", "Z"), fmt)
        except ValueError:
            continue
    return None


def write_kml(wpts: list[Wpt], name: str | None = None) -> str:
    kml_name = name or "Any2Any export"
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<kml xmlns="http://www.opengis.net/kml/2.2">',
        "<Document>",
        f"<name>{_xml_escape(kml_name)}</name>",
    ]
    for w in wpts:
        lines.append("<Placemark>")
        if w.name:
            lines.append(f"<name>{_xml_escape(w.name)}</name>")
        lines.append("<Point>")
        ele = f",{w.ele}" if w.ele is not None else ""
        lines.append(f"<coordinates>{w.lon},{w.lat}{ele}</coordinates>")
        lines.append("</Point>")
        lines.append("</Placemark>")
    lines += ["</Document>", "</kml>", ""]
    return "\n".join(lines)


def _xml_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def write_geojson(wpts: list[Wpt], name: str | None = None) -> str:
    features = []
    for w in wpts:
        coords = [w.lon, w.lat] + ([w.ele] if w.ele is not None else [])
        props = {}
        if w.name:
            props["name"] = w.name
        if w.time:
            props["time"] = w.time
        features.append({"type": "Feature", "properties": props, "geometry": {"type": "Point", "coordinates": coords}})
    doc = {"type": "FeatureCollection", "features": features}
    if name:
        doc["name"] = name
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


def execute(ctx: StepContext) -> None:
    src = ctx.input_path.suffix.lower().lstrip(".")
    tgt = ctx.output_path.suffix.lower().lstrip(".")
    if src == "gpx":
        wpts = parse_gpx(ctx.input_path)
    elif src == "kml":
        wpts = parse_kml(ctx.input_path)
    else:
        wpts = parse_geojson(ctx.input_path)
    name = ctx.input_path.stem
    if tgt == "gpx":
        out = write_gpx(wpts, name)
    elif tgt == "kml":
        out = write_kml(wpts, name)
    else:
        out = write_geojson(wpts, name)
    ctx.output_path.write_text(out, encoding="utf-8")


def register(reg: Registry) -> None:
    # gpxpy only needed for gpx write; lxml NOT used (stdlib ET)
    pairs = {
        ("gpx", "kml"): PairSpec("gpx", "kml", fidelity=0.90, test_fixture="tests/fixtures/geo/track.gpx"),
        ("gpx", "geojson"): PairSpec("gpx", "geojson", fidelity=0.90, test_fixture="tests/fixtures/geo/track.gpx"),
        ("kml", "gpx"): PairSpec("kml", "gpx", fidelity=0.90, test_fixture="tests/fixtures/geo/route.kml"),
        ("kml", "geojson"): PairSpec("kml", "geojson", fidelity=0.90, test_fixture="tests/fixtures/geo/route.kml"),
        ("geojson", "gpx"): PairSpec("geojson", "gpx", fidelity=0.90, test_fixture="tests/fixtures/geo/points.geojson"),
        ("geojson", "kml"): PairSpec("geojson", "kml", fidelity=0.90, test_fixture="tests/fixtures/geo/points.geojson"),
    }
    reg.register_adapter(
        AdapterMeta(
            id="geo",
            sources=FORMATS,
            targets=FORMATS,
            pairs=pairs,
            requires=(Requirement(kind="python", name="gpxpy", license="Apache-2.0"),),
            options=(),
            execute=execute,
        )
    )
