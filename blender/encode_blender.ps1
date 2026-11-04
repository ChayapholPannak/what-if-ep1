# encode_blender.py — png sequences -> mp4 (h264, yuv420p, silent)
$env:Path = "C:\Users\USER\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin;" + $env:Path
$base = "C:\Users\USER\OneDrive\Documents\Default Project\whatif-ep1\blender\out"
$dest = "C:\Users\USER\OneDrive\Documents\Default Project\whatif-ep1\assets\blender"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
foreach ($s in @("b1","b3","b4","b5","b6")) {
  $src = "$base\$s"
  $out = "$dest\$s.mp4"
  if (-not (Test-Path $src)) { Write-Host "SKIP $s (no frames)"; continue }
  Write-Host "ENCODE $s -> $out"
  ffmpeg -y -framerate 30 -i "$src\frame_%04d.png" -c:v libx264 -pix_fmt yuv420p `
    -crf 17 -preset slow -vf "scale=1080:1920" $out
}
Get-ChildItem $dest | Select-Object Name, Length | Format-Table
