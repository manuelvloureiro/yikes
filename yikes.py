#!/usr/bin/env python
import os
import sys
import json
import requests
import argparse
import shutil
from typing import Dict, List, Tuple

INITIAL_PROMPT = "Provide concise replies."

MODELS = {

    "deepseekv3": {
        "name": "deepseek/deepseek-chat:free",
        "api_key": "OPENROUTER_API_KEY",
        "api_endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "api_type": "openrouter",
        "prompt_format": {
            "user": ("<｜begin▁of▁sentence｜>User: ", ""),
            "assistant": ("<｜begin▁of▁sentence｜>Assistant: ", "")
        }
    },

    "llama3": {
        "name": "meta-llama/Meta-Llama-3-8B-Instruct",
        "api_key": "HUGGINGFACE_API_KEY",
        "api_endpoint": "https://api-inference.huggingface.co/models/",
        "api_type": "llama3",
        "prompt_format": {
            "system": (
                "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n",
                "<|eot_id|>"),
            "user": (
                "<|start_header_id|>user<|end_header_id|>\n",
                "<|eot_id|>"),
            "assistant": (
                "<|start_header_id|>assistant<|end_header_id|>\n",
                "<|eot_id|><|start_header_id|>user<|end_header_id|>")
        }
    },

    "phi3": {
        "name": "microsoft/Phi-3-mini-4k-instruct",
        "api_key": "HUGGINGFACE_API_KEY",
        "api_endpoint": "https://api-inference.huggingface.co/models/",
        "api_type": "phi3",
        "prompt_format": {
            "user": (
                "<|user|>\n",
                "<|end|>"),
            "assistant": (
                "<|assistant|>\n",
                "<|end|>")
        }
    }
}

DEFAULT_MODEL = "deepseekv3"


def get_api_key(api_key: str) -> str:
    """Get API key from environment variable."""

    value = os.getenv(api_key)
    if value is not None:
        return value
    try:
        with open(api_key, "r") as file:
            value = file.read().strip()
            if value:
                return value
    except FileNotFoundError:
        pass
    else:
        raise ValueError(f"{api_key} not found in environment variable or file")


def model_selection_menu() -> Dict:
    """Interactive model selection."""

    print("Available models:")
    model_list = list(MODELS.keys())
    for i, short_name in enumerate(model_list):
        print(f"[{i}] {short_name}")

    while True:
        try:
            choice = input("Select a model (enter the number or short name): ")
            if choice.isdigit():
                idx = int(choice)
                if 0 <= idx < len(model_list):
                    model_name = model_list[idx]
                    model = models[model_name]
                    model['short_name'] = model_name
                else:
                    raise IndexError("Index out of range")
            else:
                model_name = choice.strip()
                model = models[model_name]
                model['short_name'] = model_name
        except (KeyError, ValueError, IndexError):
            print("Please enter a valid number or short name.")
        else:
            print(f"Using {model['name']}:")
            return model


def format_prompt_huggingface(formats: dict, conversation_history: list) -> str:
    """Format prompt for Hugging Face models."""

    def to_prompt(role, text):
        return formats[role][0] + text + formats[role][1] + "\n"

    if 'system' in formats:
        prompt = to_prompt(*conversation_history[0]) + to_prompt(*conversation_history[1])
    else:
        prompt = to_prompt('user', conversation_history[0][1] + "\n" + conversation_history[1][1])

    for i in range(2, len(conversation_history)):
        prompt += to_prompt(*conversation_history[i])

    prompt += formats['assistant'][0]
    return prompt


def send_request(model: dict, conversation_history: List[Tuple[str, str]]) -> str:
    """Send request to the appropriate API based on model configuration."""

    api_key = get_api_key(model["api_key"])
    api_type = model["api_type"]

    if api_type == "openrouter":
        return send_openrouter_request(model, api_key, conversation_history)
    elif api_type == "huggingface":
        return send_huggingface_request(model, api_key, conversation_history)
    elif api_type == "anthropic":
        return send_anthropic_request(model, api_key, conversation_history)
    else:
        raise ValueError(f"Unsupported API type: {api_type}")


def send_openrouter_request(model: dict, api_key: str, conversation_history: List[Tuple[str, str]]) -> str:
    """Send request to OpenRouter API."""

    headers = {"Authorization": f"Bearer {api_key}"}

    messages = []

    for role, content in conversation_history:
        if role == "system":
            messages.append({"role": "system", "content": content})
        elif role == "user":
            messages.append({"role": "user", "content": content})
        elif role == "assistant":
            messages.append({"role": "assistant", "content": content})

    payload = {
        "model": model["name"],
        "messages": messages,
        "top_p": 1,
        "temperature": 0.9,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "repetition_penalty": 1,
        "top_k": 0,
    }

    response = requests.post(model["api_endpoint"], headers=headers, json=payload)
    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]


