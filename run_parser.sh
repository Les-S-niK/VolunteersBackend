#!/bin/bash
argv=("$@")
echo "First argument: ${argv[0]}" 
source ./.venv/bin/activate
python3 ./run_parser.py ${argv[0]}
