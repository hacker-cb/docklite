#!/bin/bash
# Bash completion for DockLite CLI
# Source this file or copy to /etc/bash_completion.d/

_docklite_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Root commands (6) and groups (4)
    local root_commands="start stop restart logs status test"
    local groups="dev deploy user maint"
    local all_level1="${root_commands} ${groups} version help"
    
    # Group subcommands
    local dev_commands="setup-dev rebuild test-backend test-frontend test-e2e"
    local deploy_commands="setup-user setup-ssh init-db"
    local user_commands="add list reset-password"
    local maint_commands="backup restore clean"
    
    # If we're completing the first argument (root command or group)
    if [ $COMP_CWORD -eq 1 ]; then
        COMPREPLY=( $(compgen -W "${all_level1}" -- ${cur}) )
        return 0
    fi
    
    # Get the first argument (command or group)
    local first_arg="${COMP_WORDS[1]}"
    
    # Check if first arg is a group
    case "${first_arg}" in
        dev)
            # If completing second argument, suggest dev subcommands
            if [ $COMP_CWORD -eq 2 ]; then
                COMPREPLY=( $(compgen -W "${dev_commands}" -- ${cur}) )
                return 0
            fi
            # Otherwise handle subcommand options
            local subcommand="${COMP_WORDS[2]}"
            case "${subcommand}" in
                setup-dev)
                    local opts="--help -h"
                    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                    ;;
                rebuild)
                    local opts="--no-cache --follow --help -h -f"
                    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                    ;;
                test-backend)
                    local opts="--verbose --coverage --help -h -v -k --cov --tb"
                    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                    ;;
                test-frontend)
                    local opts="--watch --ui --coverage --help -h -w -u"
                    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                    ;;
                test-e2e)
                    local opts="--ui --debug --report --headed --help -h -u -d -r"
                    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                    ;;
            esac
            ;;
        deploy)
            # If completing second argument, suggest deploy subcommands
            if [ $COMP_CWORD -eq 2 ]; then
                COMPREPLY=( $(compgen -W "${deploy_commands}" -- ${cur}) )
                return 0
            fi
            # Otherwise handle subcommand options
            local subcommand="${COMP_WORDS[2]}"
            case "${subcommand}" in
                setup-user)
                    local opts="--user --dir --help -h -u -d"
                    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                    ;;
                setup-ssh)
                    local opts="--user --help -h -u"
                    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                    ;;
                init-db)
                    local opts="--reset --help -h"
                    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                    ;;
            esac
            ;;
        user)
            # If completing second argument, suggest user subcommands
            if [ $COMP_CWORD -eq 2 ]; then
                COMPREPLY=( $(compgen -W "${user_commands}" -- ${cur}) )
                return 0
            fi
            # Otherwise handle subcommand options
            local subcommand="${COMP_WORDS[2]}"
            case "${subcommand}" in
                add)
                    # First arg is username, then suggest options
                    if [ $COMP_CWORD -eq 3 ]; then
                        # Username (no suggestions for security)
                        COMPREPLY=()
                    else
                        local opts="--password --admin --email --system-user --help -h -p -a -e -s"
                        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                    fi
                    ;;
                list)
                    local opts="--verbose --help -h -v"
                    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                    ;;
                reset-password)
                    # First arg is username, then suggest options
                    if [ $COMP_CWORD -eq 3 ]; then
                        # Username (no suggestions for security)
                        COMPREPLY=()
                    else
                        local opts="--password --help -h -p"
                        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                    fi
                    ;;
            esac
            ;;
        maint)
            # If completing second argument, suggest maint subcommands
            if [ $COMP_CWORD -eq 2 ]; then
                COMPREPLY=( $(compgen -W "${maint_commands}" -- ${cur}) )
                return 0
            fi
            # Otherwise handle subcommand options
            local subcommand="${COMP_WORDS[2]}"
            case "${subcommand}" in
                backup)
                    local opts="--output --help -h -o"
                    # If completing -o or --output, suggest directories
                    if [[ "${prev}" == "-o" ]] || [[ "${prev}" == "--output" ]]; then
                        COMPREPLY=( $(compgen -d -- ${cur}) )
                    else
                        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                    fi
                    ;;
                restore)
                    # Complete with backup files
                    if [ $COMP_CWORD -eq 3 ]; then
                        COMPREPLY=( $(compgen -f -X '!*.tar.gz' -- ${cur}) )
                    else
                        local opts="--no-confirm --help -h"
                        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                    fi
                    ;;
                clean)
                    local opts="--all --images --volumes --logs --help -h"
                    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                    ;;
            esac
            ;;
        # Root commands
        start)
            local opts="--build --follow --help -h -b -f"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            ;;
        stop)
            local opts="--volumes --help -h -v"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            ;;
        restart)
            local opts="--build --help -h -b"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            ;;
        logs)
            # Complete with service names
            if [ $COMP_CWORD -eq 2 ]; then
                local services="backend frontend traefik"
                COMPREPLY=( $(compgen -W "${services}" -- ${cur}) )
            fi
            ;;
        status)
            local opts="--verbose --help -h -v"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            ;;
        test)
            local opts="--verbose --quiet --help -h -v -q"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            ;;
        *)
            # Default: suggest --help
            if [[ ${cur} == -* ]]; then
                COMPREPLY=( $(compgen -W "--help -h" -- ${cur}) )
            fi
            ;;
    esac
}

# Register completion for both ./docklite and docklite (if in PATH)
complete -F _docklite_completion ./docklite
complete -F _docklite_completion docklite

# Also register for scripts/docklite.sh
complete -F _docklite_completion ./scripts/docklite.sh
