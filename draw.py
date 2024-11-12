import tkinter
from tkinter import ttk, colorchooser, simpledialog, messagebox
import sv_ttk
import time
from PIL import ImageGrab, Image, ImageTk
 
window = tkinter.Tk()
window.geometry("700x350")
window.state('zoomed')
 
main_frame = tkinter.Frame(window)
main_frame.pack(fill=tkinter.BOTH, expand=True, padx=10, pady=10)
 
button_frame = tkinter.Frame(main_frame)
button_frame.pack(side="left", fill=tkinter.Y, padx=5)
 
last_x, last_y = None, None
drawing = False
line_colour = "black"
line_width = 2
 
undo_stack = []
redo_stack = []
 
undo_icon = Image.open(r"C:\Users\af85339\Downloads\Kod\undo_icon.png")
undo_icon = undo_icon.resize((24, 24), Image.LANCZOS)
undo_icon = ImageTk.PhotoImage(undo_icon)
 
redo_icon = Image.open(r"C:\Users\af85339\Downloads\Kod\redo_icon.png")
redo_icon = redo_icon.resize((24, 24), Image.LANCZOS)
redo_icon = ImageTk.PhotoImage(redo_icon)
 
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
 
color_picker_button = tkinter.Button(button_frame, text="Select Color", width=15, height=2, command=colour_change)
color_picker_button.pack(pady=10)
 
width_slider = ttk.Scale(button_frame, from_=2, to=20, orient="horizontal", command=lambda w: line_change(w))
width_slider.pack(pady=10)
 
reset_button = ttk.Button(button_frame, text="Reset Canvas", width=10, command=reset)
reset_button.pack(pady=10)
 
canvas = tkinter.Canvas(main_frame, bg="white")
canvas.pack(fill=tkinter.BOTH, expand=True, padx=5, pady=5, )
 
def start_draw(event):
    global last_x, last_y, drawing
    drawing = True
    last_x, last_y = event.x, event.y
 
def stop_draw(event):
    global drawing
    drawing = False
 
def draw(event):
    global last_x, last_y, drawing
    if drawing:
        x, y = event.x, event.y
        line_id = canvas.create_line((last_x, last_y, x, y), fill=line_colour, width=line_width, tag="line")
        # Save the line properties for undo
        undo_stack.append((line_id, last_x, last_y, x, y, line_colour, line_width))
        # Clear the redo stack whenever a new line is drawn
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
 
def toggle_theme():
    current_theme = sv_ttk.get_theme()
    if current_theme == "light":
        sv_ttk.set_theme("dark")
    else:
        sv_ttk.set_theme("light")
 
toggle_button = ttk.Button(button_frame, text="Toggle Theme", command=toggle_theme)
toggle_button.pack(pady=10)
 
save_button = ttk.Button(button_frame, text="Save Image", width=10, command=capture_window)
save_button.pack(pady=10)
 
undo_button = ttk.Button(button_frame, image=undo_icon, command=undo)
undo_button.pack(pady=10)
 
redo_button = ttk.Button(button_frame, image=redo_icon, command=redo)
redo_button.pack(pady=10)
 
sv_ttk.set_theme("dark")
 
window.title("Drawing Application")
window.mainloop()