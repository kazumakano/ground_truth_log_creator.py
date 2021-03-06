from __future__ import annotations
import csv
import os.path as path
import pickle
from datetime import datetime
from typing import Any, Optional
import numpy as np
import yaml
from scipy.interpolate import interp1d


def _set_params(conf_file: str | None) -> None:
    global ROOT_DIR, BEGIN, FREQ

    ROOT_DIR = path.join(path.dirname(__file__), "../")

    if conf_file is None:
        conf_file = path.join(ROOT_DIR, "config/default.yaml")
    print(f"{path.basename(conf_file)} has been loaded")

    with open(conf_file) as f:
        conf: dict[str, Any] = yaml.safe_load(f)
    BEGIN = datetime.strptime(conf["begin"], "%Y-%m-%d %H:%M:%S")
    FREQ = np.float32(conf["freq"])

def _load_log(file: str) -> np.ndarray:
    data = np.loadtxt(file, dtype=np.float32, delimiter=",")
    print(f"{path.basename(file)} has been loaded")

    return data

def _resample_log(data: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    resampled_ts = np.arange(data[0, 0], data[-1, 0], step=1/FREQ, dtype=np.float64)

    resampled_pos = np.empty((len(resampled_ts), 2), dtype=np.float32)
    for i in range(2):
        resampled_pos[:, i] = interp1d(data[:, 0], data[:, i+1])(resampled_ts)

    return resampled_pos, resampled_ts

def _conv2datetime(ts: np.ndarray) -> np.ndarray:
    ts = ts.astype(object)

    offset = BEGIN - datetime.fromtimestamp(ts[0])
    for i, t in enumerate(ts):
        ts[i] = datetime.fromtimestamp(t) + offset

    return ts.astype(datetime)

def create_log(src_file: str, tgt_dir: Optional[str] = None) -> None:
    if tgt_dir is None:
        tgt_dir = path.join(ROOT_DIR, "formatted/")

    data = _load_log(src_file)
    pos, ts = (data[:, 1:], data[:, 0]) if FREQ == 0 else _resample_log(data)
    ts = _conv2datetime(ts)

    tgt_file = path.join(tgt_dir, path.splitext(path.basename(src_file))[0] + ".csv")
    with open(tgt_file, mode="w", newline="") as f:
        writer = csv.writer(f)
        t: datetime
        for i, t in enumerate(ts):
            writer.writerow((t.strftime("%Y-%m-%d %H:%M:%S.%f"), *pos[i]))

    print(f"written to {path.basename(tgt_file)}")

    tgt_file = path.join(tgt_dir, path.splitext(path.basename(src_file))[0] + ".pkl")
    with open(tgt_file, mode="wb") as f:
        pickle.dump((ts, pos), f)
    
    print(f"written to {path.basename(tgt_file)}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--conf_file", help="specify config file", metavar="PATH_TO_CONF_FILE")
    parser.add_argument("-s", "--src_file", required=True, help="specify source file", metavar="PATH_TO_SRC_FILE")
    parser.add_argument("-t", "--tgt_dir", help="specify target directory", metavar="PATH_TO_TGT_DIR")
    args = parser.parse_args()

    _set_params(args.conf_file)

    create_log(args.src_file, args.tgt_dir)
