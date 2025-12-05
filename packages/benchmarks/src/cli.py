"""
APP-Bench CLI - Command line interface for running benchmarks.
"""
import click
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
import json

from src.registry import BENCHMARK_REGISTRY, get_benchmark
from src.runner import BenchmarkRunner
from src.config import BenchmarkConfig

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="aureon-bench")
def cli():
    """APP-Bench: Aureon Planetary Procurement Benchmark Suite
    
    Evaluate procurement intelligence systems across 20 standardized tasks
    covering coverage, precision, compliance, and scalability.
    """
    pass


@cli.command()
def list():
    """List all available benchmark tasks."""
    table = Table(title="APP-Bench Tasks", show_header=True)
    table.add_column("ID", style="cyan", width=10)
    table.add_column("Name", style="green", width=35)
    table.add_column("Dimension", style="yellow", width=20)
    table.add_column("Difficulty", style="magenta", width=12)
    table.add_column("Status", style="blue", width=10)
    
    for task_id, task in BENCHMARK_REGISTRY.items():
        status = "✓ Ready" if task.implemented else "○ Planned"
        table.add_row(
            task_id,
            task.name,
            task.dimension,
            task.difficulty,
            status
        )
    
    console.print(table)
    console.print(f"\nTotal: {len(BENCHMARK_REGISTRY)} tasks")


@cli.command()
@click.argument("task_id")
@click.option("--org-id", help="Organization ID for context-specific benchmarks")
@click.option("--api-url", default="http://localhost:8000", help="Aureon API URL")
@click.option("--output", "-o", type=click.Path(), help="Output file for results")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def run(task_id: str, org_id: str, api_url: str, output: str, verbose: bool):
    """Run a specific benchmark task.
    
    Example: aureon-bench run APP-04 --org-id abc123
    """
    task = get_benchmark(task_id)
    if not task:
        console.print(f"[red]Error:[/red] Unknown task ID: {task_id}")
        console.print("Use 'aureon-bench list' to see available tasks.")
        raise SystemExit(1)
    
    if not task.implemented:
        console.print(f"[yellow]Warning:[/yellow] Task {task_id} is not yet implemented.")
        raise SystemExit(0)
    
    console.print(Panel(
        f"[bold]{task.name}[/bold]\n\n"
        f"Dimension: {task.dimension}\n"
        f"Difficulty: {task.difficulty}\n"
        f"Description: {task.description}",
        title=f"Running {task_id}",
        border_style="cyan"
    ))
    
    config = BenchmarkConfig(
        api_url=api_url,
        organization_id=org_id,
        verbose=verbose,
    )
    
    runner = BenchmarkRunner(config)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        run_task = progress.add_task(f"Running {task_id}...", total=None)
        
        try:
            result = runner.run(task)
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            if verbose:
                console.print_exception()
            raise SystemExit(1)
    
    # Display results
    console.print("\n[bold green]Results[/bold green]\n")
    
    metrics_table = Table(show_header=True)
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Value", style="green")
    metrics_table.add_column("Target", style="yellow")
    metrics_table.add_column("Status", style="blue")
    
    for metric_name, metric_value in result.metrics.items():
        target = task.targets.get(metric_name, "N/A")
        if isinstance(target, (int, float)) and isinstance(metric_value, (int, float)):
            status = "✓ Pass" if metric_value >= target else "✗ Fail"
        else:
            status = "—"
        
        metrics_table.add_row(
            metric_name,
            f"{metric_value:.4f}" if isinstance(metric_value, float) else str(metric_value),
            f"{target:.4f}" if isinstance(target, float) else str(target),
            status
        )
    
    console.print(metrics_table)
    console.print(f"\nDuration: {result.duration_seconds:.2f}s")
    
    # Save results
    if output:
        output_path = Path(output)
    else:
        output_path = Path("results") / task_id / f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(result.to_dict(), f, indent=2, default=str)
    
    console.print(f"\n[dim]Results saved to: {output_path}[/dim]")


@cli.command()
@click.option("--difficulty", type=click.Choice(["basic", "intermediate", "advanced", "expert"]))
@click.option("--dimension", help="Filter by dimension (e.g., 'coverage', 'precision')")
@click.option("--api-url", default="http://localhost:8000", help="Aureon API URL")
@click.option("--org-id", help="Organization ID for context-specific benchmarks")
@click.option("--all", "run_all", is_flag=True, help="Run all implemented benchmarks")
def batch(difficulty: str, dimension: str, api_url: str, org_id: str, run_all: bool):
    """Run multiple benchmarks in batch mode."""
    tasks = []
    
    for task_id, task in BENCHMARK_REGISTRY.items():
        if not task.implemented:
            continue
        
        if difficulty and task.difficulty.lower() != difficulty.lower():
            continue
        
        if dimension and dimension.lower() not in task.dimension.lower():
            continue
        
        tasks.append((task_id, task))
    
    if not tasks:
        console.print("[yellow]No matching tasks found.[/yellow]")
        return
    
    console.print(f"[bold]Running {len(tasks)} benchmark(s)...[/bold]\n")
    
    config = BenchmarkConfig(
        api_url=api_url,
        organization_id=org_id,
    )
    runner = BenchmarkRunner(config)
    
    results_summary = []
    
    for task_id, task in tasks:
        console.print(f"  • {task_id}: {task.name}...", end=" ")
        try:
            result = runner.run(task)
            passed = all(
                result.metrics.get(m, 0) >= t 
                for m, t in task.targets.items() 
                if isinstance(t, (int, float))
            )
            status = "[green]PASS[/green]" if passed else "[red]FAIL[/red]"
            console.print(status)
            results_summary.append((task_id, passed, result))
        except Exception as e:
            console.print(f"[red]ERROR[/red]: {e}")
            results_summary.append((task_id, False, None))
    
    # Summary
    passed = sum(1 for _, p, _ in results_summary if p)
    total = len(results_summary)
    
    console.print(f"\n[bold]Summary: {passed}/{total} passed[/bold]")


@cli.command()
@click.argument("run_id")
@click.option("--format", "fmt", type=click.Choice(["text", "json", "html"]), default="text")
def report(run_id: str, fmt: str):
    """Generate a report for a benchmark run."""
    results_dir = Path("results")
    
    # Find matching results
    matching = list(results_dir.rglob(f"*{run_id}*.json"))
    
    if not matching:
        console.print(f"[red]No results found matching: {run_id}[/red]")
        return
    
    console.print(f"[bold]Benchmark Report[/bold]\n")
    
    for result_file in matching:
        with open(result_file) as f:
            result = json.load(f)
        
        console.print(f"Task: {result.get('task_id', 'Unknown')}")
        console.print(f"Run Time: {result.get('started_at', 'Unknown')}")
        console.print(f"Duration: {result.get('duration_seconds', 0):.2f}s")
        console.print("\nMetrics:")
        
        for metric, value in result.get('metrics', {}).items():
            console.print(f"  {metric}: {value}")
        
        console.print()


if __name__ == "__main__":
    cli()

