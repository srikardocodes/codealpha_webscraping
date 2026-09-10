import requests
import pandas as pd
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


START_URL = "https://books.toscrape.com/"
MAX_PAGES = 5
DELAY = 1

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Educational Web Scraper)"
}



def get_html(url):
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=15
        )

        response.raise_for_status()

        return response.text

    except requests.RequestException as error:
        print(f"Error accessing {url}: {error}")
        return None



def extract_data(html, page_url):

    soup = BeautifulSoup(html, "lxml")

    records = []

    
    books = soup.select("article.product_pod")

    for book in books:

      
        title_tag = book.select_one("h3 a")

        if title_tag:
            title = title_tag.get(
                "title",
                title_tag.get_text(strip=True)
            )
        else:
            title = ""

        
        price_tag = book.select_one(".price_color")

        if price_tag:
            price = price_tag.get_text(strip=True)
        else:
            price = ""

       
        availability_tag = book.select_one(
            ".availability"
        )

        if availability_tag:
            availability = availability_tag.get_text(
                " ",
                strip=True
            )
        else:
            availability = ""

       
        if title_tag:
            product_url = urljoin(
                page_url,
                title_tag.get("href", "")
            )
        else:
            product_url = ""

        
        image_tag = book.select_one("img")

        if image_tag and image_tag.get("src"):
            image_url = urljoin(
                page_url,
                image_tag["src"]
            )
        else:
            image_url = ""

        records.append({
            "title": title,
            "price": price,
            "availability": availability,
            "product_url": product_url,
            "image_url": image_url,
            "source_page": page_url
        })

    return records




def find_next_page(html, current_url):

    soup = BeautifulSoup(html, "lxml")

    next_link = soup.select_one("li.next a")

    if next_link and next_link.get("href"):

        return urljoin(
            current_url,
            next_link["href"]
        )

    return None


def same_domain(url1, url2):

    return (
        urlparse(url1).netloc
        == urlparse(url2).netloc
    )




def scrape_website(start_url, max_pages):

    current_url = start_url

    all_records = []

    visited_pages = set()

    for page in range(1, max_pages + 1):

        print("\n" + "=" * 60)
        print(f"Scraping page {page}")
        print(f"URL: {current_url}")
        print("=" * 60)

        
        if current_url in visited_pages:
            print("Page already visited.")
            break

       
        if not same_domain(
            start_url,
            current_url
        ):
            print("Different domain detected.")
            break

        visited_pages.add(current_url)

       
        html = get_html(current_url)

        if html is None:
            break

        
        records = extract_data(
            html,
            current_url
        )

        print(
            f"Records collected: {len(records)}"
        )

        all_records.extend(records)

      
        next_url = find_next_page(
            html,
            current_url
        )

        if next_url:

            current_url = next_url

        else:

            print("No more pages found.")
            break

        
        time.sleep(DELAY)

    return all_records



def create_dataset(records):

    return pd.DataFrame(records)

def clean_dataset(df):

    if df.empty:
        return df

    
    df = df.drop_duplicates(
        subset=["product_url"]
    )

  
    for column in df.columns:

        if df[column].dtype == "object":

            df[column] = (
                df[column]
                .astype(str)
                .str.strip()
            )

   
    df["price_numeric"] = (
        df["price"]
        .str.replace(
            "£",
            "",
            regex=False
        )
        .str.strip()
    )

    df["price_numeric"] = pd.to_numeric(
        df["price_numeric"],
        errors="coerce"
    )

    
    df["in_stock"] = (
        df["availability"]
        .str.contains(
            "In stock",
            case=False,
            na=False
        )
    )

    return df




def analyze_dataset(df):

    if df.empty:
        print("No data available.")
        return

    print("\n" + "=" * 60)
    print("DATASET ANALYSIS")
    print("=" * 60)

    print(
        f"Total products: {len(df)}"
    )

    print(
        f"Average price: £"
        f"{df['price_numeric'].mean():.2f}"
    )

    print(
        f"Minimum price: £"
        f"{df['price_numeric'].min():.2f}"
    )

    print(
        f"Maximum price: £"
        f"{df['price_numeric'].max():.2f}"
    )

    print(
        f"Products in stock: "
        f"{df['in_stock'].sum()}"
    )

    print(
        f"Products out of stock: "
        f"{(~df['in_stock']).sum()}"
    )



def save_dataset(df):

    
    df.to_csv(
        "custom_books_dataset.csv",
        index=False
    )

    
    df.to_json(
        "custom_books_dataset.json",
        orient="records",
        indent=4
    )

    print("\nDataset files created:")
    print("1. custom_books_dataset.csv")
    print("2. custom_books_dataset.json")




if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("WEB SCRAPING AND DATASET CREATION")
    print("=" * 60)

   
    records = scrape_website(
        START_URL,
        MAX_PAGES
    )

    print(
        f"\nTotal records collected: "
        f"{len(records)}"
    )

    
    dataset = create_dataset(records)

   
    dataset = clean_dataset(dataset)

    
    print("\nFirst 10 records:")

    if not dataset.empty:
        print(
            dataset.head(10).to_string(
                index=False
            )
        )

    
    analyze_dataset(dataset)

   
    save_dataset(dataset)

    print("\n" + "=" * 60)
    print("PROJECT COMPLETED SUCCESSFULLY")
    print("=" * 60)
