#!/usr/bin/env python3
"""
Enhanced commands for policy-analyzer CLI.

Includes: dry-run, watch mode, config validation, shell completion.
"""

import time
import click
from pathlib import Path
from typing import Optional
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


def dry_run_analysis(
    policy_file: Path,
    domain: Optional[str],
    config: Optional[Path],
    output_dir: Optional[str],
    model: Optional[str]
):
    """Preview analysis without execution.
    
    Args:
        policy_file: Path to policy file
        domain: Policy domain
        config: Configuration file path
        output_dir: Output directory
        model: Model name
    """
    console.print("\n[bold cyan]Dry Run - Analysis Preview[/bold cyan]\n")
    
    # Create preview table
    table = Table(box=box.ROUNDED, show_header=False)
    table.add_column("Property", style="cyan", width=20)
    table.add_column("Value", style="white")
    
    table.add_row("Policy File", str(policy_file))
    table.add_row("File Size", f"{policy_file.stat().st_size / 1024:.1f} KB")
    table.add_row("File Format", policy_file.suffix.upper())
    table.add_row("Domain", domain or "[dim]Auto-detect[/dim]")
    table.add_row("Model", model or "[dim]qwen2.5:3b-instruct (default)[/dim]")
    table.add_row("Configuration", str(config) if config else "[dim]Default[/dim]")
    table.add_row("Output Directory", output_dir or "[dim]./outputs/TIMESTAMP[/dim]")
    
    console.print(table)
    console.print()
    
    # Estimate analysis time
    file_size_kb = policy_file.stat().st_size / 1024
    estimated_time = max(60, int(file_size_kb * 2))  # Rough estimate: 2 seconds per KB
    
    console.print(f"[dim]Estimated analysis time: ~{estimated_time // 60} minutes[/dim]")
    console.print()
    
    # Show what would be generated
    console.print("[bold]Outputs that would be generated:[/bold]")
    console.print("  • gap_analysis_report.md")
    console.print("  • gap_analysis_report.json")
    console.print("  • revised_policy.md")
    console.print("  • implementation_roadmap.md")
    console.print("  • implementation_roadmap.json")
    console.print("  • audit_log.json")
    console.print()
    
    console.print("[yellow]ℹ️  This is a dry run. No analysis was performed.[/yellow]")
    console.print("[dim]Remove --dry-run flag to execute the analysis.[/dim]")


class PolicyFileHandler(FileSystemEventHandler):
    """Handler for policy file events in watch mode."""
    
    def __init__(self, domain: Optional[str], config: Optional[Path], model: Optional[str]):
        """Initialize handler.
        
        Args:
            domain: Policy domain
            config: Configuration file
            model: Model name
        """
        self.domain = domain
        self.config = config
        self.model = model
        self.processed_files = set()
    
    def on_created(self, event):
        """Handle file creation event.
        
        Args:
            event: File system event
        """
        if isinstance(event, FileCreatedEvent) and not event.is_directory:
            file_path = Path(event.src_path)
            
            # Check if it's a policy file
            if file_path.suffix.lower() in ['.pdf', '.docx', '.txt', '.md']:
                # Avoid processing the same file multiple times
                if file_path in self.processed_files:
                    return
                
                self.processed_files.add(file_path)
                
                console.print(f"\n[cyan]📄 New policy detected: {file_path.name}[/cyan]")
                console.print(f"[dim]Waiting 2 seconds for file to be fully written...[/dim]")
                time.sleep(2)  # Wait for file to be fully written
                
                try:
                    # Import here to avoid circular imports
                    from cli.main import run_analysis_with_progress, load_configuration
                    
                    # Load configuration
                    pipeline_config = load_configuration(self.config, verbose=False)
                    
                    # Run analysis
                    console.print(f"[green]Starting analysis...[/green]\n")
                    exit_code = run_analysis_with_progress(
                        policy_path=file_path,
                        config=pipeline_config,
                        domain=self.domain,
                        output_dir=None,
                        model=self.model,
                        verbose=False
                    )
                    
                    if exit_code == 0:
                        console.print(f"\n[green]✓ Analysis complete for {file_path.name}[/green]")
                    else:
                        console.print(f"\n[red]✗ Analysis failed for {file_path.name}[/red]")
                
                except Exception as e:
                    console.print(f"\n[red]✗ Error analyzing {file_path.name}: {e}[/red]")
                
                console.print(f"\n[dim]Watching for new policies...[/dim]")


