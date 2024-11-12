import tkinter
from tkinter import ttk, colorchooser, simpledialog, messagebox
import sv_ttk
import time
from PIL import ImageGrab, Image, ImageTk
import base64
from io import BytesIO

window = tkinter.Tk()
window.state('zoomed')

window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)

main_frame = tkinter.Frame(window)
main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=1)

button_frame = tkinter.Frame(main_frame)
button_frame.grid(row=0, column=0, sticky="ns", padx=5)

last_x, last_y = None, None
drawing = False
line_colour = "black"
line_width = 2

undo_stack = []
redo_stack = []

# Base64 encoded undo and redo icons
undo_icon_base64 = """
iVBORw0KGgoAAAANSUhEUgAAAGAAAABgCAYAAADimHc4AAAAAXNSR0IArs4c6QAABBNJREFUeF7tnFt62jAQRke0C0lWkmQjBUIfvIsku/BDSU03UrKSuvsouBHFrUsIGluaGV9+fx8vQZbsczwj6xIc4TAl4ExbR+MEAcYPAQRAgDEB4+YRARBgTMC4eUQABBgTMG4eEQABxgSMm0cEQIAxAePmEQEQYEzAuHlEAAT8IzBfZV+rispvz/mTMRe15nsTAR4+ES38nVcVPU5FQi8ENOHXj95UJJgLOAd/ShJMBVyCPxUJZgI48GsJrqJl8ZwXaj2jYkMmAtrAJ6LtZp3fKTJRbUpdAOD/71dVAOC/DS41AYB/PrOpCAD897sVcQGAf7lPFxUA+OEXKjEBgB+G70uICAB8HnwRAYDPh59cQEv47a40rnT5OtXtP/4o/ZrDbEYv9IvKosjrv8e10PHsZCmox/BDaLauog3taWshI4mAAcNvyjERES1gJPDfiNCafY0W8Ok+e3COHkNxPrTv/YrcbE8b6bQULcCDHasEPxXudrSUlJBEwMglkNvRtZSEZAIgoVuSTSqgrQStPLtYZFf0ka789e33dOMc3b6mF/9pc5RuR3epIyG5gL5KOCW9+JzdVhXNjyIOchhHcgkiAoYiwV+nj47qAz3Um8JCElLvVxITMCQJjWv1O/OC0ZCyUxYVMDQJx7Tkt0iGJCTbqSEuYKwSUu1VUhEwNAnMgWWxWefLUJ8R+l5NwNAkzFfZj1AqStEXqAoYkoRjf/D90hPsHN0VX/Jt6Cm/WEfMyV3PZYb4oXqtwdq5ewlFQYpXUvUIqG+0jYQUT1qXh4VxjdH9gJkAbjpK9bbRRQAjDUW/jpoKCEmwhN8YJfvO+L2j3Kzz6y5y63PMBbwnwRp+DWi+yqpLgDfrPIph1Mkx5k/PbebbvsA/zhONPwKaHfOM6KfWemzoAZqcgBAQ7e8n0QlrQ23T3uhfQ9vAsCg76oGYBdA2bTLyP6UYIPbmLagNHI2y81Xm54EurRtHjwH8fUDAGZuM3J/s9ywg4EQA483ncEaqsQoENARw4fst7rFTEL2aitDI6aE2FvfZonLk14ODR4qFGAhoYGZ0uH9Lp1gDaBqedArqsLU+WeqZXAQctifO6LZydNNyN1zNqnSOlrFLkKf5TT0CQtO7wQRsVCDFoOvcpUMAQ6gUfJOB2MAiQCTtmHbCAxIQvd7LCC79qYgBCBB/6hEB5x/N0lX0pL0ah06YqHAVvWiDNxsHGKag+ucK/vxUgcK/oPayD+Bc1JTKqKegKcHl3CsEcCgJloEAQbicqiGAQ0mwDAQIwuVUDQEcSoJlIEAQLqdqCOBQEiwDAYJwOVVDAIeSYBkIEITLqRoCOJQEy0CAIFxO1RDAoSRYBgIE4XKqhgAOJcEyECAIl1M1BHAoCZaBAEG4nKp/A9ERBn/YBuE4AAAAAElFTkSuQmCC
"""

