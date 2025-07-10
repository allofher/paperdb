# paperdb

1. VirtualEnv, install dependencies, yadayada
2. Get Ollama and the models in the docker script or change the models in the docker script to ones you prefer
3. Get Docker and run the server setup script after the compose file
4. Setup a log, backup, and new note directory for the ingest script
5. Dump photos of your paper notes into the new note directory
6. Put a gemini flash API key into the API key spot
7. Run the ingest script to transcribe, vectorize, and store the notes in the db
8. Healthcheck to test DB size and responsiveness
9. Chat script to use the RAG weaviate client
