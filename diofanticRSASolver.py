
import tkinter as tk
from tkinter import messagebox

# =====================================================================
#  BEREGNINGSKJERNE (RSA & EUKLID FRA BUNNEN AV)
# =====================================================================

def format_linear_comb(coeffs):
    """Formatterer en sammentrukket lineærkombinasjon ryddig."""
    items = list(coeffs.items())
    first_num, first_mult = items[0]
    out = f"({first_mult}) × {first_num}"
    
    for num, mult in items[1:]:
        sign = "+" if mult >= 0 else "-"
        out += f" {sign} ({abs(mult)}) × {num}"
    return out


def solve_rsa_steps(p: int, q: int, e: int):
    steps = []
    steps.append(("TITLE", f"RSA KEY GENERATION:  p = {p},   q = {q},   e = {e}"))

    # Steg 1: Modulus og φ(n)
    n = p * q
    phi = (p - 1) * (q - 1)
    
    steps.append(("HEADER", "Step 1: Compute Modulus n and Totient φ(n)"))
    steps.append(("MATH", f"n = p × q = {p} × {q} = {n}"))
    steps.append(("MATH", f"φ(n) = (p - 1) × (q - 1) = ({p} - 1) × ({q} - 1) = {p - 1} × {q - 1} = {phi}"))
    steps.append(("TEXT", f"Find private key d such that:  {e} × d ≡ 1 (mod {phi})"))
    steps.append(("TEXT", f"Equivalent to Bézout's identity:  {e}·d + {phi}·k = gcd({phi}, {e})"))

    # Steg 2: Euklids divisjonskjede
    steps.append(("HEADER", "Step 2: Euclidean Algorithm (Forward Division)"))
    steps.append(("TEXT", f"Successive divisions between φ(n) = {phi} and e = {e}:"))
    
    r0, r1 = phi, e
    divisions = []
    
    while r1 != 0:
        quot = r0 // r1
        rem = r0 % r1
        divisions.append((r0, r1, quot, rem))
        steps.append(("MATH", f"{r0:>6}  =  ({quot:>3}) × {r1:<6}  +  {rem}"))
        r0, r1 = r1, rem

    g = r0
    steps.append(("MATH_ACCENT", f"=> gcd({phi}, {e}) = {g}"))

    if g != 1:
        steps.append(("ALERT", f"gcd({phi}, {e}) = {g} ≠ 1. Exponent e has no modular inverse!"))
        steps.append(("BOX", ["NO VALID PRIVATE KEY d EXISTS"]))
        return steps

    # Steg 3: Tilbakesubstitusjon med eksplisitte parenteser
    steps.append(("HEADER", "Step 3: Extended Euclidean Algorithm (Back-Substitution)"))
    steps.append(("TEXT", f"Express remainder 1 as a linear combination of {phi} and {e}:"))

    rem_table = {}
    for dividend, divisor, quot, rem in divisions[:-1]:
        rem_table[rem] = (dividend, divisor, quot)

    # Start fra linjen med rest = 1
    last_div, last_divis, last_q = rem_table[1]
    steps.append(("MATH", f"1 = {last_div} - ({last_q}) × {last_divis}"))

    coeffs = {last_div: 1, last_divis: -last_q}

    for dividend, divisor, quot, rem in reversed(divisions[:-2]):
        if rem in coeffs and rem in rem_table:
            mult = coeffs.pop(rem)
            sub_div, sub_divis, sub_q = rem_table[rem]
            
            # Viser innsettingsleddet i parentes: mult × (dividend - quot × divisor)
            parenthesised_sub = f"({sub_div} - ({sub_q}) × {sub_divis})"
            
            other_terms = []
            for k, v in coeffs.items():
                other_terms.append(f"({v}) × {k}")
            other_str = (" + " + " + ".join(other_terms)) if other_terms else ""
            
            steps.append(("SUBTEXT", f"Substitute remainder {rem} = {parenthesised_sub}:"))
            steps.append(("MATH", f"1 = ({mult}) × {parenthesised_sub}{other_str}"))
            
            # Multipliser ut og samle koeffisienter
            coeffs[sub_div] = coeffs.get(sub_div, 0) + mult
            coeffs[sub_divis] = coeffs.get(sub_divis, 0) - mult * sub_q
            
            steps.append(("MATH", f"1 = {format_linear_comb(coeffs)}"))

    d_raw = coeffs.get(e, 0)
    k_val = coeffs.get(phi, 0)

    steps.append(("MATH_ACCENT", f"=> Bézout Identity:  ({d_raw}) × {e} + ({k_val}) × {phi} = 1"))

    # Steg 4: Modulær reduksjon
    steps.append(("HEADER", "Step 4: Reduce Private Exponent d modulo φ(n)"))
    steps.append(("MATH", f"d ≡ {d_raw} (mod {phi})"))

    d_final = d_raw % phi
    if d_raw < 0:
        steps.append(("MATH", f"Since d must be positive: d = {d_raw} + {phi} = {d_final}"))
    else:
        steps.append(("MATH", f"d = {d_final}"))

    verification = (e * d_final) % phi
    steps.append(("TEXT", f"Verification: ({e} × {d_final}) mod {phi} = {e * d_final} mod {phi} = {verification}"))

    box_lines = [
        f"  Public Key (e, n)  = ({e}, {n})",
        f"  Private Key (d, n) = ({d_final}, {n})",
        f"  Value of d         = {d_final}"
    ]
    steps.append(("BOX", box_lines))
    return steps


