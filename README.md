증권사 리포트 요약 + 광고 자동화

동작: 네이버금융 리서치(기업분석) 신규 리포트 수집 → PDF 앞 4쪽 추출 → Claude로 3줄 요약 → 요약페이지(광고 2칸 + 5초 후 원문 PDF 버튼) 생성 → GitHub Pages 배포 → 텔레그램 채널에 링크 발송. 평일 09:10/12:10/15:10/18:10(KST) 자동 실행.

설정 순서
1. GitHub 가입 → 새 저장소(Public) 생성 → 이 폴더 파일 전체 업로드(.github 폴더 포함)
2. Settings > Pages > Source: Deploy from a branch, Branch: main /docs
3. Settings > Secrets and variables > Actions
   Secrets: ANTHROPIC_API_KEY, TG_TOKEN(텔레그램 봇 토큰, 선택)
   Variables: SITE_URL(예 https://아이디.github.io/저장소명), TG_CHAT(@채널아이디, 선택), ADSENSE_CLIENT(ca-pub-xxxx, 승인 후), ADSENSE_SLOT(광고단위 ID, 승인 후)
4. Actions 탭 > run > Run workflow 로 1회 수동 실행 → SITE_URL 접속 확인
5. 페이지 50개 이상 쌓이면 애드센스 신청(커스텀 도메인 연결 권장) → 승인 후 ADSENSE 변수 입력
6. 구글 서치콘솔·네이버 서치어드바이저에 SITE_URL/sitemap.xml 제출

비용: 리포트 1건당 Claude API 소액, 1회 최대 12건(MAX_PER_RUN으로 조절). GitHub Actions·Pages 무료.
텔레그램: @BotFather로 봇 생성 → 채널 만들고 봇을 관리자로 추가.
