**`try-flockmtl`**

- [FlockMTL/Ollama DuckDB Integration](#flockmtlollama-duckdb-integration)
  - [Status](#status)
  - [Why?](#why)
  - [What?](#what)
  - [How?](#how)
    - [1. Prerequisites](#1-prerequisites)
    - [2. Setup](#2-setup)
      - [a. Configure Models and Endpoint](#a-configure-models-and-endpoint)
      - [b. Start Ollama](#b-start-ollama)
      - [c. Register Models & Test](#c-register-models--test)
      - [d. Manage with Justfile](#d-manage-with-justfile)
    - [3. Troubleshooting](#3-troubleshooting)
    - [4. Project Structure](#4-project-structure)
    - [5. Extending](#5-extending)
  - [Example Usage](#example-usage)
  - [Compatibility Notes](#compatibility-notes)
  - [License](#license)
  - [Credits](#credits)

# FlockMTL/Ollama DuckDB Integration

Experiments with the FlockMTL DuckDB extension.

## Status

![Status: Experimental](https://img.shields.io/badge/status-experimental-orange.svg)

*There appears to be some issue with the FlockMTL extension and DuckDB 1.2.2, which is causing the `GetAlterInfo not implemented for this type` error. This might be due to a mismatch between the extension and the DuckDB version, however the documenation suggests that the extension is compatible with DuckDB 1.2.2.*

## Why?

Modern data workflows increasingly require local, private, and flexible access to large language models (LLMs) for analytics, summarisation, and automation. This project enables you to:

- **Integrate local LLMs (via Ollama) directly with DuckDB** using [FlockMTL](https://dsg-polymtl.github.io/flockmtl/), so you can run LLM-powered SQL queries on your data.
- **Automate and manage LLM model registration and configuration** using Python and TOML, making your setup reproducible and easy to maintain.
- **Debug and audit all SQL interactions** for transparency and troubleshooting.

This is a common pattern that is emerging in the data ecosystem, where LLMs are used to augment SQL queries and data processing. For example:

- Note that the commercial [MotherDuck](https://motherduck.com) offering offers built-in support for various LLMs via the [`prompt()` method](https://motherduck.com/blog/sql-llm-prompt-function-gpt-models/).
- Similarly, Google Sheets now has built-in support for the Gemini suite of LLMs via the `=AI()` function.

## What?

This repository provides:

- **(Configuration-driven, object-oriented Python script (`flockmtl_manager.py`)** to:
  - Check Ollama endpoint health
  - Register Ollama models with FlockMTL in DuckDB
  - Run test completions via SQL
  - Log all SQL commands (with Loguru) and export them to `flockmtl.sql`
- **Sample TOML config (`flockmtl.toml`)** for easy model and endpoint management
- **Justfile** for convenient CLI automation of common tasks (running scripts, managing Ollama models, etc.)

## How?

### 1. Prerequisites

- **Python 3.13+**
- **DuckDB** installed (CLI or Python package)
- **Ollama** installed and running (see [Ollama docs](https://ollama.com))
- **FlockMTL** DuckDB extension installed
- Python dependencies:

```sh
uv add duckdb httpx loguru
```

- (Optional) [Just](https://just.systems/) for task automation

### 2. Setup

#### a. Configure Models and Endpoint

Edit `flockmtl.toml` to specify your Ollama endpoint and models. For example:

```toml
[ollama]
api_url = "http://127.0.0.1:11434"

[[models]]
name = "mixtral_local"
ollama_name = "mixtral:latest"
context_window = 128000
max_output_tokens = 2048

[[models]]
name = "llama2_local"
ollama_name = "llama2:latest"
context_window = 4096
max_output_tokens = 1024
```

#### b. Start Ollama

```sh
ollama serve
```

or use the Justfile recipe:

```sh
just ollama-serve
```

#### c. Register Models & Test

Run the Python manager script:

```sh
python flockmtl_manager.py
```

This will:

- Check if the Ollama endpoint is available
- Register the Ollama API secret with FlockMTL
- Register each model from the TOML file
- Run a test LLM completion via SQL
- Log all SQL statements to `flockmtl.log` and `flockmtl.sql`

#### d. Manage with Justfile

Use the included `Justfile` for tasks like:

```sh
just ollama-list         # List local Ollama models
just ollama-pull llama2  # Pull a model
just run                 # Run the manager script
```

### 3. Troubleshooting

- **Extension errors:**
  Ensure the FlockMTL extension matches your DuckDB version and platform. Use `INSTALL flockmtl; LOAD flockmtl;` in DuckDB, or see [DuckDB extension docs](https://duckdb.org/docs/extensions/overview.html).
- **Hanging on test completion:**
  - Make sure Ollama is running and the specified model is available.
  - Test the model directly: `ollama run llama2 --prompt "Hello"`
- **SQL errors or debugging:**
  - Check `flockmtl.sql` for all executed SQL statements.
  - Review `flockmtl.log` for detailed logs.

### 4. Project Structure

```
.
├── flockmtl_manager.py   # Main Python script (OO, config-driven)
├── flockmtl.toml         # Model & endpoint configuration
├── flockmtl.sql          # All executed SQL commands (for debugging)
├── flockmtl.log          # Loguru logs (SQL and actions)
├── Justfile              # Task automation commands
```

### 5. Extending

- Add more models to `flockmtl.toml` as needed.
- Customise or extend the Python script for advanced workflows (e.g., model removal, batch prompts).
- Use the SQL log for bug reports or reproducibility.

______________________________________________________________________

## Example Usage

```sh
# List available tasks
just

# Start Ollama server
just ollama-serve

# Pull a new model
just ollama-pull llama2

# Run the integration script
just run
```

______________________________________________________________________

## Compatibility Notes

- **DuckDB and FlockMTL extension versions must be compatible.**
  If you see errors about `GetAlterInfo not implemented for this type`, update your FlockMTL extension to match your DuckDB version.
- **Ollama models must be pulled before use.**
- **Python 3.13+ is required for built-in TOML parsing.**

______________________________________________________________________

## License

Apache-2.0 License

This project is licensed under the Apache-2.0 License. See the [LICENSE](LICENSE) file for details.

______________________________________________________________________

## Credits

- [FlockMTL](https://dsg-polymtl.github.io/flockmtl/)
- [Ollama](https://ollama.com/)
- [DuckDB](https://duckdb.org/)
- [Loguru](https://github.com/Delgan/loguru)
- [httpx](https://www.python-httpx.org/)

______________________________________________________________________

**Questions or issues?**

Open an issue or contact [github@databooth.com.au](mailto:github@databooth.com.au).
