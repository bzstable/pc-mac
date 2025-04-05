"""
Command-line interface for the Perplexity AI code assistant.
"""

import typer
import asyncio
from typing import Tuple
from .agents.perplexity import PerplexityAPI
from .ui.terminal import TerminalUI

app = typer.Typer()

@app.command()
def main():
    """Start the Perplexity AI code assistant."""
    # Declare ui here so it's available in except block
    ui = TerminalUI() 
    api = None # Initialize api to None
    try:
        # Initialize components
        api = PerplexityAPI()
        
        # Show welcome message
        ui.show_welcome()
        
        # Define query handler that updates UI state
        async def handle_query(query: str) -> Tuple[str, bool]:
            response, is_command = await api.process_query(query)
            
            # Update UI current directory if it changed
            ui.update_current_dir(api.current_dir)
            
            return response, is_command
            
        # Start interactive loop
        asyncio.run(ui.interactive_prompt(handle_query))
        
    except ValueError as e:
        # Handle API key error specifically
        print(f"\nError: {str(e)}")
        print("Please set the PPLX_API_KEY environment variable:")
        print("    export PPLX_API_KEY='your-api-key-here'")
        raise typer.Exit(1)
    except Exception as e:
        # Use ui.show_error if available
        ui.show_error(f"Application startup error: {str(e)}")
        raise typer.Exit(1)
    finally:
        # Cleanup
        if api: # Check if api was successfully initialized
            asyncio.run(api.close())

if __name__ == "__main__":
    app() 