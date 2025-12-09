from services.signalr_client import SignalRClient

def test_connection():
    HUB_URL = "http://localhost:5283"
    client = SignalRClient(HUB_URL)

    print("Testing SignalR connection...")
    if client.connect():
        print("Connection successful!")

        # Test sending an expression
        response = client.send_expression("2+2", "test-123")
        if response:
            print(f"Calculation response: {response}")
        else:
            print("Failed to get calculation response")

        client.disconnect()
    else:
        print("Connection failed!")

if __name__ == "__main__":
    test_connection()
