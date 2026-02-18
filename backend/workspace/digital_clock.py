
import tkinter as tk
from tkinter import font
from datetime import datetime
from config import ClockConfig

class DigitalClock:
    def __init__(self):
        self.root = tk.Tk()
        self.clock_label = None
        self.setup_window()
        self.setup_styling()
        self.update_time()
        
    def setup_window(self):
        """Window basic settings"""
        self.root.title("Digital Clock")
        
        # Use config for geometry
        geom = f"{ClockConfig.WINDOW_WIDTH}x{ClockConfig.WINDOW_HEIGHT}+{ClockConfig.DEFAULT_X}+{ClockConfig.DEFAULT_Y}"
        self.root.geometry(geom)
        self.root.configure(bg=ClockConfig.WINDOW_BG_COLOR)
        
        # Always show window on top
        self.root.attributes('-topmost', True)
        
        # Window transparency
        self.root.attributes('-alpha', ClockConfig.WINDOW_ALPHA)
        
        # Hide window border
        self.root.overrideredirect(True)
        
        # Enable mouse dragging
        self.root.bind('<Button-1>', self.start_drag)
        self.root.bind('<B1-Motion>', self.drag_window)
        
    def setup_styling(self):
        """Styling settings"""
        # Modern font settings
        self.clock_font = font.Font(
            family=ClockConfig.FONT_FAMILY,
            size=ClockConfig.FONT_SIZE,
            weight=ClockConfig.FONT_WEIGHT
        )
        
        # Create label
        self.clock_label = tk.Label(
            self.root,
            text="",
            font=self.clock_font,
            fg=ClockConfig.TEXT_COLOR,
            bg=ClockConfig.WINDOW_BG_COLOR,
            relief='flat'
        )
        # Fix: Previously mixed pack() and place() causing freeze. Use only place().
        
        # Center label placement
        self.clock_label.place(relx=0.5, rely=0.5, anchor='center')
        
    def update_time(self):
        """Time update"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.clock_label.config(text=current_time)
        
        # Update interval from config
        self.root.after(ClockConfig.UPDATE_INTERVAL, self.update_time)
        
    def start_drag(self, event):
        """Save coordinates when dragging starts"""
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
    def drag_window(self, event):
        """Window drag movement"""
        x = self.root.winfo_x() + event.x - self.drag_start_x
        y = self.root.winfo_y() + event.y - self.drag_start_y
        self.root.geometry(f"+{x}+{y}")
        
    def run(self):
        """Application execution"""
        self.root.mainloop()

if __name__ == "__main__":
    clock = DigitalClock()
    clock.run()