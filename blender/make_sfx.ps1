# make_sfx.ps1 — synthesize all SFX for What-If EP.1 with ffmpeg (free, deterministic)
$ErrorActionPreference = "Stop"
$sfx = "C:\Users\USER\OneDrive\Documents\Default Project\whatif-ep1\assets\audio\sfx"
New-Item -ItemType Directory -Force -Path $sfx | Out-Null

# drone — dark bed 56s (quiet, runs under the whole clip)
ffmpeg -y -v error -f lavfi -i "sine=frequency=48:duration=56" -f lavfi -i "sine=frequency=48.6:duration=56" -f lavfi -i "anoisesrc=color=brown:amplitude=0.05:duration=56:seed=7" -filter_complex "[0:a]volume=0.4[a];[1:a]volume=0.4[b];[2:a]lowpass=f=180,volume=0.6[c];[a][b][c]amix=inputs=3:normalize=0,volume=0.55" -c:a libmp3lame -b:a 128k "$sfx\drone.mp3"

# boom — short impact
ffmpeg -y -v error -f lavfi -i "sine=frequency=52:duration=1.6" -f lavfi -i "anoisesrc=color=brown:amplitude=0.4:duration=0.15:seed=3" -filter_complex "[0:a]volume=exp(-3.5*t):eval=frame[a];[1:a]volume=0.6[b];[a][b]amix=inputs=2:duration=first:normalize=0,volume=1.1" -c:a libmp3lame "$sfx\boom.mp3"

# riser — 2.2s tension climb
ffmpeg -y -v error -f lavfi -i "anoisesrc=color=white:amplitude=0.5:duration=2.2:seed=11" -f lavfi -i "aevalsrc=0.22*sin(2*PI*(100*t+48*t*t*t)):d=2.2:s=44100" -filter_complex "[0:a]lowpass=f=3500,volume=pow(t/2.2,2)*0.7:eval=frame[a];[1:a]volume=pow(t/2.2,2):eval=frame[b];[a][b]amix=inputs=2:normalize=0,afade=t=out:st=2.05:d=0.15,volume=0.9" -c:a libmp3lame "$sfx\riser.mp3"

# sting — dissonant hit
ffmpeg -y -v error -f lavfi -i "sine=frequency=620:duration=1.5" -f lavfi -i "sine=frequency=661:duration=1.5" -f lavfi -i "sine=frequency=1244:duration=1.5" -filter_complex "[0:a]volume=0.3[a];[1:a]volume=0.3[b];[2:a]volume=0.15[c];[a][b][c]amix=inputs=3:normalize=0,volume=exp(-3.5*t):eval=frame,volume=0.9" -c:a libmp3lame "$sfx\sting.mp3"

# knock — 3 door knocks (thump every 0.45s)
ffmpeg -y -v error -f lavfi -i "aevalsrc=0.9*sin(2*PI*80*t)*exp(-28*mod(t\,0.45)):d=1.4:s=44100" -c:a libmp3lame "$sfx\knock.mp3"

# heartbeat — lub-dub 8.6s
ffmpeg -y -v error -f lavfi -i "aevalsrc=0.7*sin(2*PI*55*t)*(exp(-22*mod(t\,0.9))+0.7*exp(-22*mod(t-0.18\,0.9))):d=8.6:s=44100" -c:a libmp3lame -b:a 128k "$sfx\heartbeat.mp3"

# whoosh — 0.9s scene transition
ffmpeg -y -v error -f lavfi -i "anoisesrc=color=pink:amplitude=0.5:duration=0.9:seed=9" -af "bandpass=f=900:w=700:width_type=h,volume=sin(PI*t/0.9):eval=frame,volume=0.8" -c:a libmp3lame "$sfx\whoosh.mp3"

foreach ($f in @("drone","boom","riser","sting","knock","heartbeat","whoosh")) {
  $d = ffprobe -v error -show_entries format=duration -of csv=p=0 "$sfx\$f.mp3"
  Write-Output "$f : $([math]::Round([double]$d,2)) s"
}
