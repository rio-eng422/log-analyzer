import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

from sub import load_log_csv, IDC_COLS

def main():
    parser = argparse.ArgumentParser(description="電流ログCSVを解析して出力します")
    parser.add_argument("--input", required=True, help="入力CSVパス")
    parser.add_argument("--skip_sec", type=float, default=60.0,
                        help="開始から何秒分を除外するか（デフォルト: 60秒）")
    parser.add_argument("--min_total", type=float, default=1.0,
                        help="合計電流がこの値以下の行を除外します（デフォルト: 1.0A）")
    args = parser.parse_args()

    input_path = Path(args.input)
    out_dir = Path("output")
    plot_dir = out_dir / "plots"
    out_dir.mkdir(exist_ok=True)
    plot_dir.mkdir(exist_ok=True)

    df = load_log_csv(str(input_path))

    missing_cols = [c for c in IDC_COLS if c not in df.columns]
    if missing_cols:
        raise KeyError(f"必要な電流列が見つかりません: {missing_cols}")

    for c in IDC_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    dt = None
    if ("Date" in df.columns) and ("Time" in df.columns):
        dt = pd.to_datetime(
            df["Date"].astype(str).str.strip() + " " + df["Time"].astype(str).str.strip(),
            errors="coerce"
        )

    before_rows_time = len(df)
    if dt is not None and dt.notna().any():
        t0_all = dt.dropna().iloc[0]
        df = df[dt >= (t0_all + pd.Timedelta(seconds=args.skip_sec))].copy()
        dt = dt.loc[df.index]
        print(f"[INFO] skip_sec={args.skip_sec}s: {before_rows_time} → {len(df)} 行")
    else:
        print("[WARN] Date/Time が使えないため skip_sec は適用できません")

    before_rows_total = len(df)
    total = df[IDC_COLS].sum(axis=1, min_count=1)
    df = df[total > args.min_total].copy()
    if dt is not None:
        dt = dt.loc[df.index]
    removed = before_rows_total - len(df)
    if removed > 0:
        print(f"[INFO] min_total={args.min_total}A: {removed} 行を除外（残り {len(df)} 行）")

    summary = []
    for c in IDC_COLS:
        s = df[c]
        summary.append({"column": c, "min": s.min(), "max": s.max(), "mean": s.mean(), "std": s.std()})
    summary_df = pd.DataFrame(summary)
    (out_dir / "summary.csv").write_text(summary_df.to_csv(index=False), encoding="utf-8")

    if dt is not None and dt.notna().any():
        t0 = dt.dropna().iloc[0]
        x = (dt - t0).dt.total_seconds()
        xlabel = "Elapsed time (s)"
    elif "Laptime(ms)" in df.columns:
        x = pd.to_numeric(df["Laptime(ms)"], errors="coerce")
        xlabel = "Laptime(ms)"
    elif "Laptime" in df.columns:
        x = pd.to_numeric(df["Laptime"], errors="coerce")
        xlabel = "Laptime"
    else:
        x = range(len(df))
        xlabel = "index"

    plt.figure()
    for c in IDC_COLS:
        plt.plot(x, df[c], label=c)
    plt.xlabel(xlabel)
    plt.ylabel("Current (A)")
    plt.legend()
    plt.title("IDC currents (filtered)")
    plt.savefig(plot_dir / "idc_timeseries.png", dpi=150, bbox_inches="tight")
    plt.close()

    report_lines = []
    report_lines.append("# 電流ログ解析レポート\n")
    report_lines.append(f"- 入力ファイル: `{input_path}`")
    report_lines.append(f"- 評価開始: 開始から{args.skip_sec}秒以降")
    report_lines.append(f"- 0A区間除外条件: 合計電流 > {args.min_total}A")
    report_lines.append(f"- 行数: {before_rows_time} → {len(df)}")
    report_lines.append("")
    report_lines.append("## サマリ（CSV形式）")
    report_lines.append("```")
    report_lines.append(summary_df.to_csv(index=False))
    report_lines.append("```")
    (out_dir / "report.md").write_text("\n".join(report_lines), encoding="utf-8")

    print("完了しました。output フォルダを確認してください。")

if __name__ == "__main__":
    main()
