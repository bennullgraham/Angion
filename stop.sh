ps ax | grep fractal.py | grep -v grep | awk '{print $1}' | while read PROC; do kill "$PROC"; done
