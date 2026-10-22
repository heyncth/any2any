from any2any_core.models import FormatDecl, OptionSpec, PairSpec
from any2any_core.registry import AdapterMeta, Registry, build_registry


def test_builtins_load():
    reg = build_registry(load_plugins=False)
    assert "png" in reg.formats
    assert "csv" in reg.formats
    assert len(reg.adapters) >= 5
    assert len(reg.edges) > 20
    assert reg.broken == []


def test_duplicate_format_rejected():
    reg = Registry()
    f = FormatDecl("x", "util", (".x",), None, False)
    reg.register_format(f)
    try:
        reg.register_format(f)
        raise AssertionError("expected")
    except Exception as e:
        assert "duplicate" in str(e)


def test_unknown_format_disables_adapter():
    reg = Registry()
    reg.register_format(FormatDecl("a", "util", (".a",), None, False))
    meta = AdapterMeta(
        id="bad",
        sources=("a", "ghost"),
        targets=("a",),
        pairs={},
        requires=(),
        options=(),
        execute=lambda c: None,
    )
    reg.register_adapter(meta)
    assert "bad" not in reg.adapters
    assert reg.broken and reg.broken[0]["adapter"] == "bad"


def test_duplicate_pair_disables_adapter():
    reg = Registry()
    for fid in ("a", "b"):
        reg.register_format(FormatDecl(fid, "util", (f".{fid}",), None, False))
    from any2any_core.adapters.images import execute as _dummy

    m1 = AdapterMeta("m1", ("a",), ("b",), {("a", "b"): PairSpec("a", "b")}, (), (), execute=_dummy)
    m2 = AdapterMeta("m2", ("a",), ("b",), {("a", "b"): PairSpec("a", "b")}, (), (), execute=_dummy)
    reg.register_adapter(m1)
    reg.register_adapter(m2)
    assert "m1" in reg.adapters
    assert "m2" not in reg.adapters


def test_choice_option_requires_choices():
    reg = Registry()
    reg.register_format(FormatDecl("a", "util", (".a",), None, False))
    meta = AdapterMeta(
        "bad2",
        ("a",),
        ("a",),
        {},
        (),
        (OptionSpec("mode", "choice"),),  # no choices
        execute=lambda c: None,
    )
    # sources==targets with empty pairs → cross product s!=t is empty, ok; bad option should disable
    reg.register_adapter(meta)
    assert "bad2" not in reg.adapters
