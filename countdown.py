import tkinter as tk
import customtkinter as ctk
from PIL import Image
from datetime import datetime
import os

# --- Configuration ---
START_DATE = datetime(2026, 6, 6, 0, 0, 0) 
TARGET_DATE = datetime(2026, 12, 15, 0, 0, 0)
REFRESH_RATE_MS = 1000  

# Image Filenames
pwd = os.path.dirname(os.path.abspath(__file__))
LOGO_FILE = os.path.join(pwd, "TI_logo.png")
DIE_FILE = os.path.join(pwd, "die.png")

# Color Palette
COLOR_BG = "#0b0c10"      
COLOR_TEXT = "#ffffff"    
COLOR_ACCENT = "#ff0033"
COLOR_ACCENT_DIM = "#80001a" 
COLOR_BOX_BG = "#1f2833"  
COLOR_SUCCESS = "#45a247" 

class CountdownApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MCP0E61 Tape Out Dashboard")
        self.geometry("1400x850")
        self.configure(fg_color=COLOR_BG)
        self.pulse_state = True 
        self.attributes('-fullscreen', True)  # Start in fullscreen mode
        self.bind('<Escape>', lambda event: self.destroy())  # Exit fullscreen on Escape
        
        # --- Grid Layout ---
        self.grid_rowconfigure(0, weight=1) # Header
        self.grid_rowconfigure(1, weight=1) # Timeline Canvas
        self.grid_rowconfigure(2, weight=2) # Timers 
        self.grid_rowconfigure(3, weight=1) # Footer
        self.grid_columnconfigure(0, weight=1)

        # ==========================================
        # 1. HEADER SECTION 
        # ==========================================
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=(10, 0))
        
        # The 'uniform' attribute forces all 3 columns to be exactly the same width
        self.header_frame.grid_columnconfigure(0, weight=1, uniform="header_group") 
        self.header_frame.grid_columnconfigure(1, weight=2, uniform="header_group") 
        self.header_frame.grid_columnconfigure(2, weight=1, uniform="header_group") 

        # Left: TI Logo
        try:
            pil_logo = Image.open(LOGO_FILE)
            logo_img = ctk.CTkImage(light_image=pil_logo, size=(250, 250)) 
            self.logo_label = ctk.CTkLabel(self.header_frame, text="", image=logo_img, fg_color="transparent")
        except Exception:
            self.logo_label = ctk.CTkLabel(self.header_frame, text="[ LOGO ]", font=("Helvetica", 18, "bold"), text_color="#aaaaaa")
        
        # Removing sticky="w" to allow the logo to center in its uniformly sized column for an equibordered look
        self.logo_label.grid(row=0, column=0) 

        # Center: Die Image, Title & Subtitle
        self.title_container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        # Added pady to shift the heading block lower
        self.title_container.grid(row=0, column=1, pady=(30, 0))
        
        # Die Image (Moved from column 2 to the top of the title container)
        try:
            pil_die = Image.open(DIE_FILE)
            die_img = ctk.CTkImage(light_image=pil_die, size=(500, 300))
            self.die_label = ctk.CTkLabel(self.title_container, text="", image=die_img, fg_color="transparent")
        except Exception:
            self.die_label = ctk.CTkLabel(self.title_container, text="[ DIE ]", font=("Helvetica", 14, "bold"), text_color="#aaaaaa")
        self.die_label.pack(pady=(0, 25))

        self.title_label = ctk.CTkLabel(self.title_container, text="MCPE061 PG", font=("Helvetica", 130, "bold"), text_color=COLOR_TEXT)
        self.title_label.pack()
        self.subtitle_label = ctk.CTkLabel(self.title_container, text="TARGET: 15 DEC 2026", font=("Courier", 80, "bold"), text_color=COLOR_ACCENT)
        self.subtitle_label.pack(pady=(10, 0))

        # Right: Column 2 remains empty to balance the uniform layout grid

        # ==========================================
        # 2. COUNTDOWN TIMER SECTION 
        # ==========================================
        self.timer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.timer_frame.grid(row=2, column=0, sticky="nsew", padx=60, pady=(20, 40)) 
        self.timer_frame.grid_columnconfigure((0, 1, 2, 3), weight=1) 
        self.timer_frame.grid_rowconfigure(0, weight=1)

        self.digit_labels = {}
        self.blocks = []
        
        units = [("DAYS", 0), ("HOURS", 1), ("MINUTES", 2), ("SECONDS", 3)]
        
        for unit_name, column_index in units:
            block = ctk.CTkFrame(self.timer_frame, fg_color=COLOR_BOX_BG, corner_radius=12, border_width=4, border_color=COLOR_ACCENT)
            block.grid(row=0, column=column_index, padx=15, sticky="nsew")
            block.grid_columnconfigure(0, weight=1)
            block.grid_rowconfigure(0, weight=1) 
            block.grid_rowconfigure(1, weight=1) 
            self.blocks.append(block)

            digit_label = ctk.CTkLabel(block, text="00", font=("Courier", 300, "bold"), text_color=COLOR_ACCENT)
            digit_label.grid(row=0, column=0, sticky="s", pady=(20, 0))
            self.digit_labels[unit_name] = digit_label

            unit_label = ctk.CTkLabel(block, text=unit_name, font=("Helvetica", 60, "bold"), text_color="#aaaaaa")
            unit_label.grid(row=1, column=0, sticky="n", pady=(0, 20))

        self.bind("<Escape>", lambda e: self.quit_app())
        self.update_timer()

    def update_timer(self):
        now = datetime.now()

        if now >= TARGET_DATE:
            diff = now - TARGET_DATE
            is_negative = True
            self.status_label.configure(text="TAPE OUT DATE SURPASSED - NEGATIVE COUNTDOWN ACTIVE", text_color=COLOR_SUCCESS)
            current_accent = COLOR_SUCCESS
        else:
            diff = TARGET_DATE - now
            is_negative = False
            current_accent = COLOR_ACCENT

        total_seconds = int(diff.total_seconds())
        days = diff.days
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        def format_val(val, pad=2):
            if is_negative:
                return f"-{abs(val):0{pad}d}"
            return f"{val:0{pad}d}"

        self.digit_labels["DAYS"].configure(text=format_val(days), text_color=current_accent)
        self.digit_labels["HOURS"].configure(text=format_val(hours), text_color=current_accent)
        self.digit_labels["MINUTES"].configure(text=format_val(minutes), text_color=current_accent)
        self.digit_labels["SECONDS"].configure(text=format_val(seconds), text_color=current_accent)

        self.pulse_state = not self.pulse_state
        border_color = current_accent if self.pulse_state else COLOR_ACCENT_DIM
        if is_negative:
            border_color = current_accent 
            
        for block in self.blocks:
            block.configure(border_color=border_color)

        self.after(REFRESH_RATE_MS, self.update_timer)

    def quit_app(self):
        self.destroy()

if __name__ == "__main__":
    app = CountdownApp()
    app.mainloop()