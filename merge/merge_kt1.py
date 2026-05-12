import os
import glob
import pandas as pd

# đọc thư mục dữ liệu mẫu
KT1_SAMPLE_DIR = r"C:\Users\Admin\Downloads\KT1-3000user"

# file chứa thông tin câu hỏi
QUESTIONS_PATH = r"C:\Users\Admin\Downloads\KT1-3000user\questions.csv"

# file output sau khi merge
OUT_CSV = r"C:\Users\Admin\Downloads\kt1_merged_sample_part.csv"

# chọn part muốn lấy
TARGET_PART = 2

# đọc file questions
print("Đang đọc file questions...")

questions = pd.read_csv(
    QUESTIONS_PATH,
    usecols=["question_id", "correct_answer", "part", "tags", "bundle_id"]
)

print("Tổng số câu ban đầu:", len(questions))

# lọc theo part
questions = questions[questions["part"] == TARGET_PART]

print(f"Sau khi lọc part = {TARGET_PART}: {len(questions)} câu")

# quét các file user
print("\nBắt đầu quét các file trong thư mục KT1...")

files = glob.glob(os.path.join(KT1_SAMPLE_DIR, "u*.csv"))

print("Tổng số file tìm được:", len(files))

dfs = []

unique_users = set()
unique_questions = set()

# đọc từng file user
for i, f in enumerate(files, 1):

    user_id = os.path.splitext(os.path.basename(f))[0]

    unique_users.add(user_id)

    df = pd.read_csv(f)

    unique_questions.update(df["question_id"].unique())

    df["user_id"] = user_id

    dfs.append(df)

    if i % 200 == 0:
        print(f"Đã load {i} file...")

# gộp toàn bộ dataframe
print("\nĐang gộp tất cả file...")

data = pd.concat(dfs, ignore_index=True)

print("Rows trước merge:", len(data))

# merge với questions
print("\nGhép với questions...")

data = data.merge(questions, on="question_id", how="inner")

print("Rows sau merge:", len(data))

# tạo cột đúng sai
print("\nTạo cột đúng sai...")

data["is_correct"] = (
    data["user_answer"] == data["correct_answer"]
).astype("int8")

# đổi thời gian sang giây
print("Chuyển thời gian sang giây...")

data["elapsed_time_sec"] = (
    data["elapsed_time"] / 1000
).round(2)

# lưu file output
print("\nLưu file...")

data.to_csv(
    OUT_CSV,
    index=False,
    encoding="utf-8-sig"
)

# thống kê dữ liệu
print("\n===== THỐNG KÊ =====")

print("File output:", OUT_CSV)

print("Tổng số dòng:", len(data))

print("Số user:", data["user_id"].nunique())

print("Số item:", data["question_id"].nunique())

# in thử vài dòng
print("\nSample:")

print(data.head())
