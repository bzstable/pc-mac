import chalk from 'chalk';
import boxen from 'boxen';

const PERPLEXITY_BLUE = '#00c5e0';

export function showHelp() {
  const commands = [
    {
      name: 'analyze',
      description: 'Analyze the current project structure and dependencies'
    },
    {
      name: 'navigate',
      description: 'Navigate through project files and directories'
    },
    {
      name: 'search',
      description: 'Search for files and content within the project'
    },
    {
      name: 'help',
      description: 'Show this help message'
    },
    {
      name: 'exit',
      description: 'Exit the program'
    }
  ];

  const helpText = commands
    .map(cmd => `${chalk.hex(PERPLEXITY_BLUE).bold(cmd.name.padEnd(15))} ${cmd.description}`)
    .join('\n');

  const boxedHelp = boxen(
    `${chalk.hex(PERPLEXITY_BLUE).bold('Available Commands:')}\n\n${helpText}`,
    {
      padding: 1,
      margin: 1,
      borderStyle: 'round',
      borderColor: PERPLEXITY_BLUE
    }
  );

  console.log(boxedHelp);
  console.log(chalk.hex(PERPLEXITY_BLUE).dim('\nExample: analyze project structure'));
} 