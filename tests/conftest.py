import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def fake_csv(tmp_path):
    """CSV factice au même schéma qu'IBM AML (deux colonnes 'Account')."""
    rng = np.random.default_rng(0)
    n = 5000
    ts = pd.date_range("2022-09-01", periods=n, freq="min").strftime("%Y/%m/%d %H:%M")
    accts = [f"A{i:04d}" for i in range(400)]
    df = pd.DataFrame({
        "Timestamp": ts,
        "From Bank": rng.integers(1, 6, n),
        "Account": rng.choice(accts, n),
        "To Bank": rng.integers(1, 6, n),
        "Account.1": rng.choice(accts, n),
        "Amount Received": rng.lognormal(6, 1, n),
        "Receiving Currency": rng.choice(["US Dollar", "Euro", "Yen"], n),
        "Amount Paid": rng.lognormal(6, 1, n),
        "Payment Currency": rng.choice(["US Dollar", "Euro", "Yen"], n),
        "Payment Format": rng.choice(["Cheque", "ACH", "Credit Card"], n),
        "Is Laundering": (rng.random(n) < 0.01).astype(int),
    })
    df = df.rename(columns={"Account.1": "Account"})  # reproduit l'en-tête brut
    p = tmp_path / "fake.csv"
    df.to_csv(p, index=False)
    return p
