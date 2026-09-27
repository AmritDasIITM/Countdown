import tkinter as tk
import customtkinter as ctk
from PIL import Image
from datetime import datetime

# --- Configuration ---
START_DATE = datetime(2026, 6, 6, 0, 0, 0) 
TARGET_DATE = datetime(2026, 12, 15, 0, 0, 0)
REFRESH_RATE_MS = 1000  

# Image Filenames
LOGO_FILE = "C:/Users/Amrit/Desktop/Projects/PG_Countdown/TI_logo.png"
DIE_FILE = "C:/Users/Amrit/Desktop/Projects/PG_Countdown/die.png"

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
        self.header_frame.grid_columnconfigure(1, weight=1, uniform="header_group") 
        self.header_frame.grid_columnconfigure(2, weight=1, uniform="header_group") 

        # Left: TI Logo
        try:
            pil_logo = Image.open(LOGO_FILE)
            logo_img = ctk.CTkImage(light_image=pil_logo, size=(200, 200)) 
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
            die_img = ctk.CTkImage(light_image=pil_die, size=(400, 240))
            self.die_label = ctk.CTkLabel(self.title_container, text="", image=die_img, fg_color="transparent")
        except Exception:
            self.die_label = ctk.CTkLabel(self.title_container, text="[ DIE ]", font=("Helvetica", 14, "bold"), text_color="#aaaaaa")
        self.die_label.pack(pady=(0, 25))

        self.title_label = ctk.CTkLabel(self.title_container, text="MCPE061 TAPE OUT", font=("Helvetica", 54, "bold"), text_color=COLOR_TEXT)
        self.title_label.pack()
        self.subtitle_label = ctk.CTkLabel(self.title_container, text="TARGET: DECEMBER 15, 2026", font=("Courier", 30, "bold"), text_color=COLOR_ACCENT)
        self.subtitle_label.pack(pady=(10, 0))

        # Right: Column 2 remains empty to balance the uniform layout grid

        # ==========================================
        # 2. CUSTOM TIMELINE & MILESTONES
        # ==========================================
        self.canvas_width = 1200
        self.canvas_height = 180 
        self.timeline_canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bg=COLOR_BG, highlightthickness=0)
        self.timeline_canvas.grid(row=1, column=0, pady=(10, 10))

        # ==========================================
        # 3. COUNTDOWN TIMER SECTION 
        # ==========================================
        self.timer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.timer_frame.grid(row=2, column=0, sticky="n", padx=60, pady=(20, 0)) 
        self.timer_frame.grid_columnconfigure((0, 1, 2, 3), weight=1) 

        self.digit_labels = {}
        self.blocks = []
        
        units = [("DAYS", 0), ("HOURS", 1), ("MINUTES", 2), ("SECONDS", 3)]
        
        for unit_name, column_index in units:
            block = ctk.CTkFrame(self.timer_frame, fg_color=COLOR_BOX_BG, corner_radius=12, height=200, width=300, border_width=4, border_color=COLOR_ACCENT)
            block.grid(row=0, column=column_index, padx=15)
            block.grid_propagate(False) 
            block.grid_columnconfigure(0, weight=1)
            block.grid_rowconfigure(0, weight=1) 
            block.grid_rowconfigure(1, weight=0) 
            self.blocks.append(block)

            digit_label = ctk.CTkLabel(block, text="00", font=("Courier", 90, "bold"), text_color=COLOR_ACCENT)
            digit_label.grid(row=0, column=0, sticky="s", pady=(0, 0))
            self.digit_labels[unit_name] = digit_label

            unit_label = ctk.CTkLabel(block, text=unit_name, font=("Helvetica", 16, "bold"), text_color="#aaaaaa")
            unit_label.grid(row=1, column=0, sticky="n", pady=(0, 30))

        # ==========================================
        # 4. STATUS FOOTER 
        # ==========================================
        self.status_label = ctk.CTkLabel(self, text="PROJECT IN MOTION...", font=("Courier", 28, "bold"), text_color="#555555")
        self.status_label.grid(row=3, column=0, sticky="n", pady=(20, 0))

        self.bind("<Escape>", lambda e: self.quit_app())
        self.update_timer()

    def draw_timeline(self, now, is_negative, current_accent):
        self.timeline_canvas.delete("all")
        pad_x = 80
        line_w = self.canvas_width - 2 * pad_x
        line_y = 90 

        self.timeline_canvas.create_line(pad_x, line_y, pad_x + line_w, line_y, fill=COLOR_BOX_BG, width=12, capstyle=tk.ROUND)

        total_sec = (TARGET_DATE - START_DATE).total_seconds()
        if is_negative:
            progress = 1.0
        else:
            elapsed = (now - START_DATE).total_seconds()
            progress = max(0.0, min(1.0, elapsed / total_sec))

        fill_w = line_w * progress
        if progress > 0:
            self.timeline_canvas.create_line(pad_x, line_y, pad_x + fill_w, line_y, fill=current_accent, width=12, capstyle=tk.ROUND)

        milestones = [
            ("2025", START_DATE, -40),
            ("RTL Freeze\n(Oct 15)", datetime(2026, 10, 15, 0, 0, 0), -45),
            ("Base PG\n(Nov 15)", datetime(2026, 11, 15, 0, 0, 0), 45), 
            ("Final Tapeout\n(Dec 15)", TARGET_DATE, -45)
        ]

        for i, (name, m_date, offset) in enumerate(milestones):
            m_elapsed = (m_date - START_DATE).total_seconds()
            m_pct = max(0.0, min(1.0, m_elapsed / total_sec))
            x = pad_x + (line_w * m_pct)
            
            pole_color = current_accent if progress >= m_pct else "#555555"
            
            pole_end_y = line_y - 20 if offset < 0 else line_y + 20
            self.timeline_canvas.create_line(x, line_y, x, pole_end_y, fill=pole_color, width=4)
            
            y_pos = line_y + offset
            self.timeline_canvas.create_text(x, y_pos, text=name, fill="#ffffff", font=("Helvetica", 11, "bold"), justify="center")

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

        self.draw_timeline(now, is_negative, current_accent)

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