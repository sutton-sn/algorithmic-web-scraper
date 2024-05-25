import requests
from bs4 import BeautifulSoup
import pandas as pd
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from PIL import Image, ImageTk

def scrape_to_df(url):
    # Make a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Error accessing the page: {response.status_code}")
        return None

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract paragraphs from the article
    paragraphs = soup.find_all('p')
    
    if not paragraphs:
        print("No paragraphs found on the page.")
        return None

    # Create a list with the content of the paragraphs
    data = [p.text.strip() for p in paragraphs]

    # Define themes and associated keywords
    themes = {
        'Launch': ['launch', 'release', 'announce', 'global'],
        'Features': ['feature', 'update', 'new', 'mode', 'character'],
        'Community': ['community', 'player', 'feedback', 'event'],
        'Company': ['company', 'team', 'development']
    }

    # Create a dictionary to store paragraphs organized by theme
    organized_data = {theme: [] for theme in themes}

    # Assign each paragraph to a theme
    for paragraph in data:
        assigned = False
        for theme, keywords in themes.items():
            if any(keyword in paragraph.lower() for keyword in keywords):
                organized_data[theme].append(paragraph)
                assigned = True
                break
        if not assigned:
            organized_data.setdefault('Others', []).append(paragraph)

    # Create a DataFrame with the organized data
    rows = [{'Theme': theme, 'Paragraph': paragraph} for theme, paragraphs in organized_data.items() for paragraph in paragraphs]
    df = pd.DataFrame(rows)
    
    return df

def display_data():
    url = url_entry.get()
    if not url:
        messagebox.showerror("Error", "Please enter a URL.")
        return

    df = scrape_to_df(url)
    if df is None:
        messagebox.showerror("Error", "Could not scrape the page.")
        return

    # Clear the table before adding new data
    for item in tree.get_children():
        tree.delete(item)

    for i, (index, row) in enumerate(df.iterrows()):
        tree.insert("", "end", values=(row['Theme'], row['Paragraph']))

# Create the GUI with ttkbootstrap
root = tb.Window(themename="darkly")
root.title("Web Scraper")

# Load and display the logo
logo_image = Image.open("logo.png")
logo_photo = ImageTk.PhotoImage(logo_image)
root.iconphoto(False, logo_photo)  # Set the icon for the window

# Main frame
frame = tb.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(N, S, E, W))

# URL entry
tb.Label(frame, text="URL:").grid(row=1, column=0, sticky=W)
url_entry = tb.Entry(frame, width=50)
url_entry.grid(row=1, column=1, sticky=(E, W))

# Button to start scraping
scrape_button = tb.Button(frame, text="Start Scraping", command=display_data, bootstyle=SECONDARY)
scrape_button.grid(row=1, column=2, padx=10)

# Table to display the data
columns = ("Theme", "Paragraph")
tree = tb.Treeview(frame, columns=columns, show="headings", bootstyle=DARK)
tree.heading("Theme", text="Theme")
tree.heading("Paragraph", text="Paragraph")
tree.column("Theme", width=50)  # Adjust the width of the "Theme" column
tree.grid(row=2, column=0, columnspan=3, sticky=(N, S, E, W))

# Configure column and row expansion
frame.columnconfigure(1, weight=1)
frame.rowconfigure(2, weight=1)

# Add vertical scrollbar
scrollbar = tb.Scrollbar(frame, orient=VERTICAL, command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.grid(row=2, column=3, sticky=(N, S))

# Make the window responsive
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Run the application
root.mainloop()