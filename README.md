# CLLM - Command Line Language Model

A CLI to interact with large language models (LLMs) directly from the terminal.

## Features

- Communication with the OpenAI API (It will support the other providers soon)
- Simple and intuitive command line interface
- Rendering responses in Markdown
- Persistent configuration
- Support for different models and parameters

## Installation

### Via pip (when available)

```bash
pip install cllm
```

### Installation from source

```bash
git clone https://github.com/ialvarenga/cllm.git
cd cllm
pip install -e .
```

## Configuration

Before using the CLI, configure your OpenAI API key:

```bash
cllm set-api-key
```

Or set the `OPENAI_API_KEY` environment variable:

```bash
export OPENAI_API_KEY="sk-your-key-here"
```

## Usage

### Basic command

```bash
cllm ask "How does photosynthesis work?"
```

### Specify model

```bash
cllm ask --model gpt-4 "Explain Einstein's theory of relativity"
```

### Adjust parameters

```bash
cllm ask --temperature 0.9 --max-tokens 2000 "Write a short story about space travel"
```

### Disable Markdown formatting

```bash
cllm ask --no-markdown "What is the Pythagorean theorem?"
```

## Manage configurations

View current configurations:

```bash
cllm config_cli
```

Set default model:

```bash
cllm set-default-model gpt-4
```

## Examples

### Simple questions

```bash
cllm ask "What are the benefits of meditation?"
```

### Code analysis

```bash
cllm ask "Explain the following Python code: def fib(n): return n if n <= 1 else fib(n-1) + fib(n-2"
```

### Translation

```bash
cllm ask "Translate to English: Estou aprendendo a programar em Python"
```

## Development

### Set up development environment

```bash
# Clone the repository
git clone https://github.com/ialvarenga/cllm.git
cd cllm

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt
# Or alternatively:
pip install -e ".[dev]"
```

### Run tests

```bash
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contribution

Contributions are welcome! Please feel free to submit a Pull Request.