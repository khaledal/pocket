# improved_tracker.py

import tkinter as tk
from tkinter import messagebox, filedialog, Canvas
import csv
from collections import defaultdict, Counter
from datetime import datetime
import os
import re
from PIL import Image, ImageTk, ImageDraw
import io
from math import sin, cos, pi
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class SlotTracker:
    """
    A class to track and analyze probabilities between start and end slots.
    """
    
    def __init__(self, root):
        """
        Initialize the SlotTracker application.
        
        Args:
            root: The tkinter root window
        """
        self.root = root
        self.root.title("Start-End Slot Probability Tracker")
        self.root.configure(bg="#121212")  # Matte black background
        
        # Define color scheme
        self.colors = {
            "bg": "#121212",            # Matte black
            "accent": "#d0d0d0",        # Light gray
            "gold": "#d4af37",          # Golden
            "gold_light": "#f5d76e",    # Light golden
            "button_bg": "#1d1d1d",     # Slightly lighter than bg
            "text": "#f5f5f5"           # Almost white
        }
        
        # Create corner decorations
        self.create_corner_decorations()
        
        # Constants and default values
        self.DATA_FILE = "data.csv"
        self.slots = {
            1: "Melon",
            2: "Orange",
            3: "Apple",
            4: "Lettuce",
            5: "Fish",
            6: "Burger",
            7: "Shrimp",
            8: "Chicken"
        }
        
        # Data storage
        self.start_counter = defaultdict(int)
        self.end_counter = defaultdict(int)
        self.history_data = []
        self.total_rounds = 0
        self.selected_start = None
        self.selected_end = None
        
        # Load existing data
        self.load_data()
        
        # Set up the UI
        self.setup_ui()
        
        # Update the report
        self.update_report()
    
    def load_data(self):
        """Load historical data from the CSV file if it exists."""
        if not os.path.exists(self.DATA_FILE):
            return
            
        try:
            with open(self.DATA_FILE, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    try:
                        start = int(row[0])
                        end = int(row[1])
                        if start in self.slots and end in self.slots:
                            self.start_counter[start] += 1
                            self.end_counter[end] += 1
                            self.history_data.append((start, end))
                            self.total_rounds += 1
                    except (ValueError, IndexError) as e:
                        print(f"Error processing row {row}: {e}")
                        continue
        except IOError as e:
            messagebox.showerror("Error", f"Could not load data: {e}")
    
    def save_round(self, start, end):
        """
        Save a single round to the CSV file.
        
        Args:
            start: The starting slot number
            end: The ending slot number
        """
        try:
            with open(self.DATA_FILE, mode='a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([start, end])
        except IOError as e:
            messagebox.showerror("Error", f"Could not save data: {e}")
    
    def calculate_percentages(self, counter):
        """
        Calculate the percentage of each slot occurrence relative to total rounds.
        
        Args:
            counter: A dictionary with slot IDs as keys and counts as values
        
        Returns:
            Dictionary with slot IDs as keys and percentage values (0-100) as values
        """
        if self.total_rounds == 0:
            return {i: 0.0 for i in range(1, 9)}
        return {slot: (count / self.total_rounds) * 100 for slot, count in counter.items()}
    
    def update_report(self):
        """Update the statistics report display with current data."""
        start_stats = self.calculate_percentages(self.start_counter)
        end_stats = self.calculate_percentages(self.end_counter)

        report_text = f"Total Rounds: {self.total_rounds}\n\n"
        report_text += "Start Slot Percentages:\n"
        for i in range(1, 9):
            report_text += f"{self.slots[i]}: {start_stats.get(i, 0):.2f}%\n"
        report_text += "\nEnd Slot Percentages:\n"
        for i in range(1, 9):
            report_text += f"{self.slots[i]}: {end_stats.get(i, 0):.2f}%\n"

        self.report_label.config(text=report_text)
    
    def handle_selection(self, slot_index, selection_type):
        """
        Handle slot selection for start or end positions.
        
        Args:
            slot_index: The selected slot number
            selection_type: Either "start" or "end"
        """
        if selection_type == "start":
            self.selected_start = slot_index
            self.start_selected_label.config(text=f"Start: {self.slots[slot_index]}")
        elif selection_type == "end":
            self.selected_end = slot_index
            self.end_selected_label.config(text=f"End: {self.slots[slot_index]}")
    
    def register_round(self):
        """Record a new round with the selected start and end slots."""
        if self.selected_start is None or self.selected_end is None:
            messagebox.showerror("Error", "Start and End slots must be selected.")
            return
            
        start = self.selected_start
        end = self.selected_end
        
        # Update data structures
        self.start_counter[start] += 1
        self.end_counter[end] += 1
        self.history_data.append((start, end))
        self.total_rounds += 1
        
        # Save to file
        self.save_round(start, end)
        
        # Update UI
        self.update_report()
        messagebox.showinfo("Success", "Round recorded successfully.")
        
        # Reset selections
        self.selected_start = None
        self.selected_end = None
        self.start_selected_label.config(text="Start: Not selected")
        self.end_selected_label.config(text="End: Not selected")
    
    def create_corner_decorations(self):
        """Create golden corner decorations for a modern look."""
        # Create a canvas that covers the entire window
        self.decoration_canvas = tk.Canvas(self.root, bg=self.colors["bg"], highlightthickness=0)
        self.decoration_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Draw golden corners
        corner_size = 50
        line_width = 2
        
        # Function to create corner paths
        def draw_corners():
            # Clear previous decorations
            self.decoration_canvas.delete("corner")
            
            # Update canvas size
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            self.decoration_canvas.config(width=width, height=height)
            
            # Top-left corner
            self.decoration_canvas.create_line(
                0, corner_size, 0, 0, corner_size, 0, 
                fill=self.colors["gold"], width=line_width, tags="corner"
            )
            
            # Top-right corner
            self.decoration_canvas.create_line(
                width-corner_size, 0, width, 0, width, corner_size, 
                fill=self.colors["gold"], width=line_width, tags="corner"
            )
            
            # Bottom-left corner
            self.decoration_canvas.create_line(
                0, height-corner_size, 0, height, corner_size, height, 
                fill=self.colors["gold"], width=line_width, tags="corner"
            )
            
            # Bottom-right corner
            self.decoration_canvas.create_line(
                width-corner_size, height, width, height, width, height-corner_size, 
                fill=self.colors["gold"], width=line_width, tags="corner"
            )
            
            # Add some decorative dots at the corners
            dot_radius = 3
            for x, y in [(corner_size, corner_size), (width-corner_size, corner_size), 
                         (corner_size, height-corner_size), (width-corner_size, height-corner_size)]:
                self.decoration_canvas.create_oval(
                    x-dot_radius, y-dot_radius, x+dot_radius, y+dot_radius,
                    fill=self.colors["gold_light"], outline="", tags="corner"
                )
        
        # Initial draw (will be empty until window is fully loaded)
        draw_corners()
        
        # Update corners when window is resized or fully loaded
        def update_corners(event=None):
            self.root.after(100, draw_corners)  # Slight delay to ensure window dimensions are updated
        
        self.root.bind("<Configure>", update_corners)
        self.root.after(200, update_corners)  # Initial update after window loads
        
    def create_slot_buttons(self, parent, row, selection_type):
        """
        Create a row of slot selection buttons.
        
        Args:
            parent: The parent frame
            row: The grid row for placing buttons
            selection_type: Either "start" or "end"
        """
        button_frame = tk.Frame(parent, bg=self.colors["bg"])
        button_frame.grid(row=row, column=0, columnspan=8, sticky="w")
        
        # Create a modern button style with hover effects
        for i in range(1, 9):
            # Create a frame for each button to add a subtle border effect
            btn_container = tk.Frame(
                button_frame,
                bg=self.colors["gold"] if selection_type == "start" else self.colors["accent"],
                padx=1,
                pady=1
            )
            btn_container.grid(row=0, column=i-1, padx=5, pady=5)
            
            # Create the actual button
            btn = tk.Button(
                btn_container,
                text=self.slots[i],
                width=9,
                font=("Helvetica", 12),
                bg=self.colors["button_bg"],
                fg=self.colors["gold"] if selection_type == "start" else self.colors["accent"],
                activebackground=self.colors["gold"] if selection_type == "start" else self.colors["accent"],
                activeforeground=self.colors["bg"],
                relief=tk.FLAT,
                borderwidth=0,
                command=lambda idx=i, type=selection_type: self.handle_selection(idx, type)
            )
            btn.pack(padx=0, pady=0)
            
            # Add hover effect
            color = self.colors["gold"] if selection_type == "start" else self.colors["accent"]
            btn.bind("<Enter>", lambda e, b=btn, c=color: b.config(bg=c, fg=self.colors["bg"]))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=self.colors["button_bg"], fg=c))
    
    def open_analysis_window(self):
        """Open a new window for analyzing top end slots for each start slot."""
        analysis_window = tk.Toplevel(self.root)
        analysis_window.title("Top 5 End Slots by Start Slot")
        analysis_window.configure(bg=self.colors["bg"])
        
        tk.Label(
            analysis_window, 
            text="Select a Start Slot to Analyze:", 
            font=("Helvetica", 14, "bold"), 
            bg=self.colors["bg"], 
            fg=self.colors["gold"]
        ).pack(pady=10)
        
        # Show progress indicator
        progress_label = tk.Label(
            analysis_window, 
            text="Ready to analyze...", 
            fg=self.colors["text"], 
            bg=self.colors["bg"]
        )
        progress_label.pack(pady=5)
        
        # Add result area
        result_frame = tk.Frame(analysis_window, bg=self.colors["bg"])
        result_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Preprocess data for faster analysis
        self.preprocess_data()
        
        # Create buttons for each slot
        button_frame = tk.Frame(analysis_window, bg=self.colors["bg"])
        button_frame.pack(pady=5)
        
        for i in range(1, 9):
            # Create a frame for each button to add a subtle border effect
            btn_container = tk.Frame(
                button_frame,
                bg=self.colors["gold"],
                padx=1,
                pady=1
            )
            btn_container.pack(side=tk.LEFT, padx=3, pady=3)
            
            # Create the actual button
            btn = tk.Button(
                btn_container,
                text=self.slots[i],
                width=10,
                font=("Helvetica", 12),
                bg=self.colors["button_bg"],
                fg=self.colors["gold"],
                activebackground=self.colors["gold"],
                activeforeground=self.colors["bg"],
                relief=tk.FLAT,
                borderwidth=0,
                command=lambda idx=i, frame=result_frame: self.show_top_5_end_slots(idx, frame)
            )
            btn.pack(padx=0, pady=0)
            
            # Add hover effect
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.colors["gold"], fg=self.colors["bg"]))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.colors["button_bg"], fg=self.colors["gold"]))
    
    def preprocess_data(self):
        """Preprocess data for faster analysis queries."""
        if not hasattr(self, 'start_slot_mapping'):
            self.start_slot_mapping = defaultdict(list)
            for s, e in self.history_data:
                self.start_slot_mapping[s].append(e)
    
    def show_top_5_end_slots(self, start_slot, parent_frame):
        """
        Display the top 5 most common end slots for a given start slot,
        with the first 3 in different colors.
        
        Args:
            start_slot: The starting slot number to analyze
            parent_frame: The frame where results should be displayed
        """
        # Clear previous results
        for widget in parent_frame.winfo_children():
            widget.destroy()
            
        # Get end slots for this start slot
        end_slots = self.start_slot_mapping.get(start_slot, [])
        end_counts = Counter(end_slots)
        most_common = end_counts.most_common(5)  # Get top 5 instead of top 3
    
        # Display results header
        header_label = tk.Label(
            parent_frame, 
            text=f"Top 5 End Slots for Start Slot '{self.slots[start_slot]}':", 
            font=("Helvetica", 14, "bold"), 
            justify=tk.LEFT, 
            fg=self.colors["gold"], 
            bg=self.colors["bg"]
        )
        header_label.pack(pady=(10, 5), anchor="w")
        
        # Create a frame for the results
        results_container = tk.Frame(parent_frame, bg=self.colors["bg"])
        results_container.pack(fill="both", expand=True, padx=10)
        
        # Display results with different colors for the first 3
        if most_common:
            # Define colors for the top 3 positions
            position_colors = {
                1: "#FFD700",  # Gold for 1st place
                2: "#C0C0C0",  # Silver for 2nd place
                3: "#CD7F32",  # Bronze for 3rd place
            }
            
            for idx, (slot, count) in enumerate(most_common, 1):
                percentage = (count / len(end_slots) * 100) if end_slots else 0
                
                # Create a frame for each result row
                row_frame = tk.Frame(results_container, bg=self.colors["bg"])
                row_frame.pack(fill="x", pady=2, anchor="w")
                
                # Position number with special color for top 3
                if idx <= 3:
                    position_label = tk.Label(
                        row_frame, 
                        text=f"{idx}.", 
                        font=("Helvetica", 12, "bold"), 
                        width=2,
                        fg=position_colors[idx], 
                        bg=self.colors["bg"]
                    )
                else:
                    position_label = tk.Label(
                        row_frame, 
                        text=f"{idx}.", 
                        font=("Helvetica", 12), 
                        width=2,
                        fg=self.colors["accent"], 
                        bg=self.colors["bg"]
                    )
                position_label.pack(side="left", padx=(0, 5))
                
                # Slot name with special color for top 3
                if idx <= 3:
                    slot_label = tk.Label(
                        row_frame, 
                        text=f"{self.slots[slot]}", 
                        font=("Helvetica", 12, "bold"), 
                        fg=position_colors[idx], 
                        bg=self.colors["bg"]
                    )
                else:
                    slot_label = tk.Label(
                        row_frame, 
                        text=f"{self.slots[slot]}", 
                        font=("Helvetica", 12), 
                        fg=self.colors["accent"], 
                        bg=self.colors["bg"]
                    )
                slot_label.pack(side="left", padx=(0, 5))
                
                # Count and percentage
                stats_label = tk.Label(
                    row_frame, 
                    text=f"- {count} times ({percentage:.2f}%)", 
                    font=("Helvetica", 12), 
                    fg=self.colors["text"] if idx > 3 else position_colors[idx], 
                    bg=self.colors["bg"]
                )
                stats_label.pack(side="left")
        else:
            no_data_label = tk.Label(
                results_container, 
                text="No data available.", 
                font=("Helvetica", 12, "italic"), 
                fg=self.colors["accent"], 
                bg=self.colors["bg"]
            )
            no_data_label.pack(pady=10)
        
        # Add a visualization if we have data
        if most_common:
            self.create_chart(parent_frame, start_slot, most_common)

    def show_top_3_end_slots(self, start_slot, parent_frame):
        """Legacy method - redirects to show_top_5_end_slots"""
        self.show_top_5_end_slots(start_slot, parent_frame)
    
    def create_chart(self, parent_frame, start_slot, data):
        """
        Create a bar chart visualization of the data.
        
        Args:
            parent_frame: The frame where chart should be displayed
            start_slot: The starting slot being analyzed
            data: List of (slot, count) tuples
        """
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor(self.colors["bg"])
        ax.set_facecolor('#2d2d2d')
        
        # Define colors for the top 3 positions
        position_colors = {
            0: "#FFD700",  # Gold for 1st place
            1: "#C0C0C0",  # Silver for 2nd place
            2: "#CD7F32",  # Bronze for 3rd place
        }
        
        # Plot data
        labels = [self.slots[slot] for slot, _ in data]
        values = [count for _, count in data]
        
        # Create a list of colors for the bars
        bar_colors = [position_colors.get(i, self.colors["accent"]) for i in range(len(data))]
        
        # Create the bars with different colors
        bars = ax.bar(labels, values, color=bar_colors)
        
        # Set labels and title
        ax.set_title(f'Top 5 End Slots for {self.slots[start_slot]}', color=self.colors["text"])
        ax.set_ylabel('Count', color=self.colors["text"])
        ax.tick_params(colors=self.colors["text"])
        
        # Add value labels on bars
        for i, bar in enumerate(bars):
            height = bar.get_height()
            # Use the same color as the bar for the text
            text_color = position_colors.get(i, self.colors["text"]) if i < 3 else self.colors["text"]
            ax.annotate(f'{height}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        color=text_color,
                        fontweight='bold' if i < 3 else 'normal')
        
        # Embed in Tkinter
        chart_frame = tk.Frame(parent_frame, bg=self.colors["bg"])
        chart_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def reset_data(self):
        """Reset all data after confirmation."""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all data? This cannot be undone."):
            # Clear data structures
            self.start_counter = defaultdict(int)
            self.end_counter = defaultdict(int)
            self.history_data = []
            self.total_rounds = 0
            if hasattr(self, 'start_slot_mapping'):
                delattr(self, 'start_slot_mapping')
            
            # Backup existing file
            if os.path.exists(self.DATA_FILE):
                try:
                    backup_file = f"{self.DATA_FILE}.backup"
                    if os.path.exists(backup_file):
                        os.remove(backup_file)
                    os.rename(self.DATA_FILE, backup_file)
                    messagebox.showinfo("Backup Created", f"Your previous data was backed up to {backup_file}")
                except OSError as e:
                    messagebox.showwarning("Backup Failed", f"Could not back up data: {e}")
            
            # Create empty file
            try:
                with open(self.DATA_FILE, 'w', newline='', encoding='utf-8') as _:
                    pass
            except IOError as e:
                messagebox.showerror("Error", f"Could not create new data file: {e}")
                
            # Update UI
            self.update_report()
            messagebox.showinfo("Reset Complete", "All data has been reset.")
    
    def export_data(self):
        """Export analysis results to a text file."""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Export Analysis Results"
            )
            
            if not file_path:
                return  # User cancelled
                
            with open(file_path, 'w', encoding='utf-8') as f:
                # Overall statistics
                f.write(f"Start-End Slot Probability Analysis\n")
                f.write(f"================================\n\n")
                f.write(f"Total Rounds: {self.total_rounds}\n\n")
                
                # Start slot percentages
                start_stats = self.calculate_percentages(self.start_counter)
                f.write("Start Slot Percentages:\n")
                f.write("---------------------\n")
                for i in range(1, 9):
                    f.write(f"{self.slots[i]}: {start_stats.get(i, 0):.2f}%\n")
                f.write("\n")
                
                # End slot percentages
                end_stats = self.calculate_percentages(self.end_counter)
                f.write("End Slot Percentages:\n")
                f.write("-------------------\n")
                for i in range(1, 9):
                    f.write(f"{self.slots[i]}: {end_stats.get(i, 0):.2f}%\n")
                f.write("\n")
                
                # Detailed analysis for each start slot
                f.write("Detailed Analysis by Start Slot:\n")
                f.write("==============================\n\n")
                
                # Preprocess data if needed
                self.preprocess_data()
                
                for start_slot in range(1, 9):
                    f.write(f"Start Slot: {self.slots[start_slot]}\n")
                    f.write("-" * (len(f"Start Slot: {self.slots[start_slot]}")) + "\n")
                    
                    end_slots = self.start_slot_mapping.get(start_slot, [])
                    if end_slots:
                        total = len(end_slots)
                    f.write("\n")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not export data: {e}")
        else:
            messagebox.showinfo("Export Complete", f"Analysis results exported to {file_path}")
    
    def setup_ui(self):
        """Set up the application user interface."""
        # Main container frame with gradient background effect
        main_frame = tk.Frame(self.root, padx=20, pady=20, bg=self.colors["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a modern header with accent line
        header_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        header_frame.grid(row=0, column=0, columnspan=8, sticky="ew", pady=(0, 15))
        
        # App title with golden accent
        title_label = tk.Label(
            header_frame,
            text="SLOT TRACKER",
            font=("Helvetica", 18, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["gold"]
        )
        title_label.pack(anchor="w")
        
        # Accent line under title
        accent_canvas = tk.Canvas(header_frame, height=3, bg=self.colors["bg"], highlightthickness=0)
        accent_canvas.pack(fill="x", pady=(2, 10))
        
        # Create gradient line
        def draw_accent_line():
            width = accent_canvas.winfo_width()
            if width > 1:  # Ensure canvas has been rendered
                accent_canvas.delete("line")
                for i in range(width):
                    # Create gradient from gold to gray and back
                    if i < width/2:
                        ratio = i/(width/2)
                    else:
                        ratio = 2 - i/(width/2)
                        
                    # Mix colors based on position
                    r = int(int(self.colors["gold"][1:3], 16) * ratio + int(self.colors["accent"][1:3], 16) * (1-ratio))
                    g = int(int(self.colors["gold"][3:5], 16) * ratio + int(self.colors["accent"][3:5], 16) * (1-ratio))
                    b = int(int(self.colors["gold"][5:7], 16) * ratio + int(self.colors["accent"][5:7], 16) * (1-ratio))
                    
                    color = f"#{r:02x}{g:02x}{b:02x}"
                    accent_canvas.create_line(i, 0, i, 3, fill=color, tags="line")
        
        accent_canvas.bind("<Configure>", lambda e: draw_accent_line())
        
        # Start slot selection with modern styling
        start_label = tk.Label(
            main_frame, 
            text="Select Start Slot:", 
            font=("Helvetica", 14, "bold"), 
            bg=self.colors["bg"], 
            fg=self.colors["gold"]
        )
        start_label.grid(row=1, column=0, columnspan=8, pady=(0, 5), sticky="w")
    
        self.create_slot_buttons(main_frame, 2, "start")
        
        # Create a modern indicator for selection
        start_indicator_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        start_indicator_frame.grid(row=3, column=0, columnspan=8, sticky="w", pady=(5, 15))
        
        self.start_selected_label = tk.Label(
            start_indicator_frame, 
            text="Start: Not selected", 
            fg=self.colors["accent"], 
            bg=self.colors["bg"], 
            font=("Helvetica", 12)
        )
        self.start_selected_label.pack(side="left")
        
        # End slot selection with consistent styling
        end_label = tk.Label(
            main_frame, 
            text="Select End Slot:", 
            font=("Helvetica", 14, "bold"), 
            bg=self.colors["bg"], 
            fg=self.colors["gold"]
        )
        end_label.grid(row=4, column=0, columnspan=8, pady=(10, 5), sticky="w")
        
        self.create_slot_buttons(main_frame, 5, "end")
        
        # End selection indicator with matching style
        end_indicator_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        end_indicator_frame.grid(row=6, column=0, columnspan=8, sticky="w", pady=(5, 15))
        
        self.end_selected_label = tk.Label(
            end_indicator_frame, 
            text="End: Not selected", 
            fg=self.colors["accent"], 
            bg=self.colors["bg"], 
            font=("Helvetica", 12)
        )
        self.end_selected_label.pack(side="left")
        
        # Action buttons with modern styling
        button_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        button_frame.grid(row=7, column=0, columnspan=8, pady=(20, 15))
        
        # Create modern buttons with hover effect
        register_button = tk.Button(
            button_frame,
            text="Register Round",
            bg=self.colors["button_bg"],
            fg=self.colors["gold"],
            font=("Helvetica", 14),
            activebackground=self.colors["gold"],
            activeforeground=self.colors["bg"],
            relief=tk.FLAT,
            borderwidth=0,
            padx=15,
            pady=8,
            command=self.register_round
        )
        register_button.grid(row=0, column=0, padx=10)
        
        # Add hover effect
        def on_enter(e, button, bg, fg):
            button.config(background=fg, foreground=bg)
        
        def on_leave(e, button, bg, fg):
            button.config(background=bg, foreground=fg)
            
        register_button.bind("<Enter>", lambda e: on_enter(e, register_button, self.colors["button_bg"], self.colors["gold"]))
        register_button.bind("<Leave>", lambda e: on_leave(e, register_button, self.colors["button_bg"], self.colors["gold"]))
        
        analyze_button = tk.Button(
            button_frame,
            text="Analyze Top 3 End Slots",
            bg=self.colors["button_bg"],
            fg=self.colors["accent"],
            font=("Helvetica", 14),
            activebackground=self.colors["accent"],
            activeforeground=self.colors["bg"],
            relief=tk.FLAT,
            borderwidth=0,
            padx=15,
            pady=8,
            command=self.open_analysis_window
        )
        analyze_button.grid(row=0, column=1, padx=10)

        analyze_button.bind("<Enter>", lambda e: on_enter(e, analyze_button, self.colors["button_bg"], self.colors["accent"]))
        analyze_button.bind("<Leave>", lambda e: on_leave(e, analyze_button, self.colors["button_bg"], self.colors["accent"]))

        # Add management buttons with consistent styling
        management_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        management_frame.grid(row=8, column=0, columnspan=8, pady=(10, 15))

        export_button = tk.Button(
            management_frame,
            text="Export Results",
            bg=self.colors["button_bg"],
            fg=self.colors["accent"],
            font=("Helvetica", 12),
            activebackground=self.colors["accent"],
            activeforeground=self.colors["bg"],
            relief=tk.FLAT,
            borderwidth=0,
            padx=12,
            pady=6,
            command=self.export_data
        )
        export_button.grid(row=0, column=0, padx=8)

        export_button.bind("<Enter>", lambda e: on_enter(e, export_button, self.colors["button_bg"], self.colors["accent"]))
        export_button.bind("<Leave>", lambda e: on_leave(e, export_button, self.colors["button_bg"], self.colors["accent"]))

        reset_button = tk.Button(
            management_frame,
            text="Reset All Data",
            bg=self.colors["button_bg"],
            fg="#ff6b6b",  # Red color for warning
            font=("Helvetica", 12),
            activebackground="#ff6b6b",
            activeforeground=self.colors["bg"],
            relief=tk.FLAT,
            borderwidth=0,
            padx=12,
            pady=6,
            command=self.reset_data
        )
        reset_button.grid(row=0, column=1, padx=8)

        reset_button.bind("<Enter>", lambda e: on_enter(e, reset_button, self.colors["button_bg"], "#ff6b6b"))
        reset_button.bind("<Leave>", lambda e: on_leave(e, reset_button, self.colors["button_bg"], "#ff6b6b"))

        # Create a modern frame for statistics report
        report_frame = tk.Frame(self.root, bg=self.colors["bg"], padx=15, pady=15)
        report_frame.pack(fill="x", pady=(5, 20))

        # Add a subtle header for the stats section
        stats_header = tk.Label(
            report_frame,
            text="STATISTICS",
            font=("Helvetica", 12, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["gold"]
        )
        stats_header.pack(anchor="w")

        # Add a subtle separator line
        separator = tk.Frame(report_frame, height=2, bg=self.colors["accent"])
        separator.pack(fill="x", pady=(2, 10))

        # Statistics report with modern monospace font
        self.report_label = tk.Label(
            report_frame,
            text="",
            justify=tk.LEFT,
            font=("Consolas", 12),  # Modern monospace font
            bg=self.colors["bg"],
            fg=self.colors["text"],
            anchor="w"
        )
        self.report_label.pack(fill="x")

def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = SlotTracker(root)
    root.mainloop()


if __name__ == "__main__":
    main()