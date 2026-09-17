from pathlib import Path


KNOWLEDGE_PATH = (
    Path(__file__).resolve().parent
    / "knowledge"
    / "products.md"
)


def load_product_sections() -> list[str]:
    text = KNOWLEDGE_PATH.read_text(encoding="utf-8")

    return [
        section.strip()
        for section in text.split("## ")[1:]
    ]


def retrieve_product_context(
    question: str,
) -> str | None:
    for section in load_product_sections():
        title_line = section.splitlines()[0]
        product_names = [
            name.strip()
            for name in title_line.split("|")
        ]

        if any(
            name in question
            for name in product_names
        ):
            return f"## {section}"

    return None
