import csv
import random
from datetime import datetime, timedelta
import math

OUTPUT_PATH = "input/sample.csv"
SECONDS = 7200
BASE_CURRENT = 20.0
NOISE = 0.2
DRIFT = 0.3

start_time = datetime(2026, 1, 14, 10, 0, 0)

with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Date","Time","Laptime","Laptime(ms)","STATUS_MAXMIN","Idc_1(A)","Idc_2(A)","Idc_3(A)"])
    for t in range(SECONDS):
        now = start_time + timedelta(seconds=t)
        drift = DRIFT * math.sin(2 * math.pi * t / SECONDS)
        idc1 = BASE_CURRENT + drift + random.uniform(-NOISE, NOISE)
        idc2 = BASE_CURRENT + drift + random.uniform(-NOISE, NOISE) + 0.05
        idc3 = BASE_CURRENT + drift + random.uniform(-NOISE, NOISE) - 0.05
        status = "NORMAL"
        if random.random() < 0.002:
            status = "WARN"
        w.writerow([now.strftime("%Y/%m/%d"), now.strftime("%H:%M:%S"), t, t*1000, status,
                    round(idc1,3), round(idc2,3), round(idc3,3)])
print("ダミーCSVを作成しました:", OUTPUT_PATH)
