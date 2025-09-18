#!/usr/bin/env python3
"""
FastQCLI - Minimalist FASTQ Quality Control Tool
A simplified, focused CLI for FASTQ file analysis
"""

import click
import json
import sys
from pathlib import Path

# Import core modules (will create these next)
try:
    from core.analyzer import FastQAnalyzer
    from core.reporter import Reporter
except ImportError:
    # For development, add current directory to path
    sys.path.insert(0, str(Path(__file__).parent))
    from core.analyzer import FastQAnalyzer
    from core.reporter import Reporter

__version__ = "1.0.0"


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version=__version__, prog_name="FastQCLI")
@click.option('--help', '-h', is_flag=True, help='Show this message and exit.')
def cli(ctx, help):
    """
    FastQCLI - Simple and fast FASTQ quality control.
    
    Examples:
        fastq-cli analyze sample.fastq           # Quick analysis
        fastq-cli analyze sample.fastq --json    # JSON output
        fastq-cli analyze sample.fastq --html    # Generate HTML report
        fastq-cli check sample.fastq             # Validate format only
    """
    if help or ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit()


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', help='Output file path')
@click.option('--json', 'output_json', is_flag=True, help='JSON output')
@click.option('--html', is_flag=True, help='Generate HTML report')
@click.option('--sample-size', default=10000, type=int, help='Number of reads to sample (default: 10000)')
@click.option('--min-q30', default=80, type=float, help='Minimum Q30 threshold (default: 80)')
@click.option('--quiet', is_flag=True, help='Minimal output')
@click.option('--verbose', is_flag=True, help='Detailed output with progress')
def analyze(input_file, output, output_json, html, sample_size, min_q30, quiet, verbose):
    """
    Analyze FASTQ file quality.
    
    \b
    Examples:
        fastq-cli analyze sample.fastq
        fastq-cli analyze sample.fastq --json > metrics.json
        fastq-cli analyze sample.fastq --html -o report.html
    """
    
    if quiet and verbose:
        click.echo("Error: Cannot use --quiet and --verbose together", err=True)
        sys.exit(1)
    
    # Initialize analyzer
    analyzer = FastQAnalyzer(verbose=verbose)
    
    try:
        # Analyze the file
        if not quiet:
            click.echo(f"Analyzing: {input_file}")
        
        metrics = analyzer.analyze(input_file, sample_size=sample_size)
        
        # Initialize reporter
        reporter = Reporter()
        
        # Handle output based on format
        if output_json:
            result = json.dumps(metrics, indent=2, default=str)
            if output:
                Path(output).write_text(result)
                if not quiet:
                    click.echo(f"JSON saved to: {output}")
            else:
                click.echo(result)
        
        elif html:
            output_path = output or 'fastq_report.html'
            reporter.generate_html(metrics, output_path)
            if not quiet:
                click.echo(f"HTML report saved: {output_path}")
        
        else:
            # Default text output
            if not quiet:
                reporter.print_summary(metrics, min_q30=min_q30)
        
        # Return appropriate exit code
        status = metrics.get('status', 'UNKNOWN')
        if status == 'PASS':
            sys.exit(0)
        elif status == 'WARNING':
            sys.exit(0 if not quiet else 1)
        else:
            sys.exit(1)
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--quiet', is_flag=True, help='Only return exit code')
@click.option('--verbose', is_flag=True, help='Show validation details')
def check(input_file, quiet, verbose):
    """
    Quick validation of FASTQ format.
    
    \b
    Examples:
        fastq-cli check sample.fastq
        fastq-cli check sample.fastq --quiet
    """
    
    analyzer = FastQAnalyzer(verbose=verbose)
    
    try:
        is_valid, message = analyzer.validate(input_file)
        
        if not quiet:
            if is_valid:
                click.echo(f"[OK] Valid FASTQ: {input_file}")
            else:
                click.echo(f"[FAIL] Invalid FASTQ: {input_file}")
                if message and verbose:
                    click.echo(f"  Reason: {message}")
        
        sys.exit(0 if is_valid else 1)
    
    except Exception as e:
        if not quiet:
            click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--pattern', default='*.fastq', help='File pattern (default: *.fastq)')
@click.option('--recursive', is_flag=True, help='Search recursively')
def list(directory, pattern, recursive):
    """
    List FASTQ files in directory.
    
    \b
    Examples:
        fastq-cli list /data/fastq/
        fastq-cli list . --pattern "*.fq.gz" --recursive
    """
    from utils.io_handler import find_fastq_files
    
    files = find_fastq_files(directory, pattern=pattern, recursive=recursive)
    
    if not files:
        click.echo("No FASTQ files found")
        sys.exit(1)
    
    click.echo(f"Found {len(files)} FASTQ file(s):")
    for f in files:
        size_mb = f.stat().st_size / (1024 * 1024)
        click.echo(f"  {f.name} ({size_mb:.1f} MB)")


if __name__ == '__main__':
    cli()