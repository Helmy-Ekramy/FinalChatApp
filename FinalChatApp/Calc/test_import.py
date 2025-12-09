"""
Test script to verify imports are working correctly
"""
import sys
print("Python path:")
for p in sys.path:
    print(f"  {p}")

print("\nTrying to import SignalRClient...")
try:
    from services.signalr_client import SignalRClient
    print("✓ Import successful!")

    print("\nTesting SignalRClient initialization...")
    client = SignalRClient("http://localhost:5283/calculatorHub")
    print(f"✓ Client created successfully!")
    print(f"  Base URL: {client.base_url}")
    print(f"  Endpoint: {client.endpoint}")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()