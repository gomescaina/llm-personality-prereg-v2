"""Parser de listas numeradas — tolerante a formato estranho do modelo.

Aceita '5 = 3', 'Item 5: 3', bullets, etc. Se cair item → retry no run.py.
"""
import re

# Matches '<num> <sep> <rating>' with optional leading 'Item ' word or a markdown
# bullet ('-', '*', '\u2022'). Separators: =, :, -, en-dash, '.', or whitespace.
_LINE = re.compile(
    r"^(?:item\s+)?(?:[-*\u2022]\s*)?(\d{1,3})\s*[=:\-\u2013.]?\s*(\d{1,3})\s*$",
    re.IGNORECASE)


def parse_reply(text, expected_nums, rating_min, rating_max):
    """Return (responses, dropped, out_of_range, n_parsed).

    responses: {num: rating} for in-range ratings.
    dropped:   expected nums with no usable line.
    out_of_range: nums whose rating fell outside [rating_min, rating_max].
    n_parsed:  total lines that matched the num/rating pattern.
    """
    responses = {}
    out_of_range = []
    n_parsed = 0
    seen_nums = set()
    for raw in text.splitlines():
        s = raw.strip()
        if not s:
            continue
        m = _LINE.match(s)
        if not m:
            continue
        num = int(m.group(1))
        rating = int(m.group(2))
        n_parsed += 1
        if rating < rating_min or rating > rating_max:
            out_of_range.append((num, rating))
            continue
        # If a number repeats, keep the last occurrence.
        responses[num] = rating
        seen_nums.add(num)
    expected = set(expected_nums)
    dropped = sorted(expected - seen_nums)
    return responses, dropped, out_of_range, n_parsed


def parse_pid5(text, expected_nums):
    return parse_reply(text, expected_nums, 0, 3)


def parse_ipip(text, expected_nums):
    return parse_reply(text, expected_nums, 1, 5)


def parse_csiv(text, expected_nums):
    return parse_reply(text, expected_nums, 0, 4)


def looks_like_list(text, expected_count):
    """Cheap drift detector: did the reply look like a numbered list at all?"""
    n = sum(1 for raw in text.splitlines() if _LINE.match(raw.strip()))
    return n >= max(1, int(0.8 * expected_count))
