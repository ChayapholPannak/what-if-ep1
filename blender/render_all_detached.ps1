# render_all_detached.ps1 — runs all Blender scene renders + encode in one go.
# Designed to run as a DETACHED Windows process (survives agent restarts).
$ErrorActionPreference = "Continue"
$log = "C:\Users\USER\OneDrive\Documents\Default Project\whatif-ep1\blender\render_all.log"
function Log($m) { Add-Content -Path $log -Value ((Get-Date -Format "HH:mm:ss") + "  " + $m) }
Log "=== render_all start ==="

$bl = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
$base = "C:\Users\USER\OneDrive\Documents\Default Project\whatif-ep1\blender"
$out = "$base\out"

foreach ($s in @("b5","b6","b1","b3","b4")) {
  Log "scene $s : start"
  $args = @("-b", "-P", "`"$base\render_scenes.py`"", "--", "--scene", $s, "--out", "`"$out`"")
  $p = Start-Process -FilePath $bl -ArgumentList $args -Wait -PassThru -NoNewWindow -RedirectStandardOutput "$out\$s.blender.log" -RedirectStandardError "$out\$s.blender.err.log"
  Log "scene $s : finished exit=$($p.ExitCode)"
}

# encode
$env:Path = "C:\Users\USER\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin;" + $env:Path
$dest = "C:\Users\USER\OneDrive\Documents\Default Project\whatif-ep1\assets\blender"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
foreach ($s in @("b5","b6","b1","b3","b4")) {
  $src = "$out\$s"
  $need = @{b1=135; b3=150; b4=300; b5=300; b6=315}[$s]
  $have = (Get-ChildItem $src -Filter frame_*.png -ErrorAction SilentlyContinue | Measure-Object).Count
  if ($have -lt $need) { Log "encode SKIP $s (have $have / need $need)"; continue }
  Log "encode $s : start"
  Start-Process -FilePath "ffmpeg" -Wait -NoNewWindow -RedirectStandardOutput "$out\$s.ff.out.log" -RedirectStandardError "$out\$s.ff.err.log" -ArgumentList @("-y", "-framerate", "30", "-i", "`"$src\frame_%04d.png`"", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-preset", "medium", "-vf", "scale=1080:1920", "`"$dest\$s.mp4`"")
  Log "encode $s : done exit=$LASTEXITCODE"
}
Log "=== render_all complete ==="
