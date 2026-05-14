# Start all Legal Multi-Agent System services on Windows PowerShell
# Registry must be first, then leaf agents, then orchestrators

# Keep response budget conservative to reduce OpenRouter 402 errors.
if (-not $env:OPENROUTER_MAX_TOKENS) {
	$env:OPENROUTER_MAX_TOKENS = "512"
}

Write-Host "Starting Registry service on port 10000..."
Start-Process python -ArgumentList "-m registry" -NoNewWindow
Start-Sleep -Seconds 2

Write-Host "Starting Tax Agent on port 10102..."
Start-Process python -ArgumentList "-m tax_agent" -NoNewWindow

Write-Host "Starting Compliance Agent on port 10103..."
Start-Process python -ArgumentList "-m compliance_agent" -NoNewWindow
Start-Sleep -Seconds 3

Write-Host "Starting Law Agent on port 10101..."
Start-Process python -ArgumentList "-m law_agent" -NoNewWindow
Start-Sleep -Seconds 3

Write-Host "Starting Customer Agent on port 10100..."
Start-Process python -ArgumentList "-m customer_agent" -NoNewWindow

Write-Host ""
Write-Host "All services started:"
Write-Host "  Registry:         http://localhost:10000"
Write-Host "  Customer Agent:   http://localhost:10100"
Write-Host "  Law Agent:        http://localhost:10101"
Write-Host "  Tax Agent:        http://localhost:10102"
Write-Host "  Compliance Agent: http://localhost:10103"
Write-Host "  OPENROUTER_MAX_TOKENS: $env:OPENROUTER_MAX_TOKENS"
Write-Host ""
Write-Host "Run test_client.py to send a query:"
Write-Host "  python test_client.py"
Write-Host ""
Write-Host "Press Ctrl+C to stop all services."

# Keep script running
Read-Host "Press Enter to exit"
