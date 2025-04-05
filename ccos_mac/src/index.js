#!/usr/bin/env node

import { Command } from 'commander';
import chalk from 'chalk';
import { createInterface } from 'readline';
import { stdin as input, stdout as output } from 'process';
import { welcomeScreen } from './ui/welcome.js';
import { handleCommand } from './commands/handler.js';

const program = new Command();

// Set up the CLI program
program
  .name('ccos')
  .description('An open-source alternative to Claude Code using Perplexity AI models')
  .version('0.1.0');

// Create readline interface for interactive input
const rl = createInterface({
  input,
  output,
  prompt: chalk.cyan('> ')
});

// Display welcome screen
welcomeScreen();

// Start interactive mode
rl.prompt();

// Handle user input
rl.on('line', async (line) => {
  try {
    await handleCommand(line.trim());
  } catch (error) {
    console.error(chalk.red('Error:'), error.message);
  }
  rl.prompt();
});

// Handle program termination
rl.on('close', () => {
  console.log(chalk.cyan('\nGoodbye!'));
  process.exit(0);
}); 