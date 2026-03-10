from openai import OpenAI
from dotenv import load_dotenv
import random as r
import os

load_dotenv(override=True)

def _get_log_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "log.csv")


def read_log():
    log_path = _get_log_path()
    if not os.path.exists(log_path):
        return ""
    with open(log_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f]
    return "\n".join(lines)


def _get_next_index():
    log_path = _get_log_path()
    if not os.path.exists(log_path):
        return 0
    with open(log_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    if not lines:
        return 0
    try:
        return int(lines[-1].split(",")[0]) + 1
    except (ValueError, IndexError):
        return len(lines)


def log_words(word1, word2):
    log_path = _get_log_path()
    idx = _get_next_index()
    needs_newline = False
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()
        if content and not content.endswith("\n"):
            needs_newline = True
    with open(log_path, "a", encoding="utf-8") as f:
        if needs_newline:
            f.write("\n")
        f.write(f"{idx},{word1},{word2}")


def create_words():
    word_log = read_log()
    prompt = (
    "Generate ONE word-pair for an imposter word game.\n"
    "Two players groups get different words: most players get WordA, one player gets WordB.\n"
    "The pair must be SAME broad theme but DIFFERENT enough to create interesting discussion.\n\n"

    "Hard constraints (must follow):\n"
    "- Both words are single tokens (one word each), lowercase, ascii letters only.\n"
    "- Output exactly: worda,wordb (comma, no spaces, no extra text).\n"
    "- Do NOT repeat any word found in this log:\n"
    f"{word_log}\n\n"

    "Game-quality constraints (very important):\n"
    "- Not synonyms, not near-synonyms, not same object with different packaging.\n"
    "- Not parent/child or container/content pairs (e.g., basket/container).\n"
    "- Not ingredient/variant pairs (e.g., sauce/condiment, milk/cream).\n"
    "- Avoid pairs that would make clues identical.\n"
    "- Both words should allow distinct but overlapping clues.\n\n"

    "Target relation:\n"
    "- Same setting/activity, different role/object.\n"
    "- Examples of GOOD relations (do not reuse these exact words):\n"
    "  cinema,theater | camping,hiking | passport,visa | violin,guitar | sushi,pizza\n"
    "- Examples of BAD relations:\n"
    "  apple,pear | container,basket | condiment,sauce | laptop,computer\n\n"

    "Vocabulary constraints:\n"
    "- Common, everyday words (CEFR A2–B2). No obscure/academic words.\n"
    "- Brand names ARE allowed if they are one word (e.g., 'nike').\n\n"

    "Self-check before finalizing:\n"
    "If WordA and WordB could be described with the same 3 clues, reject and pick a new pair."
    )

    client = OpenAI()  # reads OPENAI_API_KEY from env (loaded by load_dotenv)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=20,
        temperature=1.0,
    )
    raw = response.choices[0].message.content.strip()
    words = [w.strip().lower() for w in raw.split(",")]
    return words

def initiate(player_count):
    """Generate words via OpenAI API and assign to players.

    Returns: (player_words, imp_player_idx, imp_word, civ_word)
    Raises Exception if API call fails.
    """
    word_pool = create_words()

    if len(word_pool) < 2:
        raise ValueError(f"API returned invalid words: {word_pool}")

    # Log words to prevent future duplicates
    log_words(word_pool[0], word_pool[1])

    imp_idx = r.randint(0, 1)
    imp_word = word_pool[imp_idx]
    civ_word = word_pool[1 - imp_idx]

    imp_player = r.randint(0, player_count - 1)

    player_words = []
    for i in range(player_count):
        if i == imp_player:
            player_words.append(imp_word)
        else:
            player_words.append(civ_word)

    return player_words, imp_player, imp_word, civ_word
