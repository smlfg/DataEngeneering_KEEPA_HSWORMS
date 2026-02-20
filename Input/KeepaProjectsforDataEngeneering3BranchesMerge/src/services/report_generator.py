"""
Report Generator Service
Generates HTML and plain-text emails from scored deals
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
import json

from jinja2 import Environment, BaseLoader, TemplateSyntaxError

from src.config import get_settings


class ReportGeneratorService:
    """
    Generates professional HTML emails from deal data

    Features:
    - Mobile-responsive HTML
    - Plain-text fallback
    - UTM tracking on all links
    - Deal scoring visualization
    - Unsubscribe footer
    """

    def __init__(self):
        self.settings = get_settings()
        self.env = Environment(loader=BaseLoader())

    def generate_report(
        self, deals: list, filter_name: str, filter_config: dict, locale: str = "de"
    ) -> dict:
        """
        Generate HTML and plain-text report from deals

        Args:
            deals: List of scored deal dictionaries
            filter_name: Name of the filter
            filter_config: Filter configuration for header
            locale: Language locale (de, en)

        Returns:
            dict with 'html' and 'text' keys
        """
        # Limit to top 15 deals
        top_deals = deals[:15]

        # Generate HTML
        html = self._render_html(
            deals=top_deals,
            filter_name=filter_name,
            filter_config=filter_config,
            locale=locale,
        )

        # Generate plain text
        text = self._render_text(
            deals=top_deals,
            filter_name=filter_name,
            filter_config=filter_config,
            locale=locale,
        )

        return {
            "html": html,
            "text": text,
            "deal_count": len(top_deals),
            "generated_at": datetime.utcnow().isoformat(),
        }

    def _render_html(
        self, deals: list, filter_name: str, filter_config: dict, locale: str
    ) -> str:
        """Render HTML email template"""

        # Build filter summary for header
        price_range = filter_config.get("price_range", {})
        discount_range = filter_config.get("discount_range", {})
        categories = filter_config.get("categories", [])

        filter_summary = []
        if price_range.get("min") or price_range.get("max"):
            min_p = price_range.get("min", 0)
            max_p = price_range.get("max", 10000)
            filter_summary.append(f"€{min_p}-{max_p}")
        if discount_range.get("min") or discount_range.get("max"):
            d_min = discount_range.get("min", 0)
            d_max = discount_range.get("max", 100)
            filter_summary.append(f"{d_min}-{d_max}% Rabatt")
        if categories:
            filter_summary.append(f"Kategorien: {', '.join(categories[:3])}")

        today = datetime.utcnow().strftime(
            "%d.%m.%Y" if locale == "de" else "%B %d, %Y"
        )

        html = f"""<!DOCTYPE html>
