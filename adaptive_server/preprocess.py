import pandas as pd
import numpy as np
from sqlalchemy import create_engine

# kết nối mysql
DB_USER = "moodleuser"
DB_PASS = "1234"
DB_HOST = "192.168.74.129"
DB_NAME = "moodle"

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
)

# query dữ liệu interaction
query = """
SELECT
    user_id,
    question_id,
    user_answer,
    correct_answer,
    elapsed_time,
    timestamp
FROM mdl_local_ednet_interactions
"""

# đọc dữ liệu từ mysql
df = pd.read_sql(query, engine)

print("\n--- RAW ---")
print("Rows:", len(df))

# chuẩn hóa đáp án
for col in ["user_answer", "correct_answer"]:

    df[col] = (
        df[col]
        .astype("string")
        .str.strip()
        .str.lower()
    )

# kiểm tra bỏ trống
df["is_blank"] = (
    df["user_answer"].isna()
    | (df["user_answer"] == "")
)

# phân loại trạng thái đáp án
df["answer_status"] = np.select(
    [
        df["is_blank"],

        (~df["is_blank"])
        & (df["user_answer"] == df["correct_answer"]),

        (~df["is_blank"])
        & (df["user_answer"] != df["correct_answer"])
    ],
    ["blank", "correct", "wrong"],
    default="unknown"
)

# tạo cột đúng sai
df["is_correct_valid"] = pd.Series(
    np.where(
        df["is_blank"],
        pd.NA,
        (
            df["user_answer"]
            == df["correct_answer"]
        )
    ),
    dtype="boolean"
)

df["is_correct"] = (
    df["is_correct_valid"]
    .astype("Int8")
)

# đổi thời gian sang giây
df["elapsed_time_sec"] = (
    df["elapsed_time"] / 1000
)

# ép kiểu numeric
df["response_time"] = pd.to_numeric(
    df["elapsed_time_sec"],
    errors="coerce"
)

# xóa dữ liệu null
df = df.dropna(subset=[
    "user_id",
    "question_id",
    "is_correct",
    "response_time"
])

# chỉ giữ response time > 0
df = df[
    df["response_time"] > 0
]

# format user và question id
for col in ["user_id", "question_id"]:

    df[col] = (
        df[col]
        .astype("string")
        .str.strip()
    )

# xử lý timestamp
df["timestamp"] = pd.to_numeric(
    df["timestamp"],
    errors="coerce"
)

# sort theo user question timestamp
df = df.sort_values(
    by=["user_id", "question_id", "timestamp"]
)

# bỏ duplicate
df = df.drop_duplicates(
    ["user_id", "question_id"],
    keep="first"
)

print("\n--- AFTER DUPLICATE ---")
print("Rows:", len(df))

# tính log response time
df["log_RT"] = np.log(
    df["response_time"]
)

# tính mean std theo item
stats = (
    df.groupby("question_id")["log_RT"]
    .agg(["mean", "std"])
    .reset_index()
    .rename(columns={
        "mean": "m_log",
        "std": "s_log"
    })
)

# merge thống kê
df = df.merge(
    stats,
    on="question_id",
    how="left"
)

# bỏ item không có variance
df = df[
    df["s_log"] > 0
]

# tính z-score
df["log_z_score"] = (
    (df["log_RT"] - df["m_log"])
    / df["s_log"]
)

# phát hiện outlier
z_threshold = 2.5

df["is_outlier"] = (
    (df["log_z_score"] < -z_threshold)
    |
    (df["log_z_score"] > z_threshold)
)

# bỏ outlier
df_clean = df[
    ~df["is_outlier"]
].copy()

# lấy dữ liệu cuối cùng
df_final = df_clean[[
    "user_id",
    "question_id",
    "is_correct",
    "log_RT"
]].copy()

# ép kiểu int8
df_final["is_correct"] = (
    df_final["is_correct"]
    .astype("int8")
)

# encode user
df_final["user_idx"], _ = pd.factorize(
    df_final["user_id"]
)

# encode item
df_final["item_idx"], _ = pd.factorize(
    df_final["question_id"]
)

# dataframe encode
df_encoded = df_final[[
    "user_idx",
    "item_idx",
    "is_correct",
    "log_RT"
]].copy()

# lưu file thường
df_final.to_csv(
    "irt_rt_input2.csv",
    index=False
)

# lưu file encode
df_encoded.to_csv(
    "irt_rt_input_encoded2.csv",
    index=False
)

# in thống kê cuối
print("\n DONE ")

print("Final rows:", len(df_final))

print("Users:", df_final["user_id"].nunique())

print("Items:", df_final["question_id"].nunique())
