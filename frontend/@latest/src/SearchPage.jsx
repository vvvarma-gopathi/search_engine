
import { useState } from "react";
import "./SearchPage.css";


const API_URL = (
  import.meta.env.VITE_API_URL || "https://search-engine-uxw2.onrender.com"
).replace(/\/$/, "");

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSearch(event) {
    event.preventDefault();

    const question = query.trim();

    if (question.length < 2) {
      setError("Enter a question to search.");
      return;
    }

    setLoading(true);
    setError("");
    setData(null);

    try {
      const response = await fetch(
        `${API_URL}/api/v1/search`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ query: question }),
        }
      );

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          result.detail || "Search failed. Try again."
        );
      }

      setData(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="search-page">
      <header className="search-header">
        <h1>Varma's Search Engine Agent</h1>
        <p>Search the internet. Find the answers.</p>
      </header>

      <form className="search-form" onSubmit={handleSearch}>
        <input
          type="search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Ask anything..."
          maxLength={500}
          aria-label="Search the internet"
          disabled={loading}
        />

        <button type="submit" disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {error && (
        <p className="search-error" role="alert">
          {error}
        </p>
      )}

      {loading && (
        <p className="search-status" aria-live="polite">
          Searching the web and collecting relevant sources...
        </p>
      )}

      {data && (
        <section className="search-results">
          <article className="answer-section">
            <h2>Answer</h2>
            <p className="answer-text">{data.answer}</p>
          </article>

          <section className="sources-section">
            <h2>Sources ({data.sources.length})</h2>

            {data.sources.length === 0 && (
              <p>No source links were returned.</p>
            )}

            {data.sources.map((source) => (
              <article
                className="source-card"
                key={source.url}
              >
                <h3>
                  <a
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {source.title}
                  </a>
                </h3>

                <a
                  className="source-url"
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {source.url}
                </a>

                {source.published_date && (
                  <p className="source-date">
                    Published: {source.published_date}
                  </p>
                )}

                {source.snippet && (
                  <p>{source.snippet}</p>
                )}
              </article>
            ))}
          </section>
        </section>
      )}
    </main>
  );
}
