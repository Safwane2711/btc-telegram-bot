# --------- 1. IMPORTS ----------
import os
import requests
from dotenv import load_dotenv
import schedule
import time
from datetime import datetime
import os

def send_telegram(text: str):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN manquant dans .env")
    if not chat_id:
        raise RuntimeError("TELEGRAM_CHAT_ID manquant dans .env")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id, 
        "text": text
    }

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

# --------- 2. CHARGER .env ----
load_dotenv()

# --------- 3. FONCTION API ----
def get_btc_price(vs_currency="usd"):
    api_key = os.getenv("COINGECKO_API_KEY")
    if not api_key:
        raise RuntimeError("COINGECKO_API_KEY manquante dans .env")
    
def get_btc_price_with_change(vs_currency="usd"):
    """
    Retourne(price, change_24h_pct) pour bitcoin dans la devise donnée.
    change_24h_pct est un float (ex: -1.23 pour 1.23%).
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

# --------- 4. FONCTION MAIN ----
def main():

    # Exécution immédiate (facultatif)
    job_send_price()
    # Puis à chaque HH:00
    schedule.every().hour.at(":00").do(job_send_price)

    print("⏱️ Bot planifié : envoi immédiat puis toutes les heures à HH:00. Ctrl+C pour arrêter.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par l'utilisateur.")


def job_send_price():
    """Récupère le prix, envoie sur Telegram, gère les alertes simples."""
    try:
        price_usd, chg = get_btc_price_with_change("usd")
        direction = "🔺" if chg >= 0 else "🔻"
        msg = f"BTC = {price_usd:,.2f} USD  ({direction} {chg:+.2f}% / 24h) — {datetime.now():%H:%M:%S}"
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
        # Erreur API/Telegram -> log + notification sobre
        err = f"[ERREUR job] {e}"
        print(err)
        # Tu peux décider d'envoyer aussi l'erreur sur Telegram si tu veux :
        # send_telegram(err)

# --------- 5. POINT D’ENTRÉE ---
if __name__ == "__main__":
    main()