#!/usr/bin/env python3
"""
Shell completion support for policy-analyzer CLI.

Provides bash and zsh completion scripts.
"""

import click
from pathlib import Path


def get_bash_completion_script() -> str:
    """Generate bash completion script.
    
    Returns:
        Bash completion script as string
    """
    return """
# Bash completion for policy-analyzer
# Source this file or add to ~/.bashrc

_policy_analyzer_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Main commands
    local commands="analyze list-models info init-config validate-config watch"
    
    # Global options
    local global_opts="--help --version"
    
    # Analyze options
    local analyze_opts="--domain --config --output-dir --model --verbose --quiet --dry-run"
    
    # Domain choices
    local domains="isms risk_management patch_management data_privacy"
    
    # Handle command completion
    if [ $COMP_CWORD -eq 1 ]; then
        COMPREPLY=( $(compgen -W "${commands} ${global_opts}" -- ${cur}) )
        return 0
    fi
    
    # Handle option completion based on previous word
    case "${prev}" in
        --domain|-d)
            COMPREPLY=( $(compgen -W "${domains}" -- ${cur}) )
            return 0
            ;;
        --config|-c|--output-dir|-o)
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
        --model|-m)
            # Try to get models from ollama
            local models=$(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}')
            COMPREPLY=( $(compgen -W "${models}" -- ${cur}) )
            return 0
            ;;
        analyze)
            if [[ ${cur} == -* ]]; then
                COMPREPLY=( $(compgen -W "${analyze_opts}" -- ${cur}) )
            else
                COMPREPLY=( $(compgen -f -- ${cur}) )
            fi
            return 0
            ;;
        list-models)
            COMPREPLY=( $(compgen -W "--format" -- ${cur}) )
            return 0
            ;;
        init-config|validate-config)
            if [[ ${cur} == -* ]]; then
                COMPREPLY=( $(compgen -W "--format" -- ${cur}) )
            else
                COMPREPLY=( $(compgen -f -- ${cur}) )
            fi
            return 0
            ;;
        watch)
            if [[ ${cur} == -* ]]; then
                COMPREPLY=( $(compgen -W "--domain --config --interval --recursive" -- ${cur}) )
            else
                COMPREPLY=( $(compgen -d -- ${cur}) )
            fi
            return 0
            ;;
    esac
    
    # Default to file completion
    COMPREPLY=( $(compgen -f -- ${cur}) )
}

complete -F _policy_analyzer_completion policy-analyzer
complete -F _policy_analyzer_completion offline-policy-analyzer
"""


def get_zsh_completion_script() -> str:
    """Generate zsh completion script.
    
    Returns:
        Zsh completion script as string
    """
    return """
#compdef policy-analyzer offline-policy-analyzer

# Zsh completion for policy-analyzer

_policy_analyzer() {
    local -a commands
    commands=(
        'analyze:Analyze a policy document'
        'list-models:List available LLM models'
        'info:Display system information'
        'init-config:Generate configuration file'
        'validate-config:Validate configuration file'
        'watch:Watch directory for new policies'
    )
    
    local -a analyze_opts
    analyze_opts=(
        '--domain[Policy domain]:domain:(isms risk_management patch_management data_privacy)'
        '--config[Configuration file]:file:_files'
        '--output-dir[Output directory]:directory:_directories'
        '--model[LLM model name]:model:_policy_analyzer_models'
        '--verbose[Enable verbose logging]'
        '--quiet[Suppress non-essential output]'
        '--dry-run[Preview analysis without execution]'
        '--help[Show help message]'
    )
    
    local -a list_models_opts
    list_models_opts=(
        '--format[Output format]:format:(table list json)'
        '--help[Show help message]'
    )
    
    local -a init_config_opts
    init_config_opts=(
        '--format[Configuration format]:format:(yaml json)'
        '--help[Show help message]'
    )
    
    local -a watch_opts
    watch_opts=(
        '--domain[Policy domain]:domain:(isms risk_management patch_management data_privacy)'
        '--config[Configuration file]:file:_files'
        '--interval[Check interval in seconds]:seconds:'
        '--recursive[Watch subdirectories recursively]'
        '--help[Show help message]'
    )
    
    _arguments -C \
        '1: :->command' \
        '*:: :->args'
    
    case $state in
        command)
            _describe 'command' commands
            ;;
        args)
            case $words[1] in
                analyze)
                    _arguments $analyze_opts \
                        '1:policy file:_files'
                    ;;
                list-models)
                    _arguments $list_models_opts
                    ;;
                info)
                    _arguments '--help[Show help message]'
                    ;;
                init-config|validate-config)
                    _arguments $init_config_opts \
                        '1:config file:_files'
                    ;;
                watch)
                    _arguments $watch_opts \
                        '1:directory:_directories'
                    ;;
            esac
            ;;
    esac
}

# Helper function to get available models
_policy_analyzer_models() {
    local -a models
    models=(${(f)"$(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}')"})
    _describe 'model' models
}

_policy_analyzer "$@"
"""


