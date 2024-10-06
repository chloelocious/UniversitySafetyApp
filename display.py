import tkinter as tk
from tkinter import messagebox, ttk
import threading
import os
from utils import load_csv, list_csv_files

class Display:
    def __init__(self, root):
        self.root = root
        self.root.title("University Safety App")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        self.frames = {}
        self.setup_ui()

    def setup_ui(self):
        self.setup_menu()
        self.setup_main_frame()
        self.setup_scraping_frame()
        self.setup_survey_information()
        self.setup_uptodate_crime()

        for frame in self.frames.values():
            frame.pack(expand=True, fill="both")

        self.show_frame("main")

    def thread_it(self, func, *args):
        t = threading.Thread(target=func, args=args)
        t.setDaemon(True)
        t.start()

    def setup_menu(self):
        # Set up the menu bar
        self.menubar = tk.Menu(self.root)

        # File menu
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Close", command=self.on_closing)
        self.menubar.add_cascade(label="Function", menu=self.filemenu)

        # Data Scraping menu
        self.datascaping_menu = tk.Menu(self.menubar, tearoff=0)
        self.datascaping_menu.add_command(label="Scrape CSS Data", command=lambda: self.show_frame("CSS"))
        self.datascaping_menu.add_command(label="Update Lat Long", command=lambda: self.show_frame("latlong"))
        self.datascaping_menu.add_command(label="Scrape Spot Crime Data", command=lambda: self.show_frame("spotcrime"))
        self.menubar.add_cascade(label="Scraping", menu=self.datascaping_menu)

        # Raw Data menu
        self.rawdata_menu = tk.Menu(self.menubar, tearoff=0)
        self.rawdata_menu.add_command(label="Display Survey Information", command=lambda: self.show_frame("survey"))
        self.rawdata_menu.add_command(label="Display Up-to-Date Crime", command=lambda: self.show_frame("uptodate"))
        self.menubar.add_cascade(label="Data", menu=self.rawdata_menu)

        # Configure the menu
        self.root.config(menu=self.menubar)

    def setup_main_frame(self):
        # Create the main frame
        main_frame = tk.Frame(self.root)
        self.frames["main"] = main_frame

        # Set up main UI components in the main frame
        label = tk.Label(main_frame, text="Choose a Data Display Option", font=("Arial", 16))
        label.pack(padx=10, pady=10)

        buttonframe = tk.Frame(main_frame)
        buttonframe.rowconfigure(0, weight=1)
        buttonframe.rowconfigure(1, weight=1)
        buttonframe.rowconfigure(2, weight=1)

        btn1 = tk.Button(buttonframe, text="Display Survey Information", font=("Arial", 16), command=lambda: self.show_frame("survey"))
        btn2 = tk.Button(buttonframe, text="Display Up-to-Date Crime Data", font=("Arial", 16), command=lambda: self.show_frame("uptodate"))
        btn3 = tk.Button(buttonframe, text="Initialize Scraping Method", font=("Arial", 16), command=lambda: self.show_frame("scraping"))

        btn1.grid(row=0, column=0, padx=10, pady=10)
        btn2.grid(row=1, column=0, padx=10, pady=10)
        btn3.grid(row=2, column=0, padx=10, pady=10)

        buttonframe.pack(padx=10, pady=10)

    def setup_scraping_frame(self):
        # Create the scraping frame
        scraping_frame = tk.Frame(self.root)
        self.frames["scraping"] = scraping_frame
        self.setup_CSS_scraping()
        self.setup_latlong_scraping()
        self.setup_spotcrime_scraping()

        # Set up main UI components in the main frame
        label = tk.Label(scraping_frame, text="Choose scraping method", font=("Arial", 16))
        label.pack(padx=10, pady=10)

        buttonframe = tk.Frame(scraping_frame)
        buttonframe.rowconfigure(0, weight=1)
        buttonframe.rowconfigure(1, weight=1)
        buttonframe.rowconfigure(2, weight=1)
        buttonframe.rowconfigure(3, weight=1)

        btn1 = tk.Button(buttonframe, text="Scrape CSS Data", font=("Arial", 16), command=lambda: self.show_frame("main"))
        btn2 = tk.Button(buttonframe, text="Update Lat Long", font=("Arial", 16), command=lambda: self.show_frame("main"))
        btn3 = tk.Button(buttonframe, text="Scrape Spot Crime Data", font=("Arial", 16), command=lambda: self.show_frame("main"))
        btn4 = tk.Button(buttonframe, text="Back", font=("Arial", 16), command=lambda: self.show_frame("main"))

        btn1.grid(row=0, column=0, padx=10, pady=10)
        btn2.grid(row=1, column=0, padx=10, pady=10)
        btn3.grid(row=2, column=0, padx=10, pady=10)
        btn4.grid(row=3, column=0, padx=10, pady=10)

        buttonframe.pack(padx=10, pady=10)

    def setup_CSS_scraping(self):
        data_frame = tk.Frame(self.root)
        self.frames["CSS"] = data_frame

    def setup_latlong_scraping(self):
        data_frame = tk.Frame(self.root)
        self.frames["latlong"] = data_frame

    def setup_spotcrime_scraping(self):
        data_frame = tk.Frame(self.root)
        self.frames["spotcrime"] = data_frame

    def setup_survey_information(self):
        data_frame = tk.Frame(self.root)
        self.frames["survey"] = data_frame

        # Add Back button to return to the main frame
        back_button = tk.Button(data_frame, text="Back", command=lambda: self.show_frame("main"))
        back_button.pack(padx=10, pady=10)

        # Add Listbox to select CSV file
        self.file_listbox = tk.Listbox(data_frame, selectmode="single", height=10, width=50)
        self.file_listbox.pack(padx=10, pady=10)

        # Populate Listbox with CSV files in the directory
        folder_path = './Crime2023EXCEL'
        self.thread_it(self.load_csv_files, folder_path)

        # Add Select button to load the selected file
        select_button = tk.Button(data_frame, text="Select", command=lambda: self.load_selected_file(folder_path))
        select_button.pack(padx=10, pady=10)

        # Treeview to display selected CSV data
        self.tree = ttk.Treeview(data_frame)
        self.tree.pack(expand=True, fill='both', padx=10, pady=10)

    def setup_uptodate_crime(self):
        data_frame = tk.Frame(self.root)
        self.frames["uptodate"] = data_frame

        # Add Back button to return to the main frame
        back_button = tk.Button(data_frame, text="Back", command=lambda: self.show_frame("main"))
        back_button.pack(padx=10, pady=10)

        # Add Listbox to select CSV file
        self.file_listbox = tk.Listbox(data_frame, selectmode="single", height=10, width=50)
        self.file_listbox.pack(padx=10, pady=10)

        # Populate Listbox with CSV files in the directory
        folder_path = './Crime_uptodate'
        self.thread_it(self.load_csv_files, folder_path)

        # Add Select button to load the selected file
        select_button = tk.Button(data_frame, text="Select", command=lambda: self.load_selected_file(folder_path))
        select_button.pack(padx=10, pady=10)

        # Treeview to display selected CSV data
        self.tree = ttk.Treeview(data_frame)
        self.tree.pack(expand=True, fill='both', padx=10, pady=10)

    def load_csv_files(self, folder_path):
        try:
            files = list_csv_files(folder_path)
            for file in files:
                self.file_listbox.insert(tk.END, file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load files: {e}")

    def load_selected_file(self, folder_path):
        # Get the selected file from the Listbox
        selected_index = self.file_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Warning", "Please select a file first.")
            return

        selected_file = self.file_listbox.get(selected_index)
        file_path = os.path.join(folder_path, selected_file)

        try:
            data = load_csv(file_path)
            # Clear the existing Treeview
            self.tree.delete(*self.tree.get_children())
            # Set up Treeview columns
            self.tree["columns"] = list(data.columns)
            self.tree["show"] = "headings"

            for col in data.columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=100)

            # Insert rows into the Treeview
            for _, row in data.iterrows():
                self.tree.insert("", "end", values=list(row))

        except Exception as e:
            messagebox.showerror("Error", f"Could not read file: {e}")

    def show_frame(self, frame_name):
        # Hide all frames
        for frame in self.frames.values():
            frame.pack_forget()

        # Show the selected frame
        self.frames[frame_name].pack(expand=True, fill="both")
        self.root.update_idletasks()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()

    def run(self):
        self.root.mainloop()