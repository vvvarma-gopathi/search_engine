
import os

import tiktoken

MAX_CONTENT_TOKENS = max(
    0,
    int(os.getenv("MAX_CONTENT_TOKENS", "8000")),
)

encoding = tiktoken.get_encoding("cl100k_base")


def limit_content(results: list[dict]) -> list[dict]:
    remaining = MAX_CONTENT_TOKENS
    limited_results = []

    for result in results:
        content = result.get("raw_content") or ""

        if not content:
            content = result.get("content") or ""

        if not content or remaining <= 0:
            trimmed = ""
        else:
            tokens = encoding.encode(content)
            trimmed_tokens = tokens[:remaining]
            trimmed = encoding.decode(trimmed_tokens)
            remaining -= len(trimmed_tokens)

        limited_results.append({
            **result,
            "raw_content": trimmed,
        })

    return limited_results