redo_icon_base64 = """
iVBORw0KGgoAAAANSUhEUgAAAGAAAABgCAYAAADimHc4AAAAAXNSR0IArs4c6QAAA91JREFUeF7tnG9y2jAQxVf0IE1OEnKR4oR88C2S3MIfSgq9SMlJQu9RUCvXZgwBW6C131paz2QmTLBXer99a/2xY0gPqAIGGl2DkwIAJ4ECUABgBcDh1QEKAKwAOLw6QAGAFQCHVwcoALAC4PDqAAUAVgAcXh2gAMAKgMOrAxTAcArM5vkPa2nz8614HS5qe6RkHODEJ6LMyWEtvUiBkASApvh1PkqBED2AU+JLghA1gDbxpUCIFkD2mGfWkKv7nQeyHEULwKnu4wC0E6IGMAYI0QOQDiEJAJIhJANAKoSkAEiEkBwAaRCSBCAJQrIApEBIGoAECCIAuGWDHdFXY+iGaP/j9HGfRR3cyxYwANVazR0RTSUK3UadE8LgACrhn8cm+jEQLgiDAcie8qm15eqkuLJybY3jgDAIgNk8/1WVmmv7KvI8Y+lh+VYsQxrXK4Asy2/slzLrXZ2P6uAQ3wnSG4Cq5LjMj+7gEr83AFXmf0SnvMtYhrLT1IXdAQHil7XUWHqnHa3d78tlsekb4iX3J27x2R1wZc1fmi29DiH2MUy0+OwAvj3mz8bQi2fWrs2WHhDCV0sQ3iOzPjK/1oitBF1Seoyh++X3oiwziENC5rMD8O2Uin+YciwO8M1+Ff+z31kA+NR+jml7SLnydWg1Egue4fq2lQXAbJ7bjoCb1aK49W0U9/ekis8yCvIpP2ZLt6mPds4lVbADPMoPLPslZz7bKKjr+UtU7b/k4dw+x/ld5TTYAV1Zhhz5eLiTfW2nS/Djv3MAcItuZzdZkPXfdbYNAjLzOUtQ6whotSiCIV+aVcffPwVBgvgso6DZPBftgBpGE4IU8ZMCUJejCdHv0G3EUEc2zw8uD5JvwpxC9XUtDgD7929PNRI1DO1LMO7r9g7g34b8erUo7rkbHsv1ggH4bL6jh6KSYQUDcJ3rGgmpC86nABeA1vuAC6/3gtMQWAD4rrtoKfoMgQWAZxkqoyuEQwhsAKp9AfekQefDt5JmougbNBuAroWvEx2FPQ+EFp11Jty82CUuaJyXNAhWBzhRr4TgTl1bS+vJhN7pD5WPJKK2MYd0CDuAQAhD9v1krKGXz3sBUEIY6Rsx0QAYK4SoANQe79q4h9edRgOiBFC64f+/EBP/dmS0AOokkw4iegBHIGZHb8bDq1EyAA4mcE/5dLejO2P2b1PWyxmdyxrcxJIEwC3imK7X2zxgTCIg26oAkOr3+aI2uF+jCa8OAKNSAAoArAA4vDpAAYAVAIdXBygAsALg8OoABQBWABxeHaAAwAqAw6sDFABYAXB4dYACACsADq8OAAP4C4v28HBH0/Z1AAAAAElFTkSuQmCC
"""

# Function to create an ImageTk.PhotoImage object from a base64 encoded string
def load_icon(base64_string):
    icon_data = base64.b64decode(base64_string)
    image = Image.open(BytesIO(icon_data))
    image = image.resize((24, 24), Image.LANCZOS)
    return ImageTk.PhotoImage(image)

# Load icons from base64
undo_icon = load_icon(undo_icon_base64)
redo_icon = load_icon(redo_icon_base64)

def colour_change():
    global line_colour
    color_code = colorchooser.askcolor(title="Choose line color")[1]
    if color_code:
        line_colour = color_code

def line_change(width):
    global line_width
    line_width = int(float(width))

