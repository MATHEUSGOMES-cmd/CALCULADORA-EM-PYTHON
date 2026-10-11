import ast
import re
import tkinter as tk
from decimal import Decimal, DecimalException


BACKGROUND = "#0B1120"
PANEL = "#111827"
BUTTON = "#1F2937"
BUTTON_HOVER = "#293548"
TEXT = "#F8FAFC"
MUTED = "#94A3B8"
ACCENT = "#F97316"
ACCENT_HOVER = "#FB923C"


def format_number(number: Decimal) -> str:
    value = format(number, "f")
    if "." in value:
        value = value.rstrip("0").rstrip(".")
    return "0" if value in ("", "-0") else value


def evaluate(expression: str) -> Decimal:
    tree = ast.parse(expression, mode="eval")

    def calculate(node: ast.AST) -> Decimal:
        if isinstance(node, ast.Expression):
            return calculate(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return Decimal(str(node.value))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = calculate(node.operand)
            return value if isinstance(node.op, ast.UAdd) else -value
        if isinstance(node, ast.BinOp):
            left = calculate(node.left)
            right = calculate(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
        raise ValueError("Expressão inválida")

    return calculate(tree)


class Calculator:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.expression = ""
        self.just_evaluated = False
        self.display = tk.StringVar(value="0")
        self.history = tk.StringVar(value=" ")

        root.title("Calculadora")
        root.configure(bg=BACKGROUND)
        root.resizable(False, False)
        root.minsize(350, 540)
        self._center_window(390, 600)
        self._build_interface()
        self._bind_keyboard()

    def _center_window(self, width: int, height: int) -> None:
        x = (self.root.winfo_screenwidth() - width) // 2
        y = (self.root.winfo_screenheight() - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _build_interface(self) -> None:
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        header = tk.Frame(self.root, bg=BACKGROUND)
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(28, 16))
        tk.Label(
            header,
            text="CALCULADORA",
            bg=BACKGROUND,
            fg=MUTED,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w")
        tk.Label(
            header,
            text="Simples. Rápida. Precisa.",
            bg=BACKGROUND,
            fg=TEXT,
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w", pady=(5, 0))

        panel = tk.Frame(self.root, bg=PANEL, highlightthickness=1, highlightbackground="#1E293B")
        panel.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(2, weight=1)

        tk.Label(
            panel,
            textvariable=self.history,
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 12),
            anchor="e",
        ).grid(row=0, column=0, sticky="ew", padx=20, pady=(22, 4))
        self.display_label = tk.Label(
            panel,
            textvariable=self.display,
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 36, "bold"),
            anchor="e",
            justify="right",
        )
        self.display_label.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))

        keypad = tk.Frame(panel, bg=PANEL)
        keypad.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 12))
        for column in range(4):
            keypad.grid_columnconfigure(column, weight=1, uniform="key")
        for row in range(5):
            keypad.grid_rowconfigure(row, weight=1, uniform="key")

        keys = [
            ("AC", 0, 0, "function"),
            ("⌫", 0, 1, "function"),
            ("%", 0, 2, "function"),
            ("÷", 0, 3, "operator"),
            ("7", 1, 0, "number"),
            ("8", 1, 1, "number"),
            ("9", 1, 2, "number"),
            ("×", 1, 3, "operator"),
            ("4", 2, 0, "number"),
            ("5", 2, 1, "number"),
            ("6", 2, 2, "number"),
            ("−", 2, 3, "operator"),
            ("1", 3, 0, "number"),
            ("2", 3, 1, "number"),
            ("3", 3, 2, "number"),
            ("+", 3, 3, "operator"),
            ("±", 4, 0, "function"),
            ("0", 4, 1, "number"),
            (".", 4, 2, "number"),
            ("=", 4, 3, "equals"),
        ]
        for label, row, column, style in keys:
            self._add_button(keypad, label, row, column, style)

        tk.Label(
            panel,
            text="DIGITE OU USE O TECLADO",
            bg=PANEL,
            fg="#64748B",
            font=("Segoe UI", 8, "bold"),
        ).grid(row=3, column=0, pady=(0, 12))

    def _add_button(self, parent: tk.Frame, label: str, row: int, column: int, style: str) -> None:
        colors = {
            "number": (BUTTON, TEXT, BUTTON_HOVER),
            "function": ("#263244", "#CBD5E1", "#334155"),
            "operator": ("#33251F", ACCENT, "#493126"),
            "equals": (ACCENT, "#FFFFFF", ACCENT_HOVER),
        }
        background, foreground, active = colors[style]
        button = tk.Button(
            parent,
            text=label,
            command=lambda key=label: self._press(key),
            bg=background,
            fg=foreground,
            activebackground=active,
            activeforeground=foreground,
            font=("Segoe UI", 17 if style != "equals" else 19, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
            takefocus=False,
        )
        button.grid(row=row, column=column, sticky="nsew", padx=5, pady=5, ipadx=2, ipady=5)

    def _bind_keyboard(self) -> None:
        self.root.bind("<Key>", self._on_key)
        self.root.bind("<Return>", lambda _event: self._press("="))
        self.root.bind("<KP_Enter>", lambda _event: self._press("="))
        self.root.bind("<BackSpace>", lambda _event: self._press("⌫"))
        self.root.bind("<Escape>", lambda _event: self._press("AC"))

    def _on_key(self, event: tk.Event) -> None:
        key = event.char
        if key in "0123456789." and key:
            self._press(key)
        elif key in "+-*/" and key:
            self._press({"*": "×", "/": "÷", "-": "−"}.get(key, key))

    def _refresh_display(self) -> None:
        shown = self.expression.replace("*", "×").replace("/", "÷").replace("-", "−")
        self.display.set(shown or "0")
        length = len(shown)
        size = 36 if length <= 10 else 28 if length <= 16 else 20 if length <= 24 else 16
        self.display_label.configure(font=("Segoe UI", size, "bold"))

    def _press(self, key: str) -> None:
        if key == "AC":
            self.expression = ""
            self.history.set(" ")
            self.just_evaluated = False
            self._refresh_display()
            return
        if self.display.get() == "Erro":
            self.history.set(" ")
            self.display.set("0")
        if key == "⌫":
            if self.just_evaluated:
                self.expression = ""
            else:
                self.expression = self.expression[:-1]
            self.just_evaluated = False
            self.history.set(" ")
            self._refresh_display()
            return
        if key == "=":
            self._calculate()
            return
        if key == "%":
            self._percent()
            return
        if key == "±":
            self._toggle_sign()
            return
        if key in "+−×÷":
            self._operator(key)
            return
        if key.isdigit():
            self._digit(key)
            return
        if key == ".":
            self._decimal()

    def _digit(self, digit: str) -> None:
        if self.just_evaluated:
            self.expression = ""
            self.history.set(" ")
        if self.expression.endswith(")"):
            self.expression += "*"
        if len(self.expression) < 48:
            self.expression += digit
        self.just_evaluated = False
        self._refresh_display()

    def _decimal(self) -> None:
        if self.just_evaluated:
            self.expression = ""
            self.history.set(" ")
        if self.expression.endswith(")"):
            self.expression += "*0."
        else:
            current_number = re.search(r"\d+(?:\.\d*)?$|\.\d+$", self.expression)
            if current_number is None:
                self.expression += "0."
            elif "." not in current_number.group():
                self.expression += "."
        self.just_evaluated = False
        self._refresh_display()

    def _operator(self, operator: str) -> None:
        symbol = {"×": "*", "÷": "/", "−": "-"}.get(operator, operator)
        if self.just_evaluated:
            self.history.set(" ")
        self.just_evaluated = False
        if not self.expression:
            if symbol == "-":
                self.expression = "-"
        elif self.expression[-1] in "+-*/":
            if symbol == "-" and self.expression[-1] in "*/":
                self.expression += symbol
            else:
                self.expression = self.expression[:-1] + symbol
        else:
            self.expression += symbol
        self._refresh_display()

    def _percent(self) -> None:
        match = re.search(r"(?:\d+(?:\.\d*)?|\.\d+)$", self.expression)
        if match is None:
            return
        try:
            value = Decimal(match.group()) / Decimal(100)
        except DecimalException:
            self._show_error("Expressão inválida")
            return
        self.expression = self.expression[: match.start()] + format_number(value)
        self.just_evaluated = False
        self._refresh_display()

    def _toggle_sign(self) -> None:
        match = re.search(r"(?:\d+(?:\.\d*)?|\.\d+)$", self.expression)
        if match is None:
            if not self.expression or self.expression[-1] in "+-*/(":
                self.expression += "-"
            self._refresh_display()
            return
        start = match.start()
        if start > 0 and self.expression[start - 1] == "-":
            before_minus = start - 1
            if before_minus == 0 or self.expression[before_minus - 1] in "+-*/(":
                self.expression = self.expression[:before_minus] + self.expression[start:]
            else:
                self.expression = self.expression[:start] + "-" + self.expression[start:]
        else:
            self.expression = self.expression[:start] + "-" + self.expression[start:]
        self.just_evaluated = False
        self._refresh_display()

    def _calculate(self) -> None:
        if not self.expression:
            return
        source = self.expression
        try:
            result = evaluate(source)
        except (SyntaxError, ValueError, DecimalException):
            self._show_error("Expressão inválida")
            return
        self.history.set(source.replace("*", "×").replace("/", "÷").replace("-", "−") + " =")
        self.expression = format_number(result)
        self.just_evaluated = True
        self._refresh_display()

    def _show_error(self, message: str) -> None:
        self.history.set(message)
        self.expression = ""
        self.just_evaluated = False
        self.display.set("Erro")


if __name__ == "__main__":
    window = tk.Tk()
    Calculator(window)
    window.mainloop()
