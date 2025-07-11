import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from PIL import Image
import csv, os, json, platform
from pathlib import Path
from db.db_connection import SwiggyDBConnection


class SwiggyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Swiggy Data Analysis Dashboard")
        self.geometry("1000x700")
        self.resizable(False, False)

        self.db_connection = None
        self.withdraw()  # Hide main window initially
        self.after(100, self.show_splash_screen)

        # Close button validation
        # self.protocol("WM_DELETE_WINDOW", self.confirm_exit)

    # Load Image util
    def load_image(self, path, size):
        img = Image.open(path).convert("RGBA").resize(size, Image.LANCZOS)
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)

    # Center window util
    def _center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        window.geometry(f"{width}x{height}+{x}+{y}")
        
    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()
    
    # Clear frame util     
    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()
 
    def show_splash_screen(self):
        self.splash = ctk.CTkToplevel(self)
        self.splash.overrideredirect(True)

        self._center_window(self.splash, 600, 350)
        # width, height = 600, 350
        # x = (self.winfo_screenwidth() - width) // 2
        # y = (self.winfo_screenheight() - height) // 2
        # self.splash.geometry(f"{width}x{height}+{x}+{y}")
        self.splash.configure(fg_color="#FFF3C7")

        frame = ctk.CTkFrame(self.splash, corner_radius=20, fg_color="#FFF3C7")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        try:
            logo = self.load_image("assets/swiggy.png", (120, 80))
            logo_label = ctk.CTkLabel(frame, image=logo, text="")
            # logo_label.image = logo
            logo_label.pack(pady=(10, 15))
        except Exception as e:
            print(f"Logo load error: {e}")
            ctk.CTkLabel(
                frame, 
                text="[Swiggy Logo]", 
                font=("Segoe UI", 28, "bold"), 
                text_color="#FF5722").pack(pady=(10, 15))

        ctk.CTkLabel(
            frame, 
            text="Swiggy Data Analysis", 
            font=("Segoe UI", 32, "bold"), 
            text_color="#004225").pack(pady=(10, 5))
        ctk.CTkLabel(
            frame, 
            text="Presented by Team 7", 
            font=("Segoe UI", 18), 
            text_color="#1A1A1A").pack(pady=(5, 10))

        self.splash.after(3000, lambda: [self.splash.destroy(), self.create_login_screen()])

    def create_login_screen(self):
        self.deiconify()
        self.protocol("WM_DELETE_WINDOW", self.confirm_exit)
        self.title("Login - Swiggy Data Analysis")
        self._center_window(self, 600, 680)
        self.resizable(False, False)

        for widget in self.winfo_children():
            widget.destroy()

        self.login_frame = ctk.CTkFrame(self, corner_radius=20, fg_color="#FFF8EF", border_width=2, border_color="#FF7F50")
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.85)

        try:
            logo = self.load_image("assets/swiggy.png", (120, 80))
            logo_label = ctk.CTkLabel(self.login_frame, image=logo, text="")
            logo_label.pack(pady=(20, 10))
        except:
            ctk.CTkLabel(self.login_frame, text="Swiggy", font=("Segoe UI", 28, "bold"), text_color="#FF5722").pack(pady=(20, 10))

        ctk.CTkLabel(self.login_frame, text="Login to Swiggy DB", font=("Segoe UI", 24, "bold"), text_color="#333").pack(pady=(5, 20))

        self.host_var = ctk.StringVar()
        self.user_var = ctk.StringVar()
        self.pass_var = ctk.StringVar()
        self.db_var = ctk.StringVar()
        self.entry_list = []

        self.saved_credentials = self._load_saved_credentials()

        self._labeled_entry(self.login_frame, "Host", self.host_var, suggestions=self.saved_credentials.get("host"))
        self._labeled_entry(self.login_frame, "Username", self.user_var, suggestions=self.saved_credentials.get("user"))
        self._labeled_entry(self.login_frame, "Password", self.pass_var, show="*")
        self._labeled_entry(self.login_frame, "Database", self.db_var, suggestions=self.saved_credentials.get("database"))

        self.login_btn = ctk.CTkButton(self.login_frame, text="Connect", command=self.submit_credentials, font=("Segoe UI", 16, "bold"), corner_radius=10, fg_color="#FF7F50", hover_color="#FF5722")
        self.login_btn.pack(pady=(20, 30), ipadx=10, ipady=6)

        for i, entry in enumerate(self.entry_list):
            entry.bind("<Return>", lambda e, idx=i: self.entry_list[idx + 1].focus() if idx + 1 < len(self.entry_list) else [self.login_btn.focus(), self.submit_credentials()])
            entry.bind("<Up>", lambda e, idx=i: self.entry_list[idx - 1].focus() if idx - 1 >= 0 else self.entry_list[idx].focus())

        if self.entry_list:
            self.entry_list[0].focus()

        self.bind("<Escape>", self.confirm_exit)

    def _labeled_entry(self, parent, label_text, variable, show=None, suggestions=None):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(pady=5, fill="x", padx=40)
        ctk.CTkLabel(container, text=label_text, anchor="w", font=("Segoe UI", 12), text_color="#555").pack(anchor="w")
    
        entry = ctk.CTkEntry(container, textvariable=variable, show=show, font=("Segoe UI", 12))
        entry.pack(fill="x")
        self.entry_list.append(entry)
    
        if suggestions:
            listbox_frame = tk.Frame(container, bg="white")
            scrollbar = tk.Scrollbar(listbox_frame, orient="vertical")
            listbox = tk.Listbox(listbox_frame, height=0, yscrollcommand=scrollbar.set, activestyle="dotbox", exportselection=False)
            scrollbar.config(command=listbox.yview)
            scrollbar.pack(side="right", fill="y")
            listbox.pack(side="left", fill="both", expand=True)
            listbox_frame.pack_forget()
    
            def show_suggestions(event=None):
                typed = entry.get()
                if not typed:
                    listbox_frame.pack_forget()
                    return
                matches = [val for val in suggestions if val.lower().startswith(typed.lower()) and val.lower() != typed.lower()]
                listbox.delete(0, tk.END)
                if matches:
                    for val in matches:
                        listbox.insert(tk.END, val)
                    visible_count = min(len(matches), 3)
                    listbox.config(height=visible_count)
                    listbox_frame.pack(fill="x")
                    if len(matches) > 3:
                        scrollbar.pack(side="right", fill="y")
                    else:
                        scrollbar.pack_forget()
                else:
                    listbox_frame.pack_forget()
    
            def autocomplete(event=None):
                if listbox.curselection():
                    entry.delete(0, tk.END)
                    entry.insert(0, listbox.get(listbox.curselection()))
                    listbox_frame.pack_forget()
    
            def navigate_suggestions(event):
                if listbox.size() > 0:
                    listbox.focus_set()
                    current = listbox.curselection()
                    if not current:
                        listbox.selection_set(0)
                        listbox.activate(0)
                    else:
                        next_index = (current[0] + 1) % listbox.size()
                        listbox.selection_clear(0, tk.END)
                        listbox.selection_set(next_index)
                        listbox.activate(next_index)
                    return "break"
            
            def on_down(event):
                if listbox.size() > 0:
                    return navigate_suggestions(event)
                idx = self.entry_list.index(entry)
                if idx + 1 < len(self.entry_list):
                    self.entry_list[idx + 1].focus()
                else:
                    self.login_btn.focus()
                return "break"

    
            def select_from_list(event=None):
                if listbox.curselection():
                    entry.delete(0, tk.END)
                    entry.insert(0, listbox.get(listbox.curselection()))
                    listbox_frame.pack_forget()
                    entry.focus_set()
    
            entry.bind("<KeyRelease>", show_suggestions)
            entry.bind("<Down>", on_down)
            entry.bind("<Return>", autocomplete)
    
            listbox.bind("<ButtonRelease-1>", select_from_list)
            listbox.bind("<Return>", select_from_list)
            listbox.bind("<Up>", lambda e: move_selection(listbox, up=True))
            listbox.bind("<Down>", lambda e: move_selection(listbox, up=False))
            listbox.bind("<Return>", select_from_list)
            
            def move_selection(lb, up=False):
                current = lb.curselection()
                if current:
                    index = current[0] - 1 if up else current[0] + 1
                else:
                    index = 0
                if 0 <= index < lb.size():
                    lb.selection_clear(0, tk.END)
                    lb.selection_set(index)
                    lb.activate(index)

    
            # Hide suggestion box if entry loses focus and listbox isn't clicked
            entry.bind("<FocusOut>", lambda e: self.after(100, lambda: self._safe_hide_listbox(listbox, listbox_frame)))
            listbox.bind("<FocusOut>", lambda e: listbox_frame.pack_forget())
          
        else:
            def fallback_on_down(event):
                idx = self.entry_list.index(entry)
                if idx + 1 < len(self.entry_list):
                    self.entry_list[idx + 1].focus()
                else:
                    self.login_btn.focus()
                return "break"
            entry.bind("<Down>", fallback_on_down)
        entry.bind("<Return>", lambda e: None)  # Optional, to prevent default beep on Return

    def _safe_hide_listbox(self, listbox, frame):
        try:
            if not listbox.focus_get():
                frame.pack_forget()
        except Exception:
            pass  # Suppress TclErrors if widgets are already destroyed
    
    def _load_saved_credentials(self):  # ✅ Now properly defined as a method
        try:
            if os.path.exists(os.path.join("app/credentials", "credentials.json")):
                with open(os.path.join("app/credentials", "credentials.json"), "r") as f:
                    return json.load(f)
        except:
            pass
        return {"host": [], "user": [], "database": []}

    def _save_credentials(self, host, user, database):
        creds = self._load_saved_credentials()
        for key, val in zip(["host", "user", "database"], [host, user, database]):
            if val and val not in creds[key]:
                creds[key].insert(0, val)
                creds[key] = creds[key][:5]

        os.makedirs("app/credentials", exist_ok=True)
        with open(os.path.join("app/credentials","credentials.json"), "w") as f:
            json.dump(creds, f)

    def _autocomplete_entry(self, entry_widget, creds_dict, index):
        label_map = ["host", "user", None, "database"]
        key = label_map[index]
        if key is None:
            return
        typed = entry_widget.get()
        matches = [val for val in creds_dict.get(key, []) if val.startswith(typed)]
        if matches:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, matches[0])

    def confirm_exit(self, event=None):
        try:
            if self.winfo_exists():
                if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
                    self.destroy()
        except tk.TclError:
            pass

    def submit_credentials(self):
        host = self.host_var.get().strip()
        user = self.user_var.get().strip()
        password = self.pass_var.get().strip()
        database = self.db_var.get().strip()

        if not host or not user or not password or not database:
            messagebox.showerror("Validation Error", "All fields are required.")
            return

        loading_popup = ctk.CTkToplevel(self)
        loading_popup.title("Connecting...")
        loading_popup.geometry("300x100")
        ctk.CTkLabel(loading_popup, text="Connecting to database...").pack(pady=30)
        loading_popup.update_idletasks()

        self.after(100, lambda: self.try_db_connection(host, user, password, database, loading_popup))

    def try_db_connection(self, host, user, password, database, popup):
        try:
            self.db_connection = SwiggyDBConnection(host, user, password, database)
            popup.destroy()
            messagebox.showinfo("Success", "Connected successfully!")
            self._save_credentials(host, user, database)
            self.create_main_screen()
        except Exception as e:
            popup.destroy()
            messagebox.showerror("Connection Failed", f"Failed to connect to the database.\n\n{str(e)}")

    def create_main_screen(self):
        self.title("Swiggy Dashboard")
        self._center_window(self, 1000, 700)
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.show_escape_options) 


        for widget in self.winfo_children():
            widget.destroy()

        self.main_frame = ctk.CTkFrame(self, corner_radius=20, fg_color="#FFF8EF", border_width=2, border_color="#FF7F50")
        self.main_frame.pack(expand=True, fill="both", padx=30, pady=30)

        try:
            logo = self.load_image("assets/swiggy.png", (120, 80))
            logo_label = ctk.CTkLabel(self.main_frame, image=logo, text="")
            # logo_label.image = logo
            logo_label.pack(pady=(20, 10))
        except:
            ctk.CTkLabel(self.main_frame, text="Swiggy", font=("Segoe UI", 28, "bold"), text_color="#FF5722").pack(pady=(20, 10))

        ctk.CTkLabel(self.main_frame, text="Swiggy Data Analysis Dashboard", font=("Segoe UI", 28, "bold"), text_color="#333").pack(pady=(5, 20))

        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(pady=20)

        ctk.CTkButton(button_frame, text="Recreate Tables", command=self.recreate_tables).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Show Schema", command=self.show_schema_page).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Fetch Table Data", command=self.fetch_data_page).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Run SQL Query", command=self.run_query_page).pack(side="left", padx=10)

        self.bind("<Escape>", self.show_escape_options)
        
    def recreate_tables(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Please Wait")
        popup.geometry("300x100")
        ctk.CTkLabel(popup, text="Creating tables...").pack(expand=True)

        try:
            self.db_connection.reinitialize_database()  # Assuming this method exists in your SwiggyDBConnection class
            popup.after(3000, lambda: [popup.destroy(), messagebox.showinfo("Success", "Tables recreated successfully")])
        except Exception as e:
            popup.destroy()
            messagebox.showerror("Error", f"Failed to recreate tables:\n{str(e)}")
                
    def enable_scroll_on(self, scrollable_frame):
        canvas = scrollable_frame._parent_canvas
        if not canvas:
            return

        # Windows & macOS: Use <MouseWheel>
        def _on_mousewheel(event):
            if platform.system() == "Windows":
                canvas.yview_scroll(-1 * (event.delta // 120), "units")
            elif platform.system() == "Darwin":
                canvas.yview_scroll(-1 * int(event.delta), "units")

        # Linux: Use Button-4 and Button-5
        def _on_linux_scroll_up(event):
            canvas.yview_scroll(-1, "units")

        def _on_linux_scroll_down(event):
            canvas.yview_scroll(1, "units")

        # Bind scroll events only when mouse enters the widget
        def _bind_to_mousewheel(event):
            if platform.system() in ("Windows", "Darwin"):
                canvas.bind_all("<MouseWheel>", _on_mousewheel)
            else:
                canvas.bind_all("<Button-4>", _on_linux_scroll_up)
                canvas.bind_all("<Button-5>", _on_linux_scroll_down)

        def _unbind_from_mousewheel(event):
            if platform.system() in ("Windows", "Darwin"):
                canvas.unbind_all("<MouseWheel>")
            else:
                canvas.unbind_all("<Button-4>")
                canvas.unbind_all("<Button-5>")

        scrollable_frame.bind("<Enter>", _bind_to_mousewheel)
        scrollable_frame.bind("<Leave>", _unbind_from_mousewheel)


    def show_schema_page(self):
        self.clear_window()
        self.protocol("WM_DELETE_WINDOW", self.show_escape_to_main) 
        self.title("Show Schema - Swiggy Data Analysis")
        self._center_window(self, 1000, 700)

        # self.geometry("800x600")
        self.configure(fg_color="#FFF3C7")

        def escape_popup(event=None):
            if messagebox.askyesno("Go Back", "Do you want to return to the main menu?"):
                self.create_main_screen()

        self.bind("<Escape>", escape_popup)

        ctk.CTkLabel(self, text="📊 Show Schema", font=("Segoe UI", 28, "bold"), text_color="#004225").pack(pady=20)


        self.dropdown_frame = ctk.CTkFrame(self, fg_color="#FFEFCB")
        self.dropdown_frame.pack(pady=5, padx=30, fill="x")


        ctk.CTkLabel(self.dropdown_frame, text="Select a Table:", font=("Segoe UI", 16), text_color="#333").pack(pady=(10, 5))

        try:
            table_names = self.db_connection.fetch_table_names()
        except Exception as e:
            ctk.CTkLabel(self.dropdown_frame, text=f"Error fetching tables: {e}", font=("Segoe UI", 14), text_color="red").pack()
            return

        self.table_dropdown = ctk.CTkOptionMenu(self.dropdown_frame, values=table_names, fg_color="#FFA500", text_color="white")
        self.table_dropdown.pack(pady=5)

        ctk.CTkButton(self.dropdown_frame, text="Show Schema", command=lambda: self.show_schema(self.table_dropdown.get()),
                    fg_color="#34A853", hover_color="#0C8A40", text_color="white").pack(pady=5)

        self.output_frame = ctk.CTkScrollableFrame(self, width=700, height=350, fg_color="#FFFAE5")
        self.output_frame.pack(pady=20, padx=30, fill="both", expand=True)
        
        # # Enable 2-finger scroll / mouse wheel on all OS
        # self.output_frame.bind("<Enter>", lambda e: self._bind_mousewheel(self.output_frame))
        # self.output_frame.bind("<Leave>", lambda e: self._unbind_mousewheel(self.output_frame))

        self.enable_scroll_on(self.output_frame)


        ctk.CTkButton(self, text="← Back", command=self.create_main_screen,
                    fg_color="#D97706", hover_color="#C2410C", text_color="white").pack(pady=10)

    def show_schema(self, table_name):
        for widget in self.output_frame.winfo_children():
            widget.destroy()

        try:
            schema = self.db_connection.fetch_table_description(table_name)
        except Exception as e:
            ctk.CTkLabel(self.output_frame, text=f"Error fetching schema: {e}",
                        font=("Segoe UI", 14), text_color="red").pack()
            return

        if not schema:
            ctk.CTkLabel(self.output_frame, text="No schema found.",
                        font=("Segoe UI", 14), text_color="gray").pack()
            return

        ctk.CTkLabel(self.output_frame, text=f"📄 Schema for `{table_name}`",
                    font=("Segoe UI", 20, "bold"), text_color="#004225").pack(pady=10)

        for col in schema:
            name = col[0]
            dtype = col[1]
            key = col[3]
            key_marker = ""
            if key == 'PRI':
                key_marker = " 🔑"
            elif key == 'MUL':
                key_marker = " 🔗"

            label = ctk.CTkLabel(
                self.output_frame,
                text=f"{name}{key_marker}   ({dtype})",
                font=("Segoe UI", 14),
                anchor="w",
                justify="left",
                text_color="#1F2937" if key != 'PRI' else "#B91C1C"
            )
            label.pack(fill="x", padx=20, pady=2)

    
    def fetch_data_page(self):
        self.clear_frame(self.main_frame)
        self.protocol("WM_DELETE_WINDOW", self.show_escape_to_main) 
        self._center_window(self, 750, 900)
        
        def escape_popup(event=None):
            if messagebox.askyesno("Go Back", "Do you want to return to the main menu?"):
                self.create_main_screen()

        self.bind("<Escape>", escape_popup)

        self.latest_query_results = []
        self.latest_query_columns = []
        self.query_executed_successfully = False

        # Title
        title_label = ctk.CTkLabel(self.main_frame, text="📊 Fetch Table Data", font=("Helvetica", 22, "bold"), text_color="#FFA500")
        title_label.pack(pady=15)

        # Input section frame
        input_frame = ctk.CTkFrame(self.main_frame, fg_color="#1c1c1c", corner_radius=15)
        input_frame.pack(pady=10, padx=20, fill="x")

        # Table Dropdown
        ctk.CTkLabel(input_frame, text="Table:", font=("Helvetica", 14), text_color="white").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.table_var = ctk.StringVar()
        table_names = self.db_connection.fetch_table_names()
        ctk.CTkComboBox(input_frame, variable=self.table_var, values=table_names, font=("Helvetica", 13), width=200).grid(row=0, column=1, padx=10, pady=5)

        # Columns
        ctk.CTkLabel(input_frame, text="Columns (comma separated):", font=("Helvetica", 14), text_color="white").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.columns_var = ctk.StringVar()
        ctk.CTkEntry(input_frame, textvariable=self.columns_var, width=300).grid(row=1, column=1, padx=10, pady=5)

        # Where
        ctk.CTkLabel(input_frame, text="WHERE clause:", font=("Helvetica", 14), text_color="white").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.where_var = ctk.StringVar()
        ctk.CTkEntry(input_frame, textvariable=self.where_var, width=300).grid(row=2, column=1, padx=10, pady=5)

        # GROUP BY
        ctk.CTkLabel(input_frame, text="GROUP BY:", font=("Helvetica", 14), text_color="white").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.group_by_var = ctk.StringVar()
        ctk.CTkEntry(input_frame, textvariable=self.group_by_var, width=300).grid(row=3, column=1, padx=10, pady=5)

        # HAVING
        ctk.CTkLabel(input_frame, text="HAVING:", font=("Helvetica", 14), text_color="white").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.having_var = ctk.StringVar()
        ctk.CTkEntry(input_frame, textvariable=self.having_var, width=300).grid(row=4, column=1, padx=10, pady=5)

        # ORDER BY
        ctk.CTkLabel(input_frame, text="ORDER BY:", font=("Helvetica", 14), text_color="white").grid(row=5, column=0, padx=10, pady=5, sticky="e")
        self.order_by_var = ctk.StringVar()
        ctk.CTkEntry(input_frame, textvariable=self.order_by_var, width=300).grid(row=5, column=1, padx=10, pady=5)

        # LIMIT
        ctk.CTkLabel(input_frame, text="LIMIT:", font=("Helvetica", 14), text_color="white").grid(row=6, column=0, padx=10, pady=5, sticky="e")
        self.limit_var = ctk.StringVar()
        ctk.CTkEntry(input_frame, textvariable=self.limit_var, width=300).grid(row=6, column=1, padx=10, pady=5)

        # OFFSET
        ctk.CTkLabel(input_frame, text="OFFSET:", font=("Helvetica", 14), text_color="white").grid(row=7, column=0, padx=10, pady=5, sticky="e")
        self.offset_var = ctk.StringVar()
        ctk.CTkEntry(input_frame, textvariable=self.offset_var, width=300).grid(row=7, column=1, padx=10, pady=5)

        # Submit Button
        submit_button = ctk.CTkButton(
            input_frame,
            text="Run Query",
            command=self.submit_query,
            fg_color="#FFA500",
            hover_color="#cc8400",
            font=("Helvetica", 15, "bold"),
            width=200
        )
        submit_button.grid(row=8, column=0, columnspan=2, pady=15)

        # # Output frame for table data
        # self.output_frame = ctk.CTkScrollableFrame(self.main_frame, height=350, fg_color="#252525", corner_radius=15)
        # self.output_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Output frame with both horizontal and vertical scrollbars
        output_container = ctk.CTkFrame(self.main_frame, fg_color="#252525", corner_radius=15)
        output_container.pack(pady=10, padx=20, fill="both", expand=True)

        canvas = tk.Canvas(output_container, bg="#252525", highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        v_scrollbar = tk.Scrollbar(output_container, orient=tk.VERTICAL, command=canvas.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        h_scrollbar = tk.Scrollbar(self.main_frame, orient=tk.HORIZONTAL, command=canvas.xview)
        h_scrollbar.pack(fill=tk.X, padx=20)

        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Scrollable inner frame
        self.output_frame = tk.Frame(canvas, bg="#252525")
        self.output_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=self.output_frame, anchor="nw")

        # Bindings for scrolling:

        # Vertical scroll (mouse wheel)
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        # Horizontal scroll (Shift + mouse wheel)
        def _on_shift_mousewheel(event):
            canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

        # Linux vertical scroll (Button 4 and 5)
        def _on_linux_scroll(event):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")

        # Linux horizontal scroll (Button 6 and 7)
        # def _on_linux_horiz_scroll(event):
        #     if event.num == 6:
        #         canvas.xview_scroll(-1, "units")
        #     elif event.num == 7:
        #         canvas.xview_scroll(1, "units")

        # Bind scroll events globally to canvas
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Shift-MouseWheel>", _on_shift_mousewheel)
        canvas.bind_all("<Button-4>", _on_linux_scroll)   # scroll up
        canvas.bind_all("<Button-5>", _on_linux_scroll)   # scroll down
        # canvas.bind_all("<Button-6>", _on_linux_horiz_scroll)  # horizontal scroll left
        # canvas.bind_all("<Button-7>", _on_linux_horiz_scroll)  # horizontal scroll right

        self.export_button = ctk.CTkButton(
            self.main_frame,
            text="Export to CSV",
            command=self.export_query_result_to_csv,
            fg_color="#1c8adb",
            hover_color="#146baf",
            font=("Helvetica", 14, "bold"),
            width=180
        )
        self.export_button.pack(pady=10)
        self.export_button.pack_forget()
        
    # Submit Button
    def submit_query(self):
        # Clear old content in output_frame
        for widget in self.output_frame.winfo_children():
            widget.destroy()
        
        self.export_button.pack_forget()
        self.query_executed_successfully = False
        
        table_name = self.table_var.get().strip()
        columns_input = self.columns_var.get().strip()
        columns = tuple(col.strip() for col in columns_input.split(",")) if columns_input else None

        where = self.where_var.get().strip() or None
        group_by = self.group_by_var.get().strip() or None
        having = self.having_var.get().strip() or None
        order_by = self.order_by_var.get().strip() or None

        try:
            limit = int(self.limit_var.get().strip()) if self.limit_var.get().strip() else None
        except ValueError:
            messagebox.showerror("Input Error", "LIMIT must be a valid integer.")
            return

        try:
            offset = int(self.offset_var.get().strip()) if self.offset_var.get().strip() else None
        except ValueError:
            messagebox.showerror("Input Error", "OFFSET must be a valid integer.")
            return

        try:
            rows = self.db_connection.fetch_table_data(
                table_name=table_name,
                columns=columns,
                where_clause=where,
                group_by=group_by,
                having=having,
                order_by=order_by,
                limit=limit,
                offset=offset
            )

            if columns:  # Show only selected column headers
                columns_list = list(columns)
            else:  # Show all columns
                columns_list = self.db_connection.fetch_table_columns(table_name)

            self.latest_query_results = rows
            self.latest_query_columns = columns_list
            self.query_executed_successfully = True

            # Column Headers
            for j, col_name in enumerate(columns_list):
                header = ctk.CTkLabel(self.output_frame, text=col_name, font=("Helvetica", 13, "bold"))
                header.grid(row=0, column=j, padx=10, pady=5)

            # Data Rows
            for i, row in enumerate(rows, start=1):
                for j, value in enumerate(row):
                    label = ctk.CTkLabel(self.output_frame, text=str(value), wraplength=250)
                    label.grid(row=i, column=j, padx=10, pady=3)

            self.export_button.pack(pady=10)
        except Exception as e:
            messagebox.showerror("Fetch Error", str(e))

    def run_query_page(self):
        self.clear_frame(self.main_frame)
        self.protocol("WM_DELETE_WINDOW", self.show_escape_to_main) 
        self._center_window(self, 700, 900)

        def escape_popup(event=None):
            if messagebox.askyesno("Go Back", "Do you want to return to the main menu?"):
                self.create_main_screen()

        self.bind("<Escape>", escape_popup)

        self.latest_query_results = []
        self.latest_query_columns = []
        self.query_executed_successfully = False

        # Load query history
        self.query_history_file = os.path.join("queries", "query_history.json")
        try:
            if not os.path.exists(self.query_history_file):
                with open(self.query_history_file, "w") as f:
                    json.dump([], f)
        except Exception as e:
            os.makedirs("queries", exist_ok=True)
            print(e)

        # Title
        title_label = ctk.CTkLabel(self.main_frame, text="🧠 Run Custom SQL Query", font=("Helvetica", 22, "bold"), text_color="#FFA500")
        title_label.pack(pady=15)

        # Frame for input area
        input_frame = ctk.CTkFrame(self.main_frame, fg_color="#1c1c1c", corner_radius=15)
        input_frame.pack(padx=20, pady=10, fill="x")

        # SQL query input
        ctk.CTkLabel(input_frame, text="Enter MySQL Query:", font=("Helvetica", 14), text_color="white").pack(anchor="w", padx=10, pady=5)
        self.query_textbox = ctk.CTkTextbox(input_frame, height=120, font=("Courier", 13), fg_color="#252525", text_color="white", border_color="#FFA500", border_width=2)
        self.query_textbox.pack(padx=10, pady=5, fill="x")
        # self.query_textbox.insert("1.0", "-- Example: SELECT * FROM your_table;")
        
        # Save Query Button
        ctk.CTkButton(
            input_frame,
            text="📂 Save Query",
            command=self.save_query,
            fg_color="#28a745",
            hover_color="#1e7e34",
            font=("Helvetica", 14, "bold")
        ).pack(pady=5)

        # Run button
        ctk.CTkButton(
            input_frame,
            text="▶ Run Query",
            command=self.submit_custom_query,
            fg_color="#FFA500",
            hover_color="#cc8400",
            font=("Helvetica", 15, "bold"),
            width=200
        ).pack(pady=10)

        # Collapsible Query History
        sidebar_frame = ctk.CTkFrame(self.main_frame, fg_color="#1c1c1c")
        sidebar_frame.pack(fill="x", padx=20, pady=10)

        self.history_visible = tk.BooleanVar(value=False)

        def toggle_history():
            if self.history_visible.get():
                self.query_history_container.pack_forget()
                toggle_btn.configure(text="▶ Show Query History")
            else:
                self.query_history_container.pack(fill="x", padx=10, pady=5)
                toggle_btn.configure(text="▼ Hide Query History")
            self.history_visible.set(not self.history_visible.get())


        toggle_btn = ctk.CTkButton(sidebar_frame, text="▶ Show Query History", command=toggle_history, font=("Helvetica", 14), width=200)
        toggle_btn.pack(anchor="w", padx=10, pady=5)

        self.query_history_container = ctk.CTkScrollableFrame(sidebar_frame, fg_color="#252525", height=250)
        self.load_query_history()

        # Output Frame Setup
        output_container = ctk.CTkFrame(self.main_frame, fg_color="#252525", corner_radius=15)
        output_container.pack(pady=10, padx=20, fill="both", expand=True)

        canvas = tk.Canvas(output_container, bg="#252525", highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        v_scrollbar = tk.Scrollbar(output_container, orient=tk.VERTICAL, command=canvas.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        h_scrollbar = tk.Scrollbar(output_container, orient=tk.HORIZONTAL, command=canvas.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.output_frame = tk.Frame(canvas, bg="#252525")
        self.output_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.output_frame, anchor="nw")

        # Bindings for scrolling:

        # Vertical scroll (mouse wheel)
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        # Horizontal scroll (Shift + mouse wheel)
        def _on_shift_mousewheel(event):
            canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

        # Linux vertical scroll (Button 4 and 5)
        def _on_linux_scroll(event):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")

        # Linux horizontal scroll (Button 6 and 7)
        # def _on_linux_horiz_scroll(event):
        #     if event.num == 6:
        #         canvas.xview_scroll(-1, "units")
        #     elif event.num == 7:
        #         canvas.xview_scroll(1, "units")

        # Bind scroll events globally to canvas
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Shift-MouseWheel>", _on_shift_mousewheel)
        canvas.bind_all("<Button-4>", _on_linux_scroll)   # scroll up
        canvas.bind_all("<Button-5>", _on_linux_scroll)   # scroll down
        # canvas.bind_all("<Button-6>", _on_linux_horiz_scroll)  # horizontal scroll left
        # canvas.bind_all("<Button-7>", _on_linux_horiz_scroll)  # horizontal scroll right

        self.export_button = ctk.CTkButton(
            self.main_frame,
            text="Export to CSV",
            command=self.export_query_result_to_csv,
            fg_color="#1c8adb",
            hover_color="#146baf",
            font=("Helvetica", 14, "bold"),
            width=180
        )
        self.export_button.pack(pady=10)
        self.export_button.pack_forget()

    def save_query(self):
        query = self.query_textbox.get("1.0", "end").strip()
        if not query:
            messagebox.showwarning("Input Error", "Query is empty. Please enter a valid SQL query.")
            return
    
        try:
            results = self.db_connection.fetch_query_result(query)
            if not results:
                messagebox.showwarning("No Results", "Query executed but returned no results. Cannot save.")
                return
            # Ask for title
            title = simpledialog.askstring("Save Query", "Enter a title for this query:")
            if not title:
                messagebox.showwarning("Missing Info", "Both title and query are required.")
                return
    
            # Load existing history
            try:
                with open(self.query_history_file, "r") as f:
                    try:
                        history = json.load(f)
                    except json.JSONDecodeError:
                        print("No history")
                        history = []
            except FileNotFoundError:
                history = []
    
            history.append({"title": title, "query": query})

            os.makedirs("queries", exist_ok=True)
            with open(self.query_history_file, "w") as f:
                json.dump(history, f, indent=4)

            self.load_query_history()
            messagebox.showinfo("Saved", f"Query '{title}' saved successfully.")
    
        except Exception as e:
            messagebox.showerror("Execution Failed", f"Query could not be executed.\nError: {e}")

    
    def load_query_history(self):
        for widget in self.query_history_container.winfo_children():
            widget.destroy()
        # with open(self.query_history_file) as f:
        #     history = json.load(f)
        try:
            with open(self.query_history_file) as f:
                try:
                    history = json.load(f)
                except json.JSONDecodeError:
                    history = []  # Empty or invalid file
        except Exception as e:
            history = []
            
        for index, item in enumerate(history):
            row = ctk.CTkFrame(self.query_history_container, fg_color="#333")
            row.pack(fill="both", pady=2)
            
            def run_saved_query(query=item["query"]):
                self.query_textbox.delete("1.0", tk.END)
                self.query_textbox.insert("1.0", query)
                self.submit_custom_query()  # Run immediately

            # Container for left-aligned label and right-aligned buttons
            content_frame = ctk.CTkFrame(row, fg_color="transparent")
            content_frame.pack(fill="x")

            # Left-aligned title with truncation
            title = item['title']
            truncated_title = (title[:60] + "...") if len(title) > 65 else title
            label = ctk.CTkLabel(content_frame, text=truncated_title, font=("Helvetica", 12), text_color="white", anchor="w")
            label.pack(side="left", fill="x", expand=True)
            label.bind("<Button-1>", lambda e, q=item["query"]: run_saved_query(q))
            label.configure(cursor="hand2")

            # Right-aligned buttons
            button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            button_frame.pack(side="right")

            ctk.CTkButton(button_frame, text="▶", width=30, command=lambda q=item['query']: run_saved_query(q)).pack(side="left", padx=2)
            ctk.CTkButton(button_frame, text="✏", width=30, command=lambda i=index: self.edit_query(i)).pack(side="left", padx=2)
            ctk.CTkButton(button_frame, text="🗑", width=30, command=lambda i=index: self.delete_query(i)).pack(side="left", padx=2)
    
    def edit_query(self, index):
        with open(self.query_history_file, "r+") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Could not read query history.")
                return
    
            if index >= len(history):
                messagebox.showerror("Error", "Query not found.")
                return
    
            old_title = history[index]["title"]
            old_query = history[index]["query"]
    
            new_title = simpledialog.askstring("Edit Query Title", "Update the title:", initialvalue=old_title)
            if new_title is None:
                return
    
            new_query = simpledialog.askstring("Edit SQL Query", "Update the SQL query:", initialvalue=old_query)
            if new_query is None:
                return
    
            try:
                results = self.db_connection.fetch_query_result(new_query)
            except Exception as e:
                messagebox.showerror("Query Failed", f"Failed to execute updated query:\n\n{e}")
                return
    
            if not results:
                messagebox.showinfo("No Results", "The updated query returned no results and will not be saved.")
                return
    
            # If query is valid and returns data, update and save
            history[index]["title"] = new_title
            history[index]["query"] = new_query
    
            f.seek(0)
            f.truncate()
            json.dump(history, f, indent=2)
    
        self.load_query_history()
        messagebox.showinfo("Query Updated", "Query updated and validated successfully.")


    def delete_query(self, index):
        if messagebox.askyesno("Delete Query", "Are you sure you want to delete this saved query?"):
            with open(self.query_history_file, "r+") as f:
                try:
                    history = json.load(f)
                except json.JSONDecodeError:
                    history = []

                if index < len(history):
                    del history[index]

                f.seek(0)
                f.truncate()
                json.dump(history, f, indent=2)

            self.load_query_history()
            
    def submit_custom_query(self):
        for widget in self.output_frame.winfo_children():
            widget.destroy()
        self.export_button.pack_forget()
        self.query_executed_successfully = False

        query = self.query_textbox.get("1.0", "end").strip()
        if not query:
            messagebox.showwarning("Input Error", "Please enter a SQL query.")
            return

        try:
            results = self.db_connection.fetch_query_result(query)
            cursor_description = self.db_connection.cursor.description

            if not results:
                messagebox.showinfo("Query Result", "No data returned.")
                return

            columns = [desc[0] for desc in cursor_description] if cursor_description else [f"Column {i+1}" for i in range(len(results[0]))]

            self.latest_query_results = results
            self.latest_query_columns = columns
            self.query_executed_successfully = True

            for j, col_name in enumerate(columns):
                header = ctk.CTkLabel(self.output_frame, text=col_name, font=("Helvetica", 13, "bold"), text_color="#FFA500", bg_color="#252525")
                header.grid(row=0, column=j, padx=10, pady=5)

            for i, row in enumerate(results, start=1):
                for j, value in enumerate(row):
                    label = ctk.CTkLabel(self.output_frame, text=str(value), wraplength=250, font=("Helvetica", 12), text_color="white", bg_color="#252525")
                    label.grid(row=i, column=j, padx=10, pady=3)

            self.export_button.pack(pady=10)

        except Exception as e:
            messagebox.showerror("Query Execution Error", str(e))

    def export_query_result_to_csv(self):
        if not self.latest_query_results or not self.latest_query_columns:
            messagebox.showwarning("Export Error", "No results to export.")
            return

        downloads_path = str(Path.home() / "Downloads")
        file_path = filedialog.asksaveasfilename(
            initialdir=downloads_path,
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Save query result as..."
        )

        if file_path:
            try:
                with open(file_path, "w", newline='', encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(self.latest_query_columns)
                    writer.writerows(self.latest_query_results)
                messagebox.showinfo("Export Successful", f"Results exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Export Failed", str(e))


    def show_escape_options(self, event=None):
        response = messagebox.askyesnocancel("Escape Options", "Choose an action:\n\nYes: Disconnect and Login\nNo: Exit Application\nCancel: Stay on Main Screen", icon='question')
        if response is None:  # Cancel pressed, do nothing
            return
        elif response:  # Yes pressed, disconnect and return to login
            if self.db_connection:
                self.db_connection.disconnect()
            self.create_login_screen()
        else:  # No pressed, exit application
            if self.db_connection:
                self.db_connection.disconnect()
            self.destroy()
    
    def show_escape_to_main(self, event=None):
        response = messagebox.askyesnocancel("Escape Options", "Choose an action:\n\nYes: Back to Main Menu\nNo: Exit Application\nCancel: Stay", icon='question')
        if response is None:  # Cancel pressed, do nothing
            return
        elif response:  # Yes pressed, disconnect and return to login
            if self.db_connection:
                self.db_connection.disconnect()
            self.create_main_screen()
        else:  # No pressed, exit application
            if self.db_connection:
                self.db_connection.disconnect()
            self.destroy()
    

    def navigate_to(self, title):
        for widget in self.winfo_children():
            widget.destroy()
        ctk.CTkLabel(self, text=f"{title} Window (WIP)", font=("Segoe UI", 22)).pack(pady=100)
        ctk.CTkButton(self, text="Back", command=self.create_main_screen).pack(pady=20)

if __name__ == "__main__":
    app = SwiggyApp()
    app.mainloop()
