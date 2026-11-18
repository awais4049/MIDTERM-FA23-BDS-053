import json
from pathlib import Path
import pandas as pd

def test_config_and_dataset():
    config = json.loads(Path("config.json").read_text())
    df = pd.read_csv("dataset/train.csv")
    assert set(config["features"] + ["label"]).issubset(df.columns)
    assert len(df) >= 100
    assert df["label"].nunique() == 2