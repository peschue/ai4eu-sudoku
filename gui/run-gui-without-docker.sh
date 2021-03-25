
# run without --reload so that we can kill it cleanly
uvicorn server:app --host 0.0.0.0 --port 8000 --log-level debug

