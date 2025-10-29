#!/bin/bash
# Bash completion for DockLite CLI
# Source this file or copy to /etc/bash_completion.d/

_docklite_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Main commands
    local commands="start stop restart rebuild logs test test-backend test-frontend setup-user setup-ssh init-db backup restore clean status add-user list-users reset-password install-completion version help"
    
    # If we're completing the first argument (command)
    if [ $COMP_CWORD -eq 1 ]; then
        COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
        return 0
    fi
    
    # Get the command (first argument)
    local command="${COMP_WORDS[1]}"
    
    # Command-specific completions
    case "${command}" in
        start)
            local start_opts="--build --follow --help -h -b -f"
            COMPREPLY=( $(compgen -W "${start_opts}" -- ${cur}) )
            ;;
        stop)
            local stop_opts="--volumes --help -h -v"
            COMPREPLY=( $(compgen -W "${stop_opts}" -- ${cur}) )
            ;;
        rebuild)
            local rebuild_opts="--no-cache --follow --help -h -f"
            COMPREPLY=( $(compgen -W "${rebuild_opts}" -- ${cur}) )
            ;;
        logs)
            # Complete with service names
            if [ $COMP_CWORD -eq 2 ]; then
                local services="backend frontend"
                COMPREPLY=( $(compgen -W "${services}" -- ${cur}) )
            fi
            ;;
        test)
            local test_opts="--verbose --quiet --help -h -v -q"
            COMPREPLY=( $(compgen -W "${test_opts}" -- ${cur}) )
            ;;
        test-backend)
            local backend_opts="--verbose --coverage --help -h -v -k --cov --tb"
            COMPREPLY=( $(compgen -W "${backend_opts}" -- ${cur}) )
            ;;
        test-frontend)
            local frontend_opts="--watch --ui --coverage --help -h -w -u"
            COMPREPLY=( $(compgen -W "${frontend_opts}" -- ${cur}) )
            ;;
        setup-user)
            local setup_opts="--user --dir --help -h -u -d"
            COMPREPLY=( $(compgen -W "${setup_opts}" -- ${cur}) )
            ;;
        setup-ssh)
            local ssh_opts="--user --help -h -u"
            COMPREPLY=( $(compgen -W "${ssh_opts}" -- ${cur}) )
            ;;
        init-db)
            local init_opts="--reset --help -h"
            COMPREPLY=( $(compgen -W "${init_opts}" -- ${cur}) )
            ;;
        backup)
            local backup_opts="--output --help -h -o"
            # If completing -o or --output, suggest directories
            if [[ "${prev}" == "-o" ]] || [[ "${prev}" == "--output" ]]; then
                COMPREPLY=( $(compgen -d -- ${cur}) )
            else
                COMPREPLY=( $(compgen -W "${backup_opts}" -- ${cur}) )
            fi
            ;;
        restore)
            # Complete with backup files
            if [ $COMP_CWORD -eq 2 ]; then
                COMPREPLY=( $(compgen -f -X '!*.tar.gz' -- ${cur}) )
            else
                local restore_opts="--no-confirm --help -h"
                COMPREPLY=( $(compgen -W "${restore_opts}" -- ${cur}) )
            fi
            ;;
        clean)
            local clean_opts="--all --images --volumes --logs --help -h"
            COMPREPLY=( $(compgen -W "${clean_opts}" -- ${cur}) )
            ;;
        status)
            local status_opts="--verbose --help -h -v"
            COMPREPLY=( $(compgen -W "${status_opts}" -- ${cur}) )
            ;;
        add-user)
            # First arg is username, then suggest options
            if [ $COMP_CWORD -eq 2 ]; then
                # Username (no suggestions for security)
                COMPREPLY=()
            else
                local add_opts="--password --admin --email --system --help -h -p -a -e -s"
                COMPREPLY=( $(compgen -W "${add_opts}" -- ${cur}) )
            fi
            ;;
        list-users)
            local list_opts="--verbose --help -h -v"
            COMPREPLY=( $(compgen -W "${list_opts}" -- ${cur}) )
            ;;
        reset-password)
            # First arg is username, suggest --password
            if [ $COMP_CWORD -eq 2 ]; then
                # Could suggest common usernames, but leave empty for security
                COMPREPLY=()
            else
                local reset_opts="--password --help -h -p"
                COMPREPLY=( $(compgen -W "${reset_opts}" -- ${cur}) )
            fi
            ;;
        install-completion)
            local install_opts="--global --local --uninstall --help -h"
            COMPREPLY=( $(compgen -W "${install_opts}" -- ${cur}) )
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

