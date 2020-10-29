#!/bin/echo must be run in bash with . 

conda activate ai4eusudoku

# wait for keyboard input
echo "once the servers are running, press RETURN to close all" >/dev/stderr

sleep 1

pushd gui
# run without --reload so that we can kill it cleanly
uvicorn server:app --host 0.0.0.0 --port 8000 --log-level debug &
export GUI_PID=$!
echo "GUI_PID = $GUI_PID" >/dev/stderr
popd

# open sudoku gui in Chrome
IP=$(ifconfig eth0 |grep "inet "|cut -d" " -f10)
/mnt/c/Program\ Files\ \(x86\)/Google/Chrome/Application/chrome.exe http://$IP:8000/ &

(
echo
echo
echo "From now on you can kill all servers by pressing RETURN"
echo
echo
) >/dev/stderr

# wait for RETURN
read

# kill all servers except uvicorn
kill $GUI_PID
sleep 1
killall -9 uvicorn
ps auxwww |egrep "uvicorn|python"

conda deactivate
