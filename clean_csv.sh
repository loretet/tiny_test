#!/bin/sh

if [ $# -lt 1 ]; then
    echo "Usage: $0 FILE_OR_DIR [COL1 COL2 ...]"
    exit 1
fi

TARGET="$1"
shift

if [ $# -eq 0 ]; then
    COLS="3 4 5"
else
    COLS="$*"
fi

process_file() {
    file="$1"

    awk -F',' -v cols="$COLS" '
    BEGIN {
        ncols = split(cols, c, " ")
    }

    {
        lines[NR] = $0

        nonzero = 0
        for (i = 1; i <= ncols; i++) {
            if ($(c[i]) + 0 != 0) {
                nonzero = 1
                break
            }
        }

        if (nonzero) {
            if (first == 0) first = NR
            last = NR
        }
    }

    END {
        if (first == 0) exit
        for (i = first; i <= last; i++) print lines[i]
    }
    ' "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"

    echo "Processed: $file"
}

if [ -d "$TARGET" ]; then
    for file in "$TARGET"/*.csv; do
        [ -f "$file" ] || continue
        process_file "$file"
    done
elif [ -f "$TARGET" ]; then
    process_file "$TARGET"
else
    echo "Error: not a file or directory"
    exit 1
fi
