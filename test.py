from rich.table import Table
from rich.console import Console
from rich.progress import track
import time

console = Console()
table = Table(show_header=True, header_style="bold magenta")
table.add_column("Data", style="dim", width=12)
table.add_column("Transaction", justify="right")
table.add_column("Amount", justify="right")
# table.add_column("Data", justify="right")
    

table.add_row("2024-01-25", "Deposit", "$500")
table.add_row("2024-01-26", "Withdrawal", "-$500")


for step in track(range(10), description="Loading..."):
    time.sleep(0.5)
console.print(table)
