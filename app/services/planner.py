
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

load_dotenv()

PROMPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "prompts"
    / "query_planner.txt"
)

MAX_QUERIES = min(
    3,
    max(1, int(os.getenv("MAX_SEARCH_QUERIES", "3")))
)

client = (
    genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    if os.getenv("GEMINI_API_KEY")
    else None
)


def generate_queries(user_query: str) -> list[str]:
    if client is None:
        return [user_query]

    prompt = PROMPT_PATH.read_text(encoding="utf-8")

    try:
        response = client.models.generate_content(
            model=os.getenv(
                "GEMINI_MODEL",
                "gemini-flash-latest",
            ),
            contents=(
                f"{prompt}\n\n"
                f"User question:\n{user_query}"
            ),
            config={
                "response_mime_type": "application/json",
                "response_json_schema": {
                    "type": "OBJECT",
                    "properties": {
                        "queries": {
                            "type": "ARRAY",
                            "items": {"type": "STRING"},
                        }
                    },
                    "required": ["queries"],
                },
            },
        )

        data = json.loads(response.text or "{}")
        raw_queries = data.get("queries", [])

        if not isinstance(raw_queries, list):
            return [user_query]

        queries = []
        seen = set()

        for item in raw_queries:
            if not isinstance(item, str):
                continue

            item = " ".join(item.split()).strip()

            if not item or len(item) > 500:
                continue

            key = item.casefold()

            if key not in seen:
                seen.add(key)
                queries.append(item)

            if len(queries) >= MAX_QUERIES:
                break

        if user_query.casefold() not in seen:
            queries.insert(0, user_query)

        return queries[:MAX_QUERIES] or [user_query]

    except Exception:
        return [user_query]