@click.command()
@click.argument('shell', type=click.Choice(['bash', 'zsh'], case_sensitive=False))
@click.option(
    '--install',
    is_flag=True,
    help='Install completion script to shell config'
)
def completion(shell: str, install: bool):
    """
    Generate shell completion scripts.
    
    SHELL: Shell type (bash or zsh)
    
    \b
    Examples:
      # Generate bash completion
      policy-analyzer completion bash
      
      # Install bash completion
      policy-analyzer completion bash --install
      
      # Generate zsh completion
      policy-analyzer completion zsh > ~/.zsh/completions/_policy-analyzer
    """
    from rich.console import Console
    console = Console()
    
    if shell == 'bash':
        script = get_bash_completion_script()
        
        if install:
            # Try to install to common locations
            bash_completion_dirs = [
                Path.home() / '.bash_completion.d',
                Path('/usr/local/etc/bash_completion.d'),
                Path('/etc/bash_completion.d')
            ]
            
            installed = False
            for completion_dir in bash_completion_dirs:
                if completion_dir.exists() and completion_dir.is_dir():
                    try:
                        completion_file = completion_dir / 'policy-analyzer'
                        completion_file.write_text(script)
                        console.print(f"[green]✓ Installed bash completion to: {completion_file}[/green]")
                        console.print("\n[yellow]Reload your shell or run:[/yellow]")
                        console.print(f"[dim]  source {completion_file}[/dim]")
                        installed = True
                        break
                    except PermissionError:
                        continue
            
            if not installed:
                console.print("[yellow]⚠ Could not auto-install. Add this to ~/.bashrc:[/yellow]\n")
                console.print(script)
                console.print("\n[dim]Or save to a file and source it:[/dim]")
                console.print("[dim]  policy-analyzer completion bash > ~/.policy-analyzer-completion.bash[/dim]")
                console.print("[dim]  echo 'source ~/.policy-analyzer-completion.bash' >> ~/.bashrc[/dim]")
        else:
            console.print(script)
            
    elif shell == 'zsh':
        script = get_zsh_completion_script()
        
        if install:
            # Try to install to zsh completion directory
            zsh_completion_dirs = [
                Path.home() / '.zsh' / 'completions',
                Path('/usr/local/share/zsh/site-functions'),
                Path('/usr/share/zsh/site-functions')
            ]
            
            installed = False
            for completion_dir in zsh_completion_dirs:
                if completion_dir.parent.exists():
                    try:
                        completion_dir.mkdir(parents=True, exist_ok=True)
                        completion_file = completion_dir / '_policy-analyzer'
                        completion_file.write_text(script)
                        console.print(f"[green]✓ Installed zsh completion to: {completion_file}[/green]")
                        console.print("\n[yellow]Reload your shell or run:[/yellow]")
                        console.print("[dim]  autoload -U compinit && compinit[/dim]")
                        installed = True
                        break
                    except PermissionError:
                        continue
            
            if not installed:
                console.print("[yellow]⚠ Could not auto-install. Save to zsh completions:[/yellow]\n")
                console.print("[dim]  mkdir -p ~/.zsh/completions[/dim]")
                console.print("[dim]  policy-analyzer completion zsh > ~/.zsh/completions/_policy-analyzer[/dim]")
                console.print("[dim]  echo 'fpath=(~/.zsh/completions $fpath)' >> ~/.zshrc[/dim]")
                console.print("[dim]  echo 'autoload -U compinit && compinit' >> ~/.zshrc[/dim]")
        else:
            console.print(script)


if __name__ == '__main__':
    completion()
