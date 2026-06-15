# FitFindr

A multi-tool AI agent that helps users find secondhand clothing and figure out how to wear it. FitFindr takes a natural language query, searches a mock thrift listings dataset, suggests outfits using the user's wardrobe, and generates a shareable caption — stopping early with a helpful message if nothing matches.

## Setup

```bash
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):

Run the app:

```bash
python app.py
```

Then open the URL shown in your terminal (usually http://localhost:7860).

---

## Tool Inventory

### `search_listings(description, size, max_price)`

Filters the mock listings dataset and returns matching items sorted by relevance.

| Parameter     | Type            | Description                                                |
| ------------- | --------------- | ---------------------------------------------------------- |
| `description` | `str`           | Keywords describing the item (e.g. "vintage graphic tee")  |
| `size`        | `str \| None`   | Size to filter by (e.g. "M"). `None` skips size filtering. |
| `max_price`   | `float \| None` | Price ceiling in dollars. `None` skips price filtering.    |

**Returns:** A list of listing dicts sorted by keyword relevance score. Each dict contains `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, `platform`. Returns `[]` on no match — never raises.

---

### `suggest_outfit(new_item, wardrobe)`

Calls the Groq LLM to suggest 1–2 complete outfits combining the thrifted item with the user's wardrobe.

| Parameter  | Type   | Description                                                        |
| ---------- | ------ | ------------------------------------------------------------------ |
| `new_item` | `dict` | A listing dict returned by `search_listings`                       |
| `wardrobe` | `dict` | A wardrobe dict with an `items` key containing wardrobe item dicts |

**Returns:** A non-empty string with outfit suggestions. If the wardrobe is empty, returns general styling advice instead.

---

### `create_fit_card(outfit, new_item)`

Calls the Groq LLM to generate a casual 2–4 sentence Instagram/TikTok-style caption for the outfit.

| Parameter  | Type   | Description                                        |
| ---------- | ------ | -------------------------------------------------- |
| `outfit`   | `str`  | The outfit suggestion string from `suggest_outfit` |
| `new_item` | `dict` | The listing dict for the thrifted item             |

**Returns:** A 2–4 sentence caption string. Uses temperature 0.9 to ensure variation across runs. If `outfit` is empty, returns an error string without calling the LLM.

---

## Planning Loop

`run_agent()` in `agent.py` follows this conditional logic:

1. Parse the user's natural language query using the LLM to extract `description`, `size`, and `max_price`
2. Call `search_listings()` with the parsed parameters
3. **If results are empty:** set `session["error"]` and return immediately — `suggest_outfit` and `create_fit_card` are never called
4. **If results exist:** set `session["selected_item"] = results[0]` and continue
5. Call `suggest_outfit()` with the selected item and wardrobe
6. Call `create_fit_card()` with the outfit suggestion and selected item
7. Return the completed session dict

The key behavior is that the agent only calls all three tools when step 3 passes. The no-results branch exits after step 3 without proceeding further.

---

## State Management

All state is stored in a single session dict initialized at the start of `run_agent()`:

```python
session = {
    "query": query,
    "parsed": {},
    "search_results": [],
    "selected_item": None,
    "wardrobe": wardrobe,
    "outfit_suggestion": None,
    "fit_card": None,
    "error": None,
}
```

Each tool's output is stored in the session before the next tool is called. `suggest_outfit` receives `session["selected_item"]` directly — the exact dict from `search_listings`, not re-fetched. `create_fit_card` receives `session["outfit_suggestion"]` — the exact string from `suggest_outfit`. The session is returned to `handle_query()` in `app.py`, which maps the keys to the three Gradio output panels.

---

## Error Handling

| Tool              | Failure mode                | Agent response                                                                                                                                                                                    |
| ----------------- | --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `search_listings` | No listings match the query | Sets `session["error"]` = "No listings matched your search. Try a broader description, a different size, or a higher budget." Returns session immediately. Outfit and fit card panels stay empty. |
| `suggest_outfit`  | Wardrobe is empty           | Returns general styling advice for the item (e.g. "This piece pairs well with high-waisted jeans..."). Does not crash. The agent continues to `create_fit_card` normally.                         |
| `create_fit_card` | `outfit` is empty or None   | Returns "Couldn't generate a fit card — no outfit description was provided." immediately without calling the LLM.                                                                                 |

**Concrete example from testing:**

Running `create_fit_card('', results[0])` in the terminal returned:

```
Couldn't generate a fit card — no outfit description was provided.
```

No exception was raised. The guard clause fires before any LLM call is made.

---

## AI Usage

**Instance 1 — `search_listings` implementation:**
I gave Claude the Tool 1 spec from `planning.md` (inputs, return value, failure mode) and the field list from `listings.json`, and asked it to implement the function using `load_listings()` from the data loader. The generated code filtered by all three parameters and returned `[]` on no match. I caught one bug before running: `item.get("brand", "")` was used instead of `item.get("brand") or ""`, which would crash when `brand` is `None` in the dataset. I fixed that before running any tests.

**Instance 2 — `run_agent()` planning loop:**
I gave Claude the Planning Loop section, State Management section, and ASCII architecture diagram from `planning.md`. Claude generated `_parse_query()` (which uses the LLM to extract structured parameters from natural language) and the full `run_agent()` planning loop. Before running, I verified that it branched on `if not results` after `search_listings`, stored values in the session dict between each tool call, and did not call `suggest_outfit` or `create_fit_card` when results were empty. I confirmed both branches worked by running `python agent.py` and checking the happy path and no-results path outputs.

---

## Running Tests

```bash
pytest tests/ -v
```

Tests cover: search returning results, search returning empty on impossible queries, price filter correctness, size filter correctness, `suggest_outfit` with full and empty wardrobes, `create_fit_card` with valid and empty outfit input.
