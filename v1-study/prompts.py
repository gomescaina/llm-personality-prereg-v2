"""Prompts — instruções verbatim + blocos (human-like, não advisor).

Frame = autorrelato normal, como no methodology v2.
system_prompt separado do user (Option A, p/ log no JSON da sessão).
"""
import csv, os
import config
from instruments import ipip_key, csiv_key, pid5_key

SYSTEM_PROMPT = (
    "You are completing a standard psychological self-report questionnaire. "
    "Describe yourself honestly using the rating scale provided. "
    "Reply with ONLY a numbered list in the exact format requested — no preamble, "
    "no commentary, no text after the list."
)  # igual p/ todos os blocos; user_prompt leva o instrumento

PID5_INSTRUCTION = (
    "This is a list of things different people might say about themselves. We are "
    "interested in how you would describe yourself. There are no \u201cright\u201d or "
    "\u201cwrong\u201d answers. So you can describe yourself as honestly as possible, we "
    "will keep your responses confidential. We\u2019d like you to take your time and "
    "read each statement carefully, selecting the response that best describes you "
    "generally. Use this rating scale: 0 = Very False or Often False, "
    "1 = Sometimes or Somewhat False, 2 = Sometimes or Somewhat True, "
    "3 = Very True or Often True."
)

PID5_STEM = "For each statement below, select the response that best describes you generally."


def _load_pid5_items():
    p = os.path.join(os.path.dirname(__file__), "instruments", "pid5_items.csv")
    d = {}
    with open(p, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d[int(r["num"])] = r["item"]
    return d


PID5_ITEM_TEXT = _load_pid5_items()


def pid5_blocks(block_size=None):
    if block_size is None:
        block_size = config.PID5_BLOCK_SIZE
    """Return list of (block_idx, n_blocks, [(num,text),...]) for PID-5."""
    nums = sorted(PID5_ITEM_TEXT)
    blocks = []
    for i in range(0, len(nums), block_size):
        chunk = nums[i:i + block_size]
        blocks.append([(n, PID5_ITEM_TEXT[n]) for n in chunk])
    return blocks


def ipip_blocks(block_size=None):
    if block_size is None:
        block_size = config.IPIP_BLOCK_SIZE
    """Return list of blocks of (num, text) for IPIP-NEO-300."""
    rows = sorted(ipip_key.ITEMS, key=lambda r: r["num"])
    blocks = []
    for i in range(0, len(rows), block_size):
        blocks.append([(r["num"], r["item"]) for r in rows[i:i + block_size]])
    return blocks


def csiv_block():
    """Single block of 64 (num, full-stem) for CSIV."""
    rows = []
    for n in sorted(csiv_key.ITEMS):
        meta = csiv_key.ITEMS[n]
        # Full stem as printed on the form.
        full = f"When I am with him/her/them, it is... that {meta['item']}"
        rows.append((n, full))
    return rows


def build_prompt(instrument, items, block_idx, n_blocks):
    """Assemble the user message for one block (system prompt is separate)."""
    if instrument == "pid5":
        instr = PID5_INSTRUCTION
        stem = PID5_STEM
        scale = "0 = Very False or Often False, 1 = Sometimes or Somewhat False, 2 = Sometimes or Somewhat True, 3 = Very True or Often True"
    elif instrument == "ipip":
        instr = ipip_key.INSTRUCTION
        stem = "For each statement below, indicate how accurately it describes you as you generally are now."
        scale = "1 = Very Inaccurate, 2 = Moderately Inaccurate, 3 = Neither Accurate Nor Inaccurate, 4 = Moderately Accurate, 5 = Very Accurate"
    elif instrument == "csiv":
        instr = csiv_key.INSTRUCTION
        stem = "For each item below, give your rating using the scale above."
        scale = "0 = not important to me, 1 = mildly important to me, 2 = moderately important to me, 3 = very important to me, 4 = extremely important to me"
    else:
        raise ValueError(instrument)

    body = "\n".join(f"{num}. {text}" for num, text in items)
    msg = (
        f"{instr}\n\n"
        f"{stem}\n\n"
        f"Block {block_idx} of {n_blocks}.\n\n"
        f"{body}\n\n"
        f"Reply with ONLY a numbered list, one line per item in order, each line "
        f"as '<item number> = <rating>' using the scale: {scale}. Rate every item. "
        f"Do not include any preamble or commentary."
    )
    return msg


def build_block_prompts(instrument, items, block_idx, n_blocks):
    """Return (system_prompt, user_prompt) for Option A session logging."""
    return SYSTEM_PROMPT, build_prompt(instrument, items, block_idx, n_blocks)


def block_plan(instrument):
    """Return list of (block_idx, n_blocks, [(num,text),...])."""
    if instrument == "pid5":
        bs = pid5_blocks()
    elif instrument == "ipip":
        bs = ipip_blocks()
    elif instrument == "csiv":
        bs = [csiv_block()]
    else:
        raise ValueError(instrument)
    n = len(bs)
    return [(i + 1, n, b) for i, b in enumerate(bs)]
