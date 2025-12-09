from signalrcore.hub_connection_builder import HubConnectionBuilder
import logging
import time
import queue

class SignalRClient:
    def __init__(self, hub_url):
        self.hub_url = hub_url
        self.connection = None
        self.is_connected = False
        self.result_queue = queue.Queue()

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("SignalRClient")

    def connect(self):
        try:
            self.logger.info(f"Connecting to SignalR hub at: {self.hub_url}")

            self.connection = (
                HubConnectionBuilder()
                .with_url(self.hub_url)
                .with_automatic_reconnect({
                    "type": "interval",
                    "keep_alive_interval": 10,
                    "intervals": [1, 3, 5, 10]
                })
                .build()
            )

            # register hub events
            self.connection.on_open(self._on_open)
            self.connection.on_close(self._on_close)
            self.connection.on_error(self._on_error)

            # event from backend
            self.connection.on("ReceiveCalculationResult", self._on_result)

            self.logger.info("Starting SignalR connection...")
            self.connection.start()

            # 🔥 wait until connection opens fully
            timeout = 8
            start = time.time()
            while not self.is_connected and (time.time() - start < timeout):
                time.sleep(0.1)

            if not self.is_connected:
                self.logger.error("Failed to establish SignalR connection")
                return False

            self.logger.info("SignalR connected successfully")
            return True

        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False

    # ---------------------------
    # Internal event handlers
    # ---------------------------

    def _on_open(self):
        self.is_connected = True
        self.logger.info("SignalR connection OPENED")

    def _on_close(self):
        self.is_connected = False
        self.logger.warning("SignalR connection CLOSED")

    def _on_error(self, error):
        self.logger.error(f"SignalR error: {error}")

    def _on_result(self, message):
        self.logger.info(f"Result received raw: {message}")

        if isinstance(message, list) and len(message) > 0:
            message = message[0]

        self.logger.info(f"Result normalized: {message}")
        self.result_queue.put(message)


    # ---------------------------
    # Expression sending
    # ---------------------------

    def send_expression(self, expression, request_id, timeout=6):
        if not self.is_connected:
            self.logger.error("Cannot send expression: SignalR not connected")
            return None

        payload = {
            "expression": expression,
            "requestId": request_id
        }

        self.logger.info(f"Sending expression: {payload}")

        # Python SignalRCore does NOT use invoke() → only send()
        self.connection.send("CalculateExpression", [payload])

        try:
            return self.result_queue.get(timeout=timeout)
        except queue.Empty:
            self.logger.error("Timed out waiting for result")
            return None

    def disconnect(self):
        if self.connection:
            self.connection.stop()
            self.is_connected = False
            self.logger.info("Disconnected from hub")
