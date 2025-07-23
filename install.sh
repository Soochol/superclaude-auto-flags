#!/bin/bash
set -e

echo "🚀 SuperClaude Auto Flags - Installation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'  
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# 환경 확인
check_requirements() {
    print_warning "시스템 환경 확인 중..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python3가 필요합니다."
        exit 1
    fi
    
    if ! command -v claude &> /dev/null; then
        print_warning "Claude Code가 설치되지 않은 것 같습니다."
        print_warning "SuperClaude는 Claude Code와 함께 사용됩니다."
    fi
    
    print_success "환경 확인 완료"
}

# 의존성 설치
install_dependencies() {
    print_warning "의존성 설치 중..."
    
    if ! python3 -c "import yaml" &>/dev/null; then
        if command -v pip3 &> /dev/null; then
            pip3 install PyYAML --user
        else
            print_error "pip3를 찾을 수 없습니다. PyYAML을 수동으로 설치하세요."
            exit 1
        fi
    fi
    
    print_success "의존성 설치 완료"
}

# 파일 설치  
install_files() {
    print_warning "SuperClaude 파일 설치 중..."
    
    mkdir -p ~/.claude
    
    # 핵심 파일들 복사
    cp claude_sc_preprocessor.py ~/.claude/ || { print_error "파일 복사 실패"; exit 1; }
    cp claude_smart_wrapper.py ~/.claude/ || { print_error "파일 복사 실패"; exit 1; }
    cp orchestrator_rules.yaml ~/.claude/ || { print_error "파일 복사 실패"; exit 1; }
    
    # 실행 권한 부여
    chmod +x ~/.claude/*.py
    
    print_success "파일 설치 완료"
}

# Shell Alias 설정
setup_shell_alias() {
    print_warning "Shell alias 설정 중..."
    
    # Shell 감지
    if [ -n "$ZSH_VERSION" ]; then
        SHELL_RC="$HOME/.zshrc"
        SHELL_NAME="zsh"
    elif [ -n "$BASH_VERSION" ]; then
        SHELL_RC="$HOME/.bashrc"  
        SHELL_NAME="bash"
    else
        print_warning "Shell을 감지할 수 없습니다."
        print_warning "다음 명령어를 수동으로 실행하세요:"
        echo "alias cs=\"python3 ~/.claude/claude_smart_wrapper.py\""
        return
    fi
    
    # 기존 alias 제거 후 새로 추가
    sed -i.bak '/alias cs=/d' "$SHELL_RC" 2>/dev/null || true
    echo '' >> "$SHELL_RC"
    echo '# SuperClaude Auto Flags' >> "$SHELL_RC"
    echo 'alias cs="python3 ~/.claude/claude_smart_wrapper.py"' >> "$SHELL_RC"
    
    print_success "Shell alias 설정 완료 ($SHELL_NAME)"
}

# 설치 완료 메시지
show_completion_message() {
    echo ""
    echo -e "${GREEN}🎉 SuperClaude Auto Flags 설치 완료!${NC}"
    echo ""
    echo "🔄 다음 명령어로 Shell을 재시작하세요:"
    echo "   source ~/.bashrc   # 또는 source ~/.zshrc"
    echo ""
    echo "🎯 사용 예시:"
    echo "   cs '/sc:analyze 보안 취약점 찾아줘'"
    echo "   cs '/sc:implement API 엔드포인트 만들어줘'"
    echo "   cs '/sc:improve 성능 최적화해줘'"
    echo ""
    echo "📚 도움말: cs --help"
    echo "🌟 GitHub: https://github.com/Soochol/superclaude-auto-flags"
    echo ""
    echo "✨ 이제 SuperClaude의 강력한 플래그 시스템을"
    echo "   간단한 의도 표현만으로 활용하세요!"
}

# 메인 실행 함수
main() {
    check_requirements
    install_dependencies
    install_files
    setup_shell_alias
    show_completion_message
}

# 스크립트 실행
main "$@"