#!/usr/bin/env python
import os
import requests
import argparse
import shutil
from typing import Dict, List, Tuple


INITIAL_PROMPT = "Provide concise replies."

MODELS = {

    "llama3": {
        "name": "meta-llama/Meta-Llama-3-8B-Instruct",
        "api_key": "HUGGINGFACE_API_KEY",
        "api_endpoint": "https://api-inference.huggingface.co/models/",
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


def get_api_key(api_key: str) -> str:
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


def select_model(models: Dict) -> str:
    print("Available models:")
    for i, short_name in enumerate(models.keys()):
        print(f"[{i}] {short_name}")

    while True:
        try:
            choice = input("Select a model (enter the number or short name): ")
            if choice.isdigit():
                model = list(models.values())[int(choice)]
            else:
                model = models[choice.strip()]
        except (KeyError, ValueError):
            print("Please enter a valid number or short name.")
        else:
            print(f"Chatting with {model['name']}:")
            return model


def format_prompt(formats: dict, conversation_history: list) -> str:
    def to_prompt(role, text):
        return formats[role][0] + text + formats[role][1] + "\n"

    if bool(formats.get('system')):
        prompt = to_prompt(*conversation_history[0]) + to_prompt(*conversation_history[1])
    else:
        prompt = to_prompt('user', conversation_history[0][1] + "\n" + conversation_history[1][1])
    for i in range(2, len(conversation_history)):
        prompt += to_prompt(*conversation_history[i])
    prompt += formats['assistant'][0]
    return prompt


def send_request(model: dict, conversation_history: List[Tuple[str, str]]) -> str:
    api_key = get_api_key(model["api_key"])
    headers = {"Authorization": f"Bearer {api_key}"}

    full_prompt = format_prompt(model["prompt_format"], conversation_history)

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
    reply = reply.split(model["prompt_format"]['assistant'][0])[0].strip()
    return reply


def chat_repl(model: dict):
    conversation_history = [("system", INITIAL_PROMPT)]

    while True:
        user_input = input("> ").strip()

        if not len(user_input):
            continue
        elif user_input.lower() in ["quit", ':q', 'exit']:
            break
        elif user_input.lower() in ["clear", 'restart']:
            conversation_history = conversation_history[:1]
            continue
        elif user_input.lower() in ["swap", "switch"]:
            model = select_model(MODELS)
            continue

        conversation_history.append(('user', user_input))
        try:
            reply = send_request(model, conversation_history)
            print(f"AI: {reply}")
            conversation_history.append(("assistant", reply))
        except Exception as e:
            print(e)
            conversation_history.pop(-1)


def send_query(model: dict, query: str) -> None:
    conversation_history = [("system", INITIAL_PROMPT), ("user", query)]

    try:
        reply = send_request(model, conversation_history)
        print(reply)
    except Exception as e:
        print(e)


def main():
    parser = argparse.ArgumentParser(
        description="Chat with a Hugging Face model")
    parser.add_argument(
        "command_or_query",
        nargs="*",
        help="Command to execute or query to send to the model")
    args = parser.parse_args()

    if len(args.command_or_query) == 0:
        model = select_model(MODELS)
        chat_repl(model)
    elif args.command_or_query[0] == "install":
        script_path = os.path.abspath(__file__)
        filename = __file__.split('/')[-1].split('.')[0]
        bin_path = f"/usr/local/bin/{filename}"
        shutil.copy(script_path, bin_path)
        os.chmod(bin_path, 0o755)
        print(f"Installed Yikes! at {bin_path}")
    else:
        model = MODELS["llama3"]
        query = " ".join(args.command_or_query)
        send_query(model, query)


if __name__ == "__main__":
    main()
