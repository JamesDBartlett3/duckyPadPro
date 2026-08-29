$repoRoot = $PSScriptRoot

& uv run --project $repoRoot --locked python (Join-Path $repoRoot "execute.py") @args
exit $LASTEXITCODE