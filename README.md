# Hanbyeol Administration Bot

디스코드 한별 서버를 위한 관리용 봇입니다. 봇은 처벌 내역을 전송하고 데이터베이스에 저장하며, 누가 명령어를 사용할 수 있는지도 역할 기반으로 제한합니다.

## 요구 사항

- Python 3.10 이상
- `pip install -r requirements.txt`
- Discord 봇 토큰 (환경 변수 `DISCORD_BOT_TOKEN`)

## 환경 변수

봇 토큰과 기타 설정은 환경 변수로 지정합니다. 프로젝트 루트에 `.env` 파일을 만들어 다음과 같이 입력하면 됩니다.

```env
DISCORD_BOT_TOKEN=디스코드_봇_토큰
# 필요한 경우 추가 설정도 함께 적어주세요
# HANBYEOL_ANNOUNCEMENT_CHANNEL=1434881803075846286
```

실행 시 `python-dotenv` 가 `.env` 파일을 자동으로 불러옵니다. 또는 아래 표의 이름으로 환경 변수를 직접 `export` 해도 됩니다.

| 변수 | 설명 |
| --- | --- |
| `DISCORD_BOT_TOKEN` | 필수. 디스코드 봇 토큰 |
| `DISCORD_GUILD_ID` | 선택. 특정 길드에만 명령어를 동기화하고 싶을 때 사용 |
| `HANBYEOL_ANNOUNCEMENT_CHANNEL` | 선택. 처벌/해제 내역을 올릴 채널 ID (기본값: `1434881803075846286`) |
| `HANBYEOL_PUNISHMENT_ROLE` | 선택. 처벌 관련 명령어 사용 가능 역할 ID (기본값: `1434877200208756897`) |
| `HANBYEOL_LOG_ROLE` | 선택. 로그 열람 명령어 사용 가능 역할 ID (기본값: `1434877292546621602`) |
| `HANBYEOL_DATABASE` | 선택. SQLite 데이터베이스 파일 경로 (기본값: `hanbyeol.db`) |

## 실행 방법

```bash
pip install -r requirements.txt
python bot.py
```

## Slash 명령어

명령어는 `/hanbyeol` 그룹 아래에 등록되며, 한국어 로컬라이징이 적용되어 클라이언트에서는 `/한별`로 표시됩니다.

### `/한별 처벌정보전송`

- 역할 `1434877200208756897` (또는 `HANBYEOL_PUNISHMENT_ROLE`) 보유자만 실행 가능
- 채널 `1434881803075846286` (또는 `HANBYEOL_ANNOUNCEMENT_CHANNEL`) 에 빨간색 임베드 전송
- 데이터베이스 `punishments` 테이블에 기록

### `/한별 처벌해제정보전송`

- 역할 `1434877200208756897` (또는 `HANBYEOL_PUNISHMENT_ROLE`) 보유자만 실행 가능
- 채널 `1434881803075846286` 에 파란색 임베드 전송
- 데이터베이스 `punishment_releases` 테이블에 기록

### `/한별 처벌로그`

- 역할 `1434877292546621602` (또는 `HANBYEOL_LOG_ROLE`) 보유자만 실행 가능
- 입력한 숫자 * 5 개의 최신 로그를 조회 (최대 50개)
- 결과는 슬래시 명령어를 실행한 사용자에게만 보이는 임베드로 반환

## 데이터베이스 구조

봇은 SQLite 를 사용하여 처벌 및 해제 내역을 영구 저장합니다.

- `punishments`: 처벌 대상, 종류, 사유, 기간, 담당자, 기록 시간 저장
- `punishment_releases`: 처벌 해제 대상, 종류, 사유, 담당자, 기록 시간 저장

데이터베이스 파일 위치는 `HANBYEOL_DATABASE` 환경 변수로 변경할 수 있습니다.
