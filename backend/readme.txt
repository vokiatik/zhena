cd "/home/admin/Desktop/text analyser/backend" && source ../venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000

lsof -ti :8000 | xargs kill -9 2>/dev/null; ss -tlnp | grep 8000 to turn off