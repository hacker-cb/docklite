# DockLite Bash Completion

Auto-completion for DockLite CLI commands.

## Features

✅ **Command completion** - Tab to complete commands  
✅ **Option completion** - Tab to complete --flags  
✅ **Service completion** - Tab to complete service names for logs  
✅ **File completion** - Tab to complete .tar.gz for restore  
✅ **Smart suggestions** - Context-aware completions  

## Installation

### Quick Install (Recommended)

```bash
./docklite install-completion
```

Then reload shell:
```bash
source ~/.bashrc
```

### Manual Install

**For current user only:**
```bash
echo 'source ~/docklite/scripts/completion/docklite-completion.bash' >> ~/.bashrc
source ~/.bashrc
```

**For all users (requires root):**
```bash
sudo ./docklite install-completion --global
```

## Uninstall

```bash
./docklite install-completion --uninstall
source ~/.bashrc
```

## Usage Examples

After installation and reload, try:

### Complete Commands
```bash
./docklite <TAB><TAB>
# Shows: start stop restart rebuild logs test test-backend test-frontend ...
```

### Partial Completion
```bash
./docklite st<TAB>
# Completes to: ./docklite start or ./docklite status (shows both)

./docklite reb<TAB>
# Completes to: ./docklite rebuild
```

### Complete Options
```bash
./docklite start --<TAB><TAB>
# Shows: --build --follow --help

./docklite stop --<TAB><TAB>
# Shows: --volumes --help

./docklite test-backend --<TAB><TAB>
# Shows: --verbose --coverage --help -v -k --cov --tb
```

### Complete Service Names
```bash
./docklite logs <TAB><TAB>
# Shows: backend frontend

./docklite logs back<TAB>
# Completes to: ./docklite logs backend
```

### Complete Backup Files
```bash
./docklite restore <TAB>
# Shows all .tar.gz files in current directory

./docklite restore backups/<TAB>
# Shows .tar.gz files in backups/ directory
```

### Complete Directories
```bash
./docklite backup -o <TAB>
# Shows directories for backup output
```

## How It Works

The completion script (`docklite-completion.bash`) defines a function `_docklite_completion` that:

1. Detects the current word being completed
2. Determines the command context
3. Suggests appropriate completions based on:
   - Current command
   - Previous arguments
   - File patterns
   - Available options

## Supported Commands

All 15+ commands support completion:

**Development:**
- start, stop, restart, rebuild, logs
- test, test-backend, test-frontend

**Deployment:**
- setup-user, setup-ssh, init-db

**Maintenance:**
- backup, restore, clean, status

**Setup:**
- install-completion

**Other:**
- version, help

## Completion Features by Command

| Command | Completes |
|---------|-----------|
| `start` | `--build`, `--follow`, `--help` |
| `stop` | `--volumes`, `--help` |
| `rebuild` | `--no-cache`, `--follow`, `--help` |
| `logs` | `backend`, `frontend` |
| `test` | `--verbose`, `--quiet`, `--help` |
| `test-backend` | `-v`, `-k`, `--cov`, `--tb`, `--help` |
| `test-frontend` | `--watch`, `--ui`, `--coverage`, `--help` |
| `setup-user` | `--user`, `--dir`, `--help` |
| `setup-ssh` | `--user`, `--help` |
| `init-db` | `--reset`, `--help` |
| `backup` | `--output`, `-o`, `--help` + directories |
| `restore` | `*.tar.gz` files + `--no-confirm`, `--help` |
| `clean` | `--all`, `--images`, `--volumes`, `--logs`, `--help` |
| `status` | `--verbose`, `--help` |

## Troubleshooting

### Completion not working after install

**Reload shell:**
```bash
source ~/.bashrc
```

**Or restart terminal**

### Still not working

**Check if installed:**
```bash
grep docklite ~/.bashrc
```

**Manual load:**
```bash
source ~/docklite/scripts/completion/docklite-completion.bash
```

**Check registration:**
```bash
complete -p | grep docklite
```

### Works in one terminal but not another

Each new terminal needs to source ~/.bashrc, which happens automatically on login. If it doesn't work:

```bash
# Add to top of ~/.bashrc if not already there
if [ -f ~/.bash_completion ]; then
    . ~/.bash_completion
fi
```

### Global install not working

Make sure `/etc/bash_completion.d/docklite` exists and is readable:
```bash
ls -l /etc/bash_completion.d/docklite
```

## Advanced Usage

### Add to PATH

For system-wide access, add to PATH:

```bash
# Add to ~/.bashrc
export PATH="~/docklite:$PATH"

# Then use without ./
docklite start
docklite test
docklite status
```

Completion will work with just `docklite` as well!

### Alias

Create short alias:

```bash
# Add to ~/.bashrc
alias dl='./docklite'

# Then use
dl start
dl test
dl status
```

Note: Completion works with aliases automatically!

## Technical Details

The completion script uses bash's `complete` builtin:

```bash
complete -F _docklite_completion ./docklite
```

This registers `_docklite_completion` function to handle completions for `./docklite` command.

The function uses:
- `COMP_WORDS` - Array of words in current command line
- `COMP_CWORD` - Index of current word
- `COMPREPLY` - Array of completion suggestions
- `compgen` - Generate completion matches

## Contributing

To add completion for a new command:

1. Edit `scripts/completion/docklite-completion.bash`
2. Add command to `commands` list
3. Add case in command-specific completions
4. Reload completion: `source ~/.bashrc`

Example:
```bash
# Add to commands list
local commands="... my-new-command ..."

# Add case
my-new-command)
    local opts="--option1 --option2 --help"
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    ;;
```

---

## License

MIT - Part of DockLite project

