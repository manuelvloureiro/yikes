<div style="height:125px;overflow:hidden;position:relative;">
    <img src="yikes.webp" alt="Yikes!" style="position:absolute;top:-25px;left:50%;transform:translateX(-50%);width:200px;height:200px;"/>
</div>
<div style="text-align: center;">
    <p><b>Stay in the terminal and know it all!</b></p>
</div>

# Yikes!

Yikes! is a command-line program designed to facilitate interaction with large language models (LLMs). It allows users to either query the model directly from the CLI or start an interactive REPL chat session. Yikes! aims to be a lightweight solution with minimal dependencies, enabling productivity by providing quick answers without leaving the terminal.

---

## Features

- **Direct Query**: Send a single query to the LLM and receive an immediate response without leaving the CLI.
- **REPL Chat Session**: Start an interactive chat session with a chosen language model.
- **Multiple Model Support**: Choose from a variety of models, including:
  - **Deepseek V3**: Optimized for general-purpose tasks.
  - **Llama 3**: Meta's advanced conversational model.
  - **Phi-3**: Microsoft's lightweight yet powerful instruction-following model.
- **Customizable Prompts**: Easily structure conversations with system, user, and assistant prompts.
- **Save Conversations**: Save entire chat histories to a file for later review.

---

## Installation

To install Yikes! on your system, use the following command:

```sh
python yikes.py install
```

This will copy the script to `/usr/local/bin` and make it executable from anywhere in your terminal.

---

## Setup

### API Keys

To use Yikes!, you’ll need API keys for the respective model providers. Set them as environment variables or store them in a file:

```sh
export HUGGINGFACE_API_KEY=your_api_key_here
export OPENROUTER_API_KEY=your_api_key_here
```

Alternatively, add the keys to your `~/.bashrc` or `~/.zshrc` file for persistence.

---

## Usage

### Direct Query

Send a single query to the language model:

```sh
yikes "How do I list files modified in the last 3 days?"
```

### Direct Query with Context

Pipe stdin as context to the language model:

```sh
cat context.txt | yikes "A query related to the context."
```

### Interactive Chat

Start an interactive chat session:

```sh
yikes
```

### Commands in Chat

- **Switch Models**: Use `swap` or `model` to change models during a session.
- **Restart Conversation**: Use `clear` or `restart` to reset the chat history.
- **Save Conversation**: Use `save <filepath>` to save the chat history to a file.
- **Exit**: Use `quit`, `:q`, or `exit` to end the session.

---

## Supported Models

| Short Name   | Model Name                                      | API Provider     |
|--------------|------------------------------------------------|------------------|
| `deepseekv3` | deepseek/deepseek-chat:free                    | OpenRouter       |
| `llama3`     | meta-llama/Meta-Llama-3-8B-Instruct            | Hugging Face     |
| `phi3`       | microsoft/Phi-3-mini-4k-instruct               | Hugging Face     |

---

## Examples

### Direct Query Example

```sh
$ yikes "How do I list files modified in the last 3 days?"
You can use the `find` command with the `-mtime` option:
`find /path/to/folder -type f -mtime -3`
```

### Interactive Chat Example

```sh
$ yikes
Available models:
[0] deepseekv3
[1] llama3
[2] phi3
Select a model (enter the number or short name): 1
Chatting with meta-llama/Meta-Llama-3-8B-Instruct:
> Who are you?
AI: I'm LLaMA, an AI assistant developed by Meta AI.
> How do I list files modified in the last 3 days?
AI: Use the `find` command: `find /path -type f -mtime -3`.
```

---

## Requirements

- Python 3.x

---

## License

This project is licensed under the MIT License.

---

## Contributing

Feel free to contribute by submitting a pull request or opening an issue. Happy chatting!