# =====================================================================
# 2. GUI MED ETT FELT PER VARIABEL
# =====================================================================

class RSAPencilApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RSA Key Generator — Extended Euclidean Step-by-Step")
        self.root.geometry("1060x900")
        self.root.configure(bg="#ded8cd")

        ctrl = tk.LabelFrame(root, text="Input Parameters", font=("Segoe UI", 11, "bold"),
                             bg="#eae5db", fg="#1f2421", padx=16, pady=10, relief="groove", bd=2)
        ctrl.pack(fill="x", padx=14, pady=10)

        # Rad for p
        row_p = tk.Frame(ctrl, bg="#eae5db")
        row_p.pack(fill="x", pady=2)
        tk.Label(row_p, text="Prime p:", font=("Segoe UI", 11, "bold"), width=12, anchor="w",
                 bg="#eae5db", fg="#1f2421").pack(side="left")
        self.entry_p = tk.Entry(row_p, font=("Consolas", 12), width=18, relief="solid", bd=1)
        self.entry_p.insert(0, "17")
        self.entry_p.pack(side="left")
        self.entry_p.bind("<Return>", lambda e: self.on_solve())

        # Rad for q
        row_q = tk.Frame(ctrl, bg="#eae5db")
        row_q.pack(fill="x", pady=2)
        tk.Label(row_q, text="Prime q:", font=("Segoe UI", 11, "bold"), width=12, anchor="w",
                 bg="#eae5db", fg="#1f2421").pack(side="left")
        self.entry_q = tk.Entry(row_q, font=("Consolas", 12), width=18, relief="solid", bd=1)
        self.entry_q.insert(0, "23")
        self.entry_q.pack(side="left")
        self.entry_q.bind("<Return>", lambda e: self.on_solve())

        # Rad for e + Calculate-knapp
        row_e = tk.Frame(ctrl, bg="#eae5db")
        row_e.pack(fill="x", pady=2)
        tk.Label(row_e, text="Exponent e:", font=("Segoe UI", 11, "bold"), width=12, anchor="w",
                 bg="#eae5db", fg="#1f2421").pack(side="left")
        self.entry_e = tk.Entry(row_e, font=("Consolas", 12), width=18, relief="solid", bd=1)
        self.entry_e.insert(0, "45")
        self.entry_e.pack(side="left")
        self.entry_e.bind("<Return>", lambda e: self.on_solve())

        btn = tk.Button(row_e, text="Calculate", font=("Segoe UI", 10, "bold"),
                        bg="#2e383f", fg="#ffffff", activebackground="#45535c",
                        activeforeground="#ffffff", relief="flat", padx=18, pady=3,
                        cursor="hand2", command=self.on_solve)
        btn.pack(side="left", padx=18)

        # Lerret med rullefelt
        canvas_frame = tk.Frame(root, bg="#ded8cd")
        canvas_frame.pack(fill="both", expand=True, padx=14, pady=(0, 12))

        self.v_scroll = tk.Scrollbar(canvas_frame, orient="vertical")
        self.v_scroll.pack(side="right", fill="y")

        self.canvas = tk.Canvas(canvas_frame, bg="#faf8f2", yscrollcommand=self.v_scroll.set, bd=0, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.v_scroll.config(command=self.canvas.yview)

        self.canvas.bind_all("<MouseWheel>", lambda event: self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

        self.on_solve()

    def draw_grid(self, width, height):
        grid_size = 28
        for y in range(0, height, grid_size):
            self.canvas.create_line(0, y, width, y, fill="#ece8dc", width=1)
        for x in range(0, width, grid_size):
            self.canvas.create_line(x, 0, x, height, fill="#f2efe4", width=1)
        margin_x = 80
        self.canvas.create_line(margin_x, 0, margin_x, height, fill="#e5bebe", width=2)

    def on_solve(self):
        self.canvas.delete("all")

        try:
            p = int(self.entry_p.get().strip())
            q = int(self.entry_q.get().strip())
            e = int(self.entry_e.get().strip())
            if p <= 1 or q <= 1 or e <= 1:
                raise ValueError("Verdiene for p, q og e må være større enn 1.")
        except ValueError as err:
            messagebox.showerror("Feil i input", f"Ugyldige heltallsverdier:\n{err}")
            return

        steps = solve_rsa_steps(p, q, e)

        width = 1150
        start_x = 105
        cur_y = 45

        c_title = "#111618"
        c_header = "#1a252c"
        c_text = "#434d53"
        c_subtext = "#59666e"
        c_math = "#0d1418"
        c_accent = "#1b4332"
        c_box_border = "#243238"

        f_title = ("Segoe UI", 14, "bold")
        f_header = ("Segoe UI", 12, "bold")
        f_text = ("Segoe UI", 11)
        f_subtext = ("Segoe UI", 10, "italic")
        f_math = ("Consolas", 12, "bold")
        f_accent = ("Consolas", 12, "bold")
        f_box = ("Consolas", 13, "bold")

        for item in steps:
            stype, val = item[0], item[1]

            if stype == "TITLE":
                self.canvas.create_text(start_x, cur_y, text=val, font=f_title, fill=c_title, anchor="w")
                cur_y += 24
                self.canvas.create_line(start_x, cur_y, start_x + 650, cur_y, fill="#2b363c", width=2)
                cur_y += 35

            elif stype == "HEADER":
                cur_y += 18
                self.canvas.create_text(start_x, cur_y, text=val, font=f_header, fill=c_header, anchor="w")
                cur_y += 20
                self.canvas.create_line(start_x, cur_y, start_x + 480, cur_y, fill="#8a969e", width=1.5)
                cur_y += 26

            elif stype == "TEXT":
                self.canvas.create_text(start_x + 10, cur_y, text=val, font=f_text, fill=c_text, anchor="w")
                cur_y += 28

            elif stype == "SUBTEXT":
                cur_y += 4
                self.canvas.create_text(start_x + 15, cur_y, text=val, font=f_subtext, fill=c_subtext, anchor="w")
                cur_y += 24

            elif stype == "MATH":
                self.canvas.create_text(start_x + 30, cur_y, text=val, font=f_math, fill=c_math, anchor="w")
                cur_y += 30

            elif stype == "MATH_ACCENT":
                self.canvas.create_text(start_x + 30, cur_y, text=val, font=f_accent, fill=c_accent, anchor="w")
                cur_y += 32

            elif stype == "ALERT":
                self.canvas.create_text(start_x + 30, cur_y, text=f"• {val}", font=f_math, fill="#a4161a", anchor="w")
                cur_y += 32

            elif stype == "BOX":
                cur_y += 15
                lines = val if isinstance(val, list) else [val]
                box_w = 480
                line_spacing = 30
                box_h = len(lines) * line_spacing + 24
                
                bx1, by1 = start_x + 20, cur_y
                bx2, by2 = bx1 + box_w, by1 + box_h
                
                self.canvas.create_rectangle(bx1, by1, bx2, by2, outline=c_box_border, width=2, fill="#f4efe4")

                txt_y = by1 + 22
                for line in lines:
                    self.canvas.create_text(bx1 + 20, txt_y, text=line, font=f_box, fill="#11181c", anchor="w")
                    txt_y += line_spacing
                cur_y += box_h + 30

        total_h = max(cur_y + 80, 850)
        self.draw_grid(width, total_h)
        self.canvas.tag_lower("all")
        self.canvas.config(scrollregion=(0, 0, width, total_h))


if __name__ == "__main__":
    root = tk.Tk()
    app = RSAPencilApp(root)
    root.mainloop()
