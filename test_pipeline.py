import time

def scraper():
    print("🕷️ Scraping data...")
    time.sleep(1)

def merger():
    print("🧩 Merging data...")
    time.sleep(1)

def sentiment_analysis():
    print("🧠 Performing sentiment analysis...")
    time.sleep(1)

def convert_to_jsonl():
    print("📄 Converting to JSONL...")
    time.sleep(1)

def clean_jsonl():
    print("🧹 Cleaning JSONL...")
    time.sleep(1)

def main():
    print("🚀 Starting mock pipeline simulation...\n")
    scraper()
    merger()
    sentiment_analysis()
    convert_to_jsonl()
    clean_jsonl()
    print("\n✅ Mock pipeline simulation completed successfully.")

if __name__ == "__main__":
    main()
