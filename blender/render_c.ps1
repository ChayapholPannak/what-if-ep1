# render_c.ps1 — renders c3 + c4, encodes to mp4, and cuts b8 from b7.
# Run DETACHED (survives agent session).
$ErrorActionPreference = "Continue"
$log = "C:\Users\USER\OneDrive\Documents\Default Project\whatif-ep1\blender\render_c.log"
function Log($m) { Add-Content -Path $log -Value ((Get-Date -Format "HH:mm:ss") + "  " + $m) }
Log "=== render_c start ==="

$bl = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
$base = "C:\Users\USER\OneDrive\Documents\Default Project\whatif-ep1\blender"
$out = "$base\out"

foreach ($s in @("c3","c4")) {
  Log "scene $s : start"
  $args = @("-b", "-P", "`"$base\render_scenes.py`"", "--", "--scene", $s, "--out", "`"$out`"")
  $p = Start-Process -FilePath $bl -ArgumentList $args -Wait -PassThru -NoNewWindow -RedirectStandardOutput "$out\$s.blender.log" -RedirectStandardError "$out\$s.blender.err.log"
  Log "scene $s : finished exit=$($p.ExitCode)"
}

# encode
$env:Path = "C:\Users\USER\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin;" + $env:Path
$dest = "C:\Users\USER\OneDrive\Documents\Default Project\whatif-ep1\assets\blender"
foreach ($s in @("c3","c4")) {
  $src = "$out\$s"
  $need = @{c3=150; c4=165}[$s]
  $have = (Get-ChildItem $src -Filter frame_*.png -ErrorAction SilentlyContinue | Measure-Object).Count
  if ($have -lt $need) { Log "encode SKIP $s (have $have / need $need)"; continue }
  Log "encode $s : start"
  Start-Process -FilePath "ffmpeg" -Wait -NoNewWindow -RedirectStandardOutput "$out\$s.ff.out.log" -RedirectStandardError "$out\$s.ff.err.log" -ArgumentList @("-y", "-framerate", "30", "-i", "`"$src\frame_%04d.png`"", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-preset", "medium", "-vf", "scale=1080:1920", "`"$dest\$s.mp4`"")
  Log "encode $s : done exit=$LASTEXITCODE"
}

# b8 = b7 cut from 4s, 9s long
Log "cut b8 : start"
Start-Process -FilePath "ffmpeg" -Wait -NoNewWindow -RedirectStandardOutput "$out\b8.ff.out.log" -RedirectStandardError "$out\b8.ff.err.log" -ArgumentList @("-y", "-ss", "4", "-i", "`"$dest\b7.mp4`"", "-t", "9", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium", "-an", "`"$dest\b8.mp4`"")
Log "cut b8 : done exit=$LASTEXITCODE"
Log "=== render_c complete ==="
