$path = 'c:\Users\asukharev\AppData\Roaming\Code\User\workspaceStorage\1f6c6986f6b2eefb4495b0db6ac35a96\GitHub.copilot-chat\transcripts\46b65ecd-643c-434a-843b-c524de5ddc82.jsonl'
if (-not (Test-Path $path)) { Write-Output "no transcript"; exit 1 }
$text = [System.IO.File]::ReadAllText($path)
Write-Output ("transcript chars: " + $text.Length)
$pattern = 'data:image/(png|jpeg|jpg);base64,([A-Za-z0-9+/=]{1000,})'
$ms = [regex]::Matches($text, $pattern)
Write-Output ("image matches: " + $ms.Count)
$n = 0
foreach ($m in $ms) {
  $n++
  if ($n -lt ($ms.Count - 2)) { continue }
  $ext = $m.Groups[1].Value
  if ($ext -eq 'jpeg') { $ext = 'jpg' }
  $bytes = [Convert]::FromBase64String($m.Groups[2].Value)
  $out = "c:\Users\asukharev\GitHub\DS\_audit\_user_img_" + $n + "." + $ext
  [System.IO.File]::WriteAllBytes($out, $bytes)
  Write-Output ("saved #" + $n + " " + $out + " size " + $bytes.Length)
}
