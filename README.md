☑️ 서버 실행 방법
```
poetry install
poetry run uvicorn main:app --host 0.0.0.0 --port 8000
```
<br>

☑️ Api Docs
- http://localhost:8000/docs

<br>

☑️ 요구사항
1. 퀴즈 생성/수정/삭제 API
- 관리자만 사용할 수 있습니다.
- 퀴즈(시험지 개념)를 생성 할 수 있도록 API를 구현합니다.
- 하나의 퀴즈는 여러개의 문제를 포함 할 수 있습니다.
- 각 문제는 n+2지선다로 구성되어 있습니다.
- 각 문제에는 반드시 정답이 1개 포함되어 있습니다.

2. 퀴즈 조회/응시 API
- 관리자와 사용자가 사용할 수 있습니다.
- 각 목록 조회는 페이징 처리가 되어야합니다.
- 퀴즈의 목록 조회 및 퀴즈 상세 조회를 할 수 있습니다.
- 퀴즈 상세 조회의 경우 관리자가 설정한 문제 갯수에 따라 문제들이 페이징 처리됩니다.
  예시) 총 30개 문제 중 한 페이지에 10개 문제씩 보여지게 설정 한 경우 총 3페이지로 분할됨
- 관리자는 전체 퀴즈 목록을 조회 할 수 있으며, 사용자는 응시여부(응시할/응시한)를 포함한 퀴즈 목록을 확인 할 수 있습니다.
- 관리자는 각 퀴즈에 문제를 출제할 갯수를 지정합니다. 총 문제 수는 설정한 문제 갯수보다 많을 수 있으며, 총 문제 중 설정한 갯수만큼 랜덤으로 문제가 출제됩니다.
- API에 요청할 때 마다 문제가 랜덤으로 출제됩니다.
- 관리자는 문제/선택지를 랜덤으로 배치할지 설정 할 수 있습니다.
- 문항 및 선택지가 랜덤으로 배치되면, 각 사용자 별로 다른 문제 배치의 퀴즈를 볼 수 있습니다.

3. 응시 및 답안 제출 API
- 사용자가 사용할 수 있습니다.
- 응시 중 새로고침이 되어도 출제된 문제의 구성이나 순서, 사용자가 체크한 답안이 그대로 남아있어야 합니다.
- 제출하면 사용자가 선택한 답안이 모두 저장되어 있어야합니다.
- 제출된 답안은 문제 정답과 비교하여 자동 채점 되어야합니다.

4. 기타 요구사항
- OpenAPI 등을 사용해서 API를 문서화 합니다.
- 트레픽을 고려한 최적화 및 캐싱 전략이 사용되어야 합니다.
