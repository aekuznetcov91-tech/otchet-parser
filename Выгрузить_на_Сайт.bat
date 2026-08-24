@echo off
chcp 65001 > nul
title Avtoparsing i vygruzka na Cloudflare Pages

echo ==================================================
echo   1. Avtomaticheskiy parsing dannyh...
echo ==================================================
python scripts\parser_engine.py

echo.
echo ==================================================
echo   2. Vygruzka na sayt Cloudflare Pages...
echo ==================================================
python deploy_to_cloudflare.py

echo.
echo ==================================================
echo   Zaversheno! Sayt obnovlen:
echo   - S parolem: https://dashbord-partners.beckelaguas723.workers.dev
echo   - Pryamoy:   https://dashbord-partners1.pages.dev
echo ==================================================
pause