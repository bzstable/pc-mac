"""
Perplexity AI API integration with local context awareness.
"""

import httpx
import json
import os
import re
import shutil # Needed for directory removal
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

# Try to get API key from environment variable first
API_KEY = os.getenv("PPLX_API_KEY", "")

# Constants for tree display
TREE_SPACE = "    "
TREE_BRANCH = "│   "
TREE_TEE = "├── "
TREE_LAST = "└── "

class PerplexityAPI:
    def __init__(self):
        if not API_KEY:
            raise ValueError("Perplexity API key not found. Please set PPLX_API_KEY environment variable.")
            
        self.base_url = "https://api.perplexity.ai"
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=60.0
        )
        
        # Local command handlers
        self.commands = {
            "help": self._handle_help,
            "exit": self._handle_exit,
            "quit": self._handle_exit,
            "ls": self._handle_ls,
            "tree": self._handle_ls,
            "cd": self._handle_cd,
            "pwd": self._handle_pwd,
            "create": self._handle_create_file,
            "touch": self._handle_create_file, # Alias
            "mkdir": self._handle_mkdir,
            "rm": self._handle_rm,
            "delete": self._handle_rm, # Alias
            "remove": self._handle_rm # Alias
        }
        
        # Natural language command mapping
        self.natural_commands = {
            # ls / tree
            r"list(?: files?)?(?: in(?: current)? directory)?": "ls",
            r"show(?: directory)? tree": "tree",
            # cd
            r"change(?: directory)? to (.*?)$": "cd",
            r"go to (.*?)$": "cd",
            # pwd
            r"what is the current directory\\??": "pwd",
            r"show(?: the)? current directory": "pwd",
            # create file
            r"create(?: a)?(?: new)? file(?: named)?\s+([\w./-]+)$": "create",
            r"touch\s+([\w./-]+)$": "create",
            # create directory
            r"create(?: a)?(?: new)? directory(?: named)?\s+([\w./-]+)$": "mkdir",
            r"make directory\s+([\w./-]+)$": "mkdir",
            r"mkdir\s+([\w./-]+)$": "mkdir", # Allow direct command via natural lang too
            # remove/delete
            r"delete\s+([\w./-]+)$": "rm",
            r"remove\s+([\w./-]+)$": "rm",
            r"rm\s+([\w./-]+)$": "rm" # Allow direct command
        }
        
        # Initialize current directory
        self.current_dir = os.getcwd()
        self._file_cache: Dict[str, Dict[str, Any]] = {}
        self._update_file_cache()
        self.is_processing_api = False
        
    def _update_file_cache(self):
        """Update the cache of files/dirs in the current directory (non-recursive)."""
        self._file_cache.clear()
        try:
            for item in os.listdir(self.current_dir):
                try:
                    full_path = os.path.join(self.current_dir, item)
                    is_dir = os.path.isdir(full_path)
                    self._file_cache[item] = {'is_dir': is_dir, 'content': None}
                except OSError:
                     self._file_cache[item] = {'is_dir': False, 'content': None, 'error': 'Permission denied'}
        except OSError as e:
            self._file_cache[".error"] = {'is_dir': False, 'content': f"Cannot list directory: {e}"}
            pass
                
    def _handle_help(self) -> Tuple[str, bool]:
        """Handle help command."""
        return ("""Available Mac Commands:
• help                     - Show this help message
• exit/quit                - Exit the application
• ls                       - List files in current directory
• tree                     - Show directory structure in tree format
• cd <dir>                 - Change directory (supports '..', '~', absolute paths)
• pwd                      - Print working directory
• touch <filename>         - Create an empty file
• mkdir <dirname>          - Create a directory
• rm <name>               - Remove a file or empty directory

Natural Language:
• Use phrases like:
  - 'list files'
  - 'show directory tree'
  - 'go to ~/Documents'
  - 'create file test.py'
  - 'make directory src'
  - 'delete file.txt'

For AI queries:
• Ask about code ('explain cli.py'), request explanations, analysis, or generation.""", True)

    def _handle_exit(self) -> Tuple[str, bool]:
        """Handle exit command."""
        return "exit", True
        
    def _build_tree(self, dir_path: str, prefix: str = "", level: int = 0) -> List[str]:
        """Recursively build the directory tree lines."""
        lines = []
        try:
            # Ignore hidden files/dirs for cleaner output
            items = sorted([item for item in os.listdir(dir_path) if not item.startswith('.')])
        except OSError:
             return [f"{prefix}{TREE_LAST}[Error reading directory]"]
             
        count = len(items)
        for i, item in enumerate(items):
            connector = TREE_LAST if i == count - 1 else TREE_TEE
            item_path = os.path.join(dir_path, item)
            is_dir = False
            try:
                is_dir = os.path.isdir(item_path)
            except OSError:
                 item += " [Permission Error]"
                 
            lines.append(f"{prefix}{connector}{item}{'/' if is_dir else ''}")
            
            if is_dir and level < 3:
                extension = TREE_SPACE if i == count - 1 else TREE_BRANCH
                lines.extend(self._build_tree(item_path, prefix + extension, level + 1))
        return lines
        
    def _handle_ls(self) -> Tuple[str, bool]:
        """Handle ls/tree command with tree formatting."""
        tree_lines = self._build_tree(self.current_dir)
        if not tree_lines:
            # Check if directory actually exists or if it was an error listing
            if not os.path.exists(self.current_dir):
                 return f"Error: Current directory '{self.current_dir}' not found.", True
            if not os.access(self.current_dir, os.R_OK):
                 return f"Error: Permission denied for '{self.current_dir}'", True
            return f"{self.current_dir} (empty)", True
            
        output = f"{self.current_dir}\n" + "\n".join(tree_lines)
        return output, True
        
    def _handle_cd(self, path: str) -> Tuple[str, bool]:
        """Handle cd command."""
        original_dir = self.current_dir
        try:
            if not path: return "Usage: cd <directory>", True # Handle empty path
            if path == "..":
                new_dir = os.path.dirname(self.current_dir)
            elif path == "~" or path == "$HOME":
                new_dir = os.path.expanduser("~")
            else:
                temp_path = path
                if not os.path.isabs(temp_path):
                    temp_path = os.path.join(self.current_dir, temp_path)
                # Normalize path to resolve any relative components like '.' or '..' within the path itself
                new_dir = os.path.normpath(temp_path)
                
            if not os.path.exists(new_dir):
                return f"Directory not found: {path} (resolved to {new_dir})", True
            if not os.path.isdir(new_dir):
                return f"Not a directory: {path} (resolved to {new_dir})", True
            if not os.access(new_dir, os.R_OK | os.X_OK):
                 return f"Permission denied: {new_dir}", True
                 
            self.current_dir = new_dir
            os.chdir(new_dir)
            self._update_file_cache()
            return "", True
            
        except Exception as e:
            if self.current_dir != original_dir:
                try: # Attempt to change back safely
                    os.chdir(original_dir)
                    self.current_dir = original_dir
                except Exception: pass # Ignore error if we can't revert
            return f"Error changing directory: {str(e)}", True
            
    def _handle_pwd(self) -> Tuple[str, bool]:
        """Handle pwd command."""
        return f"{self.current_dir}", True
        
    def _handle_create_file(self, filename: str) -> Tuple[str, bool]:
        """Handle create file command."""
        if not filename:
            return "Usage: create <filename>", True
        if ".." in filename or "/" in filename or "\\" in filename:
            return f"Invalid characters or path components in filename: {filename}", True
            
        filepath = os.path.join(self.current_dir, filename)
        try:
            if os.path.exists(filepath):
                return f"File or directory already exists: {filename}", True
            Path(filepath).touch()
            self._file_cache[filename] = {'is_dir': False, 'content': ""}
            return f"File created: {filename}", True
        except OSError as e:
             return f"Error creating file '{filename}': {e.strerror}", True
        except Exception as e:
            return f"Unexpected error creating file: {str(e)}", True
            
    def _handle_mkdir(self, dirname: str) -> Tuple[str, bool]:
        """Handle create directory command."""
        if not dirname:
            return "Usage: mkdir <dirname>", True
        if ".." in dirname or "/" in dirname or "\\" in dirname:
            return f"Invalid characters or path components in dirname: {dirname}", True
            
        dirpath = os.path.join(self.current_dir, dirname)
        try:
            if os.path.exists(dirpath):
                return f"File or directory already exists: {dirname}", True
                
            os.makedirs(dirpath) # Creates parent dirs if needed, no error if exists due to check above
            
            # Update cache immediately
            self._file_cache[dirname] = {'is_dir': True, 'content': None}
            
            return f"Directory created: {dirname}", True
            
        except OSError as e:
             # Provide more specific feedback if possible
             if e.errno == 17: # File exists
                 return f"File or directory already exists: {dirname}", True
             return f"Error creating directory '{dirname}': {e.strerror}", True
        except Exception as e:
            return f"Unexpected error creating directory: {str(e)}", True
            
    def _handle_rm(self, name: str) -> Tuple[str, bool]:
        """Handle remove file or empty directory command."""
        if not name:
            return "Usage: rm <file_or_empty_dir_name>", True
        if ".." in name or name == "." or "/" in name or "\\" in name:
            return f"Invalid characters or path components in name: {name}. Cannot delete relative paths.", True
            
        targetpath = os.path.join(self.current_dir, name)
        
        try:
            if not os.path.exists(targetpath):
                # Check lstat for broken symlinks
                if os.path.lexists(targetpath):
                     os.remove(targetpath) # Remove broken symlink
                     if name in self._file_cache: del self._file_cache[name]
                     return f"Removed broken symbolic link: {name}", True
                else:
                     return f"File or directory not found: {name}", True

            if os.path.isfile(targetpath) or os.path.islink(targetpath):
                os.remove(targetpath)
                if name in self._file_cache: del self._file_cache[name]
                return f"Removed file: {name}", True
            elif os.path.isdir(targetpath):
                # For safety, only remove empty directories with os.rmdir
                if not os.listdir(targetpath):
                    os.rmdir(targetpath)
                    if name in self._file_cache: del self._file_cache[name]
                    return f"Removed empty directory: {name}", True
                else:
                    return f"Directory not empty: {name}. Use specific tool for recursive removal.", True
            else:
                 return f"Cannot remove '{name}': Not a file or directory.", True # Should not happen often
                 
        except OSError as e:
             return f"Error removing '{name}': {e.strerror}", True
        except Exception as e:
            return f"Unexpected error removing '{name}': {str(e)}", True

    def _get_file_content(self, filename: str) -> Optional[str]:
        """Get content of a file if it exists in the current directory context."""
        if filename not in self._file_cache or self._file_cache[filename].get('is_dir') or self._file_cache[filename].get('error'):
            return None
        try:
            if self._file_cache[filename]['content'] is not None:
                return self._file_cache[filename]['content']
            full_path = os.path.join(self.current_dir, filename)
            if os.path.exists(full_path) and os.path.isfile(full_path):
                content = Path(full_path).read_text(encoding='utf-8')
                self._file_cache[filename]['content'] = content
                return content
        except Exception:
            self._file_cache[filename]['content'] = None 
            pass
        return None

    def _find_file_references(self, query: str) -> List[str]:
        """Find potential file references in the query, relative to current dir."""
        potential_files = re.findall(r'([\w./-]+\.\w+)', query)
        found_files = []
        for potential_file in potential_files:
            if potential_file in self._file_cache and not self._file_cache[potential_file].get('is_dir'):
                found_files.append(potential_file)
            else:
                 rel_path_check = os.path.join(self.current_dir, potential_file)
                 if os.path.isfile(rel_path_check):
                     if potential_file not in self._file_cache:
                         self._file_cache[potential_file] = {'is_dir': False, 'content': None}
                     if not self._file_cache[potential_file].get('is_dir'):
                         found_files.append(potential_file)
        return list(set(found_files))

    def _get_context(self, query: str) -> Tuple[str, str]:
        """Get relevant context based on the query."""
        model = "sonar-reasoning-pro"
        files = self._find_file_references(query)
        context_items = []
        if '.error' in self._file_cache:
             context_items.append(f"- Error accessing directory: {self._file_cache['.error']['content']}")
        elif not self._file_cache:
             context_items.append("- (empty)")
        else:
             # Show only non-hidden items
             context_items.extend([f"- {f}{'/' if self._file_cache[f].get('is_dir') else ''}" 
                                   for f in sorted(self._file_cache.keys()) if f != '.error' and not f.startswith('.')]) 
        context_parts = [
            f"Current Directory: {self.current_dir}",
            "Available files/dirs in current directory (excluding hidden):",
            *context_items
        ]
        files_to_include = files[:2]
        if files_to_include:
             context_parts.append("\nRelevant File Content:")
             for file in files_to_include:
                 content = self._get_file_content(file)
                 if content:
                     max_len = 1500
                     truncated_content = content[:max_len] + ('...' if len(content) > max_len else '')
                     context_parts.append(f"\n--- {file} ---\n{truncated_content}\n--- End {file} ---")
                 else:
                      context_parts.append(f"\n(Could not read content of {file})" )
        context = "\n".join(context_parts)
        return model, context

    async def process_query(self, query: str) -> Tuple[str, bool]:
        """Process query: Handle local commands or pass to AI.
           Returns (response_string, is_command_result)
        """
        query_lower = query.lower().strip()
        
        # 1. Check for exact commands
        cmd_parts = query.split(maxsplit=1) # Use original query for args preservation
        exact_cmd = cmd_parts[0].lower()
        if exact_cmd in self.commands:
            handler = self.commands[exact_cmd]
            # Commands needing argument: cd, create, touch, mkdir, rm, delete, remove
            if exact_cmd in ["cd", "create", "touch", "mkdir", "rm", "delete", "remove"]:
                arg = cmd_parts[1].strip() if len(cmd_parts) > 1 else ""
                return handler(arg)
            else: # ls, tree, pwd, help, exit, quit
                 return handler()

        # 2. Check for natural language commands
        for pattern, command_key in self.natural_commands.items():
            match = re.fullmatch(pattern, query, re.IGNORECASE | re.DOTALL) # Use original query
            if match:
                handler = self.commands.get(command_key)
                if handler:
                    # Commands needing argument from regex group
                    if command_key in ['cd', 'create', 'mkdir', 'rm']:
                        arg = match.group(1).strip() if match.groups() else ""
                        return handler(arg) 
                    else: # ls, tree, pwd
                         return handler()

        # 3. If not a command, process as AI query
        self.is_processing_api = True
        try:
            model, context = self._get_context(query)
            messages = [
                {"role": "system", "content": context},
                {"role": "user", "content": query}
            ]
            payload = {"model": model, "messages": messages}
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content'], False
            return "No response received from the model.", False
        except httpx.HTTPStatusError as e:
            return f"API error: {e.response.status_code} - {e.response.text}", True
        except httpx.TimeoutException:
            return "Request timed out. The Perplexity API might be slow or unreachable.", True
        except httpx.RequestError as e:
             return f"Network error: Could not connect to Perplexity API. {str(e)}", True
        except Exception as e:
            import traceback
            return f"Unexpected error during API call: {str(e)}\n{traceback.format_exc()}", True
        finally:
            self.is_processing_api = False
        
    async def close(self):
        """Close the HTTP client."""
        try:
            if hasattr(self, 'client') and self.client:
                await self.client.aclose() 
        except Exception:
            pass 