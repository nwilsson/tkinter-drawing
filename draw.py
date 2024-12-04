import tkinter
from tkinter import ttk, colorchooser, simpledialog, messagebox
import sv_ttk
import time
from PIL import ImageGrab, Image, ImageTk
import base64
from io import BytesIO

class DrawingApplication:
    def __init__(self, window):
        # Set up main window
        self.window = window
        self.window.state('zoomed')
        self.window.title("Drawing Application")

        # Configure window resizing
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        # Create main frame to hold all widgets
        self.main_frame = tkinter.Frame(window)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Configure resizing behavior for main frame
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

        # Create frame for buttons
        self.button_frame = tkinter.Frame(self.main_frame)
        self.button_frame.grid(row=0, column=0, sticky="ns", padx=5)

        # Initialize drawing variables
        self.last_x, self.last_y = None, None
        self.drawing = False
        self.line_colour = "black"
        self.line_width = 2

        self.draw_type = "line"
        self.current_line = None

        self.temp_lines = []  # To store temporary line segments for combining
        self.combined_lines = []  # To store the combined lines

        self.undo_stack = []  # Stack to store actions for undo functionality
        self.redo_stack = []  # Stack to store actions for redo functionality

        # Load icons from base64
        self.undo_icon = self.load_icon(self.undo_icon_base64())
        self.redo_icon = self.load_icon(self.redo_icon_base64())

        # Create buttons and widgets for UI
        self.create_widgets()

        # Set initial theme to dark
        sv_ttk.set_theme("dark")

        # Create the drawing canvas
        self.canvas = tkinter.Canvas(self.main_frame, bg="white")
        self.canvas.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Configure resizing behavior for canvas
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

        # Bind mouse events for drawing
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)
        self.canvas.bind("<B1-Motion>", self.draw)

        # Bind keyboard shortcuts for quick actions
        self.window.bind("<Control-z>", lambda event: self.undo())
        self.window.bind("<Control-y>", lambda event: self.redo())
        self.window.bind("<Control-s>", lambda event: self.capture_window())
        self.window.bind("<Delete>", lambda event: self.reset())
        self.window.bind("<Control-t>", lambda event: self.toggle_theme())
        self.window.bind("f", lambda event: self.set_draw_type("rectangle"))
        self.window.bind("g", lambda event: self.set_draw_type("oval"))
        self.window.bind("h", lambda event: self.set_draw_type("line"))

    def load_icon(self, base64_string):
        icon_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(icon_data))
        image = image.resize((24, 24), Image.LANCZOS)
        return ImageTk.PhotoImage(image)

    def undo_icon_base64(self):
        return """
iVBORw0KGgoAAAANSUhEUgAAAGAAAABgCAYAAADimHc4AAAAAXNSR0IArs4c6QAABBNJREFUeF7tnFt62jAQRke0C0lWkmQjBUIfvIsku/BDSU03UrKSuvsouBHFrUsIGluaGV9+fx8vQZbsczwj6xIc4TAl4ExbR+MEAcYPAQRAgDEB4+YRARBgTMC4eUQABBgTMG4eEQABxgSMm0cEQIAxAePmEQEQYEzAuHlEAAT8IzBfZV+rispvz/mTMRe15nsTAR4+ES38nVcVPU5FQi8ENOHXj95UJJgLOAd/ShJMBVyCPxUJZgI48GsJrqJl8ZwXaj2jYkMmAtrAJ6LtZp3fKTJRbUpdAOD/71dVAOC/DS41AYB/PrOpCAD897sVcQGAf7lPFxUA+OEXKjEBgB+G70uICAB8HnwRAYDPh59cQEv47a40rnT5OtXtP/4o/ZrDbEYv9IvKosjrv8e10PHsZCmox/BDaLauog3taWshI4mAAcNvyjERES1gJPDfiNCafY0W8Ok+e3COHkNxPrTv/YrcbE8b6bQULcCDHasEPxXudrSUlJBEwMglkNvRtZSEZAIgoVuSTSqgrQStPLtYZFf0ka789e33dOMc3b6mF/9pc5RuR3epIyG5gL5KOCW9+JzdVhXNjyIOchhHcgkiAoYiwV+nj47qAz3Um8JCElLvVxITMCQJjWv1O/OC0ZCyUxYVMDQJx7Tkt0iGJCTbqSEuYKwSUu1VUhEwNAnMgWWxWefLUJ8R+l5NwNAkzFfZj1AqStEXqAoYkoRjf/D90hPsHN0VX/Jt6Cm/WEfMyV3PZYb4oXqtwdq5ewlFQYpXUvUIqG+0jYQUT1qXh4VxjdH9gJkAbjpK9bbRRQAjDUW/jpoKCEmwhN8YJfvO+L2j3Kzz6y5y63PMBbwnwRp+DWi+yqpLgDfrPIph1Mkx5k/PbebbvsA/zhONPwKaHfOM6KfWemzoAZqcgBAQ7e8n0QlrQ23T3uhfQ9vAsCg76oGYBdA2bTLyP6UYIPbmLagNHI2y81Xm54EurRtHjwH8fUDAGZuM3J/s9ywg4EQA483ncEaqsQoENARw4fst7rFTEL2aitDI6aE2FvfZonLk14ODR4qFGAhoYGZ0uH9Lp1gDaBqedArqsLU+WeqZXAQctifO6LZydNNyN1zNqnSOlrFLkKf5TT0CQtO7wQRsVCDFoOvcpUMAQ6gUfJOB2MAiQCTtmHbCAxIQvd7LCC79qYgBCBB/6hEB5x/N0lX0pL0ah06YqHAVvWiDNxsHGKag+ucK/vxUgcK/oPayD+Bc1JTKqKegKcHl3CsEcCgJloEAQbicqiGAQ0mwDAQIwuVUDQEcSoJlIEAQLqdqCOBQEiwDAYJwOVVDAIeSYBkIEITLqRoCOJQEy0CAIFxO1RDAoSRYBgIE4XKqhgAOJcEyECAIl1M1BHAoCZaBAEG4nKp/A9ERBn/YBuE4AAAAAElFTkSuQmCC
"""

    def redo_icon_base64(self):
        return """
iVBORw0KGgoAAAANSUhEUgAAAGAAAABgCAYAAADimHc4AAAAAXNSR0IArs4c6QAAA91JREFUeF7tnG9y2jAQxVf0IE1OEnKR4oR88C2S3MIfSgq9SMlJQu9RUCvXZgwBW6C131paz2QmTLBXer99a/2xY0gPqAIGGl2DkwIAJ4ECUABgBcDh1QEKAKwAOLw6QAGAFQCHVwcoALAC4PDqAAUAVgAcXh2gAMAKgMOrAxTAcArM5vkPa2nz8614HS5qe6RkHODEJ6LMyWEtvUiBkASApvh1PkqBED2AU+JLghA1gDbxpUCIFkD2mGfWkKv7nQeyHEULwKnu4wC0E6IGMAYI0QOQDiEJAJIhJANAKoSkAEiEkBwAaRCSBCAJQrIApEBIGoAECCIAuGWDHdFXY+iGaP/j9HGfRR3cyxYwANVazR0RTSUK3UadE8LgACrhn8cm+jEQLgiDAcie8qm15eqkuLJybY3jgDAIgNk8/1WVmmv7KvI8Y+lh+VYsQxrXK4Asy2/slzLrXZ2P6uAQ3wnSG4Cq5LjMj+7gEr83AFXmf0SnvMtYhrLT1IXdAQHil7XUWHqnHa3d78tlsekb4iX3J27x2R1wZc1fmi29DiH2MUy0+OwAvj3mz8bQi2fWrs2WHhDCV0sQ3iOzPjK/1oitBF1Seoyh++X3oiwziENC5rMD8O2Uin+YciwO8M1+Ff+z31kA+NR+jml7SLnydWg1Egue4fq2lQXAbJ7bjoCb1aK49W0U9/ekis8yCvIpP2ZLt6mPds4lVbADPMoPLPslZz7bKKjr+UtU7b/k4dw+x/ld5TTYAV1Zhhz5eLiTfW2nS/Djv3MAcItuZzdZkPXfdbYNAjLzOUtQ6whotSiCIV+aVcffPwVBgvgso6DZPBftgBpGE4IU8ZMCUJejCdHv0G3EUEc2zw8uD5JvwpxC9XUtDgD7929PNRI1DO1LMO7r9g7g34b8erUo7rkbHsv1ggH4bL6jh6KSYQUDcJ3rGgmpC86nABeA1vuAC6/3gtMQWAD4rrtoKfoMgQWAZxkqoyuEQwhsAKp9AfekQefDt5JmougbNBuAroWvEx2FPQ+EFp11Jty82CUuaJyXNAhWBzhRr4TgTl1bS+vJhN7pD5WPJKK2MYd0CDuAQAhD9v1krKGXz3sBUEIY6Rsx0QAYK4SoANQe79q4h9edRgOiBFC64f+/EBP/dmS0AOokkw4iegBHIGZHb8bDq1EyAA4mcE/5dLejO2P2b1PWyxmdyxrcxJIEwC3imK7X2zxgTCIg26oAkOr3+aI2uF+jCa8OAKNSAAoArAA4vDpAAYAVAIdXBygAsALg8OoABQBWABxeHaAAwAqAw6sDFABYAXB4dYACACsADq8OAAP4C4v28HBH0/Z1AAAAAElFTkSuQmCC
"""

    def colour_change(self):
        color_code = colorchooser.askcolor(title="Choose line color")[1]
        if color_code:
            self.line_colour = color_code

    def line_change(self, width):
        self.line_width = int(float(width))

    def reset(self):
        askreset = messagebox.askyesno('Confirm', 'Confirm reset?')
        if askreset:
            self.canvas.delete("all")
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.temp_lines.clear()
            self.combined_lines.clear()

    def set_draw_type(self, shape):
        self.draw_type = shape

    def start_draw(self, event):
        self.drawing = True
        if 0 <= event.x <= self.canvas.winfo_width() and 0 <= event.y <= self.canvas.winfo_height():
            self.last_x, self.last_y = event.x, event.y
            self.current_line = [(self.last_x, self.last_y)]

    def stop_draw(self, event):
        self.drawing = False
        if self.current_line:
            self.temp_lines.append(self.current_line)
            if len(self.temp_lines) > 5:
                self.combine_lines()

    def draw(self, event):
        if self.drawing:
            if 0 <= event.x <= self.canvas.winfo_width() and 0 <= event.y <= self.canvas.winfo_height():
                x, y = event.x, event.y
                if self.draw_type == "line":
                    line_id = self.canvas.create_line((self.last_x, self.last_y, x, y), fill=self.line_colour, width=self.line_width, tag="line")
                    self.current_line.append((x, y))
                    self.undo_stack.append((line_id, self.last_x, self.last_y, x, y, self.line_colour, self.line_width))
                elif self.draw_type == "rectangle":
                    rect_id = self.canvas.create_rectangle(self.last_x, self.last_y, x, y, outline=self.line_colour, width=self.line_width)
                    self.undo_stack.append((rect_id, self.last_x, self.last_y, x, y, self.line_colour, self.line_width, "rectangle"))
                elif self.draw_type == "oval":
                    oval_id = self.canvas.create_oval(self.last_x, self.last_y, x, y, outline=self.line_colour, width=self.line_width)
                    self.undo_stack.append((oval_id, self.last_x, self.last_y, x, y, self.line_colour, self.line_width, "oval"))
                elif self.draw_type == "text":
                    text = simpledialog.askstring("Input", "Enter text:")
                    if text:
                        text_id = self.canvas.create_text(x, y, text=text, fill=self.line_colour, font=("Arial", self.line_width + 10))
                        self.undo_stack.append((text_id, x, y, text, self.line_colour, "text"))
                self.redo_stack.clear()
                self.last_x, self.last_y = x, y

    def combine_lines(self):
        points = []
        for line in self.temp_lines:
            points.extend(line)
        line_id = self.canvas.create_line(points, fill=self.line_colour, width=self.line_width, tag="line")
        self.combined_lines.append((line_id, points, self.line_colour, self.line_width))
        self.temp_lines.clear()
        self.undo_stack.append((line_id, points, self.line_colour, self.line_width))

    def undo(self):
        if self.undo_stack:
            line = self.undo_stack.pop()
            line_id = line[0]
            self.canvas.delete(line_id)
            self.redo_stack.append(line)

    def redo(self):
        if self.redo_stack:
            line = self.redo_stack.pop()
            if len(line) == 7:
                _, x1, y1, x2, y2, colour, width = line
                new_line_id = self.canvas.create_line((x1, y1, x2, y2), fill=colour, width=width, tag="line")
                self.undo_stack.append((new_line_id, x1, y1, x2, y2, colour, width))
            elif len(line) == 8 and line[7] == "rectangle":
                _, x1, y1, x2, y2, colour, width, _ = line
                new_rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline=colour, width=width)
                self.undo_stack.append((new_rect_id, x1, y1, x2, y2, colour, width, "rectangle"))
            elif len(line) == 8 and line[7] == "oval":
                _, x1, y1, x2, y2, colour, width, _ = line
                new_oval_id = self.canvas.create_oval(x1, y1, x2, y2, outline=colour, width=width)
                self.undo_stack.append((new_oval_id, x1, y1, x2, y2, colour, width, "oval"))
            elif len(line) == 6 and line[5] == "text":
                _, x, y, text, colour, _ = line
                new_text_id = self.canvas.create_text(x, y, text=text, fill=colour, font=("Arial", self.line_width + 10))
                self.undo_stack.append((new_text_id, x, y, text, colour, "text"))
            else:
                _, points, colour, width = line
                new_line_id = self.canvas.create_line(points, fill=colour, width=width, tag="line")
                self.undo_stack.append((new_line_id, points, colour, width))

    def toggle_theme(self):
        current_theme = sv_ttk.get_theme()
        if current_theme == "light":
            sv_ttk.set_theme("dark")
        else:
            sv_ttk.set_theme("light")

    def capture_window(self):
        x = self.canvas.winfo_rootx() + self.canvas.winfo_x()
        y = self.canvas.winfo_rooty() + self.canvas.winfo_y()
        width = self.canvas.winfo_width() + x
        height = self.canvas.winfo_height() + y
     
        # Prompt user for filename
        file_name = simpledialog.askstring("Filename", "Enter filename:", initialvalue="drawing")
        if file_name is None:
            return
     
        # Prompt user for file type
        file_type = simpledialog.askstring("Filetype", "Enter available file type (png, jpeg):", initialvalue="png")
        if file_type is None:
            return
       
        file_type = file_type.lower()
        valid_file_types = ["png", "jpeg"]
     
        if file_type not in valid_file_types:
            messagebox.showerror("Invalid file type", f"'{file_type}' is not a supported filetype.")
            return
     
        # Generate filename with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{file_name}_{timestamp}.{file_type}"
     
        # Take screenshot of canvas
        takescreenshot = ImageGrab.grab(bbox=(x, y, width, height))
        takescreenshot.save(filename, format=file_type.upper())
     
        messagebox.showinfo("File saved", f"Canvas saved as '{filename}'")

    def create_widgets(self):
        color_picker_button = tkinter.Button(self.button_frame, text="Select Color", width=15, height=2, command=self.colour_change)
        color_picker_button.grid(row=0, column=0, pady=10)

        width_slider = ttk.Scale(self.button_frame, from_=2, to=20, orient="horizontal", command=lambda w: self.line_change(w))
        width_slider.grid(row=1, column=0, pady=10)

        reset_button = ttk.Button(self.button_frame, text="Reset Canvas", width=10, command=self.reset)
        reset_button.grid(row=2, column=0, pady=10)

        toggle_button = ttk.Button(self.button_frame, text="Toggle Theme", command=self.toggle_theme)
        toggle_button.grid(row=3, column=0, pady=10)

        save_button = ttk.Button(self.button_frame, text="Save Image", width=10, command=self.capture_window)
        save_button.grid(row=4, column=0, pady=10)

        line_button = ttk.Button(self.button_frame, text="Line", command=lambda: self.set_draw_type("line"))
        line_button.grid(row=5, column=0, pady=0)

        rectangle_button = ttk.Button(self.button_frame, text="Rectangle", command=lambda: self.set_draw_type("rectangle"))
        rectangle_button.grid(row=6, column=0, pady=10)

        oval_button = ttk.Button(self.button_frame, text="Oval", command=lambda: self.set_draw_type("oval"))
        oval_button.grid(row=7, column=0, pady=10)

        text_button = ttk.Button(self.button_frame, text="Text", command=lambda: self.set_draw_type("text"))
        text_button.grid(row=8, column=0, pady=10)

        undo_button = ttk.Button(self.button_frame, image=self.undo_icon, command=self.undo)
        undo_button.grid(row=9, column=0, pady=10)

        redo_button = ttk.Button(self.button_frame, image=self.redo_icon, command=self.redo)
        redo_button.grid(row=10, column=0, pady=10)

# Main function to run app
if __name__ == "__main__":
    root = tkinter.Tk()
    app = DrawingApplication(root)
    root.mainloop()
