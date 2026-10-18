# Bookstore Intelligence — Assignment 2

A Python web-scraping project for the **Business Data and Text Mining** course. The script collects book information from [Books to Scrape](https://books.toscrape.com/), cleans it with Pandas, and produces a dataset and a short business-analysis report.

## What the project does

- Scrapes book listings across multiple catalogue pages.
- Collects each book's title, price, star rating, stock availability, and product URL.
- Converts prices and ratings into numeric values and removes duplicate product listings.
- Saves the cleaned data to a CSV file.
- Answers seven business questions, including average price, highest- and lowest-priced books, five-star count, stock availability, and top-rated books.
- Solves the £100 buying challenge by selecting in-stock books to maximize total star-rating points without exceeding the budget.
- Creates a bar chart showing the number of books at each star rating (when Matplotlib is installed).

## Requirements

- Python 3.9 or newer
- An internet connection

Install the required libraries:

```bash
pip install requests beautifulsoup4 pandas matplotlib
```

## How to run

Download or clone this repository, then open a terminal in the project folder.

Run the default scrape (first five catalogue pages):

```bash
python bookstore_scraper.py
```

Choose a different number of pages (between 1 and 50):

```bash
python bookstore_scraper.py --pages 10
```

The scraper requests each page in sequence and stops with an error if a page cannot be retrieved or required product information is missing.

## Files generated

After a successful run, the script creates these files in the project folder:

| File | Purpose |
|---|---|
| `competitor_books.csv` | Cleaned book dataset |
| `assignment_answers.txt` | Answers to the analysis questions and the £100 challenge |
| `rating_counts.png` | Bar chart of the rating distribution |

These outputs are generated from the live practice website when the script runs; they are not included as fixed results in the source code.

## Dataset columns

| Column | Description |
|---|---|
| `Title` | Book title |
| `Price` | Price in pounds (£), stored as a number |
| `Rating` | Star rating from 1 to 5 |
| `Availability` | In-stock or out-of-stock status |
| `Product URL` | Link to the individual book page |

## Notes on the £100 challenge

The script uses an exact 0/1 knapsack approach: each listed book can be selected at most once, the total cost must stay within £100, and the objective is to maximize total star-rating points. If solutions have the same score, the algorithm prefers the lower spend.

## Limitations

Books to Scrape is a practice website. Its prices and ratings are sample data and should not be treated as evidence of real customer demand or actual market prices. Results may change if the website's content changes.

## Repository

https://github.com/saifemustafa4-bot/Bookstore-Intelligence-Assignment-2
