#!/bin/echo must be run in bash with . 

# wait for keyboard input
echo "once the servers are running, press RETURN to close all" >/dev/stderr

sleep 1

conda activate ai4eu

if /bin/true; then
    echo "starting GUI server" >/dev/stderr

    pushd gui
    # run without --reload so that we can kill it cleanly
    uvicorn server:app --host 0.0.0.0 --port 8000 --log-level debug &
    GUI_PID=$!
    popd

    # open sudoku gui in Chrome
    IP=$(ifconfig eth0 |grep "inet "|cut -d" " -f10)
    /mnt/c/Program\ Files\ \(x86\)/Google/Chrome/Application/chrome.exe http://$IP:8000/ &

    sleep 1
fi

if /bin/true; then
    echo "starting design evaluator server" >/dev/stderr

    pushd evaluator
    python3 server.py &
    EVALUATOR_PID=$!
    popd

    sleep 1
fi


if /bin/true; then
    echo "starting ASP solver server" >/dev/stderr

    pushd aspsolver
    python3 server.py &
    ASPSOLVER_PID=$!
    popd

    sleep 1
fi

if /bin/true; then
    echo "starting orchestrator" >/dev/stderr

    pushd orchestrator
    python3 orchestrator.py &
    ORCHESTRATOR_PID=$!
    popd
fi

(
echo
echo
echo "From now on you can kill all servers by pressing RETURN"
echo
echo
) >/dev/stderr

# wait for RETURN
read

# kill all servers
kill $EVALUATOR_PID $ASPSOLVER_PID $ORCHESTRATOR_PID $GUI_PID
killall -9 uvicorn

