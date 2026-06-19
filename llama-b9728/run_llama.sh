#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
export LD_LIBRARY_PATH="$DIR:$LD_LIBRARY_PATH"
exec "$DIR/llama-cli" "$@"
