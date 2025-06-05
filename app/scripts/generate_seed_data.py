import os
import csv
import psycopg2
from pathlib import Path

# 1. .env 로드

DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = os.getenv("POSTGRES_PORT", 5432)

# 2. DB 연결
conn = psycopg2.connect(
    dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
    host=DB_HOST, port=DB_PORT
)
cur = conn.cursor()

current_dir = Path(__file__).parent
csv_path = current_dir / "company_tag_sample.csv"

tag_data = {}  # (ko, en, ja) 조합 → tag_id

with open(csv_path, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # 1. companies
        cur.execute("INSERT INTO companies DEFAULT VALUES RETURNING id;")
        company_id = cur.fetchone()[0]

        # 2. company_names
        for lang in ['ko', 'en', 'ja']:
            name = row[f"company_{lang}"].strip()
            if not name:
                continue
            
            cur.execute(
                "INSERT INTO company_names (company_id, language, name) VALUES (%s, %s, %s);",
                (company_id, lang, name)
            )

        # 3. tag + tag_names + company_tags
        tags_ko = row["tag_ko"].split("|")
        tags_en = row["tag_en"].split("|")
        tags_ja = row["tag_ja"].split("|")

        for ko, en, ja in zip(tags_ko, tags_en, tags_ja):
            tag_key = (ko.strip(), en.strip(), ja.strip())

            if tag_key in tag_data:
                tag_id = tag_data[tag_key]
            else:
                # 새 태그
                cur.execute("INSERT INTO tags DEFAULT VALUES RETURNING id;")
                tag_id = cur.fetchone()[0]
                tag_data[tag_key] = tag_id

                cur.executemany(
                    "INSERT INTO tag_names (tag_id, language, name) VALUES (%s, %s, %s);",
                    [
                        (tag_id, 'ko', tag_key[0]),
                        (tag_id, 'en', tag_key[1]),
                        (tag_id, 'ja', tag_key[2]),
                    ]
                )

            # 4. company_tags
            cur.execute(
                "INSERT INTO company_tags (company_id, tag_id) VALUES (%s, %s);",
                (company_id, tag_id)
            )

conn.commit()
cur.close()
conn.close()
print("작업 완료!".center(30))
