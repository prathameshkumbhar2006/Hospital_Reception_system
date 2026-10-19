# ============================================================
# HOSPITAL RECEPTION SYSTEM
# FILE: patient/keypad.py
# PURPOSE: Touchscreen Numeric Keypad
# ============================================================

import tkinter as tk
import customtkinter as ctk

from config import (
    CARD_COLOR,
    PRIMARY_COLOR,
    TEXT_COLOR,
    BORDER_COLOR,
    FONT_FAMILY
)


class NumericKeypad(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        entry,
        max_length=10
    ):

        super().__init__(
            parent,
            fg_color="transparent",
            corner_radius=0
        )

        self.entry = entry
        self.max_length = max(1, int(max_length))

        self.create_widgets()
        self.configure_entry_validation()

    # ========================================================
    # 1. CREATE KEYPAD BUTTONS
    # ========================================================

    def create_widgets(self):

        for column in range(3):
            self.grid_columnconfigure(
                column,
                weight=1
            )

        buttons = [
            ("1", 0, 0),
            ("2", 0, 1),
            ("3", 0, 2),

            ("4", 1, 0),
            ("5", 1, 1),
            ("6", 1, 2),

            ("7", 2, 0),
            ("8", 2, 1),
            ("9", 2, 2),

            ("CLEAR", 3, 0),
            ("0", 3, 1),
            ("⌫", 3, 2)
        ]

        for text, row, column in buttons:

            if text == "CLEAR":

                command = self.clear_input
                background = "#FEE2E2"
                hover = "#FECACA"
                foreground = "#DC2626"
                size = 16

            elif text == "⌫":

                command = self.backspace
                background = "#E5E7EB"
                hover = "#D1D5DB"
                foreground = TEXT_COLOR
                size = 24

            else:

                command = (
                    lambda digit=text: self.add_digit(digit)
                )

                background = CARD_COLOR
                hover = "#EFF6FF"
                foreground = PRIMARY_COLOR
                size = 27

            button = ctk.CTkButton(
                self,
                text=text,
                width=95,
                height=58,
                font=ctk.CTkFont(
                    family=FONT_FAMILY,
                    size=size,
                    weight="bold"
                ),
                fg_color=background,
                hover_color=hover,
                text_color=foreground,
                border_width=1,
                border_color=BORDER_COLOR,
                corner_radius=8,
                command=command
            )

            button.grid(
                row=row,
                column=column,
                padx=6,
                pady=6,
                sticky="nsew"
            )

    # ========================================================
    # 2. VALIDATE INPUT
    # ========================================================

    def configure_entry_validation(self):

        self.validation_command = self.register(
            self.validate_input
        )

        self.entry.configure(
            validate="key",
            validatecommand=(
                self.validation_command,
                "%P"
            )
        )

    def validate_input(self, value):

        if value == "":
            return True

        if len(value) > self.max_length:
            return False

        return all(
            character in "0123456789"
            for character in value
        )

    # ========================================================
    # 3. GET CURRENT VALUE
    # ========================================================

    def get_value(self):

        return self.entry.get()

    # ========================================================
    # 4. ADD DIGIT
    # ========================================================

    def add_digit(self, digit):

        digit = str(digit)

        if digit not in "0123456789":
            return

        if len(digit) != 1:
            return

        current_value = self.entry.get()

        if len(current_value) >= self.max_length:
            return

        # Insert at the end so touchscreen input is predictable.
        new_value = current_value + digit

        if not self.validate_input(new_value):
            return

        self.entry.insert(
            "end",
            digit
        )

        self.entry.icursor("end")
        self.entry.focus_set()

    # ========================================================
    # 5. CLEAR ALL DIGITS
    # ========================================================

    def clear_input(self):

        self.entry.delete(
            0,
            "end"
        )

        self.entry.focus_set()

    # ========================================================
    # 6. DELETE LAST DIGIT
    # ========================================================

    def backspace(self):

        current_value = self.entry.get()

        if not current_value:
            return

        self.entry.delete(
            len(current_value) - 1,
            "end"
        )

        self.entry.icursor("end")
        self.entry.focus_set()

    # ========================================================
    # 7. SET VALUE
    # ========================================================

    def set_value(self, value):

        value = str(value)

        if not self.validate_input(value):

            raise ValueError(
                "Only numeric input is allowed. "
                f"Maximum length: {self.max_length}"
            )

        self.entry.delete(
            0,
            "end"
        )

        self.entry.insert(
            0,
            value
        )

        self.entry.icursor("end")

    # ========================================================
    # 8. CHECK WHETHER INPUT IS COMPLETE
    # ========================================================

    def is_complete(self):

        value = self.get_value()

        return (
            len(value) == self.max_length
            and self.validate_input(value)
        )


# ============================================================
# END OF FILE
# ============================================================
