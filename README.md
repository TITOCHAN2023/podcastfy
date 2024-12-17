# HOW TO USE AS A QUICK SERVER 

1. create .env like 
   ```
    OPENAI_API_KEY=......

    TTS_URL="....."
    TTS_AUDIO_URL="...."
    BASE_URL="....."


    PGSQLDB_CONFIG=" {'dbname': 'xxx','user': 'postgres','password': 'xxxx','host': 'xxxx','port': '5432'}"
    URL='xxxx'
   ```
2.
``` uvicorn main:app --host '0.0.0.0' --port 8172 --reload --env-file .env                                                                            ```