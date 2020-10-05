#!/bin/echo must be run in bash with . 

conda activate ai4eu

# run gui server
uvicorn sudoku-gui-server:app --reload --host 0.0.0.0 &

# open sudoku gui in Chrome
IP=$(ifconfig eth0 |grep "inet "|cut -d" " -f10)
/mnt/c/Program\ Files\ \(x86\)/Google/Chrome/Application/chrome.exe http://$IP:8000/ &
