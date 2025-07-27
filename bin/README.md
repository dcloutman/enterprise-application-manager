# Enterprise Application Tracker Command Line Tool (eatcmd)

A comprehensive command-line interface for managing the Enterprise Application Tracker (EAT) application lifecycle.

## Installation

The `eatcmd` tool is located in the `bin/` directory and requires Python 3.12+ with the Click library:

```bash
pip install click
```

## Permissions

The script has `700` permissions (owner read/write/execute only) for security.

## Commands

### Application Management

- **`eatcmd start`** - Start the Enterprise Application Tracker
  - `--detached, -d` - Run in detached mode (default)  
  - `--foreground, -f` - Run in foreground mode

- **`eatcmd stop`** - Stop the Enterprise Application Tracker

- **`eatcmd restart`** - Restart the Enterprise Application Tracker

- **`eatcmd status`** - Show the status of application containers

### Development & Testing

- **`eatcmd test`** - Run the comprehensive test suite
  - `--backend-only` - Run only backend tests
  - `--frontend-only` - Run only frontend tests  
  - `--coverage` - Generate coverage reports

- **`eatcmd docs`** - Build project documentation using Sphinx
  - `--clean` - Clean build directory first
  - `--format [html|pdf|epub]` - Documentation format (default: html)

### Maintenance

- **`eatcmd clean-docker`** - Stop and remove all application containers, networks, and volumes
  - `--force, -f` - Force removal without confirmation

- **`eatcmd setup`** - Run the initial project setup

### Utilities

- **`eatcmd logs`** - View application logs
  - `--follow, -f` - Follow log output
  - `--service, -s SERVICE` - Show logs for specific service

- **`eatcmd shell`** - Open an interactive shell in the application container
  - `--service, -s SERVICE` - Enter specific service container

- **`eatcmd info`** - Display system and application information

## Examples

```bash
# Start the application
./bin/eatcmd start

# Check status
./bin/eatcmd status

# Run tests with coverage
./bin/eatcmd test --coverage

# Build documentation
./bin/eatcmd docs --clean

# Clean up Docker resources
./bin/eatcmd clean-docker --force

# View logs
./bin/eatcmd logs --follow

# Get system information
./bin/eatcmd info
```

## Security Features

- **Restricted Permissions**: Script has 700 permissions (owner only)
- **Docker Cleanup**: Comprehensive cleanup of containers, networks, and volumes
- **Safe Defaults**: Detached mode by default, confirmation prompts for destructive operations
- **Error Handling**: Proper error handling and user feedback

## Dependencies

- Python 3.12+
- Click library
- Docker & Docker Compose
- Sphinx (for documentation building)

The tool automatically checks for required dependencies and provides helpful error messages if they're missing.
