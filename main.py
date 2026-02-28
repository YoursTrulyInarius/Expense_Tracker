import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import Database
from app_styles import AppStyles
from datetime import datetime
import csv

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Expense Tracker")
        
        # Increased to 1350x750 for extra breathing room
        window_width = 1350
        window_height = 750
        
        # Center the window on the screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.root.configure(bg=AppStyles.BG_PRIMARY)
        
        try:
            self.db = Database()
        except Exception as e:
            messagebox.showerror("Startup Error", f"Could not initialize database:\n{str(e)}")
            self.root.destroy()
            return
        self.selected_id = None

        # Search/filter state variables
        self.search_var = tk.StringVar()
        self.filter_var = tk.StringVar(value="All")
        
        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        # Main Container
        self.main_container = tk.Frame(self.root, bg=AppStyles.BG_PRIMARY)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=AppStyles.PADDING, pady=AppStyles.PADDING)
        
        # Header
        header_label = tk.Label(
            self.main_container, 
            text="Expense Tracker", 
            font=AppStyles.FONT_TITLE,
            bg=AppStyles.BG_PRIMARY,
            fg=AppStyles.PRIMARY_COLOR
        )
        header_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))
        
        # Left Panel: Input Form
        self.form_frame = tk.Frame(self.main_container, bg=AppStyles.BG_SECONDARY, relief="flat", bd=1)
        self.form_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 20))
        self.setup_form()
        
        # Right Panel: Table
        self.table_frame = tk.Frame(self.main_container, bg=AppStyles.BG_SECONDARY)
        self.table_frame.grid(row=1, column=1, sticky="nsew")
        self.setup_table()
        
        # Configure grid expansion
        self.main_container.grid_columnconfigure(1, weight=3)
        self.main_container.grid_rowconfigure(1, weight=1)

    def validate_amount(self, P):
        """Allow only digits and at most one decimal point."""
        if P == "":
            return True
        try:
            if P.count('.') <= 1 and all(c.isdigit() or c == '.' for c in P):
                return True
            return False
        except ValueError:
            return False

    def setup_form(self):
        style = ttk.Style()
        style.configure("Large.TEntry", padding=AppStyles.ENTRY_PADDING)
        style.configure("Large.TCombobox", padding=AppStyles.ENTRY_PADDING)

        form_inner = tk.Frame(self.form_frame, bg=AppStyles.BG_SECONDARY, padx=30, pady=30)
        form_inner.pack(fill=tk.BOTH, expand=True)
        
        # Item
        tk.Label(form_inner, text="Description", bg=AppStyles.BG_SECONDARY, fg=AppStyles.TEXT_MAIN, font=AppStyles.FONT_BODY).pack(anchor="w", pady=(0, 8))
        self.item_entry = ttk.Entry(form_inner, width=35, style="Large.TEntry")
        self.item_entry.pack(fill=tk.X, pady=(0, 20))
        
        # Category
        tk.Label(form_inner, text="Category", bg=AppStyles.BG_SECONDARY, fg=AppStyles.TEXT_MAIN, font=AppStyles.FONT_BODY).pack(anchor="w", pady=(0, 8))
        self.category_combo = ttk.Combobox(form_inner, values=["Food", "Transport", "Utilities", "Entertain", "Health", "Other"], width=33, style="Large.TCombobox", state="readonly")
        self.category_combo.pack(fill=tk.X, pady=(0, 20))
        
        # Amount
        tk.Label(form_inner, text="Amount (₱)", bg=AppStyles.BG_SECONDARY, fg=AppStyles.TEXT_MAIN, font=AppStyles.FONT_BODY).pack(anchor="w", pady=(0, 8))
        vcmd = (self.root.register(self.validate_amount), '%P')
        self.amount_entry = ttk.Entry(form_inner, width=35, style="Large.TEntry", validate="key", validatecommand=vcmd)
        self.amount_entry.pack(fill=tk.X, pady=(0, 25))
        
        # Buttons
        btn_frame = tk.Frame(form_inner, bg=AppStyles.BG_SECONDARY)
        btn_frame.pack(fill=tk.X)
        
        self.add_btn = tk.Button(
            btn_frame, text="Add Expense", command=self.add_expense,
            bg=AppStyles.ACCENT_COLOR, fg=AppStyles.TEXT_ON_DARK,
            font=AppStyles.FONT_HEADER, relief="flat", padx=15, pady=10, cursor="hand2"
        )
        self.add_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.update_btn = tk.Button(
            btn_frame, text="Update", command=self.update_expense,
            bg=AppStyles.SUCCESS_COLOR, fg=AppStyles.TEXT_ON_DARK,
            activebackground=AppStyles.SUCCESS_COLOR, activeforeground=AppStyles.TEXT_ON_DARK,
            disabledforeground="#CCCCCC",
            font=AppStyles.FONT_HEADER, relief="flat", padx=15, pady=10, cursor="hand2",
            state=tk.DISABLED
        )
        self.update_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.clear_btn = tk.Button(
            form_inner, text="Clear Form", command=self.clear_form,
            bg=AppStyles.TEXT_MUTED, fg=AppStyles.TEXT_ON_DARK,
            font=AppStyles.FONT_BODY, relief="flat", pady=8, cursor="hand2"
        )
        self.clear_btn.pack(fill=tk.X, pady=(15, 0))
        
        # Export CSV Button
        self.export_btn = tk.Button(
            form_inner, text="Export to CSV", command=self.export_to_csv,
            bg=AppStyles.PRIMARY_COLOR, fg=AppStyles.TEXT_ON_DARK,
            font=AppStyles.FONT_BODY, relief="flat", pady=8, cursor="hand2"
        )
        self.export_btn.pack(fill=tk.X, pady=(10, 0))

    def setup_toolbar(self):
        """Build the search & filter toolbar above the Treeview."""
        toolbar = tk.Frame(self.table_frame, bg=AppStyles.BG_PRIMARY, pady=8, padx=8)
        toolbar.pack(fill=tk.X, side=tk.TOP)

        # --- Search ---
        tk.Label(
            toolbar, text="🔍 Search:", bg=AppStyles.BG_PRIMARY,
            fg=AppStyles.TEXT_MAIN, font=AppStyles.FONT_BODY
        ).pack(side=tk.LEFT, padx=(0, 6))

        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=22)
        search_entry.pack(side=tk.LEFT, padx=(0, 18))
        self.search_var.trace_add("write", lambda *_: self.refresh_data())

        # --- Category Filter ---
        tk.Label(
            toolbar, text="Filter:", bg=AppStyles.BG_PRIMARY,
            fg=AppStyles.TEXT_MAIN, font=AppStyles.FONT_BODY
        ).pack(side=tk.LEFT, padx=(0, 6))

        filter_combo = ttk.Combobox(
            toolbar,
            textvariable=self.filter_var,
            values=["All", "Food", "Transport", "Utilities", "Entertain", "Health", "Other"],
            width=14,
            state="readonly"
        )
        filter_combo.pack(side=tk.LEFT, padx=(0, 12))
        filter_combo.bind("<<ComboboxSelected>>", lambda _: self.refresh_data())

        # --- Clear Filters ---
        tk.Button(
            toolbar, text="✕ Clear Filters", command=self.clear_filters,
            bg=AppStyles.TEXT_MUTED, fg=AppStyles.TEXT_ON_DARK,
            font=AppStyles.FONT_BODY, relief="flat", padx=10, pady=4, cursor="hand2"
        ).pack(side=tk.LEFT)

    def clear_filters(self):
        """Reset search and filter controls."""
        self.search_var.set("")
        self.filter_var.set("All")
        self.refresh_data()

    def setup_table(self):
        # Set up toolbar first (sits above the Treeview)
        self.setup_toolbar()

        # Table Styling
        style = ttk.Style()
        style.configure("Treeview", font=AppStyles.FONT_BODY, rowheight=35)
        style.configure("Treeview.Heading", font=AppStyles.FONT_HEADER)
        
        # Container for Treeview and Scrollbar
        tree_scroll_frame = tk.Frame(self.table_frame, bg=AppStyles.BG_SECONDARY)
        tree_scroll_frame.pack(fill=tk.BOTH, expand=True)

        # extended selectmode enables Ctrl+Click / Shift+Click multi-select
        self.tree = ttk.Treeview(
            tree_scroll_frame,
            columns=("ID", "Timestamp", "Description", "Category", "Amount"),
            show="headings",
            selectmode="extended"
        )
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_scroll_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.heading("Timestamp", text="Date & Time")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Amount", text="Amount")
        
        self.tree.column("ID", width=0, stretch=tk.NO)
        self.tree.column("Timestamp", width=220, anchor="center", stretch=tk.NO)
        self.tree.column("Description", width=250, minwidth=150, stretch=tk.YES)
        self.tree.column("Category", width=130, anchor="center", stretch=tk.NO)
        self.tree.column("Amount", width=120, anchor="e", stretch=tk.NO)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)
        
        # Bottom bar: Delete button + Total label
        bottom_frame = tk.Frame(self.table_frame, bg=AppStyles.BG_PRIMARY, pady=10)
        bottom_frame.pack(fill=tk.X)
        
        self.delete_btn = tk.Button(
            bottom_frame, text="Delete Selected", command=self.delete_expense,
            bg=AppStyles.DANGER_COLOR, fg=AppStyles.TEXT_ON_DARK,
            font=AppStyles.FONT_BODY, relief="flat", padx=15, pady=5, cursor="hand2"
        )
        self.delete_btn.pack(side=tk.LEFT)

        # Selection info label (shows count when >1 rows selected)
        self.selection_label = tk.Label(
            bottom_frame, text="", font=AppStyles.FONT_BODY,
            bg=AppStyles.BG_PRIMARY, fg=AppStyles.TEXT_MUTED
        )
        self.selection_label.pack(side=tk.LEFT, padx=12)
        
        self.total_label = tk.Label(
            bottom_frame, text="Total: ₱0.00", font=AppStyles.FONT_TITLE,
            bg=AppStyles.BG_PRIMARY, fg=AppStyles.PRIMARY_COLOR
        )
        self.total_label.pack(side=tk.RIGHT)

    def on_item_select(self, event):
        selected = self.tree.selection()
        count = len(selected)

        if count == 0:
            self.selection_label.config(text="")
            return

        if count == 1:
            # Single selection: populate form
            self.selection_label.config(text="")
            values = self.tree.item(selected[0], "values")
            self.selected_id = values[0]

            self.item_entry.delete(0, tk.END)
            self.item_entry.insert(0, values[2])

            self.category_combo.set(values[3])

            amount_clean = values[4].replace("₱", "").replace(",", "")
            self.amount_entry.delete(0, tk.END)
            self.amount_entry.insert(0, amount_clean)

            self.add_btn.config(state=tk.DISABLED)
            self.update_btn.config(state=tk.NORMAL)
        else:
            # Multiple selection: show count, disable form editing
            self.selection_label.config(text=f"{count} rows selected")
            self.selected_id = None
            self.add_btn.config(state=tk.DISABLED)
            self.update_btn.config(state=tk.DISABLED)

    def clear_form(self):
        self.selected_id = None
        self.item_entry.delete(0, tk.END)
        self.category_combo.set("")
        self.amount_entry.delete(0, tk.END)
        
        self.add_btn.config(state=tk.NORMAL)
        self.update_btn.config(state=tk.DISABLED)
        self.selection_label.config(text="")
        self.tree.selection_remove(self.tree.selection())

    def validate_inputs(self):
        item = self.item_entry.get().strip()
        category = self.category_combo.get().strip()
        amount = self.amount_entry.get().strip()
        
        errors = []
        if not item:
            errors.append("- Description cannot be empty or blank.")
        if not category:
            errors.append("- Please select a category.")
        if not amount:
            errors.append("- Amount cannot be empty or blank.")
            
        if errors:
            messagebox.showwarning("Validation Error", "Please fix the following:\n" + "\n".join(errors))
            return None
            
        try:
            amount_val = float(amount)
            if amount_val <= 0:
                messagebox.showwarning("Validation Error", "Amount must be a positive number!")
                return None
        except ValueError:
            messagebox.showwarning("Validation Error", "Amount must be a valid number!")
            return None
            
        return (item, category, amount_val)

    def add_expense(self):
        data = self.validate_inputs()
        if data:
            item, category, amount_val = data

            # --- Duplicate Validation ---
            if self.db.check_duplicate(item, category, amount_val):
                proceed = messagebox.askyesno(
                    "Duplicate Entry",
                    f"A similar expense already exists:\n\n"
                    f"  Description : {item}\n"
                    f"  Category    : {category}\n"
                    f"  Amount      : ₱{amount_val:,.2f}\n\n"
                    "Do you still want to add it?"
                )
                if not proceed:
                    return

            try:
                self.db.add_expense(item, category, amount_val)
                self.refresh_data()
                self.clear_form()
                messagebox.showinfo("Success", "Expense added successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Database error: {str(e)}")

    def update_expense(self):
        if not self.selected_id:
            return
            
        data = self.validate_inputs()
        if data:
            try:
                self.db.update_expense(self.selected_id, *data)
                self.refresh_data()
                self.clear_form()
                messagebox.showinfo("Success", "Expense updated successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Database error: {str(e)}")

    def delete_expense(self):
        """Delete one or more selected expenses."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select at least one item to delete.")
            return

        count = len(selected)
        confirm_msg = (
            f"Are you sure you want to delete {count} expense(s)?"
            if count > 1
            else "Are you sure you want to delete this expense?"
        )

        if messagebox.askyesno("Confirm Delete", confirm_msg):
            try:
                ids = [self.tree.item(row, "values")[0] for row in selected]
                self.db.delete_multiple_expenses(ids)
                self.refresh_data()
                self.clear_form()
            except Exception as e:
                messagebox.showerror("Error", f"Database error: {str(e)}")

    def export_to_csv(self):
        expenses = self.db.fetch_all_expenses()
        if not expenses:
            messagebox.showwarning("Export", "No data to export.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile=f"Expenses_{datetime.now().strftime('%Y%m%d')}"
        )
        
        if file_path:
            try:
                with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(["ID", "Timestamp", "Description", "Category", "Amount"])
                    writer.writerows(expenses)
                messagebox.showinfo("Success", f"Data exported successfully to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")

    def refresh_data(self):
        """Reload the Treeview applying current search and filter values."""
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Read current search/filter state
        search = self.search_var.get()
        category = self.filter_var.get()

        # Fetch from DB with filters applied
        expenses = self.db.fetch_filtered_expenses(
            category=category if category != "All" else None,
            search=search if search.strip() else None
        )

        for exp in expenses:
            try:
                dt_obj = datetime.strptime(exp[1], "%Y-%m-%d %H:%M:%S")
                formatted_date = dt_obj.strftime("%B %d, %Y, %I:%M %p")
            except:
                formatted_date = exp[1]
                
            formatted_amount = f"₱{exp[4]:,.2f}"
            self.tree.insert("", tk.END, values=(exp[0], formatted_date, exp[2], exp[3], formatted_amount))
        
        # Update Total (filtered)
        total = self.db.get_total_expenses(
            category=category if category != "All" else None,
            search=search if search.strip() else None
        )
        self.total_label.config(text=f"Total: ₱{total:,.2f}")

if __name__ == "__main__":
    root = tk.Tk()
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
        
    app = ExpenseTrackerApp(root)
    root.mainloop()