def reset():
    canvas.delete("all")
    undo_stack.clear()
    redo_stack.clear()

color_picker_button = tkinter.Button(button_frame, text="Select Color", width=15, height=2, command=colour_change)
color_picker_button.grid(row=0, column=0, pady=10)

width_slider = ttk.Scale(button_frame, from_=2, to=20, orient="horizontal", command=lambda w: line_change(w))
width_slider.grid(row=1, column=0, pady=10)

reset_button = ttk.Button(button_frame, text="Reset Canvas", width=10, command=reset)
reset_button.grid(row=2, column=0, pady=10)

canvas = tkinter.Canvas(main_frame, bg="white")
canvas.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=1)

def start_draw(event):
    global last_x, last_y, drawing
    drawing = True
    if 0 <= event.x <= canvas.winfo_width() and 0 <= event.y <= canvas.winfo_height():
        last_x, last_y = event.x, event.y

def stop_draw(event):
    global drawing
    drawing = False

def draw(event):
    global last_x, last_y, drawing
    if drawing:
        if 0 <= event.x <= canvas.winfo_width() and 0 <= event.y <= canvas.winfo_height():
            x, y = event.x, event.y
            line_id = canvas.create_line((last_x, last_y, x, y), fill=line_colour, width=line_width, tag="line")
            undo_stack.append((line_id, last_x, last_y, x, y, line_colour, line_width))
            redo_stack.clear()
            last_x, last_y = x, y

def undo():
    if undo_stack:
        line = undo_stack.pop()
        line_id = line[0]
        canvas.delete(line_id)
        redo_stack.append(line)

def redo():
    if redo_stack:
        line = redo_stack.pop()
        _, x1, y1, x2, y2, colour, width = line
        new_line_id = canvas.create_line((x1, y1, x2, y2), fill=colour, width=width, tag="line")
        undo_stack.append((new_line_id, x1, y1, x2, y2, colour, width))

canvas.bind("<Button-1>", start_draw)
canvas.bind("<ButtonRelease-1>", stop_draw)
canvas.bind("<B1-Motion>", draw)

def toggle_theme():
    current_theme = sv_ttk.get_theme()
    if current_theme == "light":
        sv_ttk.set_theme("dark")
    else:
        sv_ttk.set_theme("light")

def capture_window():
    x = canvas.winfo_rootx() + canvas.winfo_x()
    y = canvas.winfo_rooty() + canvas.winfo_y()
    width = canvas.winfo_width() + x
    height = canvas.winfo_height() + y
 
    file_name = simpledialog.askstring("Filename", "Enter filename")
    if file_name is None:
        return
 
    file_type = simpledialog.askstring("Filetype", "Enter available file type (png, jpg, jpeg):", initialvalue="png")
    if file_type is None:
        return
   
    file_type = file_type.lower()
    valid_file_types = ["png", "jpg", "jpeg"]
 
    if file_type not in valid_file_types:
        messagebox.showerror("Invalid file type", f"'{file_type}' is not a supported filetype.")
        return
 
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{file_name}_{timestamp}.{file_type}"
 
    takescreenshot = ImageGrab.grab(bbox=(x, y, width, height))
    takescreenshot.save(filename, format=file_type.upper())
 
    messagebox.showinfo("File saved", f"Canvas saved as '{filename}'")

toggle_button = ttk.Button(button_frame, text="Toggle Theme", command=toggle_theme)
toggle_button.grid(row=3, column=0, pady=10)

save_button = ttk.Button(button_frame, text="Save Image", width=10, command=capture_window)
save_button.grid(row=4, column=0, pady=10)

undo_button = ttk.Button(button_frame, image=undo_icon, command=undo)
undo_button.grid(row=5, column=0, pady=10)

redo_button = ttk.Button(button_frame, image=redo_icon, command=redo)
redo_button.grid(row=6, column=0, pady=10)

window.bind("<Control-z>", lambda event: undo())
window.bind("<Control-y>", lambda event: redo())
window.bind("<Control-s>", lambda event: capture_window())

sv_ttk.set_theme("dark")

window.title("Drawing Application")
window.mainloop()
