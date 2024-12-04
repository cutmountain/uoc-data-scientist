# Importando las bibliotecas necesarias
from urllib.request import Request, urlopen # Para abrir URLs
from urllib.error import HTTPError # Para manejar errores HTTP
import time # Para implementar retrasos si es necesario


# Function to extract links from HTML content
def getLinks(html, max_links=10):
    url = []  # List to store the extracted URLs
    cursor = 0  # Cursor to track position in HTML content
    nlinks = 0  # Counter for number of links extracted

    # Loop to extract links until the maximum is reached or no more links are found
    while (cursor >= 0 and nlinks < max_links):
        start_link = html.find("a href", cursor)  # Find the start of a link
        if start_link == -1:  # If no more links are found, return the list of URLs
            return url
        start_quote = html.find('"', start_link)  # Find the opening quote of the URL
        end_quote = html.find('"', start_quote + 1)  # Find the closing quote of the URL
        url.append(html[start_quote + 1: end_quote])  # Extract and append the URL to the list
        cursor = end_quote + 1  # Move the cursor past this URL
        nlinks += 1  # Increment the link counter

    return url  # Return the list of URLs

# Example usage:
# Suppose you have some HTML content stored in a variable `html_content`
# You would call the function like this:
# links = getLinks(html_content)
# This would return a list of URLs extracted from `html_content`

# Expected Output:
# The output will be a list containing up to `max_links` number of URLs extracted from the given HTML content.
# If the HTML content has fewer than `max_links` URLs, all found URLs will be included in the list.



# Define the Spider class for web crawling
class Spider:
    # Initializer or constructor for the Spider class
    def __init__(self, starting_url, crawl_domain, max_iter):
        self.crawl_domain = crawl_domain  # The domain within which the spider will crawl
        self.max_iter = max_iter  # The maximum number of pages to crawl
        self.links_to_crawl = [starting_url]  # Queue of links to crawl
        self.links_visited = []  # List to keep track of visited links
        self.collection = []  # List to store the collected data
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Safari/605.1.15'

    # Method to retrieve HTML content from a URL
    def retrieveHtml(self):
        try:
            # Open the URL and read the response
            #socket = urlopen(self.url)
            req = Request(self.url)
            req.add_header('User-Agent', self.user_agent)
            socket = urlopen(req)
            # Decode the response using 'latin-1' encoding
            self.html = socket.read().decode('latin-1')
            return 0  # Return 0 if successful
        except HTTPError as e:
            # If an HTTP error occurs, print the error and return -1
            print(f"HTTP Error encountered: {e}")
            return -1

    # Main method to control the crawling process
    def run(self):
        # Continue to crawl while there are links to crawl and the max_iter is not reached
        while self.links_to_crawl and len(self.collection) < self.max_iter:
            # Get the next link to crawl
            self.url = self.links_to_crawl.pop(0)
            print(f"Currently crawling: {self.url}")
            # Add the link to the list of visited links
            self.links_visited.append(self.url)
            # If HTML retrieval is successful, store the HTML and find new links
            if self.retrieveHtml() >= 0:
                self.storeHtml()
                self.retrieveAndValidateLinks()
            time.sleep(2)

    # Method to retrieve and validate links in the HTML content
    def retrieveAndValidateLinks(self):
        # Get a list of links from the current HTML content
        items = getLinks(self.html)
        # Temporary list to store valid links
        tmpList = []

        # Iterate over the found links
        for item in items:
            item = item.strip('"')  # Remove any extra quotes
        
            # Check if the link is an absolute URL that contains the crawl domain
            if self.crawl_domain in item and item.startswith('http'):
                tmpList.append(item)
            # Handle relative links
            elif item.startswith('/'):
                # Construct the full URL using the crawl domain and relative link
                tmpList.append('https://' + self.crawl_domain + item)
            # Handle potential relative links without a leading slash (assuming they are not absolute URLs)
            elif not item.startswith('http'):
                # Construct the full URL assuming it is a relative link
                tmpList.append('https://' + self.crawl_domain + '/' + item)

        # Add valid, unvisited links to the crawl queue
        for item in tmpList:
            if item not in self.links_visited and item not in self.links_to_crawl:
                self.links_to_crawl.append(item)
                print(f'Adding to crawl queue: {item}')


    # Method to store HTML content and associated metadata
    def storeHtml(self):
        # Create a dictionary to represent the document
        doc = {
            'url': self.url,  # URL of the page
            'date': time.strftime("%d/%m/%Y"),  # Current date
            'html': self.html  # HTML content of the page
        }
        # Add the document to the collection
        self.collection.append(doc)
        print(f"Stored HTML from: {self.url}")

# Example usage of the Spider class:
# Initialize the spider with the starting URL, domain to crawl, and the maximum number of iterations.
# my_spider = Spider("http://www.example.com", "example.com", 20)

# Start the crawling process.
# my_spider.run()

# After running, my_spider.collection will contain up to 20 pages' HTML from 'example.com'.
# Each page's data includes the URL, the date when it was scraped, and the HTML content.