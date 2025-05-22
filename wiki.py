import wptools

# Fetch the Wikipedia page
page = wptools.page("Arivaali").get_parse()
#page = wptools.page("Arivaali").get_query()
infobox = page.data.get("infobox", {})
director = infobox.get("director", "Not Available")
plot = infobox.get("plot", "Not Available")
print(page.data)
print(f"Categories: {page.data['sections']}")
#if "sections" in page.data:
 #           for section in page.data["sections"]:
  #              # Look for section titles that contain 'Plot' (case insensitive)
   #             if section.get("title") and "plot" in section["title"].lower():
    #                plot = section.get("text")
     #               break
# Print the title
print(f"Title: {page.title}")

# Extract the summary text
print(f"Summary: {page.data['extract']}")

# Extract the infobox data
print(f"Infobox Data: {page.data['infobox']}")

# Extract images from the page
print(f"Images: {page.data['image']}")

# Extract categories
print(f"Categories: {page.data['categories']}")
# Extract sections
sections = page.data['sections']

# Find the "Plot" section
plot_text = None
for section in sections:
    if "Plot" in section['line']:  # Checking if the section title contains "Plot"
        plot_text = section['text']
        break

# Print the extracted plot
if plot_text:
    print("Plot Section:\n", plot_text)
else:
    print("Plot section not found.")