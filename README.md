# BTC Telegram Bot

Ce projet est un script Python qui envoie automatiquement le prix du Bitcoin sur Telegram.  
Les données sont récupérées via l'API gratuite de CoinGecko.  
Le bot envoie :
- le prix du Bitcoin en USD,
- la variation du prix sur 24 heures.

---

## 1. Installation et utilisation en local

### a) Cloner le projet
```bash
git clone https://github.com/Safwane2711/btc-telegram-bot.git
cd btc-telegram-bot
```

### b) Installer les dépendances
```bash
pip install -r requirements.txt
```

### c) Créer un fichier `.env` (à partir de `.env.example`)
Exemple de contenu :
```
COINGECKO_API_KEY=ta_clé_api
TELEGRAM_TOKEN=ton_token_telegram
TELEGRAM_CHAT_ID=ton_chat_id
```

### d) Lancer le bot
```bash
python main.py
```

Le bot enverra un message immédiatement, puis une fois par heure.

---

## 2. Déploiement sur le cloud (Railway)

1. Pousser le projet sur GitHub  
2. Créer un projet sur https://railway.app  
3. Connecter le dépôt GitHub  
4. Ajouter les variables d’environnement (.env) dans Railway  
5. Indiquer la commande de lancement :
```bash
python main.py
```

Le bot tournera alors 24h/24, même si l'ordinateur est éteint.

---

## 3. Améliorations possibles

- Ajouter l’EUR en plus de l’USD  
- Ajouter des commandes Telegram (/price, /help, etc.)  
- Sauvegarder les prix dans un fichier CSV  
- Ajouter un graphique ou une interface web

---

## Auteur

Projet réalisé par Safwane Eidel, dans le but d’apprendre Python.
