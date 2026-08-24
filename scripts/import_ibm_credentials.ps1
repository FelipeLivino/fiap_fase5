param(
    [Parameter(Mandatory = $true)]
    [string]$CredentialsPath,
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot ".."))
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $CredentialsPath -PathType Leaf)) {
    throw "Arquivo de credenciais não encontrado."
}

$credentialValues = @{}
Get-Content -LiteralPath $CredentialsPath | ForEach-Object {
    if ($_ -match '^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*["'']?(.*?)["'']?\s*$') {
        $credentialValues[$Matches[1]] = $Matches[2]
    }
}

$serviceUrl = [string]$credentialValues["ASSISTANT_URL"]
$apiKey = [string]$credentialValues["ASSISTANT_IAM_APIKEY"]
if (-not $apiKey) {
    $apiKey = [string]$credentialValues["ASSISTANT_APIKEY"]
}
if (-not $serviceUrl -or -not $apiKey) {
    throw "ASSISTANT_URL e uma API key são obrigatórios."
}

$serviceUri = [System.Uri]$serviceUrl
if ($serviceUri.Scheme -ne "https" -or $serviceUri.Host -notmatch '(^|\.)assistant\.watson\.cloud\.ibm\.com$') {
    throw "A URL não pertence ao endpoint público do watsonx Assistant."
}

$secretDirectory = Join-Path $ProjectRoot ".secrets"
$secretPath = Join-Path $secretDirectory "watson_api_key"
$environmentPath = Join-Path $ProjectRoot ".env"
if (-not (Test-Path -LiteralPath $environmentPath -PathType Leaf)) {
    throw "Arquivo .env não encontrado no projeto."
}

[System.IO.Directory]::CreateDirectory($secretDirectory) | Out-Null
[System.IO.File]::WriteAllText(
    $secretPath,
    $apiKey,
    [System.Text.UTF8Encoding]::new($false)
)

$environmentLines = [System.Collections.Generic.List[string]]::new()
Get-Content -LiteralPath $environmentPath | ForEach-Object {
    $environmentLines.Add($_)
}

function Set-EnvironmentValue {
    param([string]$Name, [string]$Value)
    $replacement = "$Name=$Value"
    for ($index = 0; $index -lt $environmentLines.Count; $index++) {
        if ($environmentLines[$index] -match "^$([regex]::Escape($Name))=") {
            $environmentLines[$index] = $replacement
            return
        }
    }
    $environmentLines.Add($replacement)
}

Set-EnvironmentValue -Name "WATSON_API_PROFILE" -Value "v2"
Set-EnvironmentValue -Name "WATSON_SERVICE_URL" -Value $serviceUrl
Set-EnvironmentValue -Name "WATSON_API_VERSION" -Value "2024-08-25"
[System.IO.File]::WriteAllLines(
    $environmentPath,
    $environmentLines,
    [System.Text.UTF8Encoding]::new($false)
)

Write-Output "ibm_credentials=imported"
Write-Output "assistant_host=$($serviceUri.Host)"
Write-Output "assistant_mode=unchanged_until_environment_is_selected"
