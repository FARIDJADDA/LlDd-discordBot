



# LlDd DiscordBot
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Pull Requests](https://img.shields.io/badge/Contributions-Welcome-brightgreen)

<p align="left">
  <img src="assets/avatar_lldd_bot1.jpg" alt="Bannière du bot" width="50%">
</p>

<p align="left">
  <img src="assets/hugging_face_discord.png" alt="Aperçu du bot" width="50%">
</p>



Un bot Discord complet et personnalisable conçu pour gérer et animer des serveurs communautaires.
Ce bot inclut des fonctionnalités de modération, mini-jeux, logs avancés, statistiques, et bien plus encore.

## Table des matières

1. [Description du projet](#description-du-projet)
2. [Prérequis](#prérequis)
3. [Installation](#installation)
4. [Structure du projet](#structure-du-projet)
5. [Commandes disponibles](#commandes-disponibles)
6. [Ajouter des fonctionnalités](#ajouter-des-fonctionnalités)
7. [Contributions](#contributions)

---

## Description du projet

Ce bot Discord propose plusieurs fonctionnalités clés :
- **Modération** : commandes pour bannir, expulser, gérer les avertissements.
- **Mini-jeux** : quiz sur le gaming, lancer de dés.
- **Logs avancés** : suivi des modifications/suppressions de messages et des changements de rôles.
- **Statistiques** : données sur l'activité du serveur et statistiques Call of Duty.
- **Attribution de rôles** : rôles automatiques pour les nouveaux membres.
- **Notifications Twitch** : alertes en cas de stream en direct.

---

## 📚 Prérequis

- **Python 3.8+** : [Télécharger Python](https://www.python.org/downloads/)
- **Clé API Discord** : Créez votre bot sur [Discord Developer Portal](https://discord.com/developers/applications).
- (Optionnel) Clés API Twitch et Call of Duty pour des fonctionnalités avancées.

---

## 🛠️ Installation

1. Clonez ce projet :
   ```bash
   git clone <URL_DU_REPO>
   cd project/
    ```
   
2. Installez les dépendances nécessaires :
    ```bash
    pip install -r requirements.txt
   ```
   
3. Configurez vos clés API :
⚠️ **Important** : Ne partagez jamais votre fichier `.env` contenant vos clés API sur des dépôts publics. Assurez-vous d'ajouter le fichier `.env` ou `config` à votre `.gitignore`.
    * Créez un fichier config à la racine du projet :
    ```
    DISCORD_TOKEN=ton_token_discord
    TWITCH_CLIENT_ID=ton_client_id_twitch
    TWITCH_CLIENT_SECRET=ton_secret_twitch
    COD_API_KEY=ta_clé_api_cod
    LOG_FILE=bot_logs.log
    LOG_LEVEL=INFO
    ```
   
4. python main.py
    ```bash
   python main.py
    ```

## 🧩 Structure du projet
```
    project/
    ├── cogs/
    │   ├── filters.py         # Gestion des mots interdits et du spam
    │   ├── games.py           # Commandes pour les mini-jeux (quiz, lancer de dés)
    │   ├── message_log.py         # Logs des messages modifiés/supprimés et des rôles
    │   ├── moderation.py      # Commandes de modération
    │   ├── roles.py           # Attribution automatique de rôles
    │   ├── stats.py           # Commande pour les statistiques du serveur
    │   ├── twitch.py          # Notifications pour les streamers Twitch
    │   ├── warnings.py        # Gestion des avertissements
    │   ├── welcome.py         # Messages de bienvenue
    ├── utils/
    │   ├── logger.py          # Gestion des logs globaux
    ├── config                 # Clés API et secrets
    ├── banned_words.json      # Liste des mots interdits
    ├── default_roles.json     # Liste des rôles par défaut
    ├── warnings.json          # Données des avertissements
    ├── main.py                # Point d'entrée principal
    ├── requirements.txt       # Dépendances nécessaires
```

## 📜 Commandes Disponibles

### **Commandes Utilitaires**
* **`/status`**  
  ➡️ Affiche le statut actuel du bot (uptime, cogs chargés, etc.).  
* **`/restart`** *(Admin uniquement)*  
  ➡️ Redémarre le bot.

---

### **Commandes de Modération**
* **`/ban`** @Utilisateur [raison] *(Permission : ban_members)*  
  ➡️ Bannit un utilisateur avec une raison facultative.  
* **`/kick`** @Utilisateur [raison] *(Permission : kick_members)*  
  ➡️ Expulse un utilisateur avec une raison facultative.  
* **`/banned_list`**  
  ➡️ Liste les utilisateurs bannis du serveur.

---

### **Commandes pour les Avertissements**
* **`/warn`** @Utilisateur [raison] *(Permission : manage_messages)*  
  ➡️ Avertit un utilisateur pour une raison donnée.  
* **`/warnings`** @Utilisateur  
  ➡️ Affiche tous les avertissements attribués à un utilisateur.  
* **`/clear_warnings`** @Utilisateur  
  ➡️ Supprime tous les avertissements d’un utilisateur.  
* **`/set_max_warnings`** <nombre>  
  ➡️ Définit le nombre maximum d'avertissements avant une sanction.

---

### **Commandes pour les Rôles**
* **`/set_default_roles`** rôle1, rôle2 *(Admin uniquement)*  
  ➡️ Définit les rôles attribués automatiquement aux nouveaux membres.  
* **`/show_default_roles`** *(Admin uniquement)*  
  ➡️ Affiche les rôles par défaut actuels.

---

### **Commandes pour les Mini-Jeux**
* **`/quiz`**  
  ➡️ Pose une question sur le gaming, l'utilisateur a 3 chances pour répondre.  
* **`/roll`** [faces=6]  
  ➡️ Simule un lancer de dés avec le nombre de faces spécifié (par défaut : 6).

---

### **Commandes de Statistiques**
* **`/stats`**  
  ➡️ Affiche les statistiques générales du serveur : membres, rôles, canaux, etc.  
* **`/codstats`** [pseudo] [plateforme]  
  ➡️ Récupère et affiche les statistiques Call of Duty pour un joueur.

---

### **Commandes pour les Sondages**
* **`/poll`** "Question" "Choix1, Choix2, Choix3" [durée en minutes]  
  ➡️ Crée un sondage interactif avec des réactions et une durée optionnelle. Les résultats sont affichés à la fin.

---

### **Commandes Hugging Face**
* **`/ask_hf`** [question]  
  ➡️ Pose une question à un modèle Hugging Face. Les modèles sont testés dynamiquement jusqu’à trouver un disponible.  

---

### **Commandes Welcome**
* **`/set_rules_channel`** <#channel>  
  ➡️ Configure le canal des règles.  
* **`/set_welcome_channel`** <channel_name>  
  ➡️ Configure le canal de bienvenue.

---

### **Commandes ChatGPT**
* **`/ask`** [question]  
  ➡️ Pose une question à ChatGPT en utilisant l’API OpenAI.

---

### **Commandes Twitch**
**Note : Fonctionnalité désactivée**  
*(L'API officielle Twitch n'étant pas disponible pour surveiller les lives, cette section a été désactivée pour le moment.)*

---

### **Mises à jour récentes**
- **Intégration Hugging Face** pour poser des questions aux modèles NLP comme **Bloom** ou **Falcon**.
- **Amélioration des sondages** : minuterie dynamique et résultats automatiques.
- **Refonte ChatGPT** pour compatibilité OpenAI v1.0.0.
- **Gestion d'erreurs enrichie**.

---

### **Étapes pour tester**
1. **Lance ton bot et utilise les commandes listées.**
2. Assure-toi que chaque fonctionnalité répond correctement et affiche les informations dans des embeds cohérents.


---

## 🛠️ Exemple de Commandes Avancées

### Modération :
 ```
/ban @Player1 Comportement inapproprié /kick @Player2 Inactivité prolongée
 ```

### Mini-Jeux :
 ```
 /quiz /roll 20
 ```

## 🔧 Ajouter vos propres fonctionnalités

### Créer une nouvelle commande :
1. **Créez un fichier dans le dossier `cogs/`**  
   Par exemple : `my_feature.py`.

2. **Ajoutez une classe avec des commandes hybrides ou Slash :**  
   Exemple de commande hybride :
   ```python
   from discord.ext import commands

   class MyFeature(commands.Cog):
       def __init__(self, bot):
           self.bot = bot

       @commands.hybrid_command(name="ma_commande", description="Ma nouvelle commande")
       async def ma_commande(self, ctx):
           if isinstance(ctx, discord.Interaction):
               await ctx.response.send_message("Ceci est une nouvelle commande Slash !")
           else:
               await ctx.send("Ceci est une nouvelle commande classique !")
   ```
   
3. **Ajoutez une fonction `setup` pour l'intégration du Cog :**
   Cela permet d'ajouter automatiquement la nouvelle classe au bot.
   ```python
   async def setup(bot):
       await bot.add_cog(MyFeature(bot))
   ```
   
4. **Rechargez ou redémarrez le bot :**
   Si votre bot est en cours d'exécution, utilisez la commande de redémarrage ou rechargez uniquement le cog concerné :
   ```
   !reload_cog cogs.my_feature
   ```

### Exemple pour tester :
1. **Créer un fichier** `cogs/example.py`
   ```python
   import discord
   from discord.ext import commands
   
   class ExampleCog(commands.Cog):
       def __init__(self, bot):
           self.bot = bot
   
       @commands.hybrid_command(name="hello", description="Dit bonjour.")
       async def hello(self, ctx):
           if isinstance(ctx, discord.Interaction):
               await ctx.response.send_message("Bonjour ! 👋")
           else:
               await ctx.send("Bonjour ! 👋")
   async def setup(bot):
        await bot.add_cog(ExampleCog(bot))
   ```
   
2. **Rechargez ou redémarrez le bot et utilisez** `/hello` ou `!hello`. 🎉


*Cette section vous guidera pour ajouter facilement vos propres fonctionnalités tout en maintenant la structure modulaire de votre bot! 😊*

## 🤝 Contributions

Les contributions sont les bienvenues ! Pour participer, suivez ces étapes :

1. Forkez ce dépôt.
2. Créez une branche pour votre fonctionnalité (par exemple, `feat/ajout-sondage`).
3. Testez vos modifications localement.
4. Ouvrez une pull request en expliquant vos changements.

### ✅ Checklist pour les Pull Requests :
- [ ] Ajout d'une fonctionnalité ou d'une correction de bug.
- [ ] Testé localement pour éviter les régressions.
- [ ] Documentation mise à jour (le cas échéant).

## ⚖️ Licence
Ce projet est sous licence **MIT**. Vous êtes libre de l'utiliser, de le modifier et de le distribuer.
Consultez le fichier [LICENSE](./LICENSE) pour plus d'informations.


# ☑️ ©️REDIT 
IF you like and clone Give a star to project ⭐

