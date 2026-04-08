#!/bin/bash
argv=("$@")
source ./.venv/bin/activate
python3 -m core.utils.run_parser ${argv[0]}
