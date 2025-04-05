"""
Terminal UI design using rich library.
Handles all terminal rendering and user interaction.
"""

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.layout import Layout
from rich.style import Style
from rich.text import Text
from rich.syntax import Syntax
from rich.align import Align
from rich.markdown import Markdown
from rich.spinner import Spinner
from rich.live import Live
from typing import Optional, Callable, Tuple, Coroutine, Any
import asyncio
import os
import re
import time # Import time for duration calculation
from pathlib import Path

# Perplexity theme color
THEME_COLOR = "#00c5e0"
THINKING_COLOR = "dim cyan"

class TerminalUI:
    def __init__(self):
        # Use strip_control_codes=True if encountering issues with raw control chars
        self.console = Console(log_time=False, log_path=False) 
        self.current_dir = os.getcwd()
        self.current_task = None # To store the asyncio task for potential cancellation
        
    def show_welcome(self):
        """Display welcome message."""
        # Welcome message in a box
        welcome_text = Text()
        welcome_text.append("Plex Code", style=f"bold {THEME_COLOR}")
        welcome_text.append(" - Powered by Perplexity AI", style="white")
        
        welcome_panel = Panel(
            Align.center(welcome_text),
            border_style=THEME_COLOR,
            padding=(1, 2)
        )
        
        # How to use guide (outside the box)
        usage_text = Text()
        usage_text.append("\nHow to use:\n\n", style="bold white")
        usage_text.append("• Just type your question or command naturally\n", style="dim white")
        usage_text.append("• Ask about code (e.g., 'explain cli.py'), get explanations, request analysis\n", style="dim white")
        usage_text.append("• Use CLI commands (", style="dim white")
        usage_text.append("ls/tree, cd, pwd, create <file>, mkdir <dir>, rm <name>", style=THEME_COLOR)
        usage_text.append(") or natural language ('list files', 'go to src', 'create data.txt')\n", style="dim white")
        usage_text.append("• Type ", style="dim white")
        usage_text.append("help", style=THEME_COLOR)
        usage_text.append(" to see available commands\n", style="dim white")
        usage_text.append("• Type ", style="dim white")
        usage_text.append("exit", style=THEME_COLOR)
        usage_text.append(" to quit\n", style="dim white")
        usage_text.append("• Press ", style="dim white")
        usage_text.append("Ctrl+C", style=THEME_COLOR)
        usage_text.append(" during API calls to interrupt\n", style="dim white")

        # Print everything with proper spacing
        self.console.print("\n")
        self.console.print(Align.center(welcome_panel))
        self.console.print(Align.center(usage_text))
        self.console.print("\n")
        
    async def get_input(self) -> str:
        """Get user input with styled prompt showing current directory."""
        cwd_display = self._get_cwd_display()
        prompt = f"[{THEME_COLOR}]{cwd_display}[/{THEME_COLOR}]> "
        
        self.console.print(Text.from_markup(prompt), end="")
        # Use run_in_executor for blocking input()
        try:
             user_input = await asyncio.get_event_loop().run_in_executor(None, input)
             return user_input
        except EOFError: # Handle Ctrl+D or similar EOF signals gracefully
             return "exit"
        except KeyboardInterrupt: # Handle Ctrl+C during input
             self.console.print("\nInput cancelled.") # Provide feedback
             return "" # Return empty string to loop back to prompt

    def _get_cwd_display(self) -> str:
         """Get a display string for the current working directory."""
         try:
             # Try to get relative path to home directory for tidiness
             home = Path.home()
             cwd_path = Path(self.current_dir)
             if cwd_path == home:
                  return "~"
             try:
                  rel_path = cwd_path.relative_to(home)
                  # Limit length of relative path display too
                  if len(str(rel_path)) > 30: 
                      return f"~/.../{'/'.join(rel_path.parts[-2:])}"
                  return f"~/" + str(rel_path)
             except ValueError: # Not relative to home
                  pass # Fall through to basename logic
         except Exception:
              pass # Fallback if home dir check fails
              
         # Default: show basename or short path
         if len(self.current_dir) > 35:
             path_parts = Path(self.current_dir).parts
             if len(path_parts) > 2:
                  return os.path.join("...", path_parts[-2], path_parts[-1])
             else:
                  return os.path.basename(self.current_dir)
         else:
             return self.current_dir
             
    def show_thinking(self, message: str = "Thinking"):
        """Placeholder: Show processing message. Main display handled by Live."""
        # This method might not be actively used when Live is active,
        # but exists for potential calls from other parts or future refactors.
        # We could potentially add a simple non-Live indicator here if needed elsewhere.
        pass # Keep it simple for now
        
    def clear_thinking(self):
         """Clear the line where the thinking indicator might have been."""
         # Overwrite the current line with spaces to ensure clearance
         # Useful after Live(transient=True) or if an error occurs
         self.console.print(" " * (self.console.width -1) , end="\r")

    def show_error(self, message: str):
        """Display error message."""
        self.clear_thinking() # Ensure line is clear before printing error
        # Ensure message is a string
        message_str = str(message) if not isinstance(message, str) else message
        self.console.print(Panel(message_str, title="Error", border_style="red", padding=(0, 1)))
        self.console.print()
        
    def show_success(self, message: str):
        """Display success message (usually for exit or non-error command results)."""
        self.clear_thinking() # Ensure line is clear
        if message and message.strip(): # Only print if there's content
             self.console.print(f"[{THEME_COLOR}]{message}[/]")
             self.console.print()
        
    def _display_reasoning(self, reasoning: str):
        """Display the extracted <think> content in a distinct way."""
        # Use a Panel with a specific title and dimmed style
        reasoning_panel = Panel(
            Markdown(reasoning.strip()), # Render reasoning as Markdown
            title="[dim]Reasoning[/dim]",
            border_style="dim cyan",
            padding=(0, 1),
            title_align="left"
        )
        self.console.print(reasoning_panel)

    def _parse_and_display_response(self, response: str, duration: Optional[float]):
        """Parse response for <think> tags and display accordingly, with duration."""
        think_pattern = re.compile(r"<think>(.*?)</think>", re.DOTALL | re.IGNORECASE)
        reasoning_match = think_pattern.search(response)
        
        final_response = think_pattern.sub("", response).strip() # Remove think tags
        
        # Display duration first if available
        # This is now printed by show_output before calling this function
        # if duration is not None:
        #      self.console.print(f"[dim](took {duration:.2f}s)[/dim]")
             
        if reasoning_match:
            reasoning = reasoning_match.group(1)
            self._display_reasoning(reasoning)
            
        if final_response:
             # Use Panel with Theme color title for the main response
             response_panel = Panel(
                Markdown(final_response),
                border_style=THEME_COLOR,
                padding=(1, 1),
                title=f"[{THEME_COLOR}]Perplexity Response[/]",
                title_align="left"
             )
             self.console.print(response_panel)
        elif not reasoning_match:
             # If no reasoning and no final response, maybe show a message?
             self.console.print("[dim](No response content)[/dim]")

    def show_output(self, output: str, is_command_result: bool, duration: Optional[float] = None):
        """Display output, differentiating formats and handling reasoning/duration."""
        self.clear_thinking() # Clear any potential leftover indicator line
        if not output or not output.strip():
            # Still print duration if it was an AI call that resulted in empty output
            if not is_command_result and duration is not None:
                 self.console.print(f"[dim](took {duration:.2f}s)[/dim]")
                 self.console.print() # Add blank line after duration
            return
            
        if is_command_result:
            # Simple print for command results (ls, pwd, create, errors etc.)
            self.console.print(output)
        else:
            # Print final duration before showing response parts
            if duration is not None:
                self.console.print(f"[dim](took {duration:.2f}s)[/dim]")
            # Parse for <think> tags and display AI response 
            self._parse_and_display_response(output, duration) # Pass duration for context if needed, though not used in parse func now
            
        self.console.print() # Add a blank line after any output
        
    async def interactive_prompt(self, handler: Callable[..., Coroutine[Any, Any, Tuple[str, bool]]]):
        """Start interactive prompt loop with Live display for thinking/timing."""
        while True:
            self.current_task = None # Clear previous task reference
            start_time = None # Reset start time for each loop
            try:
                command = await self.get_input()
                if not command:
                     continue # Loop back on empty input (e.g., Ctrl+C during input)
                     
                if command.lower().strip() in ["exit", "quit"]:
                    self.show_success("Goodbye!")
                    break
                    
                # --- Assume API call might happen, prepare Live display --- 
                # We need to know *beforehand* if it's a local command or API call
                # Let's add a quick check based on the command structure
                is_likely_local = False
                cmd_check = command.lower().strip().split(maxsplit=1)[0]
                # Check against known local command prefixes (could be more robust)
                local_prefixes = ["ls", "tree", "cd", "pwd", "create", "touch", "mkdir", "rm", "delete", "remove", "help"]
                if cmd_check in local_prefixes:
                     is_likely_local = True
                # Add checks for natural language patterns if needed, but keep it simple for now

                if is_likely_local:
                     # Handle local command directly without Live display
                     response, is_command = await handler(command)
                     # Ensure is_command is True for consistency
                     self.show_output(response, True, duration=None)
                else:
                    # Handle potential API call with Live display
                    start_time = time.monotonic()
                    self.current_task = asyncio.create_task(handler(command))

                    response = None
                    is_command = False # Assume API call initially
                    end_time = None

                    # --- Live display section --- 
                    spinner = Spinner("dots", style=THEME_COLOR)
                    thinking_text = Text("Thinking", style=THEME_COLOR)
                    timer_text = Text("(0.00s)", style="dim") # Initial timer text

                    def get_renderable():
                        # Create a new Text object each time to ensure fresh state
                        current_time = time.monotonic()
                        display = Text()
                        display.append(thinking_text)
                        display.append(" ")
                        # Pass current time for frame calculation
                        display.append(spinner.render(current_time))
                        display.append(" ")
                        display.append(timer_text)
                        return display

                    with Live(get_renderable(), console=self.console, refresh_per_second=10, transient=True) as live:
                        while not self.current_task.done():
                            elapsed = time.monotonic() - start_time
                            timer_text.plain = f"({elapsed:.2f}s)"
                            live.update(get_renderable())
                            await asyncio.sleep(0.1)

                    response, is_command = await self.current_task 
                    end_time = time.monotonic()
                    # Live context exited, display is cleaned up
                    
                    self.current_task = None
                    duration = end_time - start_time if end_time and start_time else None
                    final_duration = duration if not is_command else None # Should always be not is_command here
                    self.show_output(response, is_command, duration=final_duration)
                    
            except KeyboardInterrupt: # Catch Ctrl+C 
                self.clear_thinking() # Ensure line is clear after interrupt
                if self.current_task and not self.current_task.done():
                    self.current_task.cancel()
                    self.console.print("\n[yellow]API call interrupted.[/yellow]")
                    try:
                        await asyncio.wait_for(self.current_task, timeout=0.5)
                    except (asyncio.CancelledError, asyncio.TimeoutError):
                        pass 
                    except Exception as e:
                         self.show_error(f"Error during task cancellation: {e}")
                    self.current_task = None
                else:
                    # Interrupt happened outside API call or during input
                    # get_input handles its own message for input cancellation
                    # If interrupt happened *after* task finished but before output, just ensure newline
                    self.console.print() # Ensure we are on a new line after ^C
                     # self.console.print("\nOperation cancelled.") # Maybe redundant
                # self.console.print() # Extra newline for clarity - might be too much now
                     
            except asyncio.CancelledError:
                 self.clear_thinking() # Ensure line is clear
                 self.console.print("\n[yellow]Operation cancelled externally.[/yellow]")
                 self.current_task = None
                 
            except Exception as e:
                self.clear_thinking() # Ensure line is clear
                import traceback
                self.show_error(f"Unexpected error in main loop: {str(e)}\n{traceback.format_exc()}")
                if self.current_task and not self.current_task.done():
                    self.current_task.cancel()
                self.current_task = None
                
    def update_current_dir(self, new_dir: str):
        """Update the current working directory state for the prompt."""
        self.current_dir = new_dir 