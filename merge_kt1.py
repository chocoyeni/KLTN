import os
import glob
import pandas as pd

# mỗi file là 1 user
KT1_SAMPLE_DIR = r"C:\Users\yennh\Downloads\KT1-3000user"

# file đáp án
QUESTIONS_PATH = r"C:\Users\yennh\Downloads\KT1-3000user\questions.csv"

# gộp xong
OUT_CSV = r"C:\Users\yennh\Downloads\kt1_merged_sample.csv"

print("Đang đọc file questions...")
questions = pd.read_csv(
    QUESTIONS_PATH,
    usecols=["question_id", "correct_answer", "part", "tags", "bundle_id"]
)

print("Bắt đầu quét các file trong thư mục KT1...")
files = glob.glob(os.path.join(KT1_SAMPLE_DIR, "u*.csv"))
print("Tổng số file tìm được:", len(files))

dfs = []

for i, f in enumerate(files, 1):
    # Lấy tên user từ tên file
    user_id = os.path.splitext(os.path.basename(f))[0]

    # Đọc file của từng user
    df = pd.read_csv(f)

    #  thêm cột user id
    df["user_id"] = user_id

    dfs.append(df)

    if i % 200 == 0:
        print(f"Đã load được {i} file...")

print("Đang gộp tất cả file lại thành 1 bảng lớn...")
data = pd.concat(dfs, ignore_index=True)

print("Ghép với bảng questions để lấy đáp án đúng...")
data = data.merge(questions, on="question_id", how="left")

print("Tạo cột kiểm tra đúng sai...")
data["is_correct"] = (data["user_answer"] == data["correct_answer"]).astype("int8")

print("Đổi thời gian làm bài từ mili giây sang giây...")
data["elapsed_time_sec"] = (data["elapsed_time"] / 1000).round(2)

print("Lưu file kết quả ra CSV...")
data.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

print("XONGGGGG")
print("File output:", OUT_CSV)
print("Tổng số dòng:", len(data))
print(data.head())
