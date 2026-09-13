# Headless screenshot of the prototype page (Edge) for pixel comparison
$edge = @(
  "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
  "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $edge) { Write-Output 'EDGE NOT FOUND'; exit 1 }
$out = Join-Path $PSScriptRoot 'render.png'
if (Test-Path $out) { Remove-Item $out -Force }
$url = 'file:///C:/Users/asukharev/GitHub/DS/iiko-ds-prototypes/figma-1276-metro-desktop.html?ui=0'
& $edge --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --window-size=1184,635 --screenshot=$out $url 2>$null | Out-Null
Start-Sleep -Milliseconds 500
if (Test-Path $out) {
  Add-Type -AssemblyName System.Drawing
  $img = [System.Drawing.Image]::FromFile($out)
  Write-Output ("render.png " + $img.Width + "x" + $img.Height)
  $img.Dispose()
} else { Write-Output 'screenshot failed' }
