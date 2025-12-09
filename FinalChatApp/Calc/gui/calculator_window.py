import tkinter as tk
from tkinter import messagebox
from gui.styles import COLORS, FONTS, WINDOW_SIZE, BUTTON_SIZE, PADDING
from models.calculator_state import CalculatorState
from services.signalr_client import SignalRClient
import threading

class CalculatorWindow:
    def __init__(self, root, signalr_client):
        self.root = root
        self.signalr_client = signalr_client
        self.state = CalculatorState()

        # Configure window
        self.root.title("Real-Time Calculator")
        self.root.geometry(f"{WINDOW_SIZE['width']}x{WINDOW_SIZE['height']}")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS['bg_main'])

        # Create UI components
        self._create_display()
        self._create_buttons()
        self._create_status_bar()  # Add this line
    def _create_display(self):
        """Create the display panel"""
        display_frame = tk.Frame(self.root, bg=COLORS['bg_display'], padx=PADDING['frame'], pady=PADDING['frame'])
        display_frame.pack(fill=tk.BOTH, padx=PADDING['frame'], pady=PADDING['frame'])

        # Expression label (shows what user is typing)
        self.expression_label = tk.Label(
            display_frame,
            text="",
            font=FONTS['expression'],
            bg=COLORS['bg_display'],
            fg=COLORS['fg_display'],
            anchor=tk.E,
            height=1
        )
        self.expression_label.pack(fill=tk.BOTH)

        # Result label (shows calculation result)
        self.result_label = tk.Label(
            display_frame,
            text="0",
            font=FONTS['display'],
            bg=COLORS['bg_display'],
            fg=COLORS['fg_display'],
            anchor=tk.E,
            height=2
        )
        self.result_label.pack(fill=tk.BOTH)

    def _create_buttons(self):
        """Create the calculator button grid"""
        button_frame = tk.Frame(self.root, bg=COLORS['bg_main'])
        button_frame.pack(fill=tk.BOTH, expand=True, padx=PADDING['frame'], pady=PADDING['frame'])

        # Button layout: 4x4 grid
        # Row 0: 7 8 9 /
        # Row 1: 4 5 6 *
        # Row 2: 1 2 3 -
        # Row 3: C 0 = +

        buttons = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['C', '0', '=', '+']
        ]

        # Store operator buttons for enabling/disabling
        self.operator_buttons = {}

        for row_idx, row in enumerate(buttons):
            for col_idx, btn_text in enumerate(row):
                if btn_text in ['+', '-', '*', '/']:
                    # Operator button
                    btn = self._create_button(button_frame, btn_text, 'operator')
                    self.operator_buttons[btn_text] = btn
                elif btn_text == 'C':
                    # Clear button
                    btn = self._create_button(button_frame, btn_text, 'special')
                elif btn_text == '=':
                    # Equals button
                    btn = self._create_button(button_frame, btn_text, 'special')
                else:
                    # Number button
                    btn = self._create_button(button_frame, btn_text, 'number')

                btn.grid(row=row_idx, column=col_idx, padx=PADDING['button'], pady=PADDING['button'], sticky='nsew')

        # Configure grid weights for even spacing
        for i in range(4):
            button_frame.grid_rowconfigure(i, weight=1)
            button_frame.grid_columnconfigure(i, weight=1)

    def _create_status_bar(self):
        """Create status bar at the bottom"""
        status_frame = tk.Frame(self.root, bg=COLORS['bg_main'], height=30)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=PADDING['frame'])
        
        self.status_label = tk.Label(
            status_frame,
            text="● Connected" if self.signalr_client.is_connected else "● Disconnected",
            font=('Arial', 9),
            bg=COLORS['bg_main'],
            fg='#4CAF50' if self.signalr_client.is_connected else '#FF3B30',
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, padx=5, pady=5)

    def _create_button(self, parent, text, button_type):
        """Create a styled button"""
        if button_type == 'operator':
            bg_color = COLORS['bg_operator']
            hover_color = COLORS['hover_operator']
            command = lambda: self._on_operator_click(text)
        elif button_type == 'special':
            bg_color = COLORS['bg_special']
            hover_color = COLORS['hover_special']
            if text == 'C':
                command = self._on_clear_click
            else:  # '='
                command = self._on_equals_click
        else:  # number
            bg_color = COLORS['bg_number']
            hover_color = COLORS['hover_number']
            command = lambda: self._on_number_click(text)

        btn = tk.Button(
            parent,
            text=text,
            font=FONTS['button'],
            bg=bg_color,
            fg=COLORS['fg_button'],
            activebackground=hover_color,
            activeforeground=COLORS['fg_button'],
            borderwidth=0,
            command=command,
            width=BUTTON_SIZE['width'],
            height=BUTTON_SIZE['height']
        )

        # Bind hover effects
        btn.bind('<Enter>', lambda e: btn.configure(bg=hover_color))
        btn.bind('<Leave>', lambda e: btn.configure(bg=bg_color))

        return btn
     
    # def _create_status_bar(self):
    #     """Create status bar at the bottom"""
    #     status_frame = tk.Frame(self.root, bg=COLORS['bg_main'], height=30)
    #     status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=PADDING['frame'])
        
    #     self.status_label = tk.Label(
    #         status_frame,
    #         text="● Connected" if self.signalr_client.is_connected else "● Disconnected",
    #         font=('Arial', 9),
    #         bg=COLORS['bg_main'],
    #         fg='#4CAF50' if self.signalr_client.is_connected else '#FF3B30',
    #         anchor=tk.W
    #     )
    #     self.status_label.pack(side=tk.LEFT, padx=5, pady=5)
    def _on_number_click(self, number):
        """Handle number button click"""
        self.state.add_number(number)
        self._update_display()
        self._enable_operator_buttons()
        self._send_to_backend()

    def _on_operator_click(self, operator):
        """Handle operator button click"""
        if self.state.can_add_operator():
            self.state.add_operator(operator)
            self._update_display()
            self._disable_operator_buttons()
            self._send_to_backend()

    def _on_clear_click(self):
        """Handle clear button click"""
        self.state.clear()
        self._update_display()
        self._enable_operator_buttons()

    def _on_equals_click(self):
        """Handle equals button click (same as current result display)"""
        # Since we show real-time results, equals just confirms the current result
        pass

    def _update_display(self):
        """Update the display labels"""
        self.expression_label.config(text=self.state.expression or " ")
        self.result_label.config(text=self.state.result, fg=COLORS['fg_display'])

    def _enable_operator_buttons(self):
        """Enable all operator buttons"""
        for btn in self.operator_buttons.values():
            btn.config(state=tk.NORMAL)

    def _disable_operator_buttons(self):
        """Disable all operator buttons"""
        for btn in self.operator_buttons.values():
            btn.config(state=tk.DISABLED)

    def _send_to_backend(self):
        """Send expression to backend via SignalR"""
        def send():
            request_id = self.state.generate_request_id()
            response = self.signalr_client.send_expression(self.state.expression, request_id)

            if response and self.state.is_latest_request(response.get('requestId', '')):
                # Update result on main thread
                self.root.after(0, lambda: self._handle_response(response))

        # Run in separate thread to avoid blocking UI
        threading.Thread(target=send, daemon=True).start()

    def _handle_response(self, response):
        """Handle response from backend"""
        if response.get('isValid', False):
            self.state.result = response.get('result', '0')
            self.result_label.config(text=self.state.result, fg=COLORS['fg_display'])
        else:
            # Show error
            error = response.get('error', 'Error')
            self.state.result = error
            self.result_label.config(text=error, fg=COLORS['fg_error'])
