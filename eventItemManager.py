import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["event_collector"]
events_collection = db["events"]

class EventApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Event Item Manager")
        self.root.geometry("700x550")
        self.root.configure(bg="#f0f0f0")
        
        self.current_event = None
        self.setup_ui()
        self.load_events()
        
    def setup_ui(self):
        header = ttk.Frame(self.root)
        header.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(header, text="Events", font=("Arial", 14, "bold")).pack(side="left")
        ttk.Button(header, text="+ New Event", command=self.new_event).pack(side="right")
        
        self.events_listbox = tk.Listbox(self.root, height=6, bg="white", relief="flat")
        self.events_listbox.pack(fill="both", padx=10, pady=5)
        self.events_listbox.bind("<<ListboxSelect>>", self.on_event_select)
        
        items_header = ttk.Frame(self.root)
        items_header.pack(fill="x", padx=10, pady=(10, 5))
        ttk.Label(items_header, text="Items", font=("Arial", 12, "bold")).pack(side="left")
        ttk.Button(items_header, text="+ Add Item", command=self.add_item).pack(side="right")
        
        self.items_tree = ttk.Treeview(self.root, columns=("needed", "cost", "collected", "total"), height=8)
        self.items_tree.column("#0", width=150)
        self.items_tree.column("needed", width=60)
        self.items_tree.column("cost", width=60)
        self.items_tree.column("collected", width=70)
        self.items_tree.column("total", width=80)
        
        self.items_tree.heading("#0", text="Item")
        self.items_tree.heading("needed", text="Needed")
        self.items_tree.heading("cost", text="$/Each")
        self.items_tree.heading("collected", text="Have")
        self.items_tree.heading("total", text="Total Cost")
        
        self.items_tree.pack(fill="both", padx=10, pady=5)
        
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(buttons_frame, text="Mark Amount Collected", command=self.mark_amount).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Delete Item", command=self.delete_item).pack(side="left", padx=5)
        
        cost_frame = ttk.Frame(self.root)
        cost_frame.pack(fill="x", padx=10, pady=10)
        ttk.Label(cost_frame, text="Total Event Cost:", font=("Arial", 11, "bold")).pack(side="left")
        self.total_cost_label = ttk.Label(cost_frame, text="$0.00", font=("Arial", 11, "bold"), foreground="green")
        self.total_cost_label.pack(side="left", padx=10)
        
        remaining_frame = ttk.Frame(self.root)
        remaining_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(remaining_frame, text="Cost Remaining:", font=("Arial", 11, "bold")).pack(side="left")
        self.remaining_cost_label = ttk.Label(remaining_frame, text="$0.00", font=("Arial", 11, "bold"), foreground="red")
        self.remaining_cost_label.pack(side="left", padx=10)
        
        ttk.Button(self.root, text="Delete Event", command=self.delete_event).pack(pady=10)
    
    def load_events(self):
        self.events_listbox.delete(0, tk.END)
        for event in events_collection.find():
            self.events_listbox.insert(tk.END, event["name"])
    
    def on_event_select(self, event):
        selection = self.events_listbox.curselection()
        if selection:
            event_name = self.events_listbox.get(selection[0])
            self.current_event = events_collection.find_one({"name": event_name})
            self.refresh_items()
    
    def new_event(self):
        name = simpledialog.askstring("New Event", "Event name:")
        if name:
            if events_collection.find_one({"name": name}):
                messagebox.showerror("Error", "Event already exists")
                return
            events_collection.insert_one({"name": name, "items": []})
            self.load_events()
    
    def add_item(self):
        if not self.current_event:
            messagebox.showwarning("Warning", "Select an event first")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Item")
        dialog.geometry("300x200")
        
        ttk.Label(dialog, text="Item Name:").grid(row=0, padx=10, pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Amount Needed:").grid(row=1, padx=10, pady=5)
        needed_entry = ttk.Entry(dialog)
        needed_entry.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Cost per Item:").grid(row=2, padx=10, pady=5)
        cost_entry = ttk.Entry(dialog)
        cost_entry.grid(row=2, column=1, padx=10, pady=5)
        
        def save():
            try:
                item = {
                    "name": name_entry.get(),
                    "needed": int(needed_entry.get()),
                    "cost": float(cost_entry.get()),
                    "collected": 0
                }
                self.current_event["items"].append(item)
                events_collection.update_one({"_id": self.current_event["_id"]}, {"$set": self.current_event})
                self.refresh_items()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid input")
        
        ttk.Button(dialog, text="Save", command=save).grid(row=3, column=0, columnspan=2, pady=10)
    
    def mark_amount(self):
        if not self.current_event:
            messagebox.showwarning("Warning", "Select an event first")
            return
        
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Select an item first")
            return
        
        item_id = selection[0]
        item_index = int(item_id)
        item = self.current_event["items"][item_index]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Mark Amount Collected")
        dialog.geometry("300x150")
        
        ttk.Label(dialog, text=f"Item: {item['name']}", font=("Arial", 10, "bold")).grid(row=0, columnspan=2, padx=10, pady=10)
        
        ttk.Label(dialog, text="Amount Collected:").grid(row=1, padx=10, pady=5)
        collected_entry = ttk.Entry(dialog)
        collected_entry.insert(0, str(item["collected"]))
        collected_entry.grid(row=1, column=1, padx=10, pady=5)
        
        def save():
            try:
                self.current_event["items"][item_index]["collected"] = int(collected_entry.get())
                events_collection.update_one({"_id": self.current_event["_id"]}, {"$set": self.current_event})
                self.refresh_items()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid input")
        
        ttk.Button(dialog, text="Save", command=save).grid(row=2, column=0, columnspan=2, pady=10)
    
    def delete_item(self):
        if not self.current_event:
            messagebox.showwarning("Warning", "Select an event first")
            return
        
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Select an item first")
            return
        
        item_id = selection[0]
        item_index = int(item_id)
        item_name = self.current_event["items"][item_index]["name"]
        
        if messagebox.askyesno("Delete", f"Delete '{item_name}'?"):
            self.current_event["items"].pop(item_index)
            events_collection.update_one({"_id": self.current_event["_id"]}, {"$set": self.current_event})
            self.refresh_items()
    
    def delete_event(self):
        if not self.current_event:
            messagebox.showwarning("Warning", "Select an event first")
            return
        if messagebox.askyesno("Delete", f"Delete '{self.current_event['name']}'?"):
            events_collection.delete_one({"_id": self.current_event["_id"]})
            self.current_event = None
            self.load_events()
            self.refresh_items()
    
    def refresh_items(self):
        self.items_tree.delete(*self.items_tree.get_children())
        total_cost = 0
        remaining_cost = 0
        
        if self.current_event:
            for idx, item in enumerate(self.current_event["items"]):
                total = item["needed"] * item["cost"]
                collected_cost = item["collected"] * item["cost"]
                remaining = (item["needed"] - item["collected"]) * item["cost"]
                
                total_cost += total
                remaining_cost += max(0, remaining)
                
                self.items_tree.insert("", "end", iid=idx, text=item["name"],
                    values=(item["needed"], f"${item['cost']:.2f}", item["collected"], f"${total:.2f}"))
        
        self.total_cost_label.config(text=f"${total_cost:.2f}")
        self.remaining_cost_label.config(text=f"${remaining_cost:.2f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = EventApp(root)
    root.mainloop()
