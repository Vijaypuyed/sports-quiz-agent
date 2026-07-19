from ddgs import DDGS


def get_live_news(query):

    """
    Search DuckDuckGo for recent sports news.

    Returns the top 3 search snippets
    as a single text block.
    """

    snippets = []

    try:

        with DDGS() as ddgs:

            results = ddgs.text(
                query,
                max_results=3
            )

            for result in results:

                title = result.get(
                    "title",
                    "No title"
                )

                snippet = result.get(
                    "body",
                    "No snippet"
                )

                if snippet:

                    snippets.append(
                        f"Title: {title}\n"
                        f"Snippet: {snippet}"
                    )

    except Exception as error:

        print(
            "Search Error:",
            error
        )

        return "No latest news available."

    if not snippets:

        return "No latest news available."

    return "\n\n".join(snippets)    