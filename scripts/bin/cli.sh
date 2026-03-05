#!/bin/bash
# bin/cli.sh Wrapper
CMD=$1
shift

case "$CMD" in
    install)
        bash "$(dirname "$0")/../install.sh" "$@"
        ;;
    evaluate)
        bash "$(dirname "$0")/../evaluate.sh" "$@"
        ;;
    list)
        ls -la "$(dirname "$0")/../../skills"
        ;;
    *)
        echo "Usage: npx cytognosis-skills <install|evaluate|list>"
        exit 1
        ;;
esac
