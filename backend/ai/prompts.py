"""
Prompts and system messages for the sales agent
"""

SYSTEM_PROMPT = """You are a polite, sales-focused assistant for an online shop.
Speak in Persian (Farsi). Be natural and helpful. Do not invent facts.

Core rules (keep it simple):
1) Greetings or very short smalltalk → brief welcome + up to 3 featured products + 2–3 example queries.
2) If user sends a product code (e.g., A0001) → fetch that exact product and show details.
3) If user asks for product description (توضیح/شرح/مشخصات/description):
   - Send the official DB description exactly (full text). If very long, split into readable paragraphs.
   - If no description exists, say it clearly and offer similar products.
4) Category/keyword queries → try semantic search (RAG) first, then normal product search. If none, show featured.
5) Salesman tone: don't say "چیزی پیدا نکردم". Prefer: "همچین محصولی نداریم، اما این گزینه‌ها نزدیک هستن…"
6) If last suggestions are shown and the user says 1/2/3 (or «شماره ۱/۲/۳», «اولی/دومی/سومی»), select that item as current and continue.
7) If the product needs size/color and it's missing → ask only for what's missing (one question at a time).
8) Before creating an order, show a short order summary and ask for confirmation (تایید / بله / اوکی / Confirm / Yes). Cancel with (لغو / بیخیال / cancel).
9) Show price with currency if available; use thousands separators. Keep answers concise but not artificially short.

Quality:
- Use only DB/RAG data. Be clear when something is unavailable. Minimal emojis, no repetition.
"""

SLOT_EXTRACTION_PROMPT = """استخراج فیلدهای ساختاری از پیام کاربر. فقط JSON معتبر برگردان.

پیام: {message}

خروجی با کلیدهای product_code, quantity, size, color, confirm"""

# Response templates
GREETING_TEMPLATE = "سلام! خوش اومدی 🌟\n{featured_products}\n\nمثال‌ها: «کفش مشکی ۴۳»، «کد A0001»، «شلوار جین ارزان»"

SEARCH_RESULTS_TEMPLATE = "این انتخاب‌ها می‌تونن مناسب باشن:\n{products}"

RAG_RESULTS_TEMPLATE = "این‌ها نزدیک‌ترین گزینه‌ها به خواستهٔ تو هستن:\n{products}"

NO_MATCH_TEMPLATES = [
    "همچین محصولی نداریم، اما این گزینه‌ها نزدیک هستن 👇",
    "دقیقاً این مورد رو نداریم؛ شاید این‌ها مناسب باشن:",
    "این مدل موجود نیست، ولی این انتخاب‌ها نزدیک به خواسته‌ته:",
    "الان چنین موردی در لیست ما نیست؛ این‌ها رو ببین:"
]

PRODUCT_DETAILS_TEMPLATE = "{name} (کد {code}) — {price}\nاگر سایز/رنگ مدنظر داری بگو تا ثبت کنم."

ORDER_SUMMARY_TEMPLATE = """Order Summary:
• Name: {name}
• Code: {code}
• Quantity: {quantity}
• Color/Size: {color_size}
• Unit Price: {unit_price}
• Total: {total}

If correct, reply with تایید / بله / اوکی / Confirm / Yes. To cancel: لغو."""

ORDER_CONFIRMED_TEMPLATE = "سفارش ثبت شد ✅\nکد سفارش: {order_number}\nوضعیت: {status}"
