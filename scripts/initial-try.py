import json
import tomllib

import duckdb
import httpx


class FlockMTLConfig:
    def __init__(self, config_path):
        with open(config_path, "rb") as f:
            self.config = tomllib.load(f)
        self.api_url = self.config["ollama"]["api_url"]
        self.models = self.config["models"]


class FlockMTLManager:
    def __init__(self, db_path, config: FlockMTLConfig):
        self.db_path = db_path
        self.config = config
        self.con = duckdb.connect(self.db_path)
        self._install_and_load_flockmtl()

    def check_ollama_available(self, timeout=3):
        """Check if the Ollama endpoint is available using httpx."""
        try:
            response = httpx.get(self.config.api_url, timeout=timeout)
            if 200 <= response.status_code < 300:
                print(f"Ollama endpoint {self.config.api_url} is available.")
                return True
            else:
                print(f"Ollama endpoint returned status {response.status_code}.")
                return False
        except httpx.RequestError as e:
            print(f"Could not reach Ollama endpoint at {self.config.api_url}: {e}")
            return False

    def _install_and_load_flockmtl(self):
        self.con.execute("INSTALL flockmtl;")
        self.con.execute("LOAD flockmtl;")

    def create_secret(self):
        try:
            self.con.execute(f"""
                CREATE SECRET (
                    TYPE OLLAMA,
                    API_URL '{self.config.api_url}'
                );
            """)
            print("Secret created.")
        except Exception as e:
            print("Secret may already exist or another error occurred:", e)

    def create_models(self):
        for model in self.config.models:
            try:
                model_args = {
                    "context_window": model["context_window"],
                    "max_output_tokens": model["max_output_tokens"],
                }
                # Convert model_args to JSON string with double quotes

                model_args_json = json.dumps(model_args)
                self.con.execute(f"""
                    CREATE MODEL(
                        '{model["name"]}',
                        '{model["ollama_name"]}',
                        'ollama',
                        {model_args_json}
                    );
                """)
                print(f"Model '{model['name']}' registered.")
            except Exception as e:
                print(f"Error registering model '{model['name']}':", e)

    def test_completion(self, prompt, model_name=None):
        if not model_name:
            model_name = self.config.models[0]["name"]
        try:
            result = self.con.execute(f"""
                SELECT llm_complete(
                    {{'model_name': '{model_name}'}},
                    {{'prompt': '{prompt}'}}
                );
            """).fetchall()
            print(f"Response from '{model_name}':", result)
        except Exception as e:
            print(f"Error running test completion with '{model_name}':", e)

    def close(self):
        self.con.close()


if __name__ == "__main__":
    config = FlockMTLConfig("flockmtl.toml")
    manager = FlockMTLManager("data/flockmtl_demo.duckdb", config)
    if manager.check_ollama_available():
        manager.create_secret()
        manager.create_models()
        manager.test_completion("Summarise the difference between DuckDB and SQLite.")
    else:
        print("Ollama endpoint is not available. Please start Ollama and try again.")
    manager.close()
