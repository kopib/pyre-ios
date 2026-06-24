"""Analyst opinion scraper for finanzen.net with local file caching."""

import logging
import re
from collections import defaultdict
from datetime import datetime, timedelta
from operator import itemgetter
from pathlib import Path
from typing import Final, TypedDict

from bs4 import BeautifulSoup
from curl_cffi import requests
from utils.logger import setup_standalone_logging

# Setup self-contained logger targeting stderr
logger = logging.getLogger(__name__)


# Constants for linter compliance
MIN_TDS_COUNT: Final[int] = 4
HTTP_SUCCESS: Final[int] = 200
MAX_PAGES_LIMIT: Final[int] = 50

# List of all analyst ratings we want to parse
RATINGS_LIST: Final[list[str]] = [
    "equal weight",
    "sector perform",
    "equal-weight",
    "market-perform",
    "equalweight",
    "sector-perform",
    "outperform",
    "underperform",
    "underweight",
    "overweight",
    "akkumulieren",
    "reduzieren",
    "kaufen",
    "verkaufen",
    "halten",
    "buy",
    "hold",
    "sell",
    "neutral",
    "add",
]

# Pattern to extract rating from anchor text
RATINGS_PATTERN: Final[re.Pattern[str]] = re.compile(
    rf"\s+({'|'.join(RATINGS_LIST)})$", re.IGNORECASE
)

# Map raw ratings to standard BUY/HOLD/SELL categories
RATING_MAP: Final[dict[str, str]] = {
    "buy": "BUY",
    "kaufen": "BUY",
    "outperform": "BUY",
    "overweight": "BUY",
    "akkumulieren": "BUY",
    "add": "BUY",
    "hold": "HOLD",
    "halten": "HOLD",
    "neutral": "HOLD",
    "equal weight": "HOLD",
    "equal-weight": "HOLD",
    "equalweight": "HOLD",
    "market-perform": "HOLD",
    "sector perform": "HOLD",
    "sector-perform": "HOLD",
    "sell": "SELL",
    "verkaufen": "SELL",
    "underperform": "SELL",
    "underweight": "SELL",
    "reduzieren": "SELL",
}


class Opinion(TypedDict):
    """Represents a parsed analyst opinion."""

    date: datetime
    stock: str
    rating: str
    analyst: str


class AggregatedStock(TypedDict):
    """Represents aggregated ratings statistics for a single stock."""

    stock: str
    buy_total: int
    buy_unique: int
    hold_total: int
    hold_unique: int
    sell_total: int
    sell_unique: int


def parse_date(date_str: str) -> datetime:
    """Parses date string from finanzen.net.

    Supports 'HH:MM' (for today) and 'DD.MM.YY' (for past dates).
    """
    now = datetime.now().astimezone()
    if ":" in date_str:
        parts = date_str.split(":")
        hour = int(parts[0])
        minute = int(parts[1])
        return now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # DD.MM.YY split manually to satisfy DTZ007
    parts = date_str.split(".")
    day = int(parts[0])
    month = int(parts[1])
    year = 2000 + int(parts[2])
    return datetime(year, month, day, tzinfo=now.tzinfo)


def _parse_row(row: BeautifulSoup, link: BeautifulSoup) -> Opinion | None:
    """Parses a single row from the analyst opinions table."""
    tds = row.find_all("td")
    if len(tds) < MIN_TDS_COUNT:
        return None

    date_text = tds[0].get_text(strip=True)
    link_text = link.get_text(strip=True)
    analyst = tds[3].get_text(strip=True)

    match = RATINGS_PATTERN.search(link_text)
    if not match:
        logger.debug("Skipping row with unmatched rating text: %s", link_text)
        return None

    raw_rating = match.group(1).lower()
    stock = link_text[: match.start()].strip()
    rating = RATING_MAP.get(raw_rating, "HOLD")

    try:
        date = parse_date(date_text)
    except ValueError:
        logger.warning("Could not parse date text: %s", date_text)
        return None

    return {
        "date": date,
        "stock": stock,
        "rating": rating,
        "analyst": analyst,
    }


def _parse_page_anchors(
    anchors: list[BeautifulSoup], cutoff_date: datetime, opinions: list[Opinion]
) -> bool:
    """Parses anchors on a page. Returns True to continue, False to stop."""
    for a in anchors:
        row = a.find_parent("tr")
        if not row:
            continue
        opinion = _parse_row(row, a)
        if not opinion:
            continue

        if opinion["date"] < cutoff_date:
            return False

        opinions.append(opinion)
    return True


