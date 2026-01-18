from pathlib import Path
import pandas as pd

IDC_COLS = ["Idc_1(A)", "Idc_2(A)", "Idc_3(A)"]

COLUMN_ALIASES = {
    "Idc1(A)": "Idc_1(A)",
    "Idc2(A)": "Idc_2(A)",
    "Idc3(A)": "Idc_3(A)",
    "Idc 1(A)": "Idc_1(A)",
    "Idc 2(A)": "Idc_2(A)",
    "Idc 3(A)": "Idc_3(A)",
}

def _detect_header_row(path: Path, max_rows: int = 40) -> int | None:
    preview = pd.read_csv(path, header=None, nrows=max_rows, dtype=str, engine="python")
    for i in range(len(preview)):
        row = preview.iloc[i].astype(str).str.strip().tolist()
        if "Date" in row:
            return i
    return None

def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.astype(str).str.strip()
    rename_map = {c: COLUMN_ALIASES[c] for c in df.columns if c in COLUMN_ALIASES}
    if rename_map:
        df = df.rename(columns=rename_map)
    return df

def load_log_csv(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"入力CSVが見つかりません: {p}")

    header_row = _detect_header_row(p)
    if header_row is None:
        df = pd.read_csv(p, engine="python")
    else:
        df = pd.read_csv(p, header=header_row, engine="python")

    return _normalize_columns(df)
