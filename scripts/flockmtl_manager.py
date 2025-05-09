import duckdb
import tomllib
import httpx
from loguru import logger
import json


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

    def _install_and_load_flockmtl(self):
        self.execute_sql("INSTALL flockmtl;")
        self.execute_sql("LOAD flockmtl;")

    def execute_sql(self, sql, *args, **kwargs):
        logger.info(f"Executing SQL: {sql.strip()}")
        return self.con.execute(sql, *args, **kwargs)

    def check_ollama_available(self, timeout=3):
        """Check if the Ollama endpoint is available using httpx."""
        try:
            response = httpx.get(self.config.api_url, timeout=timeout)
            if 200 <= response.status_code < 300:
                logger.info(f"Ollama endpoint {self.config.api_url} is available.")
                return True
            else:
                logger.error(f"Ollama endpoint returned status {response.status_code}.")
                return False
        except httpx.RequestError as e:
            logger.error(
                f"Could not reach Ollama endpoint at {self.config.api_url}: {e}"
            )
            return False

    def create_secret(self):
        try:
            self.execute_sql(f"""
                CREATE SECRET (
                    TYPE OLLAMA,
                    API_URL '{self.config.api_url}'
                );
            """)
            logger.info("Secret created.")
        except Exception as e:
            logger.warning(f"Secret may already exist or another error occurred: {e}")

    def create_models(self):
        for model in self.config.models:
            try:
                model_args = {
                    "context_window": model["context_window"],
                    "max_output_tokens": model["max_output_tokens"],
                }
                model_args_json = json.dumps(model_args)
                self.execute_sql(f"""
                    CREATE MODEL(
                        '{model["name"]}',
                        '{model["ollama_name"]}',
                        'ollama',
                        {model_args_json}
                    );
                """)
                logger.info(f"Model '{model['name']}' registered.")
            except Exception as e:
                logger.warning(f"Error registering model '{model['name']}': {e}")

    def test_completion(self, prompt, model_name=None):
        if not model_name:
            model_name = self.config.models[0]["name"]
        try:
            sql = f"""
                SELECT llm_complete(
                    {{'model_name': '{model_name}'}},
                    {{'prompt': '{prompt}'}}
                );
            """
            result = self.execute_sql(sql).fetchall()
            logger.info(f"Response from '{model_name}': {result}")
        except Exception as e:
            logger.error(f"Error running test completion with '{model_name}': {e}")

    def close(self):
        self.con.close()


if __name__ == "__main__":
    logger.add("flockmtl.log", rotation="1 MB", retention="10 days")
    config = FlockMTLConfig("flockmtl.toml")
    manager = FlockMTLManager("flockmtl_demo.duckdb", config)
    if manager.check_ollama_available():
        manager.create_secret()
        manager.create_models()
        manager.test_completion(
            "Summarise the difference between DuckDB and SQLite.",
            model_name="mixtral_local",
        )
    else:
        logger.error(
            "Ollama endpoint is not available. Please start Ollama and try again."
        )
    manager.close()