@click.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option(
    '--domain', '-d',
    type=click.Choice(['isms', 'risk_management', 'patch_management', 'data_privacy'], case_sensitive=False),
    help='Policy domain for CSF prioritization'
)
@click.option(
    '--config', '-c',
    type=click.Path(exists=True),
    help='Path to configuration file (YAML/JSON)'
)
@click.option(
    '--model', '-m',
    type=str,
    help='LLM model name'
)
@click.option(
    '--interval', '-i',
    type=int,
    default=5,
    help='Check interval in seconds (default: 5)'
)
@click.option(
    '--recursive', '-r',
    is_flag=True,
    help='Watch subdirectories recursively'
)
def watch(
    directory: str,
    domain: Optional[str],
    config: Optional[str],
    model: Optional[str],
    interval: int,
    recursive: bool
):
    """
    Watch a directory for new policy files and analyze them automatically.
    
    DIRECTORY: Directory to watch for new policy files
    
    \b
    Examples:
      # Watch current directory
      policy-analyzer watch . --domain isms
      
      # Watch with custom config
      policy-analyzer watch ./policies --config my-config.yaml
      
      # Watch recursively
      policy-analyzer watch ./policies --recursive
    """
    watch_path = Path(directory)
    config_path = Path(config) if config else None
    
    console.print(Panel(
        f"[bold cyan]Watch Mode[/bold cyan]\n\n"
        f"[bold]Directory:[/bold] {watch_path.absolute()}\n"
        f"[bold]Domain:[/bold] {domain or 'Auto-detect'}\n"
        f"[bold]Recursive:[/bold] {'Yes' if recursive else 'No'}\n"
        f"[bold]Check Interval:[/bold] {interval}s\n\n"
        f"[dim]Watching for new policy files (.pdf, .docx, .txt, .md)...[/dim]\n"
        f"[dim]Press Ctrl+C to stop[/dim]",
        box=box.ROUNDED,
        border_style="cyan"
    ))
    
    # Create event handler and observer
    event_handler = PolicyFileHandler(domain, config_path, model)
    observer = Observer()
    observer.schedule(event_handler, str(watch_path), recursive=recursive)
    
    try:
        observer.start()
        console.print("[green]✓ Watch mode started[/green]\n")
        
        while True:
            time.sleep(interval)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Stopping watch mode...[/yellow]")
        observer.stop()
    
    observer.join()
    console.print("[green]✓ Watch mode stopped[/green]")


@click.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Show detailed configuration information'
)
def validate_config(config_file: str, verbose: bool):
    """
    Validate a configuration file.
    
    CONFIG_FILE: Path to configuration file (YAML/JSON)
    
    \b
    Examples:
      # Validate config
      policy-analyzer validate-config config.yaml
      
      # Validate with details
      policy-analyzer validate-config config.yaml --verbose
    """
    from cli.config_validator import validate_config_file
    
    config_path = Path(config_file)
    is_valid = validate_config_file(config_path, verbose)
    
    if is_valid:
        sys.exit(0)
    else:
        sys.exit(1)


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
    from cli.completion import completion as completion_cmd
    
    # Call the completion command from completion module
    ctx = click.get_current_context()
    ctx.invoke(completion_cmd, shell=shell, install=install)


# Export commands
__all__ = ['watch', 'validate_config', 'completion', 'dry_run_analysis']
