param(
  [string]$File,
  [double]$Row = 0.5,   # доля высоты (0..1): строка для RLE
  [double]$Col = 0.5    # доля ширины (0..1): столбец для RLE
)
Add-Type -AssemblyName System.Drawing
$img = [System.Drawing.Bitmap]::FromFile((Resolve-Path $File))
$y = [int][Math]::Round(($img.Height - 1) * $Row)
$x = [int][Math]::Round(($img.Width - 1) * $Col)
Write-Output ("# {0}  size {1}x{2}  row y={3}  col x={4}" -f (Split-Path $File -Leaf), $img.Width, $img.Height, $y, $x)

function Rle([System.Drawing.Color[]]$px) {
  $runs = @(); $prev = $null; $n = 0
  foreach ($p in $px) {
    $key = "{0},{1},{2}" -f $p.R, $p.G, $p.B
    if ($key -eq $prev) { $n++ } else { if ($null -ne $prev) { $runs += ("${n}x($prev)") }; $prev = $key; $n = 1 }
  }
  if ($null -ne $prev) { $runs += ("${n}x($prev)") }
  return ($runs -join ' | ')
}

$rowPx = @(); for ($i = 0; $i -lt $img.Width; $i++) { $rowPx += $img.GetPixel($i, $y) }
Write-Output ("ROW : " + (Rle $rowPx))
$colPx = @(); for ($i = 0; $i -lt $img.Height; $i++) { $colPx += $img.GetPixel($x, $i) }
Write-Output ("COL : " + (Rle $colPx))
$img.Dispose()
