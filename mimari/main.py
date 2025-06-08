import tkinter as tk
from tkinter import ttk, messagebox
import math
import random

class HammingCode:
    @staticmethod
    def get_total_length(data_length):
        """Calculate total bits needed (data + parity + overall parity)."""
        r = 0
        while 2**r < data_length + r + 1:
            r += 1
        return data_length + r + 1  # +1 for overall parity bit

    @staticmethod
    def is_power_of_two(n):
        """Check if n is a power of two."""
        return n > 0 and (n & (n - 1)) == 0

    @staticmethod
    def is_valid_binary(data, bit_length):
        """Validate if data is a binary string of the correct length."""
        return len(data) == bit_length and all(c in '01' for c in data)

    @staticmethod
    def calculate_hamming_code(data):
        """Calculate Hamming code with overall parity bit."""
        data_length = len(data)
        total_length = HammingCode.get_total_length(data_length)
        r = total_length - data_length - 1
        hamming_code = ['0'] * total_length
        data_index = 0

        # Place data bits
        for i in range(1, total_length):
            if not HammingCode.is_power_of_two(i):
                if data_index < len(data):
                    hamming_code[i - 1] = data[data_index]
                    data_index += 1

        # Calculate parity bits
        for i in range(r):
            parity_pos = 2**i
            parity = 0
            for j in range(1, total_length):
                if (j & parity_pos) != 0 and hamming_code[j - 1] == '1':
                    parity ^= 1
            hamming_code[parity_pos - 1] = str(parity)

        # Calculate overall parity (p0)
        overall_parity = 0
        for bit in hamming_code[:-1]:
            if bit == '1':
                overall_parity ^= 1
        hamming_code[-1] = str(overall_parity)

        return ''.join(hamming_code)

    @staticmethod
    def introduce_random_error(code):
        """Introduce a random single-bit error."""
        pos = random.randint(1, len(code))
        code_list = list(code)
        code_list[pos - 1] = '1' if code_list[pos - 1] == '0' else '0'
        return f"{''.join(code_list)},{pos}"

    @staticmethod
    def introduce_error_at_position(code, pos):
        """Introduce an error at the specified position."""
        code_list = list(code)
        code_list[pos - 1] = '1' if code_list[pos - 1] == '0' else '0'
        return f"{''.join(code_list)},{pos}"

    @staticmethod
    def detect_and_correct_error(code, original_data):
        """Detect and correct errors in the Hamming code."""
        total_length = len(code)
        data_length = len(original_data)
        r = total_length - data_length - 1
        syndrome = 0
        overall_parity = 0

        # Calculate syndrome
        for i in range(r):
            parity_pos = 2**i
            parity = 0
            for j in range(1, total_length + 1):
                if (j & parity_pos) != 0 and code[j - 1] == '1':
                    parity ^= 1
            if parity != int(code[parity_pos - 1]):
                syndrome |= parity_pos

        # Calculate overall parity
        for bit in code:
            if bit == '1':
                overall_parity ^= 1

        # Analyze syndrome and overall parity
        if syndrome == 0 and overall_parity == 0:
            return "Hata yok.", code, code[-1]
        elif syndrome != 0 and overall_parity == 1:
            # Single-bit error
            code_list = list(code)
            code_list[syndrome - 1] = '1' if code_list[syndrome - 1] == '0' else '0'
            return f"{syndrome}. bitten hata tespit edildi ve düzeltildi.", ''.join(code_list), code_list[-1]
        else:
            # Double-bit error or other
            return "Çift bit hatası tespit edildi, düzeltilemez.", code, code[-1]

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hamming SEC-DED Simülatörü")
        self.root.state('zoomed')  # Pencereyi maksimize edilmiş olarak aç
        self.root.configure(bg="#B3E5FC")  # Light blue background

        # Main frame
        main_frame = tk.Frame(self.root, bg="#B3E5FC")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Title
        tk.Label(
            main_frame,
            text="Hamming SEC-DED Simülatörü",
            font=("Arial", 24, "bold"),
            bg="#B3E5FC",
            fg="#0288D1"
        ).pack(pady=10)

        # Center panel
        center_frame = tk.Frame(main_frame, bg="#B3E5FC")
        center_frame.pack(fill="both", expand=True)

        # Input panel
        input_frame = tk.Frame(center_frame, bg="#B3E5FC")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        # Bit length selection
        tk.Label(
            input_frame,
            text="Bit Uzunluğu Seç:",
            font=("Arial", 12, "bold"),
            bg="#B3E5FC",
            fg="#37474F"
        ).grid(row=0, column=0, sticky="w", pady=5)
        self.bit_length_combo = ttk.Combobox(
            input_frame,
            values=["8 Bit", "16 Bit", "32 Bit"],
            font=("Arial", 12),
            state="readonly",
            width=10
        )
        self.bit_length_combo.grid(row=0, column=1, pady=5, sticky="w")
        self.bit_length_combo.current(0)
        self.bit_length_combo.bind("<<ComboboxSelected>>", self.update_error_positions)

        # Data input
        tk.Label(
            input_frame,
            text="Veri Girişi:",
            font=("Arial", 12, "bold"),
            bg="#B3E5FC",
            fg="#37474F"
        ).grid(row=1, column=0, sticky="w", pady=5)
        self.data_input = tk.Entry(input_frame, font=("Courier New", 12), width=32)
        self.data_input.grid(row=1, column=1, pady=5, sticky="w")
        self.data_input.bind("<KeyRelease>", self.restrict_input)

        # Error position
        tk.Label(
            input_frame,
            text="Hata Pozisyonu Seç:",
            font=("Arial", 12, "bold"),
            bg="#B3E5FC",
            fg="#37474F"
        ).grid(row=2, column=0, sticky="w", pady=5)
        self.error_pos_combo = ttk.Combobox(input_frame, font=("Arial", 12), state="readonly", width=10)
        self.error_pos_combo.grid(row=2, column=1, pady=5, sticky="w")

        # Buttons
        buttons = [
            ("Kodla", self.code_action),
            ("Rastgele Hata Oluştur", self.random_error_action),
            ("Seçili Bit'te Hata Oluştur", self.error_at_pos_action),
            ("Hata Tespit & Düzelt", self.check_error_action)
        ]
        for idx, (text, command) in enumerate(buttons):
            btn = tk.Button(
                input_frame,
                text=text,
                font=("Arial", 12, "bold"),
                bg="#26C6DA",
                fg="white",
                relief="flat",
                command=command,
                width=20 if idx % 2 == 0 else 22
            )
            btn.grid(row=3 + idx // 2, column=idx % 2, pady=5, padx=5)
            self.style_button(btn)

        # Output panel
        output_frame = tk.Frame(center_frame, bg="#B3E5FC")
        output_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")

        self.hamming_code_label = tk.Label(
            output_frame,
            text="Hamming Kodu: ",
            font=("Courier New", 14, "bold"),
            bg="#B3E5FC",
            fg="#37474F"
        )
        self.hamming_code_label.grid(row=0, column=0, sticky="w", pady=5)

        self.overall_parity_label = tk.Label(
            output_frame,
            text="Toplam Parity (p0): ",
            font=("Courier New", 14, "bold"),
            bg="#B3E5FC",
            fg="#37474F"
        )
        self.overall_parity_label.grid(row=1, column=0, sticky="w", pady=5)

        self.corrected_code_label = tk.Label(
            output_frame,
            text="Düzeltilmiş Kod: ",
            font=("Courier New", 14, "bold"),
            bg="#B3E5FC",
            fg="#37474F"
        )
        self.corrected_code_label.grid(row=2, column=0, sticky="w", pady=5)

        self.error_status_label = tk.Label(
            output_frame,
            text=" ",
            font=("Arial", 12, "bold"),
            bg="#B3E5FC",
            fg="#37474F"
        )
        self.error_status_label.grid(row=3, column=0, sticky="w", pady=5)

        self.bit_positions_label = tk.Label(
            output_frame,
            text="Bit Pozisyonları: []",
            font=("Courier New", 14, "bold"),
            bg="#B3E5FC",
            fg="#37474F",
            justify="left"
        )
        self.bit_positions_label.grid(row=4, column=0, sticky="w", pady=5)

        # Description panel
        description_container = tk.Frame(main_frame, bg="#B3E5FC")
        description_container.pack(fill="x", padx=10, pady=10)

        self.toggle_description_button = tk.Button(
            description_container,
            text="Uygulama Detayı İçin Tıklayın  ▼",
            font=("Arial", 12, "bold"),
            bg="#26C6DA",
            fg="white",
            relief="flat",
            command=self.toggle_description
        )
        self.toggle_description_button.pack()
        self.style_button(self.toggle_description_button)

        self.description_panel = tk.Frame(description_container, bg="#E3F2FD", borderwidth=2, relief="solid")
        description_text = (
            "Bu uygulama, Hamming SEC-DED (Single Error Correction - Double Error Detection) simülatörüdür. "
            "Kullanıcılar, 8, 16 veya 32 bitlik veri girişi yaparak Hamming kodu oluşturabilir, rastgele veya belirli bir pozisyonda hata ekleyebilir, "
            "ve bu hataları tespit edip düzeltebilir. SEC-DED, Hamming koduna eklenen bir genel parite biti ile tek bitlik hataları düzeltebilir ve "
            "çift bitlik hataları algılayabilir. Bu simülatör, veri iletişiminde hata tespiti ve düzeltme süreçlerini görselleştirmek için tasarlanmıştır."
        )
        tk.Label(
            self.description_panel,
            text=description_text,
            font=("Arial", 10),
            bg="#E3F2FD",
            fg="#37474F",
            wraplength=800,
            justify="left",
            padx=10,
            pady=10
        ).pack()
        self.description_visible = False

        # Initialize error positions
        self.update_error_positions()

    def style_button(self, button):
        """Apply hover effects to buttons."""
        def on_enter(e):
            button.config(bg="#00ACC1")
        def on_leave(e):
            button.config(bg="#26C6DA")
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def restrict_input(self, event):
        """Restrict input to binary and correct length."""
        bit_length = int(self.bit_length_combo.get().split()[0])
        current_text = self.data_input.get()
        # Remove non-binary characters
        filtered_text = ''.join(c for c in current_text if c in '01')
        if len(filtered_text) > bit_length:
            filtered_text = filtered_text[:bit_length]
        if filtered_text != current_text:
            self.data_input.delete(0, tk.END)
            self.data_input.insert(0, filtered_text)

    def show_error_message(self, message):
        """Show error message in a dialog."""
        messagebox.showerror("Hata", message, parent=self.root)

    def update_error_positions(self, event=None):
        """Update error position dropdown based on bit length."""
        bit_length = int(self.bit_length_combo.get().split()[0])
        self.data_input.delete(0, tk.END)
        self.data_input.focus_set()
        total_bits = HammingCode.get_total_length(bit_length)
        self.error_pos_combo['values'] = [''] + list(range(1, total_bits + 1))
        self.error_pos_combo.current(0)
        self.update_bit_positions(bit_length)

    def update_bit_positions(self, bit_length):
        """Update bit positions label."""
        total_bits = HammingCode.get_total_length(bit_length)
        positions = []
        data_index = 1
        for i in range(1, total_bits + 1):
            if HammingCode.is_power_of_two(i):
                positions.append(f"p{i}")
            elif i == total_bits:
                positions.append("p0")
            else:
                positions.append(f"d{data_index}")
                data_index += 1
        # Format with line breaks every 8 bits
        lines = []
        for i in range(0, len(positions), 8):
            lines.append(", ".join(positions[i:i+8]))
        positions_text = "Bit Pozisyonları:\n[" + "\n".join(lines) + "]"
        self.bit_positions_label.config(text=positions_text)

    def code_action(self):
        """Handle 'Kodla' button action."""
        data = self.data_input.get().strip()
        bit_length = int(self.bit_length_combo.get().split()[0])
        if not HammingCode.is_valid_binary(data, bit_length):
            self.show_error_message(f"Lütfen tam olarak {bit_length} bitlik 0/1 dizisi girin!")
            return
        hamming_code = HammingCode.calculate_hamming_code(data)
        self.hamming_code_label.config(text=f"Hamming Kodu: {hamming_code}")
        self.overall_parity_label.config(text=f"Toplam Parity (p0): {hamming_code[-1]}")
        self.corrected_code_label.config(text="Düzeltilmiş Kod: ")
        self.error_status_label.config(text="Kod oluşturuldu, hata yok.")
        self.update_bit_positions(bit_length)

    def random_error_action(self):
        """Handle 'Rastgele Hata Oluştur' button action."""
        code = self.hamming_code_label.cget("text").replace("Hamming Kodu: ", "")
        if not code:
            self.show_error_message("Önce kod oluşturun!")
            return
        result = HammingCode.introduce_random_error(code)
        code, pos = result.split(",")
        self.hamming_code_label.config(text=f"Hamming Kodu: {code}")
        self.error_status_label.config(text=f"{pos}. bitten rastgele hata oluşturuldu.")
        self.corrected_code_label.config(text="Düzeltilmiş Kod: ")

    def error_at_pos_action(self):
        """Handle 'Seçili Bit'te Hata Oluştur' button action."""
        code = self.hamming_code_label.cget("text").replace("Hamming Kodu: ", "")
        if not code:
            self.show_error_message("Önce kod oluşturun!")
            return
        pos = self.error_pos_combo.get()
        if not pos:
            self.show_error_message("Hata pozisyonu seçin!")
            return
        result = HammingCode.introduce_error_at_position(code, int(pos))
        code, pos = result.split(",")
        self.hamming_code_label.config(text=f"Hamming Kodu: {code}")
        self.error_status_label.config(text=f"{pos}. bitten hata oluşturuldu.")
        self.corrected_code_label.config(text="Düzeltilmiş Kod: ")

    def check_error_action(self):
        """Handle 'Hata Tespit & Düzelt' button action."""
        code = self.hamming_code_label.cget("text").replace("Hamming Kodu: ", "")
        if not code:
            self.show_error_message("Önce kod oluşturun!")
            return
        original_data = self.data_input.get().strip()
        status, corrected_code, overall_parity = HammingCode.detect_and_correct_error(code, original_data)
        self.error_status_label.config(text=status)
        self.corrected_code_label.config(text=f"Düzeltilmiş Kod: {corrected_code}")
        self.overall_parity_label.config(text=f"Toplam Parity (p0): {overall_parity}")

    def toggle_description(self):
        """Toggle description panel visibility."""
        self.description_visible = not self.description_visible
        if self.description_visible:
            self.description_panel.pack(fill="x", padx=10, pady=10)
            self.toggle_description_button.config(text="Uygulama Detayı İçin Tıklayın  ▲")
        else:
            self.description_panel.pack_forget()
            self.toggle_description_button.config(text="Uygulama Detayı İçin Tıklayın  ▼")

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()