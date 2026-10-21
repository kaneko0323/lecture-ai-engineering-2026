"""第1回: 素のLLMに1回だけ質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 質問を省略すると、講座に固有の質問をする

ツールも会話履歴も持たない「素の」呼び出し。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse

from google import genai
from google.genai.chats import Chat
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def create_chat_session(history=None) -> tuple[genai.Client, Chat]:
    client = genai.Client(api_key=get_api_key())
    chat = client.chats.create(model=MODEL, history=history or [])
    return client, chat


def ask(question: str, chat: Chat | None = None, history=None) -> str:
    if chat is None:
        _client, chat = create_chat_session(history=history)

    response = chat.send_message(question)

    usage = getattr(response, "usage_metadata", None)
    if usage is not None:
        prompt_tokens = getattr(usage, "prompt_token_count", None)
        output_tokens = getattr(usage, "candidates_token_count", None)
        if prompt_tokens is not None or output_tokens is not None:
            print(f"[入力トークン数] {prompt_tokens}")
            print(f"[出力トークン数] {output_tokens}")

    return response.text


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?", default=None)
    args = parser.parse_args()

    print(f"[model] {MODEL}")

    if args.question is not None:
        print(f"[質問] {args.question}\n")
        try:
            print(ask(args.question))
        except errors.APIError as e:
            print(api_error_message(e.code, e.message))
            raise SystemExit(1)
        return

    _client, chat = create_chat_session()
    print("会話を続けます。終了するには 'exit' または Ctrl-D を入力してください。\n")
    while True:
        try:
            question = input("質問> ")
        except EOFError:
            print()
            break

        if not question.strip() or question.strip().lower() in {"exit", "quit", "q"}:
            break

        print(f"\n[質問] {question}\n")
        try:
            print(ask(question, chat=chat))
        except errors.APIError as e:
            print(api_error_message(e.code, e.message))
            raise SystemExit(1)
        print()


if __name__ == "__main__":
    main()
