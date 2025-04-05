import chalk from 'chalk';
import boxen from 'boxen';

const PERPLEXITY_BLUE = '#00c5e0';

export function welcomeScreen() {
  const title = chalk.hex(PERPLEXITY_BLUE).bold('Welcome to CCOS (Claude Code Open Source)');
  const subtitle = chalk.hex(PERPLEXITY_BLUE).dim('An open-source alternative using Perplexity AI models');
  
  const asciiArt = `
  ╔════════════════════════════════════════════════════════════════════════════╗
  ║                                                                           ║
  ║   ██████╗ ██████╗ ███████╗    ██████╗ ██████╗ ███████╗                   ║
  ║  ██╔════╝██╔═══██╗██╔════╝    ██╔══██╗██╔══██╗██╔════╝                   ║
  ║  ██║     ██║   ██║███████╗    ██████╔╝██║  ██║█████╗                     ║
  ║  ██║     ██║   ██║╚════██║    ██╔══██╗██║  ██║██╔══╝                     ║
  ║  ╚██████╗╚██████╔╝███████║    ██║  ██║██████╔╝██║                        ║
  ║   ╚═════╝ ╚═════╝ ╚══════╝    ╚═╝  ╚═╝╚═════╝ ╚═╝                        ║
  ║                                                                           ║
  ╚════════════════════════════════════════════════════════════════════════════╝
  `;

  const boxedContent = boxen(
    `${asciiArt}\n${title}\n${subtitle}`,
    {
      padding: 1,
      margin: 1,
      borderStyle: 'round',
      borderColor: PERPLEXITY_BLUE
    }
  );

  console.log(boxedContent);
  console.log(chalk.hex(PERPLEXITY_BLUE).dim('\nType your command or "help" for available commands.\n'));
} 