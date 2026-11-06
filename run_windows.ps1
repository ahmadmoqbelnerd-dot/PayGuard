Set-Location $PSScriptRoot
Write-Host 'PayGuard runs locally. All payments use PayPal Sandbox.'
Write-Host 'First install Python and Ollama, then run: ollama pull qwen2.5:7b'
$client = Read-Host 'Sandbox Client ID (Enter to review evidence without payments)'
if ($client) {
    $env:PAYPAL_CLIENT_ID = $client
    $secret = Read-Host 'Sandbox Client Secret' -AsSecureString
    $env:PAYPAL_CLIENT_SECRET = [System.Net.NetworkCredential]::new('', $secret).Password
}
$env:OLLAMA_MODEL = 'qwen2.5:7b'
try { py server.py } finally { Remove-Item Env:PAYPAL_CLIENT_SECRET -ErrorAction SilentlyContinue }
