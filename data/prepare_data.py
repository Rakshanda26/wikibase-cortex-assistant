from pathlib import Path
import wikipedia

# Topic you want to build the QA system for
TOPIC = "LLaMA (language model)"
SAVE_DIR = Path(r'F:\wikibase-cortex-assistant\data') / "articles"
SAVE_DIR.mkdir(exist_ok=True, parents=True)

def fetch_and_save_article(topic: str):
    try:
        print(f"Fetching Wikipedia article for topic: {topic}")
        content = wikipedia.page(topic).content
    except wikipedia.exceptions.DisambiguationError as e:
        print(f"DisambiguationError: {e}. Try a more specific topic.")
        return
    except wikipedia.exceptions.PageError:
        print("Page not found.")
        return

    filepath = SAVE_DIR / f"{topic.lower().replace(' ', '_').replace('(', '').replace(')', '')}.txt"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved article to: {filepath}")

if __name__ == "__main__":
    fetch_and_save_article(TOPIC)
