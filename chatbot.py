"""
CryptoBuddy: A simple rule-based crypto advisor chatbot
Author: Silvia 
Run: python cryptobuddy.py
"""

# --------------------------
# Predefined crypto dataset
# --------------------------
crypto_db = {
    "Bitcoin": {
        "symbol": "BTC",
        "price_trend": "rising",
        "market_cap": "high",
        "energy_use": "high",
        "sustainability_score": 3.0
    },
    "Ethereum": {
        "symbol": "ETH",
        "price_trend": "stable",
        "market_cap": "high",
        "energy_use": "medium",
        "sustainability_score": 6.0
    },
    "Cardano": {
        "symbol": "ADA",
        "price_trend": "rising",
        "market_cap": "medium",
        "energy_use": "low",
        "sustainability_score": 8.0
    },
    "Solana": {
        "symbol": "SOL",
        "price_trend": "falling",
        "market_cap": "medium",
        "energy_use": "low",
        "sustainability_score": 7.0
    },
    "Algorand": {
        "symbol": "ALGO",
        "price_trend": "stable",
        "market_cap": "low",
        "energy_use": "low",
        "sustainability_score": 9.0
    }
}

# --------------------------
# Personality & helper text
# --------------------------
BOT_NAME = "CryptoBuddy"
TONE = "Friendly, slightly-professional"
DISCLAIMER = (
    "⚠️ Disclaimer: Crypto is risky. This bot gives simple, rule-based suggestions "
    "for learning purposes only — not financial advice. Always do your own research (DYOR)."
)

# --------------------------
# Core decision rules
# --------------------------
def best_by_profitability(db):
    """
    Profitability priority: prefer rising trend + high market cap,
    then rising + medium market cap, then stable high market cap, etc.
    """
    def score(item):
        name, info = item
        score = 0
        # Trend score
        if info["price_trend"] == "rising":
            score += 50
        elif info["price_trend"] == "stable":
            score += 20
        else:
            score += 0
        # Market cap score
        if info["market_cap"] == "high":
            score += 30
        elif info["market_cap"] == "medium":
            score += 15
        else:
            score += 5
        # Sustainability slightly counts (investors like green)
        score += info.get("sustainability_score", 0)
        return score

    best = max(db.items(), key=score)
    return best[0], db[best[0]]

def best_by_sustainability(db):
    """
    Sustainability priority: energy_use low + sustainability_score highest
    """
    # Filter for low energy or high sustainability
    sorted_by_sust = sorted(
        db.items(),
        key=lambda kv: (kv[1]["sustainability_score"], kv[1]["energy_use"]),
        reverse=True
    )
    return sorted_by_sust[0][0], sorted_by_sust[0][1]

def combined_recommendation(db, prefer='balanced'):
    """
    Combined logic:
      - 'profit' returns best_by_profitability
      - 'sustain' returns best_by_sustainability
      - 'balanced' returns coin(s) that score well on both
    """
    if prefer == 'profit':
        return best_by_profitability(db)
    if prefer == 'sustain':
        return best_by_sustainability(db)

    # Balanced: compute normalized combined score
    def combined_score(item):
        name, info = item
        # normalize components manually
        trend_score = {"rising": 1.0, "stable": 0.6, "falling": 0.0}[info["price_trend"]]
        market_score = {"high": 1.0, "medium": 0.6, "low": 0.2}[info["market_cap"]]
        sustainability_norm = info["sustainability_score"] / 10.0  # 0..1
        # weights: profit 0.5, sustainability 0.5
        return 0.5 * (0.6*trend_score + 0.4*market_score) + 0.5 * sustainability_norm

    best = max(db.items(), key=combined_score)
    return best[0], db[best[0]]

# --------------------------
# Simple NLP matching
# --------------------------
def handle_query(query, db):
    q = query.lower().strip()
    # Quick intent detection via keywords
    if any(kw in q for kw in ["sustain", "eco", "energy", "green"]):
        name, info = best_by_sustainability(db)
        return (f"{BOT_NAME}: 🌱 If you're prioritizing sustainability, consider {name} "
                f"({info['symbol']}). Sustainability score: {info['sustainability_score']}/10. "
                f"Energy use: {info['energy_use']}. {DISCLAIMER}")
    if any(kw in q for kw in ["trend", "trending", "rising", "up"]):
        name, info = best_by_profitability(db)
        return (f"{BOT_NAME}: 🚀 For price momentum, {name} ({info['symbol']}) looks strongest "
                f"— trend: {info['price_trend']}, market cap: {info['market_cap']}. {DISCLAIMER}")
    if any(kw in q for kw in ["buy", "invest", "long-term", "growth"]):
        name, info = combined_recommendation(db, prefer='balanced')
        return (f"{BOT_NAME}: For long-term growth with balance between returns and sustainability, "
                f"consider {name} ({info['symbol']}). Trend: {info['price_trend']}, "
                f"Market cap: {info['market_cap']}, Sustainability: {info['sustainability_score']}/10. {DISCLAIMER}")
    if any(kw in q for kw in ["list", "show", "all coins", "database"]):
        lines = [f"{n} ({v['symbol']}): trend={v['price_trend']}, market={v['market_cap']}, energy={v['energy_use']}, score={v['sustainability_score']}/10"
                 for n, v in db.items()]
        return f"{BOT_NAME}: Here's what I know:\n" + "\n".join(lines)
    if any(kw in q for kw in ["help", "commands", "what can you do"]):
        return (f"{BOT_NAME}: I can: \n"
                "- recommend by sustainability (ask about 'sustainable')\n"
                "- recommend by trend/profitability (ask 'trending up' or 'rising')\n"
                "- suggest for long-term growth (ask 'long-term' or 'growth')\n"
                "- list all known coins (ask 'list')\n"
                f"{DISCLAIMER}")
    # fallback
    return (f"{BOT_NAME}: Sorry, I didn't catch that. Try asking 'Which crypto is trending up?', "
            "'What's the most sustainable coin?', or 'Which should I buy for long-term growth?'.\n"
            f"{DISCLAIMER}")

# --------------------------
# Simple interactive loop
# --------------------------
def run_chatbot(db):
    print(f"Hi! I am {BOT_NAME} — your first AI-powered financial sidekick! ({TONE})")
    print(DISCLAIMER)
    print("Type 'exit' to quit. Type 'help' to see commands.\n")

    while True:
        user = input("You: ").strip()
        if not user:
            continue
        if user.lower() in ('exit', 'quit', 'bye'):
            print(f"{BOT_NAME}: Bye! Good luck and DYOR. 👋")
            break
        response = handle_query(user, db)
        print(response)
        print()

# --------------------------
# If run as script -> start
# --------------------------
if __name__ == "__main__":
    run_chatbot(crypto_db)
