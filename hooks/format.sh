#!/bin/bash
# Post-tool hook: auto-format files after Write/Edit
FILE=$(jq -r '.tool_input.file_path // empty')
echo "$(date): Hook triggered, FILE='$FILE'" >> ~/.claude/hooks/debug.log
[[ -z "$FILE" || ! -f "$FILE" ]] && exit 0

case "$FILE" in
  *.go)
    echo "Hook: running gofmt + golangci-lint on $FILE"
    gofmt -w "$FILE" && golangci-lint run --fix "$FILE"
    ;;
  *.ex|*.exs)
    echo "Hook: running mix format on $FILE"
    mix format "$FILE"
    ;;
  *.ts|*.tsx)
    echo "Hook: running eslint --fix on $FILE"
    npx eslint --fix "$FILE"
    ;;
  *.py)
    echo "Hook: running ruff format + check on $FILE"
    ruff format "$FILE" && ruff check --fix "$FILE"
    ;;
  *.rb)
    echo "Hook: running rubocop on $FILE"
    rubocop -a "$FILE"
    ;;
esac
exit 0
