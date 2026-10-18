"""Assignment 2: Bookstore Intelligence Mission.

Install: pip install requests beautifulsoup4 pandas matplotlib
Run:     python bookstore_scraper.py
Optional: python bookstore_scraper.py --pages 50

The dataset, chart, and written results are generated from the live practice website.
"""

import argparse
from pathlib import Path
from urllib.parse import urljoin
import requests
import pandas as pd
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
RATING_VALUES = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
OUTPUT_DIR = Path(__file__).resolve().parent


def scrape_page(page_number, session):
    """Return product records from one catalogue page."""
    url = urljoin(BASE_URL, f"catalogue/page-{page_number}.html")
    response = session.get(url, timeout=25)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    books = []

    for card in soup.select("article.product_pod"):
        title_link = card.select_one("h3 a")
        price_tag = card.select_one("p.price_color")
        rating_tag = card.select_one("p.star-rating")
        stock_tag = card.select_one("p.instock.availability")
        if not all([title_link, price_tag, rating_tag, stock_tag]):
            raise ValueError(f"Missing required HTML element on page {page_number}")

        title = title_link.get("title", title_link.get_text(strip=True)).strip()
        price = float(price_tag.get_text(strip=True).replace("£", "").replace("Â", "").strip())
        rating_word = next((c for c in rating_tag.get("class", []) if c in RATING_VALUES), None)
        if rating_word is None:
            raise ValueError(f"Unrecognized star rating for {title}")
        availability = "In stock" if "In stock" in stock_tag.get_text(" ", strip=True) else "Out of stock"
        product_url = urljoin(url, title_link["href"])
        books.append({
            "Title": title,
            "Price": price,
            "Rating": RATING_VALUES[rating_word],
            "Availability": availability,
            "Product URL": product_url,
        })
    return books


def best_purchase(books, budget_pence=10000):
    """Exact 0/1 knapsack in integer pennies. Each listed book can be bought once.

    The solution maximizes rating points; if tied, it minimizes spend.
    """
    states = {0: (0, ())}  # cost in pence -> (rating, tuple of row indices)
    for idx, book in books.iterrows():
        price = int(round(float(book["Price"]) * 100))
        rating = int(book["Rating"])
        for spent, (score, chosen) in list(states.items()):
            new_spent = spent + price
            if new_spent > budget_pence:
                continue
            new_score = score + rating
            if new_spent not in states or new_score > states[new_spent][0]:
                states[new_spent] = (new_score, chosen + (idx,))
    spent, (score, selected) = max(states.items(), key=lambda pair: (pair[1][0], -pair[0]))
    return books.loc[list(selected)], spent / 100, score


