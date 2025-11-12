import json
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text

console = Console()

def create_dashboard():
    """Create comprehensive dashboard"""
    
    # Header
    console.print(Panel.fit(
        "[bold cyan]🎯 MCP SERVER TESTING DASHBOARD[/bold cyan]\n"
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        border_style="cyan"
    ))
    
    # Server Log Stats
    if os.path.exists("logs/mcp_server.log"):
        with open("logs/mcp_server.log", 'r') as f:
            lines = f.readlines()
            
            info_count = sum(1 for line in lines if "[INFO]" in line)
            success_count = sum(1 for line in lines if "[SUCCESS]" in line)
            error_count = sum(1 for line in lines if "[ERROR]" in line)
            
            log_table = Table(title="📊 Server Log Statistics", show_header=False)
            log_table.add_column("Metric", style="cyan")
            log_table.add_column("Value", style="yellow")
            
            log_table.add_row("Total Log Entries", str(len(lines)))
            log_table.add_row("INFO Messages", f"[blue]{info_count}[/blue]")
            log_table.add_row("SUCCESS Messages", f"[green]{success_count}[/green]")
            log_table.add_row("ERROR Messages", f"[red]{error_count}[/red]")
            
            console.print(log_table)
    
    # Test Report
    if os.path.exists("logs/test_report.json"):
        with open("logs/test_report.json", 'r') as f:
            report = json.load(f)
            
            test_table = Table(title="🧪 Test Results", show_header=False)
            test_table.add_column("Metric", style="cyan")
            test_table.add_column("Value", style="yellow")
            
            test_table.add_row("Total Queries", str(report['total_queries']))
            test_table.add_row("Successful", f"[green]{report['successful']}[/green]")
{