
# company-metadata-api

회사 메타데이터 관리 API 서버

- [Git Repo](https://github.com/eehwan/company-metadata-api)
- [Swagger UI](http://company.eehwan.duckdns.org/docs)
- [ReDoc 문서](http://company.eehwan.duckdns.org/redoc)

## 작업 요약
요구사항을 기반으로 기업, 태그, 언어별 번역 정보를 분리하여 1차, 2차 정규화된 구조로 테이블을 설계했습니다.
테이블 간 관계를 적절하게 설정하여 다국어 확장이 가능하도록 구성했습니다.

검색 API에서는 회사 정보와 태그가 언어 우선순위로 정렬하여 사용자 언어에 맞는 결과가 노출되도록 처리했습니다.

마이그레이션 및 더미 데이터 입력은 app/scripts/ 디렉토리 스크립트로 자동화하였고,
제공된 test_senior_app.py 기준으로 모든 테스트가 정상적으로 통과됩니다.

## 추가가 필요한 부분
- response에 대한 DTO만 정의 되어 있어, 나머지에 대한 DTO도 필요함
- testcode가 async기반으로 동작하지 않아, 시간상 sync기반으로 수정을 해놨는데 확인 후, 재변경 필요

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
python app/scripts/init_db.py
python app/scripts/generate_seed_data.py
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

## [테스트 방법]

flask기반 test코드라서 원본파일에서 약간의 수정
> fastapi.testclient 사용 & json.loads(resp.data.decode("utf-8")) -> resp.json()

```bash
docker exec -it company_web bash

# 디비가 세팅되어있지 않다면 테스트 전, 아래의 작업 필요!
python app/scripts/init_db.py
python app/scripts/generate_seed_data.py

# pytest
pytest app/scripts/test_senior_app.py
```
