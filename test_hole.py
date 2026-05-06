import tkinter as tk
import ctypes
import time

root = tk.Tk()
root.geometry("300x300")
root.overrideredirect(True)

top = tk.Frame(root, bg="red", height=50)
top.pack(side="top", fill="x")

bottom = tk.Frame(root, bg="blue", height=50)
bottom.pack(side="bottom", fill="x")

left = tk.Frame(root, bg="green", width=10)
left.pack(side="left", fill="y")

right = tk.Frame(root, bg="yellow", width=10)
right.pack(side="right", fill="y")

center = tk.Frame(root, bg="magenta")
center.pack(expand=True, fill="both")

def make_hole():
    hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
    if hwnd == 0: hwnd = root.winfo_id()
    
    w = root.winfo_width()
    h = root.winfo_height()
    
    hRgn = ctypes.windll.gdi32.CreateRectRgn(0, 0, w, h)
    hRgnHole = ctypes.windll.gdi32.CreateRectRgn(10, 50, w-10, h-50)
    ctypes.windll.gdi32.CombineRgn(hRgn, hRgn, hRgnHole, 4)
    ctypes.windll.user32.SetWindowRgn(hwnd, hRgn, True)
    ctypes.windll.gdi32.DeleteObject(hRgnHole)
    print("Hole created!")
    
    # Wait a bit then close so test ends
    root.after(2000, root.destroy)

root.after(500, make_hole)
root.mainloop()
