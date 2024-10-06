import tkinter as tk
from display import Display

def main():
    root = tk.Tk()
    app = Display(root)
    app.run()

if __name__ == "__main__":
    main()