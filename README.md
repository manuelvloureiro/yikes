<div style="height:125px;overflow:hidden;position:relative;">
    <img src="yikes.webp" alt="Yikes!" style="position:absolute;top:-25px;left:50%;transform:translateX(-50%);width:200px;height:200px;"/>
</div>
<div style="text-align: center;">
    <p><b>Stay in the terminal and know it all!</b></p>
</div>

# Yikes!

Yikes! is a command-line program designed to facilitate interaction with large language models (LLMs).
It allows users to either query the model directly from the CLI or start a REPL chat session.
Yikes! aims to be a lightweight solution with no dependencies beyond Python's standard library, enabling productivity by providing quick answers without leaving the terminal.

## Features

- **Direct Query**: Send a single query to the LLM and receive an immediate response without ever leaving the CLI.
- **REPL Chat Session**: Start an interactive chat session with a chosen language model.

Currently set up with Hugging Face's free endpoints for Llama 3 and Phi-3 models.
Llama 3 is the default model for direct querying.

## Installation

To install Yikes! on your system, use the following command:

```sh
python yikes.py install
```

This will copy the script to `/usr/local/bin` and make it executable from anywhere in your terminal.

### Setting Up the API Key

If you use Yikes! as is, you need to get an API key from [Hugging Face](https://huggingface.co/).

Ensure your API key is either set as an environment variable or available in the same folder as Yikes!.
To set the API key as an environment variable:

```sh
export HUGGINGFACE_API_KEY=your_api_key_here
```

To add the API key to your `~/.bashrc` file, open the file in a text editor and add the following line:

```sh
export HUGGINGFACE_API_KEY=your_api_key_here
```

After editing `~/.bashrc`, run the following command to apply the changes:

```sh
source ~/.bashrc
```

## Usage

### Direct Query

To send a single query to the language model, use the following syntax:

```sh
yikes "How do I list the full path of files, in folder /foo/bar and all its subfolders, that were modified in the past 3 days?"
```

#### Example of a Direct Query

```sh
$ yikes "How do I list the full path of files, in folder /foo/bar and all its subfolders, that were modified in the past 3 days?"
You can use the `find` command with the `-path` and `-mtime` options to achieve this:

`find /foo/bar -path "*/" -mtime -3 -exec ls -ld {} \;`

This command will list the full path of files in the `/foo/bar` directory and its subdirectories that were modified within the past 3 days. The `-path "*/"` option ensures that only directories are considered, and the `-mtime -3` option specifies that the files should have been modified within the past 3 days. The `-exec` option runs the `ls -ld` command on each matching file, displaying the full path and other file information.
```

### REPL Chat Session

To start a REPL chat session, simply run the following command:

```sh
yikes
```

You will be prompted to select a model and then you can start chatting.

#### Example of a REPL Conversation

```sh
$ yikes
Available models:
[0] llama3
[1] phi3
Select a model (enter the number or short name): 0
Chatting with meta-llama/Meta-Llama-3-8B-Instruct:
> Who are you?
AI: I'm LLaMA, an AI assistant developed by Meta AI that can understand and respond to human input in a conversational manner.
> How do you like being integrated into Yikes!?
AI: I'm excited to be a part of Yikes! and help users like you with information and tasks. It's a great platform to assist and learn from users.
```

### Available Commands in the Chat

- **Exit the Application**: Use `quit`, `:q`, or `exit` to exit the REPL chat session.
- **Restart the Conversation**: Use `clear` or `restart` to clear the conversation history and start anew.
- **Swap the Model**: Use `swap` or `switch` to change to a different language model during the REPL chat session.

## Requirements

- Python 3.x

## License

This project is licensed under the MIT License.

## Contributing

Feel free to contribute by submitting a pull request or opening an issue.

---

Happy chatting!
