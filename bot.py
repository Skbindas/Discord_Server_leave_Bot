import os
import json
import requests
import threading
from queue import Queue
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from rich import print as rprint
from rich.panel import Panel

class ServerManagerCLI:
    def __init__(self):
        self.console = Console()
        
        # Load environment variables
        load_dotenv()
        self.token = os.getenv('DISCORD_TOKEN')
        self.headers = {
            "Authorization": self.token,
            "Content-Type": "application/json"
        }

        # Initialize variables
        self.servers = []
        self.selected_servers = []
        self.operation_queue = Queue()
        self.is_processing = False

    def display_menu(self):
        self.console.clear()
        # ASCII Art Header
        header = """
    ____  _                       _   _                     ____        __ 
   |  _ \(_)___  ___ ___  _ __ __| | | |     ___  __ ___   _____  | __ )  ___ | |_ 
   | | | | / __|/ __/ _ \| '__/ _` | | |    / _ \/ _` \ \ / / _ \ |  _ \ / _ \|  _|
   | |_| | \ __\ (_| (_) | | | (_| | | |___|  __/ (_| |\ V /  __/ | |_) | (_) | |_ 
   |____/|_|___/\___\___/|_|  \__,_| |_____|\___|\__,_| \_/ \___| |____/ \___/ \__|
                                                                      
        """
        self.console.print(header, style="bold cyan")
        self.console.print("\n[bold]Choose an option:[/bold]")
        self.console.print(Panel.fit(
            "[1] [yellow]Select Servers to Leave[/yellow]\n" +
            "[2] [red]Exit[/red]",
            title="Menu",
            border_style="blue"        ))
        self.console.print("\n[blue]Connect with me:[/blue]")
        self.console.print("[bold blue][link=https://github.com/Skbindas]https://github.com/Skbindas[/link][/bold blue] • [bold blue][link=https://t.me/AirdropGuru47]https://t.me/AirdropGuru47[/link][/bold blue]")

    def load_servers(self):
        with self.console.status("[bold blue]Loading servers...[/bold blue]") as status:
            try:
                response = requests.get(
                    "https://discord.com/api/v9/users/@me/guilds",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    self.servers = response.json()
                    self.display_servers()
                else:
                    self.console.print(f"[bold red]Error: Failed to load servers (Status: {response.status_code})[/bold red]")
            except Exception as e:
                self.console.print(f"[bold red]Error: {str(e)}[/bold red]")

    def display_servers(self):
        if not self.servers:
            self.console.print("[yellow]No servers found.[/yellow]")
            return

        table = Table(show_header=True, header_style="bold magenta", border_style="blue")
        table.add_column("#", style="dim", width=4)
        table.add_column("Server Name", style="cyan")
        table.add_column("Server ID", style="green")

        # Sort servers alphabetically by name
        sorted_servers = sorted(self.servers, key=lambda x: x['name'].lower())

        for idx, server in enumerate(sorted_servers, 1):
            row_style = "on grey15" if idx % 2 == 0 else ""
            table.add_row(
                str(idx),
                server['name'],
                server['id'],
                style=row_style
            )

        self.console.print("[bold]Available Servers[/bold]")
        self.console.print(table, style="blue")
        self.console.print(f"\n[dim]Total Servers: {len(self.servers)}[/dim]")

    def auto_refresh_servers(self):
        while not getattr(self, '_stop_refresh', False):
            try:
                response = requests.get(
                    "https://discord.com/api/v9/users/@me/guilds",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    self.servers = response.json()
            except Exception:
                pass
            threading.Event().wait(1.0)

    def select_servers(self):
        if not self.servers:
            self.console.print("[yellow]Please refresh the server list first.[/yellow]")
            return

        self.display_servers()
        self.console.print("\n[bold cyan]Enter server numbers to select (comma-separated) or 'all' for all servers:[/bold cyan]")
        selection = input("> ").strip()

        if selection.lower() == 'all':
            self.selected_servers = self.servers
        else:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                self.selected_servers = [self.servers[i] for i in indices if 0 <= i < len(self.servers)]
            except (ValueError, IndexError):
                self.console.print("[bold red]Invalid selection. Please try again.[/bold red]")
                return

        if self.selected_servers:
            self.console.print(f"[yellow]Selected {len(self.selected_servers)} servers[/yellow]")
            if Confirm.ask("[bold red]Are you sure you want to leave these servers?[/bold red]"):
                self.leave_servers()

    def leave_servers(self):
        if self.is_processing:
            return

        self.is_processing = True
        total = len(self.selected_servers)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TextColumn("[progress.completed]/{task.total}"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            "[time remaining]",
            auto_refresh=False
        ) as progress:
            task = progress.add_task("[cyan]Leaving servers...[/cyan]", total=total)

            for idx, server in enumerate(self.selected_servers, 1):
                try:
                    url = f"https://discord.com/api/v9/users/@me/guilds/{server['id']}"
                    response = requests.delete(url, headers=self.headers, json={})

                    if response.status_code == 204:
                        progress.update(task, advance=1, refresh=True,
                                      description=f"[green]Left {idx}/{total} servers - {server['name']}[/green]")
                    elif response.status_code == 429:
                        retry_after = float(response.headers.get('Retry-After', 5))
                        progress.update(task, description=f"[yellow]Rate limited. Waiting {retry_after} seconds...[/yellow]")
                        threading.Event().wait(retry_after)
                    else:
                        progress.update(task, description=f"[red]Failed to leave {server['name']}: {response.status_code}[/red]")

                except Exception as e:
                    progress.update(task, description=f"[red]Error leaving {server['name']}: {str(e)}[/red]")

                threading.Event().wait(1.0)

        self.is_processing = False
        self.selected_servers = []
        self.console.print("[bold green]Server leave operations completed![/bold green]")

    def run(self):
        # Start auto-refresh in a separate thread
        refresh_thread = threading.Thread(target=self.auto_refresh_servers)
        refresh_thread.daemon = True
        refresh_thread.start()

        # Initial server load
        self.load_servers()

        while True:
            self.display_menu()
            choice = input("Enter your choice (1-2): ").strip()

            if choice == '1':
                self.select_servers()
            elif choice == '2':
                self._stop_refresh = True
                self.console.print("[bold blue]Goodbye![/bold blue]")
                break
            else:
                self.console.print("[bold red]Invalid choice. Please try again.[/bold red]")

            input("\nPress Enter to continue...")


def main():
    app = ServerManagerCLI()
    app.run()

if __name__ == "__main__":
    main()