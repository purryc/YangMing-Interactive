#!/bin/zsh
set -eu
cd "$(dirname "$0")"
exec ./src/realtime_v1/open_realtime.command
