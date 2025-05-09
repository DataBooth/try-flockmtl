INSTALL flockmtl;

LOAD flockmtl;

CREATE SECRET (
                    TYPE OLLAMA,
                    API_URL 'http://127.0.0.1:11434'
                );

CREATE MODEL(
                        'mixtral_local',
                        'mixtral:latest',
                        'ollama',
                        {"context_window": 128000, "max_output_tokens": 2048}
                    );

CREATE MODEL(
                        'llama2_local',
                        'llama2:latest',
                        'ollama',
                        {"context_window": 4096, "max_output_tokens": 1024}
                    );

SELECT llm_complete(
                    {'model_name': 'mixtral_local'},
                    {'prompt': 'Summarise the difference between DuckDB and SQLite.'}
                );

