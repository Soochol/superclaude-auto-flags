#!/usr/bin/env python3
"""
SuperClaude Auto Flags with Hooks - Advanced Installation
Hook 기반 통합 기능을 포함한 고급 설치 스크립트
"""

import os
import shutil
import subprocess
import sys
import json
from pathlib import Path

def print_success(msg):
    print(f"\033[0;32m✅ {msg}\033[0m")

def print_warning(msg):
    print(f"\033[1;33m⚠️  {msg}\033[0m")

def print_error(msg):
    print(f"\033[0;31m❌ {msg}\033[0m")

def print_info(msg):
    print(f"\033[0;36mℹ️  {msg}\033[0m")

def check_requirements():
    """시스템 요구사항 확인"""
    print_warning("Checking system requirements...")
    
    # Python3 확인
    if sys.version_info < (3, 6):
        print_error("Python 3.6+ is required.")
        sys.exit(1)
    
    # Claude Code 확인
    try:
        subprocess.run(['claude', '--version'], capture_output=True, check=True)
        print_success("Claude Code found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_warning("Claude Code not found.")
        print_warning("SuperClaude works best with Claude Code.")
    
    print_success("System requirements check completed")

def install_dependencies():
    """의존성 설치"""
    print_warning("Installing dependencies...")
    
    try:
        import yaml
        print_success("PyYAML is already installed.")
    except ImportError:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--user', 'PyYAML'])
            print_success("PyYAML installation completed")
        except subprocess.CalledProcessError:
            print_error("Failed to install PyYAML. Please install manually: pip3 install PyYAML --user")
            sys.exit(1)

def install_files():
    """파일 설치 - 새로운 체계적 폴더 구조"""
    print_warning("Installing SuperClaude files...")
    
    # .claude 디렉토리 및 하위 폴더 생성
    claude_dir = Path.home() / '.claude'
    superclaude_dir = claude_dir / 'superclaude'
    core_dir = superclaude_dir / 'core'
    hooks_dir = superclaude_dir / 'hooks'
    learning_dir = superclaude_dir / 'learning'
    data_dir = claude_dir / 'learning'
    
    # 모든 필요한 디렉토리 생성
    for directory in [claude_dir, superclaude_dir, core_dir, hooks_dir, learning_dir, data_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # 현재 디렉토리에서 파일들 복사 - 새로운 구조
    current_dir = Path.cwd()
    files_to_copy = [
        # 핵심 시스템 파일들 (core/)
        ('src/claude_sc_preprocessor.py', 'superclaude/core/claude_sc_preprocessor.py'),
        ('src/claude_smart_wrapper.py', 'superclaude/core/claude_smart_wrapper.py'), 
        ('src/orchestrator_rules.yaml', 'superclaude/core/orchestrator_rules.yaml'),
        
        # Hook 시스템 파일들 (hooks/)
        ('src/superclaude_prompt_hook.py', 'superclaude/hooks/superclaude_prompt_hook.py'),
        ('src/tool_optimizer.py', 'superclaude/hooks/tool_optimizer.py'),
        ('src/superclaude_hooks_config.json', 'superclaude/hooks/superclaude_hooks_config.json'),
        
        # 학습 시스템 파일들 (learning/)
        ('learning/adaptive_recommender.py', 'superclaude/learning/adaptive_recommender.py'),
        ('learning/data_collector.py', 'superclaude/learning/data_collector.py'),
        ('learning/feedback_processor.py', 'superclaude/learning/feedback_processor.py'),
        ('learning/learning_engine.py', 'superclaude/learning/learning_engine.py'),
        ('learning/learning_storage.py', 'superclaude/learning/learning_storage.py'),
        ('learning/performance_optimizer.py', 'superclaude/learning/performance_optimizer.py')
    ]
    
    for source_path, dest_path in files_to_copy:
        source = current_dir / source_path
        destination = claude_dir / dest_path
        
        if source.exists():
            shutil.copy2(source, destination)
            destination.chmod(0o755)  # 실행 권한 부여
            print_success(f"{dest_path} installed successfully")
        else:
            print_error(f"Cannot find {source_path} file.")
            sys.exit(1)
    
    print_success("Files installation completed with organized structure")

def setup_shell_alias():
    """Shell alias 설정"""
    print_warning("Setting up shell alias...")
    
    # Shell 감지
    shell_name = os.environ.get('SHELL', '').split('/')[-1]
    
    if 'zsh' in shell_name:
        shell_rc = Path.home() / '.zshrc'
        shell_display_name = 'zsh'
    elif 'bash' in shell_name:
        shell_rc = Path.home() / '.bashrc'
        shell_display_name = 'bash'
    else:
        print_warning("Cannot detect shell type.")
        print_warning("Please manually run this command:")
        print('alias cs="python3 ~/.claude/claude_smart_wrapper.py"')
        return
    
    # 기존 alias 제거 후 새로 추가 - 새 경로 적용
    alias_line = 'alias cs="python3 ~/.claude/superclaude/core/claude_smart_wrapper.py"'
    
    try:
        if shell_rc.exists():
            # 기존 내용 읽기
            with open(shell_rc, 'r') as f:
                lines = f.readlines()
            
            # 기존 cs alias 제거
            lines = [line for line in lines if 'alias cs=' not in line]
        else:
            lines = []
        
        # 새 alias 추가
        lines.extend([
            '\n',
            '# SuperClaude Auto Flags\n',
            f'{alias_line}\n'
        ])
        
        # 파일에 쓰기
        with open(shell_rc, 'w') as f:
            f.writelines(lines)
        
        print_success(f"Shell alias setup completed ({shell_display_name})")
        
    except Exception as e:
        print_error(f"Shell alias setup failed: {e}")
        print_warning("Please manually add this line to ~/.bashrc or ~/.zshrc:")
        print(alias_line)

def setup_hooks(enable_hooks=False):
    """Hook 설정 (선택사항)"""
    if not enable_hooks:
        print_info("Hook integration skipped (use --hooks to enable)")
        return
    
    print_warning("Setting up Claude Code Hooks integration...")
    
    # 현재 설정 파일 위치 확인
    claude_settings_paths = [
        Path.home() / '.claude' / 'settings.json',
        Path.home() / '.claude' / 'settings.local.json'
    ]
    
    settings_file = None
    for path in claude_settings_paths:
        if path.exists():
            settings_file = path
            break
    
    if not settings_file:
        settings_file = Path.home() / '.claude' / 'settings.local.json'
    
    try:
        # 기존 설정 읽기
        if settings_file.exists():
            with open(settings_file, 'r') as f:
                settings = json.load(f)
        else:
            settings = {}
        
        # Hook 설정 로드 - 새 경로에서
        hook_config_path = Path.cwd() / 'src' / 'superclaude_hooks_config.json'
        if hook_config_path.exists():
            with open(hook_config_path, 'r') as f:
                hook_config = json.load(f)
            
            # Hook 경로를 새 구조에 맞게 업데이트
            if 'hooks' in hook_config:
                for hook_name, hook_settings in hook_config['hooks'].items():
                    if 'scriptPath' in hook_settings:
                        # 새 경로로 업데이트
                        old_path = hook_settings['scriptPath']
                        if 'superclaude_prompt_hook.py' in old_path:
                            hook_settings['scriptPath'] = '~/.claude/superclaude/hooks/superclaude_prompt_hook.py'
                        elif 'tool_optimizer.py' in old_path:
                            hook_settings['scriptPath'] = '~/.claude/superclaude/hooks/tool_optimizer.py'
            
            # 기존 설정에 Hook 추가
            settings.update(hook_config)
            
            # 설정 파일에 쓰기
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            print_success(f"Hook configuration added to {settings_file}")
            print_info("Hooks enabled:")
            print_info("  ✓ UserPromptSubmit: Direct claude command support")
            print_info("  ✓ PreToolUse: Tool optimization")
            
        else:
            print_error("Hook configuration file not found")
            
    except Exception as e:
        print_error(f"Hook setup failed: {e}")
        print_warning("You can manually add hooks later using superclaude_hooks_config.json")

def show_completion_message(hooks_enabled=False):
    """설치 완료 메시지"""
    print("\n\033[0;32m🎉 SuperClaude Auto Flags installation completed!\033[0m\n")
    print("🔄 Restart your shell with:")
    print("   source ~/.bashrc   # or source ~/.zshrc\n")
    
    if hooks_enabled:
        print("🎯 Usage (Hook-based integration):")
        print("   claude '/sc:analyze find security vulnerabilities'")
        print("   claude '/sc:implement API endpoint'")
        print("   claude '/sc:improve performance optimization'\n")
    
    print("🎯 Usage (Traditional wrapper):")
    print("   cs '/sc:analyze find security vulnerabilities'")
    print("   cs '/sc:implement API endpoint'")
    print("   cs '/sc:improve performance optimization'\n")
    
    print("📚 Help: cs --help")
    print("🌟 GitHub: https://github.com/Soochol/superclaude-auto-flags\n")
    
    if hooks_enabled:
        print("🎣 Hook Features Enabled:")
        print("   ✅ Direct claude command support")
        print("   ✅ Automatic tool optimization")
        print("   ✅ Enhanced safety checks")
        print("\n✨ You can now use both 'claude' and 'cs' commands!")
    else:
        print("✨ Use 'cs' command for SuperClaude features!")
        print("💡 To enable Hook integration, run: python3 install_with_hooks.py --hooks")

def main():
    """메인 함수"""
    print("🚀 SuperClaude Auto Flags - Advanced Installation")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    # 명령행 옵션 확인
    enable_hooks = '--hooks' in sys.argv
    
    if enable_hooks:
        print_info("Hook integration mode enabled")
    else:
        print_info("Standard installation mode (use --hooks for Hook integration)")
    
    print()
    
    try:
        check_requirements()
        install_dependencies()
        install_files()
        setup_shell_alias()
        setup_hooks(enable_hooks)
        show_completion_message(enable_hooks)
    except KeyboardInterrupt:
        print_error("\nInstallation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Installation error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()