def write_analysis(df, pages):
    expensive = df.loc[df["Price"].idxmax()]
    cheapest = df.loc[df["Price"].idxmin()]
    five_star = df.loc[df["Rating"] == 5]
    top_five = df.sort_values(["Rating", "Price", "Title"], ascending=[False, True, True]).head(5)
    budget_books = df.loc[df["Availability"] == "In stock"].reset_index(drop=True)
    chosen, cost, rating_points = best_purchase(budget_books)
    five_count = len(five_star)
    in_stock_count = int(df["Availability"].eq("In stock").sum())
    in_stock_pct = in_stock_count / len(df) * 100
    average = df["Price"].mean()
    cheapest_five = five_star.sort_values(["Price", "Title"]).iloc[0] if five_count else None

    lines = [
        "ASSIGNMENT 2 — THE BOOKSTORE INTELLIGENCE MISSION",
        f"Source: {BASE_URL}",
        f"Scope: first {pages} catalogue pages; {len(df)} unique product listings",
        "",
        "MISSION 1 — RECONNAISSANCE",
        "Title: article.product_pod h3 a — full title is in the title attribute.",
        "Price: article.product_pod p.price_color — remove the pound symbol and convert to float.",
        "Rating: article.product_pod p.star-rating — star count is stored in a class (One to Five).",
        "Availability: article.product_pod p.instock.availability — clean the whitespace and read stock status.",
        "",
        "MISSIONS 2 AND 3 — DATA COLLECTION",
        f"The script used requests, BeautifulSoup and pandas to collect {len(df)} books across {pages} pages.",
        "It saved competitor_books.csv with clean prices, numeric 1–5 ratings, availability and product URLs.",
        "",
        "MISSION 4 — INTELLIGENCE ANALYSIS",
        f"1. Most expensive: {expensive['Title']} — £{expensive['Price']:.2f}.",
        f"2. Cheapest: {cheapest['Title']} — £{cheapest['Price']:.2f}.",
        f"3. Average price: £{average:.2f}.",
        f"4. Five-star books: {five_count}.",
        f"5. Books in stock: {in_stock_count} of {len(df)} ({in_stock_pct:.1f}%).",
        "6. Top five highest-rated books (ties settled by lowest price):",
    ]
    for n, (_, book) in enumerate(top_five.iterrows(), 1):
        lines.append(f"   {n}. {book['Title']} — {int(book['Rating'])} stars — £{book['Price']:.2f}")
    lines.append(
        f"7. Cheapest five-star book: {cheapest_five['Title']} — £{cheapest_five['Price']:.2f}."
        if cheapest_five is not None else "7. No five-star books found in the selected pages."
    )
    lines.extend(["", "FINAL CHALLENGE — THE CEO HAS £100", "Chosen books (one copy per title):"])
    for _, book in chosen.iterrows():
        lines.append(f"- {book['Title']} — £{book['Price']:.2f} — {int(book['Rating'])} stars")
    lines.extend([
        f"Total cost: £{cost:.2f}",
        f"Total star rating score: {rating_points}",
        f"Money left: £{100-cost:.2f}",
        "Method: exact 0/1 knapsack, optimizing total star points without exceeding £100.",
        "",
        "MISSION DEBRIEF — BUSINESS RECOMMENDATION",
    ])
    if cheapest_five is not None:
        lines.append(
            f"I would start by considering {cheapest_five['Title']} because it has a five-star rating "
            f"and costs only £{cheapest_five['Price']:.2f}, compared with an average catalogue price of £{average:.2f}. "
            f"There are {five_count} five-star books and {in_stock_pct:.1f}% of the books are listed as in stock, "
            "so I would compare the well-rated affordable titles before deciding what to test in our store."
        )
    else:
        lines.append(
            f"I would focus on the higher-rated affordable books first, since the average price is £{average:.2f} "
            f"and {in_stock_pct:.1f}% of the products are currently listed as in stock. "
            "This gives us a practical shortlist for further research before buying inventory."
        )
    lines.extend([
        "",
        "IMPORTANT LIMITATION",
        "Books to Scrape is a practice site. Its ratings and prices are randomly assigned, not real customer feedback.",
        "These findings demonstrate the method rather than establish actual consumer demand.",
    ])
    report = "\n".join(lines) + "\n"
    (OUTPUT_DIR / "assignment_answers.txt").write_text(report, encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description="Bookstore Intelligence scraper")
    parser.add_argument("--pages", type=int, default=5, help="Number of catalogue pages, 1-50 (default: 5)")
    args = parser.parse_args()
    if not 1 <= args.pages <= 50:
        parser.error("--pages must be between 1 and 50")

    records = []
    with requests.Session() as session:
        session.headers.update({"User-Agent": "StudentBookstoreIntelligence/1.0 (educational practice)"})
        for page in range(1, args.pages + 1):
            page_books = scrape_page(page, session)
            if not page_books:
                raise RuntimeError(f"No books returned on page {page}; stopping to avoid incomplete results")
            print(f"Page {page}: {len(page_books)} books")
            records.extend(page_books)

    df = pd.DataFrame(records)
    df.drop_duplicates(subset=["Product URL"], inplace=True)
    df["Price"] = pd.to_numeric(df["Price"], errors="raise").round(2)
    df["Rating"] = pd.to_numeric(df["Rating"], errors="raise").astype(int)
    df.to_csv(OUTPUT_DIR / "competitor_books.csv", index=False, encoding="utf-8-sig")
    print("\nFirst five rows:\n", df.head().to_string(index=False))
    print("\nColumns:", list(df.columns))
    print("\n" + write_analysis(df, args.pages))

    try:
        import matplotlib.pyplot as plt
        counts = df["Rating"].value_counts().reindex(range(1, 6), fill_value=0).sort_index()
        ax = counts.plot.bar(figsize=(7, 4), rot=0, title="Books by star rating")
        ax.set_xlabel("Star rating")
        ax.set_ylabel("Number of books")
        ax.figure.tight_layout()
        ax.figure.savefig(OUTPUT_DIR / "rating_counts.png", dpi=160)
        plt.close(ax.figure)
        print("Saved rating_counts.png")
    except ImportError:
        print("Matplotlib not installed; chart skipped.")
    print("Saved competitor_books.csv and assignment_answers.txt")


if __name__ == "__main__":
    main()
