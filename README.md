# 🚀 Algo-Trader Pro: Intelligent Forex Trading System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Stable-brightgreen?style=for-the-badge)
![Strategy](https://img.shields.io/badge/Strategy-Trend%20Confirmation-orange?style=for-the-badge)

מערכת מסחר אלגוריתמית מתקדמת ומודולרית, שנבנתה בשפת Python.
המערכת מתמחה במסחר בצמדי מט"ח (Forex) וסחורות, ומתבססת על אסטרטגיית **"Trend Confirmation Hook"** – זיהוי היפוך מגמה בתוך טרנד קיים.

הפרויקט כולל מנוע Backtesting סופר-מהיר (מבוסס Numpy), מערכת אופטימיזציה מקבילית (Parallel Processing), וויזואליזציה מתקדמת לניתוח ביצועים.

---

## 📊 ביצועים נבחרים (EURUSD H1)

התוצאות להלן מבוססות על בדיקת **Out-of-Sample** של שנה אחרונה (365 ימים), עם ניהול סיכונים שמרני.

| מדד | תוצאה | משמעות |
| :--- | :--- | :--- |
| **Profit Factor** | **1.78** 🏆 | יעילות גבוהה: על כל 1$ הפסד, המערכת מרוויחה 1.78$. |
| **Max Drawdown** | **6.1%** 🛡️ | סיכון מינימלי לתיק ההשקעות. |
| **Annual Return** | **~33%-40%** 💰 | תשואה שנתית משוערת בסיכון נמוך. |
| **Risk/Reward** | **1:2.5** ⚖️ | כל טרייד מרוויח פי 2.5 מהסיכון שלו. |

> **הערה:** המערכת נבדקה בהצלחה גם על **GBPUSD** ו-**XAUUSD** (זהב) עם התאמות פרמטרים ייעודיות.

---

## 📂 מבנה הפרויקט (Project Hierarchy)

המערכת בנויה בארכיטקטורה מודולרית (OOP), כאשר כל רכיב אחראי על תפקיד יחיד ומוגדר היטב.

```mermaid
graph TD;
    Main(main.py) --> Loader(data_loader.py);
    Main --> Optimizer(optimizer.py);
    Optimizer --> Backtester(backtester.py);
    Main --> Backtester;
    Backtester --> Strategy(strategy.py);
    Strategy --> Indicators(indicators.py);
    Main --> Viz(visualization.py);