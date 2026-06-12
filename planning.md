# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**

<!-- Describe what this tool does in 1–2 sentences -->

This tool takes in a description, size, and maximum price and returns a list of dictionaries. Each element is a listing that fulfills all the parameter requirements. The tool then filters the mock listings against three criteria and returns matching items sorted by relevance (closest price to max_price first).

**Input parameters:**

<!-- List each parameter, its type, and what it represents -->

- `description` (str): description of the listing
- `size` (str): listing size (S, M, L, etc)
- `max_price` (float): maximum price that a listing can be

**What it returns:**

<!-- Describe the return value — what fields does a result contain? -->

This tool returns a list of listings, in the form of dictionaries, that fulfill each parameter.

**What happens if it fails or returns nothing:**

<!-- What should the agent do if no listings match? -->

If nothing is returned, but if the description matches and size or price don't, the agent should tell the user that an item was found, but the price and sizes don't match up. Otherwise, if description doesn't match, the agent tells the user that there isn't a matching description.

---

### Tool 2: suggest_outfit

**What it does:**

<!-- Describe what this tool does in 1–2 sentences -->

Given a thrifted item and the user's wardrobe, the tool suggests 1 or 2 complete outfits from both the parameters.

**Input parameters:**

<!-- List each parameter, its type, and what it represents -->

- `new_item` (dict): a dictionary with the item the user is considering to buy
- `wardrobe` (dict): A wardrobe dict with an 'items' key containing a list of
  wardrobe item dicts.

**What it returns:**

<!-- Describe the return value -->

A string with outfit suggestions

**What happens if it fails or returns nothing:**

<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? -->

If nothing is returned, the agent should offer general styling advice for the item

---

### Tool 3: create_fit_card

**What it does:**

<!-- Describe what this tool does in 1–2 sentences -->

Generate a short, shareable outfit caption for the thrifted find

**Input parameters:**

<!-- List each parameter, its type, and what it represents -->

- `outfit` (str) The outfit suggestion string from suggest_outfit().
- `new_item` (str) The listing dict for the thrifted item.

**What it returns:**

<!-- Describe the return value -->

        A 2–4 sentence string usable as an Instagram/TikTok caption.

**What happens if it fails or returns nothing:**

<!-- What should the agent do if the outfit data is incomplete? -->

If outfit is empty or missing, return a descriptive error message
string — do NOT raise an exception.

---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**

<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->

1. Extract `description`, `size`, and `max_price` from the query.
2. Call `search_listings(description, size, max_price)`.
3. Check if there are results
   - If yes: set `session["error"] = "No listings found. Try..."`, return session immediately. Do NOT proceed.
   - If no: set `session["selected_item"] = results[0]`, continue.
4. Call `suggest_outfit(session["selected_item"], wardrobe)`.
5. Set `session["outfit_suggestion"] = <returned string>`.
6. Call `create_fit_card(session["outfit_suggestion"],
session["selected_item"])`.
7. Set `session["fit_card"] = <returned string>`.
8. Return session.

Here, the agent will only run all three tools if the first tool passes.

---

## State Management

**How does information from one tool get passed to the next?**

<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->

```python
session = {
    "query": query,
    "selected_item": None,
    "outfit_suggestion": None,
    "fit_card": None,
    "error": None,
}
```

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool            | Failure mode                          | Agent response                                                                                                                 |
| --------------- | ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| search_listings | No results match the query            | Early return - agent determines what went wrong                                                                                |
| suggest_outfit  | Wardrobe is empty                     | Returns general styling advice for the item. Agent uses this with create_fit_card normally                                     |
| create_fit_card | Outfit input is missing or incomplete | Returns the string "Error: Unable to generate a fit card because no outfit description was provided." without calling the LLM. |

---

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:
     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     ASCII art, a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html), or an embedded
     sketch are all fine. You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->

```
User query

│

▼

Planning Loop — run_agent()

│

▼

search_listings(description, size, max_price)

│                           │

│ results = []              │ results = [item, ...]

▼                           ▼

session["error"] = "..."   session["selected_item"] = results[0]

return session early            │

│                           ▼

│               suggest_outfit(selected_item, wardrobe)

│                           │

│               session["outfit_suggestion"] = "..."

│                           │

│                           ▼

│               create_fit_card(outfit_suggestion, selected_item)

│                           │

│               session["fit_card"] = "..."

│                           │

▼                           ▼

[Error response        Return session to user

to user]              (outfit + fit card)
Session state (updated after each tool):

session["selected_item"]     ← set after search_listings

session["outfit_suggestion"] ← set after suggest_outfit

session["fit_card"]          ← set after create_fit_card
```

---

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

I plan to use Claude for general advice and Copilot for coding help. I'll give Claude my Tool 1, 2, and 3 specs, as well as my agent diagram (for context) to help generate the functions search_listings(), suggest_outfit(), and create_fit_card().

For tool 1, search_listing() should return a list of dictionaries, which I'll print out to check that it's proper. I'll test it 3 queries, where there's a normal query, a query that doesn't match any description, and something completely off topic, and ensure its responses make sense.

For tool 2, suggest_outfit() should return a description of the suggested outfit. I'll test both on an empty and nonempty wardrobe, and check the response before proceeding.

For tool 3, create_fit_card() should return the fit card, and I'll test it on an empty and nonempty suggested outfit to make sure an output is being given and errors are being handled.

**Milestone 3 — Individual tool implementations:**

**Milestone 4 — Planning loop and state management:**

---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Milestone 1:**
Fitfindr needs to take in a query, and return a fit corresponding to what the user is looking for and what the user already has. It first calls search_listings(), using the user's interests as parameters to get a fitting item, then suggest_outfit() to suggest an outfit with both the new item and existing user wardrobe, and then create_fit_card() with the outfit and new item as a parameter and returns a fit card. If the function is unable to find a listing, the model should output that a listing with that description doesn't exist.

**Step 1:**

<!-- What does the agent do first? Which tool is called? With what input? -->

**Step 2:**

<!-- What happens next? What was returned from step 1? What tool is called now? -->

**Step 3:**

<!-- Continue until the full interaction is complete -->

**Final output to user:**

<!-- What does the user actually see at the end? -->

```

```
