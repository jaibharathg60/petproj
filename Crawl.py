import requests
from bs4 import BeautifulSoup
import csv
import time
import wptools
import re
import ast


def get_filmography():
    """
    Scrapes the filmography page for Shivaji Ganesan from Wikipedia.
    Returns a list of movie titles found in tables with class "wikitable".
    """
    # URL for Shivaji Ganesan's filmography page
    url = "https://en.wikipedia.org/wiki/Sivaji_Ganesan_filmography"
    filmography = set()
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching filmography page: {e}")
        return list(filmography)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    # Find all wikitable elements (filmography is usually contained in one or more such tables)
    tables = soup.find_all("table", class_="wikitable")
    
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            # Skip header rows (they often use <th> tags)
            if row.find("th"):
                continue
            cols = row.find_all("td")
            if cols:
                # It's common that the first column contains the movie title in a link (<a>)
                first_cell = cols[0]
                link = first_cell.find('a')
                if link:
                    title = link.get('title')
                    if title:
                        filmography.add(title.strip())
                    else:
                        filmography.add(link.get_text(strip=True))
                else:
                    text = first_cell.get_text(strip=True)
                    if text:
                        filmography.add(text)
    
    print(f"Found {len(filmography)} film titles.")
    return list(filmography)

def get_movie_details(movie_title):
    """
    Retrieve details for a given movie from Wikipedia.
    Extracts information from the infobox and looks for a section that contains 'Plot'.
    
    Returns a dictionary with movie name, director, music, cast, and a plot excerpt.
    """
    try:
        # Create a page object for the movie using wptools
        page = wptools.page(movie_title, silent=True)
        page.get_parse()  # Fetch and parse the page
        
        # Retrieve infobox data (the key names may vary)
        infobox = page.data.get("infobox", {})
        director = infobox.get("director", "Not Available")
        # Try alternative keys for music entry
        music = infobox.get("music") or infobox.get("music_by") or "Not Available"
        cast   = infobox.get("starring", "Not Available")
        
        # Attempt to extract the Plot text.
        p_data = page.data
        d_data=ast.literal_eval(str(p_data))
        wikitext = d_data.get("wikitext", "")
        if not wikitext:
            print("No wikitext found in the provided data.")
            return
        plot = extract_plot_section(wikitext)
        if "sections" in page.data:
            for section in page.data["sections"]:
                # Look for section titles that contain 'Plot' (case insensitive)
                if section.get("title") and "plot" in section["title"].lower():
                    plot = section.get("text")
                    break

        # Prepare the result dictionary.
        return {
            "movie": movie_title,
            "director": director,
            "music": music,
            "cast": cast,
            "plot": plot if plot else "Not Available"
        }
    except Exception as e:
        print(f"Error processing '{movie_title}': {e}")
        return {
            "movie": movie_title,
            "director": "Error",
            "music": "Error",
            "cast": "Error",
            "plot": "Error"
        }

def write_to_csv(movie_details_list, filename="shivaji_movies.csv"):
    """
    Writes the list of movie details dictionaries into a CSV file.
    """
    fieldnames = ["movie", "director", "music", "cast", "plot_excerpt"]
    try:
        with open(filename, mode="w", newline='', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for details in movie_details_list:
                # Take only the first 300 characters of the plot for brevity
                details["plot_excerpt"] = details["plot"]  if details["plot"] != "Not Available" else details["plot"]
                writer.writerow({
                    "movie": details["movie"],
                    "director": details["director"],
                    "music": details["music"],
                    "cast": details["cast"],
                    "plot_excerpt": details["plot_excerpt"]
                })
        print(f"Details written to {filename}")
    except Exception as e:
        print(f"Error writing CSV: {e}")

def main():
    # Step 1: Extract filmography list dynamically.
    movie_titles = get_filmography()
    
    # Optional: For testing/debugging you might limit the number of movies:
    # movie_titles = movie_titles[:5]
    
    movie_details_list = []
    
    # Step 2: For each movie title, fetch its details.
    for title in movie_titles:
        print(f"Processing movie: {title}")
        details = get_movie_details(title)
        movie_details_list.append(details)
        # Be polite and wait a bit between requests
        time.sleep(1)

    # Step 3: Write the results to a CSV file.
    write_to_csv(movie_details_list)


def extract_plot_section(wikitext):
    """
    Attempt to extract the 'Plot' section from wiki markup using regex, 
    then fall back to splitting if needed.
    """
    
    # Pattern to capture text after a line that starts with "== Plot ==" 
    # and before the next section heading, which also starts with "=="
    pattern = r'==\s*Plot\s*==\s*\n(.*?)(?=\n==)'
    
    # Try regex extraction (case-insensitive and DOTALL to capture newlines)
    match = re.search(pattern, wikitext, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # Fallback method: split by headings
    # Split the text on headings that start with "=="
    sections = re.split(r'\n==\s*', wikitext)
    for sec in sections:
        if sec.lower().startswith("plot"):
            # Remove the heading ("Plot ==") from the section
            lines = sec.split("\n", 1)
            if len(lines) == 2:
                return lines[1].strip()
    return None

if __name__ == '__main__':
    main()