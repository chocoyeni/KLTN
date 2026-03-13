import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))


// part 2 

import pandas as pd
import numpy as np

#load data vào 
df = pd.read_csv("/kaggle/input/data-kltn/kt1_merged_sample.csv")

# chuẩn hóa lowercase
for col in ["user_answer", "correct_answer"]:
    df[col] = df[col].astype("string").str.strip().str.lower()

# blank 
df["is_blank"] = df["user_answer"].isna() | (df["user_answer"] == "")

df["answer_status"] = np.select(
    [
        df["is_blank"],
        (~df["is_blank"]) & (df["user_answer"] == df["correct_answer"]),
        (~df["is_blank"]) & (df["user_answer"] != df["correct_answer"])
    ],
    ["blank", "correct", "wrong"],
    default="unknown"
)

# blank thì không tính đúng/sai
df["is_correct_valid"] = pd.Series(
    np.where(df["is_blank"], pd.NA, (df["user_answer"] == df["correct_answer"])),
    dtype="boolean"
)

# bản int để tính difficulty
df["is_correct_valid_int"] = df["is_correct_valid"].astype("Int8")  # có NA

# chuẩn hóa time
# nếu chưa có elapsed_time_sec thì tạo từ ms
if "elapsed_time_sec" not in df.columns:
    df["elapsed_time_sec"] = df["elapsed_time"] / 1000

# tạo time flag
df["time_flag"] = np.select(
    [
        df["elapsed_time_sec"].isna(),
        df["elapsed_time_sec"] < 1,
        df["elapsed_time_sec"] > 300,
    ], 
    ["missing", "too_fast", "too_long"],
    default="valid"
)

df["time_valid"] = (df["time_flag"] == "valid").astype("Int8")

# chỉ giữ time hợp lệ
df["elapsed_time_sec_valid"] = df["elapsed_time_sec"].where(df["time_valid"] == 1)

# answer valid chỉ có a b c d
df["answer_valid"] = df["user_answer"].isin(["a", "b", "c", "d"])
df["user_answer_abcd"] = df["user_answer"].where(df["answer_valid"])

# chuẩn hóa các cột id text + trim
for col in ["user_id", "question_id", "bundle_id", "tags"]:
    df[col] = df[col].astype("string").str.strip()

# xuất
out_path = "kt1_merged_sample_clean.csv"
df.to_csv(out_path, index=false)

print(" DONE. Exported:", out_path)
print("Rows:", len(df))
print("Blank rate:", df["is_blank"].mean())
print("Time valid rate:", df["time_valid"].mean())
print("Answer valid rate:", df["answer_valid"].mean())

//part 3

import pandas as pd
import os

df = pd.read_csv("/kaggle/input/data-kltn/kt1_merged_sample.csv")

out_dir = "data_by_part"
os.makedirs(out_dir, exist_ok=True)

# Tách thành 7 file
for p in sorted(df["part"].dropna().unique()):
    df_p = df[df["part"] == p]
    
    print(f"Part {p}: {len(df_p)} rows")
    
    df_p.to_csv(f"{out_dir}/data_part{p}.csv", index=False)

print(" Đã tách xong 7 part")