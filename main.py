# --------- 1. IMPORTS ----------
import os
import requests
from dotenv import load_dotenv
import schedule
import time
from datetime import datetime
from zoneinfo import ZoneInfo

# --------- 2. TELEGRAM ----------
def send_telegram(text: str):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN manquant dans .env")
    if not chat_id:
        raise RuntimeError("TELEGRAM_CHAT_ID manquant dans .env")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    try:
        resp = requests.post(url, data=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("ok"):
            raise RuntimeError(f"Réponse Telegram non OK: {data}")
        return data
    except requests.exceptions.Timeout as e:
        raise RuntimeError("Timeout Telegram") from e
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"HTTP Telegram {resp.status_code}: {resp.text[:120]}") from e
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError("Connexion Telegram échouée") from e

# --------- 3. CHARGER .env ----
load_dotenv()

# --------- 4. API COINGECKO ----
def get_btc_price_with_change(vs_currency="usd"):
    """
    Retourne (price, change_24h_pct) pour bitcoin dans la devise donnée.
    change_24h_pct est un float (ex: -1.23 pour -1,23%).
    """
    api_key = os.getenv("COINGECKO_API_KEY")
    if not api_key:
        raise RuntimeError("COINGECKO_API_KEY manquante dans .env")

    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin",
        "vs_currencies": vs_currency,
        "include_24hr_change": "true",
        "x_cg_demo_api_key": api_key,
    }
    headers = {
        "User-Agent": "btc-edu-bot/1.0 (learning project)",
        "x-cg-demo-api-key": api_key,
    }

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.Timeout as e:
        raise RuntimeError("Timeout: l'API a mis trop de temps à répondre") from e
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError("ConnectionError: problème réseau/connexion") from e
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"HTTPError: statut {resp.status_code} - {resp.text[:120]}") from e
    except ValueError as e:
        raise RuntimeError("Réponse invalide (JSON illisible)") from e

    try:
        price = float(data["bitcoin"][vs_currency])
        change_key = f"{vs_currency}_24h_change"
        change_24h = float(data["bitcoin"][change_key])
        return price, change_24h
    except Exception as e:
        raise RuntimeError(f"Schéma JSON inattendu: {data}") from e

# --------- 5. JOB D'ENVOI ----
def job_send_price():
    """Récupère le prix, envoie sur Telegram, gère les alertes simples."""
    try:
        price_usd, chg = get_btc_price_with_change("usd")
        direction = "🔺" if chg >= 0 else "🔻"

        # Heure locale Paris
        now_paris = datetime.now(ZoneInfo("Europe/Paris"))

        msg = f"BTC = {price_usd:,.2f} USD ({direction} {chg:+.2f}% / 24h) — {now_paris:%H:%M:%S}"
        msg = msg.replace(",", " ")
        print(msg)
        send_telegram(msg)

        # --- Alertes (seuils optionnels via .env) ---
        alert_min = os.getenv("ALERT_MIN_USD")
        alert_max = os.getenv("ALERT_MAX_USD")
        if alert_min:
            try:
                if price_usd < float(alert_min):
                    send_telegram(f"⚠️ Alerte: BTC < {float(alert_min):,.0f} USD".replace(",", " "))
            except ValueError:
                print("[WARN] ALERT_MIN_USD invalide (non numérique)")
        if alert_max:
            try:
                if price_usd > float(alert_max):
                    send_telegram(f"⚠️ Alerte: BTC > {float(alert_max):,.0f} USD".replace(",", " "))
            except ValueError:
                print("[WARN] ALERT_MAX_USD invalide (non numérique)")

    except RuntimeError as e:
        err = f"[ERREUR job] {e}"
        print(err)
        # Optionnel:
        # send_telegram(err)

# --------- 6. CHECKER HEURE PARIS ----
def check_scheduled_tasks():
    now = datetime.now(ZoneInfo("Europe/Paris"))

    # Envoi à 09:00 (heure de Paris)
    if now.hour == 9 and now.minute == 0:
        job_send_price()

    # Envoi toutes les 4 heures (09h, 13h, 17h, 21h, 01h, 05h)
    # Note : 9,13,17,21,1,5 -> hour % 4 == 1
    elif now.hour % 4 == 1 and now.minute == 0:
        job_send_price()

# --------- 7. MAIN / SCHEDULER ----
def main():
    # Vérifie chaque minute et déclenche selon l'heure Europe/Paris
    schedule.every(1).minutes.do(check_scheduled_tasks)

    print("Bot lancé : vérification chaque minute (heure Europe/Paris)")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("Arrêt manuel.")

# --------- 8. POINT D’ENTRÉE ----
if __name__ == "__main__":
    main()
