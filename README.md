
# company-metadata-api

회사 메타데이터 관리 API 서버

## 1. 프로젝트 클론
```bash
git clone https://github.com/eehwan/company-metadata-api.git
cd company-metadata-api
```

## 2. .env 파일 생성 (필수)
```bash
cat <<EOF > .env
POSTGRES_DB=your_db
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
EOF
```

## 3. Docker 커테이너 빌드 및 실행
```bash
docker-compose build
docker-compose up -d
```

## 4. DB 초기화 및 데이터 삽입
```bash
docker exec -it company_api bash
python scripts/init_db.py
python scripts/generate_seed_data.py
```

## [추가] 검색 성능 최적화 (자동완성 검색)

회사명 자동완성 검색(`ILIKE '%query%'`)의 성능을 위해 PostgreSQL `pg_trgm` 확장과 GIN 인덱스를 추가

```bash
docker exec -it company_postgress psql -U $POSTGRES_USER -d $POSTGRES_DB
```

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_company_name_trgm ON company_names USING gin (name gin_trgm_ops);
```