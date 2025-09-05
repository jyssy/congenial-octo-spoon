#!/bin/bash
OLD_STRING="$1"
NEW_STRING="$2"

if [ -z "$OLD_STRING" ] || [ -z "$NEW_STRING" ]; then
    echo "Usage: $0 'old-string' 'new-string'"
    exit 1
fi

for file in *.cfg; do
    if [ -f "$file" ] && grep -q "$OLD_STRING" "$file"; then
        cp "$file" "$file.bak"
        sed -i.tmp "s/$OLD_STRING/$NEW_STRING/g" "$file"
        [ -f "$file.tmp" ] && rm "$file.tmp"
        echo "Modified: $file (backup created)"
    fi
done