<html lang="{locale}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Deine Deals</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px 20px; text-align: center; }}
        .header h1 {{ color: #ffffff; font-size: 24px; margin-bottom: 5px; }}
        .header p {{ color: rgba(255,255,255,0.9); font-size: 14px; }}
        .filter-info {{ background: #f8f9fa; padding: 15px 20px; border-bottom: 1px solid #eee; }}
        .filter-info p {{ color: #666; font-size: 13px; margin: 0; }}
        .deal {{ padding: 20px; border-bottom: 1px solid #eee; display: flex; gap: 15px; }}
        .deal-rank {{ font-size: 24px; font-weight: bold; color: #667eea; min-width: 40px; }}
        .deal-content {{ flex: 1; }}
        .deal-title {{ font-size: 15px; font-weight: 600; color: #333; margin-bottom: 8px; line-height: 1.4; }}
        .deal-meta {{ display: flex; gap: 15px; margin-bottom: 10px; font-size: 13px; color: #666; }}
        .deal-price {{ font-size: 18px; font-weight: bold; color: #e53e3e; }}
        .deal-price .original {{ text-decoration: line-through; color: #999; font-weight: normal; font-size: 14px; }}
        .deal-discount {{ background: #48bb78; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
        .deal-score {{ display: inline-block; background: #edf2f7; padding: 4px 10px; border-radius: 12px; font-size: 12px; color: #4a5568; }}
        .deal-score strong {{ color: #667eea; }}
        .cta-button {{ display: block; background: #667eea; color: white; text-align: center; padding: 12px; border-radius: 6px; text-decoration: none; font-weight: 600; margin: 15px 20px; }}
        .footer {{ background: #2d3748; padding: 30px 20px; text-align: center; }}
        .footer a {{ color: #a0aec0; text-decoration: none; font-size: 13px; margin: 0 10px; }}
        .footer p {{ color: #718096; font-size: 12px; margin-top: 15px; }}
        @media (max-width: 480px) {{ .deal {{ flex-direction: column; }} .deal-rank {{ margin-bottom: 10px; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 {filter_name}</h1>
            <p>{today}</p>
        </div>

        <div class="filter-info">
            <p>Filter: {", ".join(filter_summary) if filter_summary else "Alle Kategorien"}</p>
        </div>

        <div class="deals">
"""

        for i, deal in enumerate(deals, 1):
            title = deal.get("title", "Unknown Product")[:80]
            if len(deal.get("title", "")) > 80:
                title += "..."

            current_price = deal.get("current_price")
            original_price = deal.get("original_price")
            discount = deal.get("discount_percent", 0)
            rating = deal.get("rating")
            reviews = deal.get("review_count", 0)
            score = deal.get("deal_score", 0)
            asin = deal.get("asin", "")
            amazon_url = deal.get("amazon_url", "")

            # Add UTM tracking
            utm_url = (
                f"{amazon_url}?utm_source=dealfinder&utm_medium=email&utm_campaign={filter_name[:20].replace(' ', '_')}"
                if amazon_url
                else "#"
            )

            price_html = ""
            if current_price:
                price_html = f'<span class="deal-price">€{current_price}'
                if original_price and float(original_price) > float(current_price):
                    price_html += f' <span class="original">€{original_price}</span>'
                price_html += "</span>"

            rating_html = ""
            if rating:
                stars = "⭐" * int(float(rating))
                rating_html = f"{stars} {float(rating)} ({reviews})"

            html += f"""
            <div class="deal">
                <div class="deal-rank">#{i}</div>
                <div class="deal-content">
                    <div class="deal-title">{title}</div>
                    <div class="deal-meta">
                        {price_html}
                        {f'<span class="deal-discount">-{discount}%</span>' if discount else ""}
                        {f"<span>{rating_html}</span>" if rating else ""}
                    </div>
                    <div class="deal-score">Deal-Score: <strong>{score:.0f}</strong></div>
                    <a href="{utm_url}" class="cta-button">Auf Amazon ansehen →</a>
                </div>
            </div>
"""

        unsubscribe_url = "https://dealfinder.app/unsubscribe"

        html += f"""
        </div>

        <div class="footer">
            <a href="{unsubscribe_url}">Unsubscribe</a>
            <a href="https://dealfinder.app/preferences">Preferences</a>
            <a href="https://dealfinder.app/view-in-browser">View in Browser</a>
            <p>Diese E-Mail wurde gesendet, weil du dich angemeldet hast.<br>
            DealFinder - Finde die besten Schnäppchen</p>
        </div>
    </div>
</body>
</html>
"""

        return html

    def _render_text(
        self, deals: list, filter_name: str, filter_config: dict, locale: str
    ) -> str:
        """Render plain-text email fallback"""

        today = datetime.utcnow().strftime(
            "%d.%m.%Y" if locale == "de" else "%B %d, %Y"
        )

        text = f"""🔥 {filter_name} - {today}

"""

        for i, deal in enumerate(deals, 1):
            title = deal.get("title", "Unknown Product")[:60]
            current_price = deal.get("current_price", "N/A")
            discount = deal.get("discount_percent")
            rating = deal.get("rating")
            score = deal.get("deal_score", 0)
            amazon_url = deal.get("amazon_url", "")

            text += f"""#{i}. {title}
   Preis: €{current_price}"
"""

            if discount:
                text += f"   Rabatt: -{discount}%\n"
            if rating:
                text += f"   Rating: {float(rating)} Sterne\n"
            text += f"   Score: {score:.0f}/100\n"
            text += f"   Link: {amazon_url}\n\n"

        text += """--
DealFinder - Finde die besten Schnäppchen
Unsubscribe: https://dealfinder.app/unsubscribe
"""

        return text

    def generate_deal_card(self, deal: dict, rank: int = 1) -> str:
        """
        Generate a single deal card (for embed in other pages)

        Args:
            deal: Deal dictionary
            rank: Position in list

        Returns:
            HTML string for single deal card
        """
        title = deal.get("title", "Unknown")[:60]
        price = deal.get("current_price", "N/A")
        discount = deal.get("discount_percent", 0)
        rating = deal.get("rating")
        score = deal.get("deal_score", 0)

        return f"""
        <div class="deal-card">
            <span class="rank">#{rank}</span>
            <span class="title">{title}</span>
            <span class="price">€{price}</span>
            <span class="discount">-{discount}%</span>
            <span class="rating">{rating if rating else "N/A"}</span>
            <span class="score">{score:.0f}</span>
        </div>
        """


# Singleton instance
_report_generator: Optional[ReportGeneratorService] = None


def get_report_generator() -> ReportGeneratorService:
    """Get or create report generator singleton"""
    global _report_generator
    if _report_generator is None:
        _report_generator = ReportGeneratorService()
    return _report_generator
