import chalk from 'chalk';
import { analyzeProject } from './analyze.js';
import { navigateFiles } from './navigate.js';
import { searchFiles } from './search.js';
import { showHelp } from './help.js';

const PERPLEXITY_BLUE = '#00c5e0';

export async function handleCommand(input) {
  if (!input) return;

  const command = input.toLowerCase().trim();
  
  // Handle special commands
  if (command === 'help') {
    showHelp();
    return;
  }

  if (command === 'exit' || command === 'quit') {
    console.log(chalk.hex(PERPLEXITY_BLUE)('\nGoodbye!'));
    process.exit(0);
  }

  // Show thinking animation
  process.stdout.write(chalk.hex(PERPLEXITY_BLUE)('\rThinking... '));

  try {
    // Route to appropriate command handler
    if (command.startsWith('analyze') || command.startsWith('explain')) {
      await analyzeProject(command);
    } else if (command.startsWith('navigate') || command.startsWith('cd') || command.startsWith('ls')) {
      await navigateFiles(command);
    } else if (command.startsWith('search') || command.startsWith('find')) {
      await searchFiles(command);
    } else {
      console.log(chalk.yellow('\nUnknown command. Type "help" for available commands.'));
    }
  } catch (error) {
    console.error(chalk.red('\nError:'), error.message);
  }
} 