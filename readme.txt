docker run -p 8000:8000 rasa/duckling is a command for parsing dates service running on docker
docker run --rm -p 11434:11434 ollama/ollama is a command for local olama in a docker 
docker exec <container_id> ollama pull qwen3:1.7b
pull after that 

to start the postgres locally 
cd "/home/admin/Desktop/text analyser" && docker compose up postgres -d 2>&1

to run smtp
cd "/home/admin/Desktop/text analyser" && docker compose up -d mailhog