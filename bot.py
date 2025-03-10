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
            "[2] [yellow]Leave Server by ID[/yellow]\n" +
            "[3] [red]Exit[/red]",
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
                    if self.servers:
                        self.display_servers()
                    else:
                        self.console.print("[yellow]No servers found. Please check your Discord token.[/yellow]")
                else:
                    self.console.print(f"[bold red]Error: Failed to load servers (Status: {response.status_code})[/bold red]")
            except Exception as e:
                self.console.print(f"[bold red]Error: {str(e)}[/bold red]")

    def display_servers(self):
        if not self.servers:
            self.console.print("[yellow]No servers found.[/yellow]")
            return

        table = Table(show_header=True, header_style="bold magenta", border_style="blue", padding=(0, 2))
        table.add_column("#", style="dim", width=6, justify="center")
        table.add_column("Server Name", style="cyan", min_width=30)
        table.add_column("Server ID", style="green", width=20)

        # Sort servers alphabetically by name
        sorted_servers = sorted(self.servers, key=lambda x: x['name'].lower())

        for idx, server in enumerate(sorted_servers, 1):
            row_style = "on grey15" if idx % 2 == 0 else ""
            # Ensure server name is properly displayed
            server_name = server.get('name', 'Unknown Server')
            server_id = server.get('id', 'N/A')
            
            table.add_row(
                f"[bold]#{idx}[/bold]",
                server_name,
                server_id,
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
            self.load_servers()
            if not self.servers:
                self.console.print("[yellow]No servers available to leave.[/yellow]")
                return

        self.display_servers()
        self.console.print("\n[bold cyan]Enter server numbers to select (comma-separated) or 'all' for all servers:[/bold cyan]")
        selection = input("> ").strip()

        if selection.lower() == 'all':
            self.selected_servers = self.servers
        else:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                # Validate indices are within range
                if any(i < 0 or i >= len(self.servers) for i in indices):
                    self.console.print("[bold red]Error: One or more server numbers are out of range. Please try again.[/bold red]")
                    return
                self.selected_servers = [self.servers[i] for i in indices]
            except (ValueError, IndexError):
                self.console.print("[bold red]Invalid selection. Please enter valid server numbers.[/bold red]")
                return

        if self.selected_servers:
            self.console.print(f"\n[yellow]Selected {len(self.selected_servers)} servers to leave:[/yellow]")
            for server in self.selected_servers:
                self.console.print(f"[yellow]• {server['name']} (ID: {server['id']})[/yellow]")
            if Confirm.ask("\n[bold red]Are you sure you want to leave these servers?[/bold red]"):
                self.leave_servers()
            else:
                self.console.print("[blue]Operation cancelled.[/blue]")
                self.selected_servers = []

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
                    progress.update(task, description=f"[yellow]Leaving server #{idx}: {server.get('name', 'Unknown Server')} (ID: {server.get('id', 'N/A')})...[/yellow]")
                    url = f"https://discord.com/api/v9/users/@me/guilds/{server['id']}"
                    response = requests.delete(url, headers=self.headers, json={})

                    if response.status_code == 204:
                        progress.update(task, advance=1, refresh=True,
                                      description=f"[green]Left server #{idx}/{total}: {server.get('name', 'Unknown Server')}[/green]")
                        # Refresh server list after successful leave
                        response = requests.get("https://discord.com/api/v9/users/@me/guilds", headers=self.headers)
                        if response.status_code == 200:
                            self.servers = response.json()
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

    def leave_by_server_id(self):
        self.console.print("\n[bold cyan]Enter server ID to leave (or multiple IDs separated by commas):[/bold cyan]")
        server_ids = input("> ").strip().split(',')
        server_ids = [sid.strip() for sid in server_ids if sid.strip()]

        if not server_ids:
            self.console.print("[bold red]No valid server IDs provided.[/bold red]")
            return

        # Verify server IDs exist in the current server list
        valid_servers = []
        for server_id in server_ids:
            server = next((s for s in self.servers if s['id'] == server_id), None)
            if server:
                valid_servers.append(server)
            else:
                self.console.print(f"[red]Server with ID {server_id} not found.[/red]")

        if valid_servers:
            self.console.print(f"\n[yellow]Selected {len(valid_servers)} servers to leave:[/yellow]")
            for server in valid_servers:
                self.console.print(f"[yellow]• {server['name']} (ID: {server['id']})[/yellow]")
            if Confirm.ask("\n[bold red]Are you sure you want to leave these servers?[/bold red]"):
                self.selected_servers = valid_servers
                self.leave_servers()
            else:
                self.console.print("[blue]Operation cancelled.[/blue]")
                self.selected_servers = []
        else:
            self.console.print("[bold red]No valid servers found to leave.[/bold red]")

    def run(self):
        # Start auto-refresh in a separate thread
        refresh_thread = threading.Thread(target=self.auto_refresh_servers)
        refresh_thread.daemon = True
        refresh_thread.start()

        # Initial server load
        self.load_servers()

        while True:
            self.display_menu()
            choice = input("Enter your choice (1-3): ").strip()

            if choice == '1':
                self.select_servers()
            elif choice == '2':
                self.leave_by_server_id()
            elif choice == '3':
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