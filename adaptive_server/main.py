from fastapi import FastAPI
from fastapi import HTTPException

from sqlalchemy import create_engine
from pydantic import BaseModel

import pandas as pd
import random
import subprocess
import os

from sklearn.cluster import KMeans

# tạo fastapi app

app = FastAPI()

# kết nối mysql

engine = create_engine(
    "mysql+pymysql://moodleuser:1234@192.168.74.129/moodle"
)

# model request

class QuizRequest(BaseModel):

    easy: int
    medium: int
    hard: int

# api test

@app.get("/")
def home():

    return {
        "message": "Adaptive server running"
    }

# api test database

@app.get("/interactions")
def get_interactions():

    query = """
    SELECT *
    FROM mdl_local_ednet_interactions
    LIMIT 10
    """

    df = pd.read_sql(query, engine)

    return df.to_dict(orient="records")

# api sinh quiz

@app.post("/generate_quiz")
def generate_quiz(req: QuizRequest):

    # kiểm tra request

    if req.easy < 0 \
    or req.medium < 0 \
    or req.hard < 0:

        raise HTTPException(

            status_code=400,

            detail=
            "Question count cannot be negative"
        )

    total_requested = (

        req.easy
        + req.medium
        + req.hard
    )

    if total_requested == 0:

        raise HTTPException(

            status_code=400,

            detail=
            "Total questions must be greater than 0"
        )

    # chạy fast mode

    # kiểm tra file lnirt

    if not os.path.exists(
        "lnirt_item_clean.csv"
    ):

        raise HTTPException(

            status_code=500,

            detail=
            "lnirt_item_clean.csv not found"
        )

    df = pd.read_csv(
        "lnirt_item_clean.csv"
    )

    # kiểm tra dữ liệu csv

    required_columns = [

        "item_idx_original",

        "beta"
    ]

    missing_cols = [

        col for col
        in required_columns

        if col not in df.columns
    ]

    if len(missing_cols) > 0:

        raise HTTPException(

            status_code=500,

            detail=
            f"Missing columns: {missing_cols}"
        )

    if len(df) == 0:

        raise HTTPException(

            status_code=500,

            detail=
            "CSV file is empty"
        )

    # chạy preprocess và train lại model

#     print("\nDang preprocess...\n")

#     subprocess.run(
#         ["python", "preprocess.py"],
#         check=True
#     )

#     print("\nDang train lnirt...\n")

#     subprocess.run(
#         ["Rscript", "train.R"],
#         check=True
#     )

#     print("\nDang load ket qua...\n")

#     # load lại file kết quả

#     df = pd.read_csv(
#     "lnirt_item_clean.csv"
# )

    # phân cụm bằng kmeans

    print("\nDang chay KMeans...\n")

    kmeans = KMeans(
        n_clusters=3,
        random_state=42,
        n_init=10
    )

    try:

        df["cluster"] = kmeans.fit_predict(
            df[["beta"]]
        )

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=
            f"KMeans failed: {str(e)}"
        )

    # sắp xếp cluster theo beta

    cluster_mean = (
        df
        .groupby("cluster")["beta"]
        .mean()
        .sort_values()
    )

    easy_cluster = cluster_mean.index[0]
    medium_cluster = cluster_mean.index[1]
    hard_cluster = cluster_mean.index[2]

    # tách dữ liệu theo mức độ khó

    easy_df = df[
        df["cluster"] == easy_cluster
    ]

    medium_df = df[
        df["cluster"] == medium_cluster
    ]

    hard_df = df[
        df["cluster"] == hard_cluster
    ]

    print("\nPhan bo cau hoi\n")

    print("Easy:", len(easy_df))
    print("Medium:", len(medium_df))
    print("Hard:", len(hard_df))

    # cảnh báo nếu thiếu câu hỏi

    warnings = []

    if len(easy_df) < req.easy:

        warnings.append(

            f"Only {len(easy_df)} easy questions available"
        )

    if len(medium_df) < req.medium:

        warnings.append(

            f"Only {len(medium_df)} medium questions available"
        )

    if len(hard_df) < req.hard:

        warnings.append(

            f"Only {len(hard_df)} hard questions available"
        )

    # lấy câu easy

    easy_questions = (
        easy_df
        .sample(min(req.easy, len(easy_df)))
        [[
            "item_idx_original"
        ]]
        .to_dict(orient="records")
    )

    for q in easy_questions:

        q["difficulty"] = "Easy"

    # lấy câu medium

    medium_questions = (
        medium_df
        .sample(min(req.medium, len(medium_df)))
        [[
            "item_idx_original"
        ]]
        .to_dict(orient="records")
    )

    for q in medium_questions:

        q["difficulty"] = "Medium"

    # lấy câu hard

    hard_questions = (
        hard_df
        .sample(min(req.hard, len(hard_df)))
        [[
            "item_idx_original"
        ]]
        .to_dict(orient="records")
    )

    for q in hard_questions:

        q["difficulty"] = "Hard"

    # gộp toàn bộ câu hỏi

    final_questions = (
        easy_questions
        + medium_questions
        + hard_questions
    )

    random.shuffle(final_questions)

    # format dữ liệu trả về

    formatted_questions = []

    for q in final_questions:

        formatted_questions.append({

            "question_id":
                q["item_idx_original"],

            "difficulty":
                q["difficulty"]
        })

    print("\nDa tao quiz\n")

    print("Total questions:",
          len(formatted_questions))

    # trả kết quả api

    return {

        "success": True,

        "warnings": warnings,

        "total": len(formatted_questions),

        "questions": formatted_questions
    }
