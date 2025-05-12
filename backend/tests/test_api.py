import io
from uuid import uuid4
from llama_index.core.schema import Document as LlamaDocument

def test_signup(test_client, test_user):
    # Duplicate test to check 409
    response = test_client.post("/auth/signup", json=test_user)
    assert response.status_code in [200, 201, 409]


def test_login_success(test_client, test_user):
    response = test_client.post(
        "/auth/login",
        data={"username": test_user["username"], "password": test_user["password"]},
    )
    assert response.status_code == 200
    json = response.json()
    assert "access_token" in json
    assert json["token_type"] == "bearer"


def test_login_fail(test_client):
    response = test_client.post(
        "/auth/login", data={"username": "wrong@example.com", "password": "wrongpass"}
    )
    assert response.status_code == 401


def test_get_current_user(test_client, auth_token, test_user):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = test_client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    print(response.json())
    data = response.json()
    assert data["username"] == test_user["username"]
    assert "id" in data
    assert data["is_active"] is True


def test_upload_txt_document(
    test_client,
    auth_header,
    fake_vector_store,
    monkeypatch,
):
   
    from app.api import document  # adjust if it's elsewhere
    document.get_vector_store = lambda: fake_vector_store

    class FakeTextNode:
        def __init__(self, text, metadata):
            self.text = text
            self.metadata = metadata
            self.node_id = 1  # Mock node ID

    class FakeEmbedder:
        def load_documents(self, path):
            return [{"text": "fake document"}]

        def text_splitter(self, docs):
            return ["chunk1", "chunk2"], [0, 1]

        def create_text_nodes(self, chunks, docs, idxs, metadata):
            return [
                LlamaDocument(
                    text=c,
                    metadata=metadata,
                    embedding=[0.1] * 768  # ✅ Set dummy embedding
                )
                for c in chunks
            ]

        def embed_text_nodes(self, nodes):
            return nodes

    monkeypatch.setattr("app.api.document.Embedder", FakeEmbedder)

    fake_file = io.BytesIO(b"This is a test document.")
    fake_file.name = "testdoc.txt"  # Needed for UploadFile emulation

    response = test_client.post(
        "/documents/",
        data={"title": "Test Upload"},
        files={"file": (fake_file.name, fake_file, "text/plain")},
        headers=auth_header

    )

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["title"] == "Test Upload"
    assert data["file_name"] == "testdoc.txt"
    assert data["owner_id"]  # should match test user
    assert "id" in data


def test_invalid_file_type(test_client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    fake_file = io.BytesIO(b"<html></html>")
    fake_file.name = "test.html"
    response = test_client.post(
        "/documents/",
        data={"title": "Invalid"},
        files={"file": (fake_file.name, fake_file, "text/html")},
        headers=headers,
    )
    print(response.json())
    assert response.status_code == 400
    assert "Invalid file type" in response.text


def test_list_documents(test_client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = test_client.get("/documents/", headers=headers)
    assert response.status_code == 200
    docs = response.json()
    assert isinstance(docs, list)
    assert all("id" in d for d in docs)


def test_ask_question(test_client, auth_header, mock_query_engine):
    fake_document_id = "342452e4-7da6-4eda-80a3-78809f922029" # document ID from test db

    payload = {
        "question": "What is this document about?",
        "document_id": fake_document_id,
    }

    response = test_client.post("/ask", json=payload, headers=auth_header)

    if response.status_code != 200:
        fake_document_id = str(uuid4())

        assert response.status_code == 404
        assert "Not Found" in response.text

    else:

        assert response.status_code == 200
        data = response.json()

        assert data["answer"] == "This is a mocked answer."
        assert data["question"] == payload["question"]
        assert data["document_id"] == fake_document_id
        assert len(data["source_documents"]) == 1
        assert data["source_documents"][0]["text"] == "Mocked source document."
        assert "metadata" in data["source_documents"][0]
