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
        
        self.db = Database()
        self.selected_id = None
        
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
        self.main_container.grid_columnconfigure(1, weight=3) # Give more weight to the table area
        self.main_container.grid_rowconfigure(1, weight=1)

    def setup_form(self):
        # Configure Style for larger entries
        style = ttk.Style()
        style.configure("Large.TEntry", padding=AppStyles.ENTRY_PADDING)
        style.configure("Large.TCombobox", padding=AppStyles.ENTRY_PADDING)

        form_inner = tk.Frame(self.form_frame, bg=AppStyles.BG_SECONDARY, padx=30, pady=30)
        form_inner.pack(fill=tk.BOTH, expand=True)
        
        # Removed Date Entry as it's now automatic
        
        # Item
        tk.Label(form_inner, text="Description", bg=AppStyles.BG_SECONDARY, fg=AppStyles.TEXT_MAIN, font=AppStyles.FONT_BODY).pack(anchor="w", pady=(0, 8))
        self.item_entry = ttk.Entry(form_inner, width=35, style="Large.TEntry")
        self.item_entry.pack(fill=tk.X, pady=(0, 20))
        
        # Category
        tk.Label(form_inner, text="Category", bg=AppStyles.BG_SECONDARY, fg=AppStyles.TEXT_MAIN, font=AppStyles.FONT_BODY).pack(anchor="w", pady=(0, 8))
        self.category_combo = ttk.Combobox(form_inner, values=["Food", "Transport", "Utilities", "Entertain", "Health", "Other"], width=33, style="Large.TCombobox")
        self.category_combo.pack(fill=tk.X, pady=(0, 20))
        
        # Amount
        tk.Label(form_inner, text="Amount (₱)", bg=AppStyles.BG_SECONDARY, fg=AppStyles.TEXT_MAIN, font=AppStyles.FONT_BODY).pack(anchor="w", pady=(0, 8))
        self.amount_entry = ttk.Entry(form_inner, width=35, style="Large.TEntry")
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
            disabledforeground="#CCCCCC", # Light gray when disabled, white when active
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

    def setup_table(self):
        # Table Styling
        style = ttk.Style()
        style.configure("Treeview", font=AppStyles.FONT_BODY, rowheight=35) # Increased rowheight
        style.configure("Treeview.Heading", font=AppStyles.FONT_HEADER)
        
        # Container for Treeview and Scrollbar
        tree_scroll_frame = tk.Frame(self.table_frame, bg=AppStyles.BG_SECONDARY)
        tree_scroll_frame.pack(fill=tk.BOTH, expand=True)

        # ID is still in columns but not in show="headings" logic or shown visually
        self.tree = ttk.Treeview(tree_scroll_frame, columns=("ID", "Timestamp", "Description", "Category", "Amount"), show="headings")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_scroll_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # self.tree.heading("ID", text="ID") # Removed
        self.tree.heading("Timestamp", text="Date & Time")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Amount", text="Amount")
        
        self.tree.column("ID", width=0, stretch=tk.NO) # Hide ID column
        self.tree.column("Timestamp", width=220, anchor="center", stretch=tk.NO)
        self.tree.column("Description", width=250, minwidth=150, stretch=tk.YES)
        self.tree.column("Category", width=130, anchor="center", stretch=tk.NO)
        self.tree.column("Amount", width=120, anchor="e", stretch=tk.NO)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)
        
        # Delete Button and Total
        bottom_frame = tk.Frame(self.table_frame, bg=AppStyles.BG_PRIMARY, pady=10)
        bottom_frame.pack(fill=tk.X)
        
        self.delete_btn = tk.Button(
            bottom_frame, text="Delete Selected", command=self.delete_expense,
            bg=AppStyles.DANGER_COLOR, fg=AppStyles.TEXT_ON_DARK,
            font=AppStyles.FONT_BODY, relief="flat", padx=15, pady=5, cursor="hand2"
        )
        self.delete_btn.pack(side=tk.LEFT)
        
        self.total_label = tk.Label(
            bottom_frame, text="Total: ₱0.00", font=AppStyles.FONT_TITLE,
            bg=AppStyles.BG_PRIMARY, fg=AppStyles.PRIMARY_COLOR
        )
        self.total_label.pack(side=tk.RIGHT)

    def on_item_select(self, event):
        selected = self.tree.focus()
        if not selected:
            return
            
        values = self.tree.item(selected, "values")
        self.selected_id = values[0]
        
        # values[1] is Timestamp, no entry for it now
        
        self.item_entry.delete(0, tk.END)
        self.item_entry.insert(0, values[2])
        
        self.category_combo.set(values[3])
        
        # Clean amount string for entry
        amount_clean = values[4].replace("₱", "").replace(",", "")
        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, amount_clean)
        
        self.add_btn.config(state=tk.DISABLED)
        self.update_btn.config(state=tk.NORMAL)

    def clear_form(self):
        self.selected_id = None
        self.item_entry.delete(0, tk.END)
        self.category_combo.set("")
        self.amount_entry.delete(0, tk.END)
        
        self.add_btn.config(state=tk.NORMAL)
        self.update_btn.config(state=tk.DISABLED)
        self.tree.selection_remove(self.tree.selection())

    def validate_inputs(self):
        item = self.item_entry.get().strip()
        category = self.category_combo.get().strip()
        amount = self.amount_entry.get().strip()
        
        if not all([item, category, amount]):
            messagebox.showwarning("Validation Error", "All fields are required!")
            return None
            
        try:
            amount_val = float(amount)
            if amount_val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation Error", "Amount must be a positive number!")
            return None
            
        return (item, category, amount_val)

    def add_expense(self):
        data = self.validate_inputs()
        if data:
            try:
                self.db.add_expense(*data)
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
        if not self.selected_id:
            messagebox.showwarning("Selection", "Please select an item to delete.")
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this expense?"):
            try:
                self.db.delete_expense(self.selected_id)
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
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Fetch from DB
        expenses = self.db.fetch_all_expenses()
        for exp in expenses:
            # Format timestamp: SQLite format "YYYY-MM-DD HH:MM:SS" -> "January 22, 2026, 01:56 PM"
            try:
                dt_obj = datetime.strptime(exp[1], "%Y-%m-%d %H:%M:%S")
                formatted_date = dt_obj.strftime("%B %d, %Y, %I:%M %p")
            except:
                formatted_date = exp[1] # Fallback
                
            # Format amount as currency
            formatted_amount = f"₱{exp[4]:,.2f}"
            self.tree.insert("", tk.END, values=(exp[0], formatted_date, exp[2], exp[3], formatted_amount))
            
        # Update Total
        total = self.db.get_total_expenses()
        self.total_label.config(text=f"Total: ₱{total:,.2f}")

if __name__ == "__main__":
    root = tk.Tk()
    # Simple fix for blurry text on high DPI Windows displays
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
        
    app = ExpenseTrackerApp(root)
    root.mainloop()
