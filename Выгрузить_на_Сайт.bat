@echo off
chcp 65001 > nul
title Выгрузка на Cloudflare Pages (dashbord-partners1)

echo ==================================================
echo   Выгрузка проекта на сайт dashbord-partners1...
echo ==================================================
echo.

python deploy_to_cloudflare.py

echo.
echo ==================================================
echo   Завершено! Сайт обновлен:
echo   https://dashbord-partners1.pages.dev
echo ==================================================
pause