def fetch_analyst_opinions(days: int = 14) -> list[Opinion]:
    """Fetches analyst opinions from finanzen.net for the last N days."""
    opinions: list[Opinion] = []
    today_start = (
        datetime.now().astimezone().replace(hour=0, minute=0, second=0, microsecond=0)
    )
    cutoff_date = today_start - timedelta(days=days)

    page = 1
    should_continue = True

    logger.info("Fetching analyst opinions for the last %d days...", days)

    while should_continue:
        url = f"https://www.finanzen.net/analysen?p={page}"
        logger.info("Loading page %d...", page)

        try:
            response = requests.get(url, impersonate="chrome", timeout=15)
            if response.status_code != HTTP_SUCCESS:
                logger.error(
                    "Failed to fetch page %d: HTTP %d",
                    page,
                    response.status_code,
                )
                break
        except Exception:
            logger.exception("Error loading page %d", page)
            break

        soup = BeautifulSoup(response.text, "html.parser")
        anchors = soup.select('a[href^="/analyse/"]')
        if not anchors:
            logger.warning("No analyst opinion anchors found on page %d", page)
            break

        initial_len = len(opinions)
        should_continue = _parse_page_anchors(anchors, cutoff_date, opinions)
        page_opinions_count = len(opinions) - initial_len

        logger.info("Found %d valid opinions on page %d", page_opinions_count, page)

        if page_opinions_count == 0:
            logger.info("No opinions found on page %d, stopping.", page)
            break

        page += 1
        if page > MAX_PAGES_LIMIT:
            logger.warning("Reached page limit safety threshold.")
            break

    return opinions


def aggregate_opinions(opinions_list: list[Opinion]) -> list[AggregatedStock]:
    """Aggregates opinions stats by stock."""
    stats = defaultdict(
        lambda: {
            "buy_total": 0,
            "buy_analysts": set(),
            "hold_total": 0,
            "hold_analysts": set(),
            "sell_total": 0,
            "sell_analysts": set(),
        }
    )

    for op in opinions_list:
        stock = op["stock"]
        rating = op["rating"]
        analyst = op["analyst"]

        if rating == "BUY":
            stats[stock]["buy_total"] += 1
            stats[stock]["buy_analysts"].add(analyst)
        elif rating == "HOLD":
            stats[stock]["hold_total"] += 1
            stats[stock]["hold_analysts"].add(analyst)
        elif rating == "SELL":
            stats[stock]["sell_total"] += 1
            stats[stock]["sell_analysts"].add(analyst)

    rows: list[AggregatedStock] = []
    for stock, data in stats.items():
        rows.append(
            {
                "stock": stock,
                "buy_total": data["buy_total"],
                "buy_unique": len(data["buy_analysts"]),
                "hold_total": data["hold_total"],
                "hold_unique": len(data["hold_analysts"]),
                "sell_total": data["sell_total"],
                "sell_unique": len(data["sell_analysts"]),
            }
        )
    return rows


def generate_plain_text_report(
    title: str, aggregated_rows: list[AggregatedStock]
) -> str:
    """Generates a vertical, mobile-friendly layout for standard messaging apps."""
    sorted_rows = sorted(aggregated_rows, key=itemgetter("stock"))
    sorted_rows = sorted(sorted_rows, key=itemgetter("buy_total"), reverse=True)
    sorted_rows = sorted(sorted_rows, key=itemgetter("buy_unique"), reverse=True)

    text_block = f"\n{title}\n"
    if not sorted_rows:
        return text_block + "• Keine Daten gefunden.\n\n"

    for r in sorted_rows[:5]:
        text_block += (
            f"{r['stock']}\n"
            f"├ 🟢 Kauf: {r['buy_total']} (Uniq: {r['buy_unique']})\n"
            f"├ 🟡 Hold: {r['hold_total']} (Uniq: {r['hold_unique']})\n"
            f"└ 🔴 Verkauf: {r['sell_total']} (Uniq: {r['sell_unique']})\n\n"
        )
    return text_block


def build_sms_report_string(opinions: list[Opinion]) -> str:
    """Builds the final text message report string."""
    today_start = (
        datetime.now().astimezone().replace(hour=0, minute=0, second=0, microsecond=0)
    )
    seven_days_ago = today_start - timedelta(days=7)
    opinions_7d = [op for op in opinions if op["date"] >= seven_days_ago]

    agg_14d = aggregate_opinions(opinions)
    agg_7d = aggregate_opinions(opinions_7d)

    final_sms = f"📈 ANALYSTEN REPORT ({today_start.strftime('%d.%m.%Y')})\n"
    final_sms += generate_plain_text_report("🔥 TOP 5 - 7 TAGE", agg_7d)
    final_sms += generate_plain_text_report("📊 TOP 5 - 14 TAGE", agg_14d)
    return final_sms


def main() -> None:
    """Main execution entry point for the stock pipeline."""
    setup_standalone_logging()

    logger.info("Starting stock pipeline...")

    # 1. Run your optimized 14-day scrape loop
    opinions = fetch_analyst_opinions(days=14)

    if not opinions:
        logger.warning("No new stock opinions fetched today. Standing down.")
        return

    # 2. Build your text string layout
    final_sms = build_sms_report_string(opinions)

    # 3. Save clean report text to dedicated file
    file_path = Path(__file__).resolve()
    outputs_dir = file_path.parents[1] / "outputs"
    try:
        outputs_dir.mkdir(parents=True, exist_ok=True)
        sms_file_path = outputs_dir / f"{file_path.stem}_sms.txt"
        sms_file_path.write_text(final_sms, encoding="utf-8")
        logger.info("💾 Clean report cached to %s", sms_file_path)
    except Exception:
        logger.exception("Failed to write SMS text file")


if __name__ == "__main__":
    main()
