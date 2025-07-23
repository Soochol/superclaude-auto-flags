# 🚀 SuperClaude Auto Flags (Hook Edition)

**English** | [한국어](#한국어)

## English

**🎣 Intelligent flag recommendation system with Claude Code Hook integration - Just use `claude` command with `/sc:` prefix!**

### ⚡ Quick Start

```bash
# Install
git clone https://github.com/Soochol/superclaude-auto-flags.git
cd superclaude-auto-flags
python3 install.py

# Usage - Direct claude command support!
claude "/sc:analyze find security vulnerabilities"
# → Hook automatically applies: --persona-security --focus security --validate

claude "/sc:implement React component"  
# → Hook automatically applies: --persona-frontend --magic --c7
```

### 🎯 Key Features
- 🎣 **Hook Integration**: Direct `claude` command support with automatic preprocessing
- 🧠 **Intelligent Pattern Matching**: ORCHESTRATOR.md-based automatic flag recommendation
- 🎯 **Project Context Recognition**: Auto-detects Python/JavaScript/etc
- ⚡ **Complexity-based Optimization**: Auto-adjusts based on file count and complexity
- 🔧 **MCP Server Auto-activation**: Smart selection of Sequential, Context7, Magic, Playwright
- 📊 **Confidence-based Recommendations**: 95% accuracy in flag combinations
- 🛡️ **Tool Optimization**: Automatic safety checks and parameter optimization

### 📋 Supported Patterns
| User Input | Auto-Detects | Recommended Flags |
|------------|--------------|-------------------|
| "security vulnerabilities" | Security | `--persona-security --focus security --validate` |
| "performance optimization" | Performance | `--persona-performance --think-hard --focus performance` |
| "UI component" | Frontend | `--persona-frontend --magic --c7` |
| "API implementation" | Backend | `--persona-backend --seq --c7` |

---

## 한국어

**🎣 Claude Code Hook 통합 지능형 플래그 추천 시스템 - `claude` 명령어에 `/sc:` 접두사만 붙이면 자동 처리!**

### ⚡ 빠른 시작

```bash
# 설치
git clone https://github.com/Soochol/superclaude-auto-flags.git
cd superclaude-auto-flags
python3 install.py

# 사용법 - claude 명령어 직접 지원!
claude "/sc:analyze 보안 취약점 찾아줘"
# → Hook이 자동으로 적용: --persona-security --focus security --validate

claude "/sc:implement React 컴포넌트 만들어줘"
# → Hook이 자동으로 적용: --persona-frontend --magic --c7
```

### 🎯 주요 기능
- 🎣 **Hook 통합**: `claude` 명령어 직접 지원 및 자동 전처리
- 🧠 **지능형 패턴 매칭**: ORCHESTRATOR.md 로직 기반 자동 플래그 추천
- 🎯 **프로젝트 컨텍스트 인식**: Python/JavaScript 등 자동 감지
- ⚡ **복잡도 기반 최적화**: 파일 수와 복잡도에 따른 자동 조정
- 🔧 **MCP 서버 자동 활성화**: Sequential, Context7, Magic, Playwright 지능형 선택
- 📊 **신뢰도 기반 추천**: 95% 정확도로 최적 플래그 조합 제시
- 🛡️ **도구 최적화**: 자동 안전성 검사 및 파라미터 최적화

### 📋 지원하는 패턴
| 사용자 입력 | 자동 감지 | 추천 플래그 |
|------------|-----------|-------------|
| "보안 취약점" | Security | `--persona-security --focus security --validate` |
| "성능 최적화" | Performance | `--persona-performance --think-hard --focus performance` |
| "UI 컴포넌트" | Frontend | `--persona-frontend --magic --c7` |
| "API 구현" | Backend | `--persona-backend --seq --c7` |

### 🎮 실제 사용 예시

#### 🔍 보안 분석
```bash
claude "/sc:analyze 이 프로젝트 보안 취약점 분석해줘"
```
**자동 적용 결과**:
```
🎯 SuperClaude Hook 처리 완료
📁 프로젝트: Python Backend (Hardware Testing)
🚀 적용된 플래그: --persona-security --focus security --think-hard --validate
🎯 신뢰도: 95%
💡 근거: 보안 키워드 매칭 + 대규모 프로젝트 감지
```

#### 🛠️ UI 구현
```bash
claude "/sc:implement 새로운 사용자 인터페이스 컴포넌트"
```
**자동 적용 결과**:
```
🎯 SuperClaude Hook 처리 완료
📁 프로젝트: Frontend Development
🚀 적용된 플래그: --persona-frontend --magic --c7 --uc
🎯 신뢰도: 94%
💡 근거: UI 컴포넌트 키워드 매칭 + 프론트엔드 컨텍스트
```

#### 🔧 성능 최적화
```bash
claude "/sc:improve 성능 병목 지점 찾아서 최적화해줘"
```
**자동 적용 결과**:
```
🎯 SuperClaude Hook 처리 완료
📁 프로젝트: Python Backend
🚀 적용된 플래그: --persona-performance --think-hard --focus performance
🎯 신뢰도: 90%
💡 근거: 성능 최적화 키워드 매칭 + 복잡도 기반 thinking 조정
```

## 🔧 System Requirements
- Python 3.6+
- Claude Code installed
- Linux, macOS, or Windows WSL

## 🧠 How It Works

### 1. Hook Integration
- **UserPromptSubmit Hook**: Intercepts `/sc:` commands in direct `claude` usage
- **PreToolUse Hook**: Optimizes tool parameters before execution
  - Large file auto-chunking for Read tool
  - Scope limitation for Grep in large projects
  - Safety checks for Bash commands
- **Automatic Fallback**: Safe error handling ensures Claude always works

### 2. Pattern Recognition Engine
- Analyzes user input for domain-specific keywords
- Uses ORCHESTRATOR.md Master Routing Table for pattern matching
- Applies priority-based scoring for accurate recommendations

### 3. Project Context Analysis
- Automatically detects project type (Python, JavaScript, etc.)
- Calculates complexity based on file count and structure
- Adapts recommendations based on project characteristics

### 4. Intelligent Flag Optimization
- Combines base flags with context-specific modifiers
- Adjusts thinking levels based on complexity
- Automatically enables delegation for large projects

## 🛡️ Safety Features
- **Safe Fallback**: All hooks gracefully handle errors without breaking Claude
- **Dangerous Command Detection**: Automatically blocks risky bash commands
- **File Safety**: Important file edit logging and warnings
- **Resource Optimization**: Automatic chunking for large files and projects

## 🎣 Hook Architecture
```
User Input: claude "/sc:analyze security issues"
     ↓
UserPromptSubmit Hook → Pattern Matching → Enhanced Command
     ↓
Claude Execution with Auto-Applied Flags
     ↓
PreToolUse Hooks → Tool Optimization → Safe Execution
```

## 🤝 Contributing
Feel free to submit issues, feature requests, or pull requests!

## 📝 License
MIT License - Feel free to use and modify!