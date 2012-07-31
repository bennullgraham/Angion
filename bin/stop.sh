ps ax | grep Angion.py | grep -v grep | awk '{print $1}' | while read PROC; do kill "$PROC"; done
