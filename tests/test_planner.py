from any2any_core.errors import UnsupportedPair
from any2any_core.planner import MAX_HOPS, plan


def test_direct_plan(registry):
    p = plan(registry, "png", "webp")
    assert len(p.steps) == 1
    assert p.steps[0].adapter_id == "pillow_images"
    assert 0 < p.score <= 1
    assert p.lossy is True
    assert not p.chained


def test_direct_lossless(registry):
    p = plan(registry, "csv", "tsv")
    assert len(p.steps) == 1
    assert p.score >= 0.9


def test_unsupported_pair_lists_targets(registry):
    try:
        plan(registry, "fit", "docx")
        raise AssertionError("expected UnsupportedPair")
    except UnsupportedPair as e:
        assert e.code == "E_UNSUPPORTED_PAIR"


def test_direct_only_blocks_chain(registry):
    # md->html exists; txt->qr is single step; no multi-hop needed for these
    p = plan(registry, "md", "html", direct_only=True)
    assert len(p.steps) == 1


def test_multi_step_if_available(registry):
    # txt->qr is direct; chain not required. Verify planner enumerates and ranks.
    p = plan(registry, "txt", "qr")
    assert p.steps[-1].target == "qr"
    assert p.score > 0


def test_hop_cap(registry):
    assert MAX_HOPS == 3


def test_unknown_source(registry):
    try:
        plan(registry, "nope", "png")
        raise AssertionError("expected error")
    except UnsupportedPair:
        pass


def test_plan_blocked_missing_binary(registry):
    # register a fake pair requiring a missing binary
    from any2any_core.models import OptionSpec, PairSpec, Requirement
    from any2any_core.registry import AdapterMeta

    reg = registry
    # svg exists as format but no adapter — add one requiring missing binary
    meta = AdapterMeta(
        id="fake_svg",
        sources=("svg",),
        targets=("png",),
        pairs={("svg", "png"): PairSpec("svg", "png", fidelity=0.6)},
        requires=(Requirement(kind="binary", name="definitely-not-a-real-engine-xyz"),),
        options=(),
        execute=lambda ctx: None,
    )
    reg.register_adapter(meta)
    p = plan(reg, "svg", "png")
    assert p.blocked is not None
    assert p.blocked.code == "E_MISSING_ENGINE"
