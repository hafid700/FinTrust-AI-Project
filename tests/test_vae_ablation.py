import json

import numpy as np
import pytest

from src.data.load import load_transactions
from src.detection.aggregate import collect
from src.detection.vae_ablation import repair, run_ablation


def test_repair_produces_valid_samples():
    names = ["same_currency", "cross_bank", "payment_format_ACH", "payment_format_Wire",
             "payment_currency_Euro", "payment_currency_Yen", "src_out_cnt_all", "src_passthrough_all"]
    X = np.random.default_rng(0).normal(size=(50, len(names))).astype(np.float32)
    R = repair(X, names)
    assert set(np.unique(R[:, :2])) <= {0.0, 1.0}
    assert (R[:, 2:4].sum(axis=1) == 1).all() and (R[:, 4:6].sum(axis=1) == 1).all()
    assert (R[:, 6] >= 0).all()
    assert (R[:, 7] == X[:, 7]).all()                       # passthrough peut être négatif : inchangé


def test_ablation_without_vae(fake_csv, tmp_path):
    df = load_transactions(str(fake_csv))
    s = run_ablation(df, variants=("none", "class_weight", "oversample", "smote"), seeds=(1,), ratio=0.1,
                     out_dir=str(tmp_path))
    assert set(s) == {"none", "class_weight", "oversample", "smote"}
    for v in s.values():
        assert 0.0 <= v["pr_auc"]["mean"] <= 1.0
    assert json.loads((tmp_path / "ablation.json").read_text())["config"]["seeds"] == [1]


def test_vae_smoke(fake_csv, tmp_path):
    pytest.importorskip("torch")
    df = load_transactions(str(fake_csv))
    s = run_ablation(df, variants=("vae",), seeds=(1,), ratio=0.1, latent_dims=(2,), epochs=3, out_dir=str(tmp_path))
    r = s["vae_d2"]["per_seed"][0]
    assert r["n_synthetic"] > 0 and r["realism_auc"] is not None
    assert (tmp_path / "latent_space.png").exists() and (tmp_path / "vae_training.png").exists()


def test_aggregate_collect(tmp_path):
    for i, v in enumerate((0.7, 0.8)):
        d = tmp_path / f"s{i}"; d.mkdir()
        (d / "m.json").write_text(json.dumps({"model": "m", "test": {"pr_auc": v}}))
    g = collect([tmp_path / "s0", tmp_path / "s1"])
    assert np.isclose(np.mean([t["pr_auc"] for t in g["m"]]), 0.75)
