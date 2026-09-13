# Crop the textarea area from render.png at 3x (check frame corners/radius)
Add-Type -AssemblyName System.Drawing
$src = [System.Drawing.Image]::FromFile((Join-Path $PSScriptRoot 'render.png'))
$regions = [ordered]@{
  render_area_rest = @(40, 280, 720, 140)
  ref_area_rest    = @(40, 280, 720, 140)
}
foreach ($k in $regions.Keys) {
  $file = if ($k -like 'ref*') { 'frame1276.png' } else { 'render.png' }
  $img = [System.Drawing.Image]::FromFile((Join-Path $PSScriptRoot $file))
  $r = $regions[$k]
  $rect = [System.Drawing.Rectangle]::new([int]$r[0], [int]$r[1], [int]$r[2], [int]$r[3])
  $bmp = [System.Drawing.Bitmap]::new($rect.Width * 3, $rect.Height * 3)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
  $g.DrawImage($img, [System.Drawing.Rectangle]::new(0, 0, $rect.Width * 3, $rect.Height * 3), $rect, [System.Drawing.GraphicsUnit]::Pixel)
  $g.Dispose()
  $bmp.Save((Join-Path $PSScriptRoot ($k + '.png')), [System.Drawing.Imaging.ImageFormat]::Png)
  $bmp.Dispose()
  $img.Dispose()
}
$src.Dispose()
Write-Output 'area crops done'
