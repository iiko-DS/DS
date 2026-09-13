# Скриншоты состояний Input (демо-панель, ?state=) + сборка сетки для ревью
$edge = @(
  "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
  "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $edge) { Write-Output 'EDGE NOT FOUND'; exit 1 }
$base = 'file:///C:/Users/asukharev/GitHub/DS/iiko-ds-prototypes/figma-1276-metro-desktop.html'
$states = @('default', 'hover', 'focus', 'error', 'disabled')
foreach ($s in $states) {
  $out = Join-Path $PSScriptRoot "state-$s.png"
  if (Test-Path $out) { Remove-Item $out -Force }
  & $edge --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --window-size=1184,640 --screenshot=$out "${base}?ui=0&state=$s" 2>$null | Out-Null
}
Start-Sleep -Milliseconds 400
Add-Type -AssemblyName System.Drawing
$crop = [System.Drawing.Rectangle]::new(16, 156, 760, 388)
$capH = 28
$cols = 3
$cellW = $crop.Width
$cellH = $crop.Height + $capH
$grid = [System.Drawing.Bitmap]::new($cellW * $cols, $cellH * 2)
$g = [System.Drawing.Graphics]::FromImage($grid)
$g.Clear([System.Drawing.Color]::White)
$font = [System.Drawing.Font]::new('Segoe UI', 13, [System.Drawing.FontStyle]::Bold)
for ($i = 0; $i -lt $states.Count; $i++) {
  $path = Join-Path $PSScriptRoot ("state-" + $states[$i] + ".png")
  $img = [System.Drawing.Image]::FromFile($path)
  $col = $i % $cols
  $row = [Math]::Floor($i / $cols)
  $x = $col * $cellW
  $y = $row * $cellH
  $g.DrawString($states[$i], $font, [System.Drawing.Brushes]::Black, $x + 8, $y + 4)
  $g.DrawImage($img, [System.Drawing.Rectangle]::new($x, $y + $capH, $cellW, $crop.Height), $crop, [System.Drawing.GraphicsUnit]::Pixel)
  $img.Dispose()
}
$g.Dispose()
$grid.Save((Join-Path $PSScriptRoot 'input-states.png'), [System.Drawing.Imaging.ImageFormat]::Png)
$grid.Dispose()
$font.Dispose()
Write-Output 'input-states.png done'
