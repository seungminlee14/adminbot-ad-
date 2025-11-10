# Hanbyeol Administration Bot

디스코드 한별 서버를 위한 관리용 봇입니다. 봇은 처벌 내역을 전송하고 텍스트 파일(메모장 형태)에 기록하며, 누가 명령어를 사용할 수 있는지도 역할 기반으로 제한합니다.

## 요구 사항

- Python 3.10 이상
- `pip install -r requirements.txt`
- Discord 봇 토큰 (환경 변수 `DISCORD_BOT_TOKEN`)

## 환경 변수

봇 토큰과 기타 설정은 환경 변수로 지정합니다. **`bot.py`와 같은 위치(프로젝트 루트)에 있는 `.env` 파일**을 사용하세요. 처음 설정할 때는 `.env.example`을 복사하여 이름을 `.env`로 바꾸고 아래 값을 채우면 됩니다.

```env
DISCORD_BOT_TOKEN=디스코드_봇_토큰
# 필요한 경우 추가 설정도 함께 적어주세요
# HANBYEOL_ANNOUNCEMENT_CHANNEL=1434881803075846286
```

실행 시 `python-dotenv` 가 `.env` 파일을 자동으로 불러옵니다. `.env` 파일이 같은 폴더에 없으면 로딩되지 않으니, 반드시 `bot.py`와 같은 디렉터리에 위치시켜 주세요. 또는 아래 표의 이름으로 환경 변수를 직접 `export` 해도 됩니다.

> ❗️ 실행 중 `DISCORD_BOT_TOKEN 환경 변수가 설정되어 있지 않습니다` 오류가 발생한다면 다음 항목을 다시 확인하세요.
> 1. `.env` 파일이 실제로 존재하는지 (Windows 의 경우 파일 확장자가 `.env.txt`로 저장되지 않았는지)
> 2. 파일 내용이 `DISCORD_BOT_TOKEN=실제_봇_토큰` 형식으로 되어 있는지
> 3. 봇을 실행한 경로가 `.env` 파일과 동일한지 (`python bot.py` 명령을 실행하는 위치)

| 변수 | 설명 |
| --- | --- |
| `DISCORD_BOT_TOKEN` | 필수. 디스코드 봇 토큰 |
| `DISCORD_GUILD_ID` | 선택. 특정 길드에만 명령어를 동기화하고 싶을 때 사용 |
| `HANBYEOL_ANNOUNCEMENT_CHANNEL` | 선택. 처벌/해제 내역을 올릴 채널 ID (기본값: `1434881803075846286`) |
| `HANBYEOL_PUNISHMENT_ROLE` | 선택. 모든 명령어를 사용할 수 있는 관리자 역할 ID (기본값: `1434877292546621602`) |
| `HANBYEOL_LOG_ROLE` | 선택. 로그 열람 명령어 사용 가능 역할 ID (기본값: `1434877292546621602`) |
| `HANBYEOL_DATABASE` | 선택. 로그를 저장할 텍스트 파일 경로 (기본값: `hanbyeol_logs.txt`) |

## 실행 방법

```bash
pip install -r requirements.txt
python bot.py
```

## Slash 명령어

명령어는 `/한별` 그룹 아래에 등록되며, 모든 명령어 이름도 한국어로 고정되어 표시됩니다. (영문 클라이언트에서는 `/hanbyeol` 등 영문 이름으로 표기될 수 있습니다.)

### `/한별 처벌정보전송`

- 역할 `1434877292546621602` (또는 `HANBYEOL_PUNISHMENT_ROLE`) 보유자만 실행 가능
- 채널 `1434881803075846286` (또는 `HANBYEOL_ANNOUNCEMENT_CHANNEL`) 에 빨간색 임베드 전송
- 로그 파일에 처벌 내역을 JSON 줄 형식으로 기록
- 처리자와 대상자에게 동일한 처벌 임베드를 DM 으로 안내

### `/한별 처벌해제정보전송`

- 역할 `1434877292546621602` (또는 `HANBYEOL_PUNISHMENT_ROLE`) 보유자만 실행 가능
- 채널 `1434881803075846286` 에 파란색 임베드 전송
- 로그 파일에 처벌 해제 내역을 JSON 줄 형식으로 기록
- 처리자와 대상자에게 처벌 해제 안내를 DM 으로 전달

### `/한별 처벌로그`

- 역할 `1434877292546621602` (또는 `HANBYEOL_LOG_ROLE`) 보유자만 실행 가능
- 입력한 숫자 * 5 개의 최신 로그를 조회 (최대 50개)
- 결과는 슬래시 명령어를 실행한 사용자에게만 보이는 임베드로 반환

## 로그 파일 구조

봇은 메모장으로 열 수 있는 일반 텍스트 파일을 데이터 저장소로 사용합니다. 각 줄에는 JSON 객체가 들어 있으며, `kind` 값으로 `punishment` 또는 `release`를 구분합니다. 예시는 다음과 같습니다.

```json
{"kind": "punishment", "user_id": 123, "user_name": "User#0001", "punishment": "밴", "reason": "욕설", "duration": "7일", "moderator_id": 456, "moderator_name": "Mod#9999", "created_at": "2025-11-09T15:42:00"}
```

`HANBYEOL_DATABASE` 환경 변수로 파일 경로를 원하는 위치/이름으로 변경할 수 있습니다.
