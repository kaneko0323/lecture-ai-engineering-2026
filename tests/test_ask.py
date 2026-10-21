from app.ask import ask, create_chat_session


class DummyResponse:
    def __init__(self, text: str):
        self.text = text


class DummyChat:
    def __init__(self):
        self.questions = []

    def send_message(self, question: str):
        self.questions.append(question)
        return DummyResponse(f"回答: {question}")


def test_ask_uses_chat_session_for_history(monkeypatch):
    chat = DummyChat()

    monkeypatch.setattr("app.ask.get_api_key", lambda: "dummy-key")

    result = ask("最初の質問", chat=chat)

    assert result == "回答: 最初の質問"
    assert chat.questions == ["最初の質問"]


def test_create_chat_session_keeps_client_available(monkeypatch):
    chat = DummyChat()

    class DummyClient:
        class Chats:
            def create(self, *, model, history):
                assert model
                assert history == []
                return chat

        chats = Chats()

    client = DummyClient()
    monkeypatch.setattr("app.ask.get_api_key", lambda: "dummy-key")
    monkeypatch.setattr("app.ask.genai.Client", lambda **kwargs: client)

    returned_client, returned_chat = create_chat_session()

    assert returned_client is client
    assert returned_chat is chat
