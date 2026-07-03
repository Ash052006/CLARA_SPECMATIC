def test_home_returns_expected_message(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "CLARA is alive"}


def test_health_reports_contract_test_runtime(client):
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["conversation_manager"] == "available"


def test_chat_returns_normalized_response(client, sample_messages):
    response = client.get(f"/chat/{sample_messages['normal']}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["response"].startswith("Contract test response for:")
    assert "timestamp" in payload
    assert "conversation_id" in payload


def test_chat_rejects_blank_message(client, sample_messages):
    response = client.get(f"/chat/{sample_messages['blank']}")

    assert response.status_code == 400
    payload = response.json()
    assert payload["error_code"] == "EMPTY_MESSAGE"


def test_chat_returns_structured_server_error(client):
    response = client.get("/chat/raise%20error")

    assert response.status_code == 500
    payload = response.json()
    assert payload["error_code"] == "INTERNAL_SERVER_ERROR"
