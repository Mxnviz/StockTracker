import customtkinter as ctk
from yahoo_fin import stock_info
import tkinter as tk
from tkinter import messagebox
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from datetime import datetime, timedelta

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ModernStockTracker(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure main window
        self.title("Stock Tracker")
        self.geometry("1200x800")
        
        # Initialize variables
        self.current_symbol = None
        self.users = {"admin": "password"}  # Default user for login
        
        # Create main container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Initialize frames
        self.create_login_frame()
        self.create_signup_frame()
        self.create_main_frame()
        
        # Show login frame initially
        self.show_login_frame()

    def create_login_frame(self):
        self.login_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        
        # Center login content
        login_content = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        login_content.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Login header
        ctk.CTkLabel(login_content, text="STOCK TRACKER", font=ctk.CTkFont(size=32, weight="bold")).pack(pady=(0, 40))
        
        # Login fields
        self.username_entry = ctk.CTkEntry(login_content, width=300, height=50, placeholder_text="Username")
        self.username_entry.pack(pady=10)
        
        self.password_entry = ctk.CTkEntry(login_content, width=300, height=50, placeholder_text="Password", show="●")
        self.password_entry.pack(pady=10)
        
        # Login button
        ctk.CTkButton(login_content, text="Login", width=300, height=50, font=ctk.CTkFont(size=15, weight="bold"),
                     command=self.login).pack(pady=20)
        
        # Signup button
        ctk.CTkButton(login_content, text="Sign Up", width=300, height=50, font=ctk.CTkFont(size=15, weight="bold"),
                     command=self.show_signup_frame).pack(pady=10)

    def create_signup_frame(self):
        self.signup_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        
        # Center signup content
        signup_content = ctk.CTkFrame(self.signup_frame, fg_color="transparent")
        signup_content.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Signup header
        ctk.CTkLabel(signup_content, text="SIGN UP", font=ctk.CTkFont(size=32, weight="bold")).pack(pady=(0, 40))
        
        # Signup fields
        self.signup_username_entry = ctk.CTkEntry(signup_content, width=300, height=50, placeholder_text="Username")
        self.signup_username_entry.pack(pady=10)
        
        self.signup_password_entry = ctk.CTkEntry(signup_content, width=300, height=50, placeholder_text="Password", show="●")
        self.signup_password_entry.pack(pady=10)
        
        self.signup_confirm_password_entry = ctk.CTkEntry(signup_content, width=300, height=50, placeholder_text="Confirm Password", show="●")
        self.signup_confirm_password_entry.pack(pady=10)
        
        # Signup button
        ctk.CTkButton(signup_content, text="Sign Up", width=300, height=50, font=ctk.CTkFont(size=15, weight="bold"),
                     command=self.signup).pack(pady=20)
        
        # Back to login button
        ctk.CTkButton(signup_content, text="Back to Login", width=300, height=50, font=ctk.CTkFont(size=15, weight="bold"),
                     command=self.show_login_frame).pack(pady=10)

    def create_main_frame(self):
        self.main_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        
        # Create left and right panels
        left_panel = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_panel = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Search section in left panel
        search_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        search_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Enter Stock Symbol",
                                       height=40, font=ctk.CTkFont(size=14))
        self.search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        
        search_button = ctk.CTkButton(search_frame, text="Search", width=100, height=40,
                                    font=ctk.CTkFont(size=14), command=self.get_stock_price)
        search_button.pack(side=tk.LEFT)
        
        # Price display
        self.price_frame = ctk.CTkFrame(left_panel)
        self.price_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.symbol_label = ctk.CTkLabel(self.price_frame, text="", font=ctk.CTkFont(size=24, weight="bold"))
        self.symbol_label.pack(pady=(20, 10))
        
        self.price_label = ctk.CTkLabel(self.price_frame, text="", font=ctk.CTkFont(size=36, weight="bold"))
        self.price_label.pack(pady=(0, 20))
        
        # Graph section
        self.graph_frame = ctk.CTkFrame(left_panel)
        self.graph_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top stocks section in right panel
        ctk.CTkLabel(right_panel, text="TOP 10 STOCKS", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0, 20))
        
        # Create modern table for top stocks
        self.top_stocks_frame = ctk.CTkFrame(right_panel)
        self.top_stocks_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create top stocks table
        self.create_top_stocks_table()

    def create_top_stocks_table(self):
        # Headers
        headers_frame = ctk.CTkFrame(self.top_stocks_frame, fg_color="transparent")
        headers_frame.pack(fill=tk.X, padx=20, pady=(10, 0))
        
        ctk.CTkLabel(headers_frame, text="Symbol", font=ctk.CTkFont(size=14, weight="bold")).pack(side=tk.LEFT, expand=True)
        ctk.CTkLabel(headers_frame, text="Price", font=ctk.CTkFont(size=14, weight="bold")).pack(side=tk.LEFT, expand=True)
        ctk.CTkLabel(headers_frame, text="Change", font=ctk.CTkFont(size=14, weight="bold")).pack(side=tk.LEFT, expand=True)
        
        # Scrollable frame for stocks
        self.stocks_frame = ctk.CTkScrollableFrame(self.top_stocks_frame, fg_color="transparent")
        self.stocks_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Initialize with loading message
        self.loading_label = ctk.CTkLabel(self.stocks_frame, text="Loading stocks...",
                                        font=ctk.CTkFont(size=14))
        self.loading_label.pack(pady=20)

    def update_top_stocks(self):
        while True:
            try:
                # Clear previous stocks
                for widget in self.stocks_frame.winfo_children():
                    widget.destroy()
                
                # Get top stocks data
                stocks = [
                    "AAPL", "MSFT", "GOOGL", "AMZN", "META",
                    "TSLA", "NVDA", "NFLX", "JPM", "V"
                ]
                
                for symbol in stocks:
                    try:
                        current_price = stock_info.get_live_price(symbol)
                        prev_price = stock_info.get_data(symbol, interval="1d")['close'].iloc[-2]
                        change = ((current_price - prev_price) / prev_price) * 100
                        
                        # Create stock row
                        row = ctk.CTkFrame(self.stocks_frame, fg_color="transparent")
                        row.pack(fill=tk.X, pady=5)
                        
                        ctk.CTkLabel(row, text=symbol, font=ctk.CTkFont(size=14)).pack(side=tk.LEFT, expand=True)
                        ctk.CTkLabel(row, text=f"${current_price:.2f}",
                                   font=ctk.CTkFont(size=14)).pack(side=tk.LEFT, expand=True)
                        
                        color = "#00ff00" if change >= 0 else "#ff0000"
                        ctk.CTkLabel(row, text=f"{change:+.2f}%", font=ctk.CTkFont(size=14),
                                   text_color=color).pack(side=tk.LEFT, expand=True)
                        
                    except Exception as e:
                        print(f"Error fetching data for {symbol}: {e}")
                
            except Exception as e:
                print(f"Error updating top stocks: {e}")
            
            time.sleep(30)  # Update every 30 seconds

    def get_stock_price(self):
        symbol = self.search_entry.get().upper()
        if not symbol:
            return
            
        try:
            price = stock_info.get_live_price(symbol)
            self.current_symbol = symbol
            
            # Update price display
            self.symbol_label.configure(text=symbol)
            self.price_label.configure(text=f"${price:.2f}")
            
            # Update graph
            self.update_graph(symbol)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_graph(self, symbol):
        try:
            # Clear previous graph
            for widget in self.graph_frame.winfo_children():
                widget.destroy()
            
            # Get historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)
            hist_data = stock_info.get_data(symbol, start_date=start_date, end_date=end_date)
            
            # Create figure with dark theme
            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(8, 4))
            
            # Plot data
            ax.plot(hist_data.index, hist_data['close'], color='#00a3ff', linewidth=2)
            ax.fill_between(hist_data.index, hist_data['close'], alpha=0.1, color='#00a3ff')
            
            # Customize graph
            ax.set_title(f"{symbol} - 6 Month History", color='white', pad=20)
            ax.grid(True, alpha=0.2)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Add to frame
            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch historical data: {e}")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if username in self.users and self.users[username] == password:
            self.show_main_frame()
            # Start top stocks update thread
            threading.Thread(target=self.update_top_stocks, daemon=True).start()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def signup(self):
        username = self.signup_username_entry.get()
        password = self.signup_password_entry.get()
        confirm_password = self.signup_confirm_password_entry.get()
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            return
        
        if username in self.users:
            messagebox.showerror("Error", "Username already exists!")
            return
        
        # Add new user to the users dictionary
        self.users[username] = password
        messagebox.showinfo("Success", "Signup successful!")
        self.show_login_frame()

    def show_login_frame(self):
        self.main_frame.pack_forget()
        self.signup_frame.pack_forget()
        self.login_frame.pack(fill=tk.BOTH, expand=True)

    def show_signup_frame(self):
        self.login_frame.pack_forget()
        self.main_frame.pack_forget()
        self.signup_frame.pack(fill=tk.BOTH, expand=True)

    def show_main_frame(self):
        self.login_frame.pack_forget()
        self.signup_frame.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    app = ModernStockTracker()
    app.mainloop()