def send_huggingface_request(model: dict, api_key: str, conversation_history: List[Tuple[str, str]]) -> str:
    """Send request to Hugging Face API."""

    headers = {"Authorization": f"Bearer {api_key}"}
    full_prompt = format_prompt_huggingface(model["prompt_format"], conversation_history)

    payload = {
        "inputs": full_prompt,
        "parameters": {
            "return_full_text": False,
            "max_new_tokens": 2500,
            "temperature": 1,
        }
    }

    response = requests.post(model["api_endpoint"] + model["name"], headers=headers, json=payload)
    response.raise_for_status()

    reply = response.json()[0]['generated_text']
    reply = reply.split(model["prompt_format"]['assistant'][0])[-1]

    # Handle different prompt formats
    if model["prompt_format"]['assistant'][1]:
        reply = reply.split(model["prompt_format"]['assistant'][1])[0].strip()

    return reply


def save_conversation(filepath: str, conversation_history: dict):
    sep = 80 * '-' + '\n\n'
    output = sep.join(f"ROLE: {role}\n\n{text}\n\n" for role, text in conversation_history)
    with open(filepath, 'w') as f:
        f.write(output)


def interactive_chat(model: dict):
    """Interactive chat REPL."""

    conversation_history = [("system", INITIAL_PROMPT)]

    while True:
        try:
            user_input = input("> ").strip()
            words = user_input.split()

            if not words:
                continue

            command = words[0].lower()

            if len(words) == 1:
                if command in ["quit", ':q', 'exit']:
                    break
                elif command in ["clear", 'restart']:
                    conversation_history = conversation_history[:1]
                    continue
                elif command in ["swap", "switch", "model"]:
                    model = model_selection_menu()
                    continue

            if command in ["save"] and len(words) == 2:
                filepath = words[1]
                save_conversation(filepath, conversation_history)
                continue

            conversation_history.append(('user', user_input))

        except KeyboardInterrupt:
            user_input = ""
            while user_input not in ["yes", "no", "cancel", "y", "n", "c"]:
                user_input = input("\nSave converation to file (y)es/(n(o)/(c)ancel:").strip().lower()
            if user_input in ["yes", "y"]:
                filepath = input("Insert filepath:").strip().lower()
                save_conversation(filepath, conversation_history)
            elif user_input in ["cancel", "c"]:
                continue
            exit(0)

        try:
            reply = send_request(model, conversation_history)
            print(f"AI: {reply}")
            conversation_history.append(("assistant", reply))
        except Exception as e:
            print(f"Error: {e}")
            conversation_history.pop()


def send_query(model: dict, query: str, system_prompt: str = INITIAL_PROMPT) -> str:
    """Send a single query to the model."""
    conversation_history = [("system", system_prompt), ("user", query)]

    try:
        return send_request(model, conversation_history)
    except Exception as e:
        return f"Error: {e}"


def main():
    parser = argparse.ArgumentParser(description="Yikes!")
    parser.add_argument("args", nargs="*", help="Command arguments")
    parser.add_argument("--model", "-m", help="Specify the model to use", default=DEFAULT_MODEL)
    parser.add_argument("--server", action="store_true", help="Run in server mode")

    args = parser.parse_args()
    model_name = args.model or DEFAULT_MODEL
    model = MODELS.get(model_name)
    command = args.args[0] if args.args else None

    if command is None:
        # Interactive chat mode
        if not model_name or model_name not in MODELS:
            model = model_selection_menu()
        print(f"Using {model['name']}:")
        interactive_chat(model)

    elif command == "list":
        # List available models
        print("Available models:")
        for name, model in MODELS.items():
            print(f"- {name}: {model['name']}")
        print(f"\nDefault model: {DEFAULT_MODEL}")

    elif command == "install":
        # Install the script to a bin directory
        script_path = os.path.abspath(__file__)
        filename = os.path.basename(script_path).split('.')[0]
        bin_path = f"/usr/local/bin/{filename}"

        try:
            shutil.copy(script_path, bin_path)
            os.chmod(bin_path, 0o755)
            print(f"Installed at {bin_path}")
        except PermissionError:
            print("Error: Permission denied. Try with sudo.")

    else:
        # Single query mode
        if model_name not in MODELS:
            print(f"Model '{model_name}' not found, using default")
            model = MODELS[DEFAULT_MODEL]

        query = " ".join(args.args)

        if not sys.stdin.isatty():
            # Use stdin as context.
            context = sys.stdin.read()
            query += " " + context

        response = send_query(model, query=query)
        print(response)
        sys.exit(0)


if __name__ == "__main__":
    main()

