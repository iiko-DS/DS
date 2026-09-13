# Скриншоты поведения полей (Empty / Focus / Populated) + сетка для ревью
$edge = @(
  "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
  "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $edge) { Write-Output 'EDGE NOT FOUND'; exit 1 }
$base = 'file:///C:/Users/asukharev/GitHub/DS/iiko-ds-prototypes/figma-1276-metro-desktop.html'
$files = @('beh-rest.png', 'beh-focus.png', 'beh-filled.png')
$qs = @('?ui=0', '?ui=0&demo=focus', '?ui=0&demo=filled')
$captions = @('Empty (rest)', 'Focus (click) - Label up', 'Populated (value)')
for ($i = 0; $i -lt $files.Count; $i++) {
  $out = Join-Path $PSScriptRoot $files[$i]
  if (Test-Path $out) { Remove-Item $out -Force }
  & $edge --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --window-size=1184,640 --screenshot=$out ($base + $qs[$i]) 2>$null | Out-Null
}
Start-Sleep -Milliseconds 400
Add-Type -AssemblyName System.Drawing
$crop = [System.Drawing.Rectangle]::new(16, 156, 760, 388)
$capH = 28
$cellW = $crop.Width
$cellH = $crop.Height + $capH
$grid = [System.Drawing.Bitmap]::new($cellW * $files.Count, $cellH)
$g = [System.Drawing.Graphics]::FromImage($grid)
$g.Clear([System.Drawing.Color]::White)
$font = [System.Drawing.Font]::new('Segoe UI', 13, [System.Drawing.FontStyle]::Bold)
for ($i = 0; $i -lt $files.Count; $i++) {
  $img = [System.Drawing.Image]::FromFile((Join-Path $PSScriptRoot $files[$i]))
  $x = $i * $cellW
  $g.DrawString($captions[$i], $font, [System.Drawing.Brushes]::Black, $x + 8, 4)
  $g.DrawImage($img, [System.Drawing.Rectangle]::new($x, $capH, $cellW, $crop.Height), $crop, [System.Drawing.GraphicsUnit]::Pixel)
  $img.Dispose()
}
$g.Dispose()
$grid.Save((Join-Path $PSScriptRoot 'input-behavior.png'), [System.Drawing.Imaging.ImageFormat]::Png)
$grid.Dispose()
$font.Dispose()
Write-Output 'input-behavior.png done'
