import tkinter as tk
from tkinter import messagebox
from gui.calculator_window import CalculatorWindow
from services.signalr_client import SignalRClient
import sys
import logging

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # SignalR hub URL
    HUB_URL = "http://localhost:5283/calculatorHub"

    print("="*60)
    print("Real-Time Calculator - Starting...")
    print("="*60)
    
    # Create SignalR client
    logger.info("Creating SignalR client...")
    signalr_client = SignalRClient(HUB_URL)

    # Connect to backend
    logger.info("Connecting to calculator backend...")
    if not signalr_client.connect():
        logger.error("Failed to establish connection")
        messagebox.showerror(
            "Connection Error",
            "Failed to connect to the calculator backend.\n\n"
            "Please ensure the .NET backend is running:\n\n"
            "1. Open a terminal in the project directory\n"
            "2. Navigate to: backend/CalculatorBackend/\n"
            "3. Run: dotnet restore\n"
            "4. Run: dotnet run\n"
            "5. Wait for: 'Now listening on: http://localhost:5283'\n\n"
            "Then restart this application.\n\n"
            "Check the console for detailed troubleshooting information."
        )
        sys.exit(1)

    logger.info("✓ Connection established successfully!")
    print("="*60)

    # Create Tkinter root window
    root = tk.Tk()

    # Create calculator window
    calculator = CalculatorWindow(root, signalr_client)

    # Handle window close
    def on_closing():
        logger.info("Closing application...")
        signalr_client.disconnect()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Start the GUI event loop
    logger.info("Starting GUI...")
    root.mainloop()

if __name__ == "__main__":
    main()