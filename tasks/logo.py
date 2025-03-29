import pyfiglet
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# Генерация ASCII-арта
ascii_text = pyfiglet.figlet_format("BULDOZER", font="big")
max_length = max(len(line) for line in ascii_text.split("\n"))

# Вывод красивого ASCII-арта
console.print(f"[cyan]{ascii_text}[/cyan]")

table = Table(width=max_length)
table.add_column("Info", justify="center", style="cyan", no_wrap=True)
table.add_row("🛠️ Soneium Badges Farmer 1.0 🛠️")
table.add_row("💻 GitHub: https://github.com/Buldozerch")
table.add_row("👨 Channel: https://t.me/buldozercode")
console.print(table)
