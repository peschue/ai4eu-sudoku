#!/bin/echo must be run in bash with . 

conda activate ai4eu

if /bin/false; then
    # run gui server
    pushd gui
    uvicorn server:app --reload --host 0.0.0.0 --port 8000 &
    popd

    # open sudoku gui in Chrome
    IP=$(ifconfig eth0 |grep "inet "|cut -d" " -f10)
    /mnt/c/Program\ Files\ \(x86\)/Google/Chrome/Application/chrome.exe http://$IP:8000/ &
fi

if /bin/true; then
    # run design evaluator server
    pushd evaluator
    python3 server.py &
    popd
fi


if /bin/false; then
    # run asp solver server
    pushd aspsolver
    python3 server.py &
    popd
fi

if /bin/false; then
    # run orchestrator
    pushd orchestrator
    python3 orchestrator.py
    popd
fi

