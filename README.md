# Document Manager RAG and QA application

To setup in local environment

1. clone the respository
2. execute `chmod +x entrypoint.sh` to give permission to setup ollama container with models preloaded
3. Run `docker-compose up` to start the application

Services involved:

1. Backend - Fast API  and PostgreSQL with Pgvector extension

   - Implemented JWT authentication
   - Document Ingestion (Added only pdf support ) - Need to implement for other file formats too like `.doc, .docx, .txt etc..`
   - RAG - used `llama-index` to implement RAG with the help of Ollama and Pgvector
2. Ollama -  to use LLM model and Embedding model , `llama3.1:8b` and `nomic-embed-text-v:1.5` respectively
3. Frontend - React (Work in-progress for future implementation)
