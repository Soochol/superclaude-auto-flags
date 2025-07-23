# SuperClaude Installation Scripts

이 폴더에는 SuperClaude Auto Flags의 다양한 설치 옵션이 포함되어 있습니다.

## 📁 설치 스크립트 선택 가이드

### 🚀 `install.sh` (추천)
**가장 간단하고 빠른 설치 방법**
```bash
bash install/install.sh
```
- ✅ 핵심 기능만 설치 (빠름)
- ✅ Shell alias 자동 설정
- ✅ 의존성 자동 설치
- ✅ Linux/macOS/WSL 지원

### ⚡ `install_with_hooks.py` (고급)
**Hook 통합을 포함한 완전한 설치**
```bash
python3 install/install_with_hooks.py --hooks
```
- ✅ 모든 기능 포함 (install.sh + 추가 기능)
- ✅ Claude Code Hook 통합
- ✅ 직접 `claude` 명령어 지원
- ✅ 도구 최적화 자동 적용

### 🧠 `install_learning_deps.py` (선택적)
**학습 시스템 의존성 별도 설치**
```bash
python3 install/install_learning_deps.py
```
- 📦 학습 시스템용 추가 패키지 설치
- 🔍 모듈 import 테스트
- 💡 학습 기능을 사용하지 않으면 생략 가능

## 💡 권장 설치 순서

### 일반 사용자
```bash
# 1. 기본 설치
bash install/install.sh
source ~/.bashrc

# 2. 사용 시작
cs '/sc:analyze 프로젝트 분석해줘'
```

### 고급 사용자 (Hook 통합)
```bash
# 1. Hook 통합 설치
python3 install/install_with_hooks.py --hooks
source ~/.bashrc

# 2. 학습 기능 원하면 추가 설치
python3 install/install_learning_deps.py

# 3. 사용 시작 (두 가지 방법 모두 가능)
claude '/sc:analyze 프로젝트 분석해줘'  # Hook을 통한 직접 지원
cs '/sc:implement 새 기능 만들어줘'     # 기존 래퍼 방식
```

## 🔧 문제 해결

**설치 실패 시:**
1. Python 3.6+ 설치 확인
2. pip 업그레이드: `pip3 install --upgrade pip`
3. 권한 문제: `--user` 플래그 사용
4. Claude Code 설치 확인

**문의 사항:**
- GitHub Issues: https://github.com/Soochol/superclaude-auto-flags/issues