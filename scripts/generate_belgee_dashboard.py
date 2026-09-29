# -*- coding: utf-8 -*-
"""
Belgee Standalone HTML Dashboard Generator
Generates an interactive, responsive, self-contained single-page dashboard:
- belgee_dashboard.html
- site/belgee_dashboard.html
Embedded Tailwind CSS (CDN) + Chart.js (CDN) + Standalone Fallbacks + Full Embedded Data
"""

import os
import sys
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'belgee_analytics.json')

def generate_dashboard():
    print("[1/3] Loading belgee_analytics.json...")
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    aug = data['august']
    sep = data['september']
    vitrina = data['vitrina']
    crm_funnel = data['crm_funnel']
    partner_matrix = data['partner_matrix']
    discount_info = data['discount_info']
    deals_aug = data['deals_aug']
    deals_sep = data['deals_sep']
    leads_aug = data['leads_aug']
    leads_sep = data['leads_sep']

    # Pre-encode JSON safely for embedding into <script>
    embedded_json = json.dumps(data, ensure_ascii=False).replace('</script>', '<\\/script>')

    html_content = f'''<!DOCTYPE html>
<html lang="ru" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BELGEE (Белджи) — Аналитика лидов и сделок | Август–Сентябрь 2026</title>
  
  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  <!-- Chart.js -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <!-- Google Fonts: Inter -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          fontFamily: {{
            sans: ['Inter', 'sans-serif'],
          }},
          colors: {{
            brand: {{
              50: '#f0fdf4',
              100: '#dcfce7',
              500: '#10b981',
              600: '#059669',
              700: '#047857',
              800: '#065f46',
              900: '#064e3b',
            }},
            belgee: {{
              red: '#e11d48',
              dark: '#0f172a',
              accent: '#3b82f6',
            }}
          }}
        }}
      }}
    }}
  </script>
  <style>
    /* Custom Scrollbars */
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: #f1f5f9; }}
    .dark ::-webkit-scrollbar-track {{ background: #1e293b; }}
    ::-webkit-scrollbar-thumb {{ background: #cbd5e1; border-radius: 4px; }}
    .dark ::-webkit-scrollbar-thumb {{ background: #475569; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #94a3b8; }}

    /* Print styling */
    @media print {{
      .no-print {{ display: none !important; }}
      body {{ font-size: 11pt; color: #000; background: #fff; }}
      .page-break {{ page-break-before: always; }}
    }}
  </style>
</head>
<body class="bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-100 min-h-screen font-sans antialiased transition-colors duration-200">

  <!-- Top Navigation & Header -->
  <header class="sticky top-0 z-40 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 transition-colors">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo & Title -->
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 via-teal-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-500/20 text-white font-black text-xl tracking-wider">
            B
          </div>
          <div>
            <div class="flex items-center space-x-2">
              <span class="font-extrabold text-xl tracking-tight text-slate-900 dark:text-white">BELGEE</span>
              <span class="px-2 py-0.5 text-xs font-semibold rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800">Белджи</span>
              <span class="text-xs px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-950/60 text-blue-700 dark:text-blue-400 border border-blue-200 dark:border-blue-800 font-mono">Авг vs Сен 2026</span>
            </div>
            <p class="text-xs text-slate-500 dark:text-slate-400 hidden sm:block">Аналитический дашборд переданных лидов, продаж, воронки и дилерской сети</p>
          </div>
        </div>

        <!-- Header Actions -->
        <div class="flex items-center space-x-3 no-print">
          <button id="themeToggle" class="p-2 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition" title="Переключить тему">
            <svg id="themeMoon" class="w-5 h-5 hidden dark:block" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
            <svg id="themeSun" class="w-5 h-5 block dark:hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/></svg>
          </button>
          <button onclick="window.print()" class="px-3 py-1.5 text-xs font-medium rounded-lg border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 flex items-center space-x-1.5 transition">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/></svg>
            <span>Печать / PDF</span>
          </button>
          <button onclick="exportAllToCSV()" class="px-3 py-1.5 text-xs font-semibold rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm flex items-center space-x-1.5 transition">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
            <span>Экспорт CSV</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 border-t border-slate-100 dark:border-slate-800/60 no-print">
      <nav class="flex space-x-2 sm:space-x-4 py-2 overflow-x-auto text-xs font-medium scrollbar-none" id="mainTabs">
        <button onclick="switchTab('overview')" id="tab-btn-overview" class="tab-btn px-3 py-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 font-semibold border border-emerald-200 dark:border-emerald-800">
          📊 Главный обзор & KPI
        </button>
        <button onclick="switchTab('funnel')" id="tab-btn-funnel" class="tab-btn px-3 py-1.5 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800">
          🌪️ Сквозная воронка (Витрина ➔ Сделки)
        </button>
        <button onclick="switchTab('models')" id="tab-btn-models" class="tab-btn px-3 py-1.5 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800">
          🚘 Модельный ряд (X50 / X70 / S50)
        </button>
        <button onclick="switchTab('dealers')" id="tab-btn-dealers" class="tab-btn px-3 py-1.5 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800">
          🏢 Дилеры и КАМ-матрица
        </button>
        <button onclick="switchTab('registries')" id="tab-btn-registries" class="tab-btn px-3 py-1.5 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800">
          📋 Реестр сделок (86) и лидов (74)
        </button>
        <button onclick="switchTab('pricing')" id="tab-btn-pricing" class="tab-btn px-3 py-1.5 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800">
          🏷️ Скидки и Ценообразование
        </button>
      </nav>
    </div>
  </header>

  <!-- Main Container -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">

    <!-- KPI Summary Cards (Always Visible) -->
    <section>
      <div class="flex items-center justify-between mb-3">
        <h2 class="text-sm font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center space-x-2">
          <span>Сводные показатели бренда BELGEE</span>
          <span class="inline-block w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
        </h2>
        <span class="text-xs text-slate-400">Сравнение: Август 2026 (факт) vs Сентябрь 2026 (MTD факт)</span>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <!-- Card 1: Leads -->
        <div class="bg-white dark:bg-slate-800/80 rounded-2xl p-4 border border-slate-200 dark:border-slate-700/60 shadow-sm relative overflow-hidden group hover:border-emerald-500/50 transition">
          <div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
            <span>Передано лидов</span>
            <span class="px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300">
              ▲ +17.6%
            </span>
          </div>
          <div class="mt-2 flex items-baseline space-x-2">
            <span class="text-3xl font-black text-slate-900 dark:text-white">40</span>
            <span class="text-xs text-slate-400">в сен / 34 в авг</span>
          </div>
          <div class="mt-2 text-xs text-emerald-600 dark:text-emerald-400 font-medium">
            +6 переданных лидов к августу
          </div>
          <div class="absolute -right-4 -bottom-4 w-16 h-16 bg-emerald-500/5 rounded-full pointer-events-none group-hover:scale-125 transition"></div>
        </div>

        <!-- Card 2: Deals -->
        <div class="bg-white dark:bg-slate-800/80 rounded-2xl p-4 border border-slate-200 dark:border-slate-700/60 shadow-sm relative overflow-hidden group hover:border-emerald-500/50 transition">
          <div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
            <span>Закрыто сделок (Продажи)</span>
            <span class="px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300">
              ▲ +9.8%
            </span>
          </div>
          <div class="mt-2 flex items-baseline space-x-2">
            <span class="text-3xl font-black text-slate-900 dark:text-white">45</span>
            <span class="text-xs text-slate-400">в сен / 41 в авг</span>
          </div>
          <div class="mt-2 text-xs text-emerald-600 dark:text-emerald-400 font-medium">
            +4 продажи (рекордный месяц года)
          </div>
          <div class="absolute -right-4 -bottom-4 w-16 h-16 bg-blue-500/5 rounded-full pointer-events-none group-hover:scale-125 transition"></div>
        </div>

        <!-- Card 3: Turnover -->
        <div class="bg-white dark:bg-slate-800/80 rounded-2xl p-4 border border-slate-200 dark:border-slate-700/60 shadow-sm relative overflow-hidden group hover:border-emerald-500/50 transition">
          <div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
            <span>Товарооборот сети</span>
            <span class="px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300">
              ▲ +6.0%
            </span>
          </div>
          <div class="mt-2 flex items-baseline space-x-1.5">
            <span class="text-2xl font-black text-slate-900 dark:text-white">109.63</span>
            <span class="text-sm font-semibold text-slate-500">млн ₽</span>
          </div>
          <div class="mt-2 text-xs text-emerald-600 dark:text-emerald-400 font-medium">
            +6.21 млн ₽ к августу (103.42 млн)
          </div>
          <div class="absolute -right-4 -bottom-4 w-16 h-16 bg-purple-500/5 rounded-full pointer-events-none group-hover:scale-125 transition"></div>
        </div>

        <!-- Card 4: Revenue / Comm -->
        <div class="bg-white dark:bg-slate-800/80 rounded-2xl p-4 border border-slate-200 dark:border-slate-700/60 shadow-sm relative overflow-hidden group hover:border-emerald-500/50 transition">
          <div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
            <span>Комиссионный доход</span>
            <span class="px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300">
              ▲ +9.6%
            </span>
          </div>
          <div class="mt-2 flex items-baseline space-x-1.5">
            <span class="text-2xl font-black text-slate-900 dark:text-white">1.47</span>
            <span class="text-sm font-semibold text-slate-500">млн ₽</span>
          </div>
          <div class="mt-2 text-xs text-emerald-600 dark:text-emerald-400 font-medium">
            +128.7 тыс ₽ к августу (1.34 млн)
          </div>
          <div class="absolute -right-4 -bottom-4 w-16 h-16 bg-amber-500/5 rounded-full pointer-events-none group-hover:scale-125 transition"></div>
        </div>

        <!-- Card 5: Avg Price -->
        <div class="bg-white dark:bg-slate-800/80 rounded-2xl p-4 border border-slate-200 dark:border-slate-700/60 shadow-sm">
          <div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
            <span>Средний чек авто</span>
            <span class="px-2 py-0.5 rounded-full text-[11px] font-bold bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300">
              ▼ -3.4%
            </span>
          </div>
          <div class="mt-2 flex items-baseline space-x-1">
            <span class="text-2xl font-black text-slate-900 dark:text-white">2.44</span>
            <span class="text-xs text-slate-500">млн ₽ (2 436 131 ₽)</span>
          </div>
          <div class="mt-2 text-xs text-slate-500 dark:text-slate-400">
            Снижение чека из-за роста доли X50 (86.7%)
          </div>
        </div>

        <!-- Card 6: Avg Commission -->
        <div class="bg-white dark:bg-slate-800/80 rounded-2xl p-4 border border-slate-200 dark:border-slate-700/60 shadow-sm">
          <div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
            <span>Средняя комиссия / авто</span>
            <span class="px-2 py-0.5 rounded-full text-[11px] font-bold bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300">
              ≈ 32.7k ₽
            </span>
          </div>
          <div class="mt-2 flex items-baseline space-x-1">
            <span class="text-2xl font-black text-slate-900 dark:text-white">32 693</span>
            <span class="text-xs text-slate-500">₽</span>
          </div>
          <div class="mt-2 text-xs text-slate-500 dark:text-slate-400">
            Стабильно: 32 745 ₽ в авг vs 32 693 ₽ в сен
          </div>
        </div>

        <!-- Card 7: Prepayment -->
        <div class="bg-white dark:bg-slate-800/80 rounded-2xl p-4 border border-slate-200 dark:border-slate-700/60 shadow-sm">
          <div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
            <span>Доля сделок с предоплатой</span>
            <span class="px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300">
              ▲ +2.9 п.п.
            </span>
          </div>
          <div class="mt-2 flex items-baseline space-x-1">
            <span class="text-2xl font-black text-emerald-600 dark:text-emerald-400">95.6%</span>
            <span class="text-xs text-slate-400">(43 из 45 сделок)</span>
          </div>
          <div class="mt-2 text-xs text-slate-500 dark:text-slate-400">
            92.7% в августе (38 из 41)
          </div>
        </div>

        <!-- Card 8: Channel Split -->
        <div class="bg-white dark:bg-slate-800/80 rounded-2xl p-4 border border-slate-200 dark:border-slate-700/60 shadow-sm">
          <div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
            <span>Структура канала B2C</span>
            <span class="px-2 py-0.5 rounded-full text-[11px] font-bold bg-blue-100 text-blue-800 dark:bg-blue-950/80 dark:text-blue-300">
              МП2: 97.8%
            </span>
          </div>
          <div class="mt-2 flex items-baseline space-x-1">
            <span class="text-2xl font-black text-slate-900 dark:text-white">44 МП2</span>
            <span class="text-xs text-slate-400">+ 1 Online</span>
          </div>
          <div class="mt-2 text-xs text-slate-500 dark:text-slate-400">
            Август: 38 МП2 + 3 Передача лида
          </div>
        </div>
      </div>
    </section>

    <!-- TAB 1: OVERVIEW & FUNNEL -->
    <div id="tab-overview" class="tab-content space-y-6">
      
      <!-- Key Insights Alert -->
      <div class="bg-gradient-to-r from-emerald-500/10 via-teal-500/10 to-blue-500/10 border border-emerald-500/20 rounded-2xl p-5">
        <h3 class="font-bold text-sm text-emerald-900 dark:text-emerald-200 flex items-center space-x-2">
          <svg class="w-5 h-5 text-emerald-600 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          <span>Ключевые управленческие выводы по бренду BELGEE</span>
        </h3>
        <div class="mt-3 grid grid-cols-1 md:grid-cols-3 gap-3 text-xs text-slate-700 dark:text-slate-300">
          <div class="p-3 bg-white/60 dark:bg-slate-800/60 rounded-xl border border-slate-200/50 dark:border-slate-700/50">
            <div class="font-bold text-emerald-700 dark:text-emerald-400 mb-1">🚀 Опережающая динамика</div>
            Продажи выросли до <span class="font-bold">45 авто</span> (+9.8%), а переданные лиды до <span class="font-bold">40</span> (+17.6%), опережая темпы августа еще до завершения календарного месяца.
          </div>
          <div class="p-3 bg-white/60 dark:bg-slate-800/60 rounded-xl border border-slate-200/50 dark:border-slate-700/50">
            <div class="font-bold text-blue-700 dark:text-blue-400 mb-1">🚘 Бестселлер BELGEE X50</div>
            Модель <span class="font-bold">X50 / X50+</span> сформировала <span class="font-bold">86.7%</span> всех продаж сентября (39 шт против 28 шт в августе). X70 занял 8.9%, седан S50 — 4.4%.
          </div>
          <div class="p-3 bg-white/60 dark:bg-slate-800/60 rounded-xl border border-slate-200/50 dark:border-slate-700/50">
            <div class="font-bold text-purple-700 dark:text-purple-400 mb-1">🏛️ Топовые партнеры</div>
            Лидеры продаж: <span class="font-bold">РОЛЬФ</span> (18 сделок в сен, 22 в авг) и <span class="font-bold">АвтоГермес</span> (взрывной рост с 7 до 11 сделок, +57%).
          </div>
        </div>
      </div>

      <!-- Funnel Chart and Step-by-Step Breakdown -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Chart: Funnel Comparison -->
        <div class="bg-white dark:bg-slate-800 rounded-2xl p-5 border border-slate-200 dark:border-slate-700/60 shadow-sm">
          <div class="flex items-center justify-between mb-4">
            <div>
              <h3 class="font-bold text-sm text-slate-900 dark:text-white">Сквозная воронка: Август vs Сентябрь</h3>
              <p class="text-xs text-slate-500 dark:text-slate-400">Сравнение ключевых этапов пути клиента</p>
            </div>
            <span class="text-xs px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-700 font-mono text-slate-600 dark:text-slate-300">Log Scale</span>
          </div>
          <div class="h-72">
            <canvas id="chartFunnel"></canvas>
          </div>
        </div>

        <!-- Funnel Metrics Table -->
        <div class="bg-white dark:bg-slate-800 rounded-2xl p-5 border border-slate-200 dark:border-slate-700/60 shadow-sm flex flex-col justify-between">
          <div>
            <h3 class="font-bold text-sm text-slate-900 dark:text-white mb-3">Детализация этапов воронки и конверсий</h3>
            <div class="overflow-x-auto">
              <table class="w-full text-xs text-left">
                <thead class="bg-slate-50 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400 uppercase font-semibold">
                  <tr>
                    <th class="py-2 px-3">Этап воронки</th>
                    <th class="py-2 px-2 text-right">Август</th>
                    <th class="py-2 px-2 text-right">Сентябрь</th>
                    <th class="py-2 px-2 text-right">CR Авг</th>
                    <th class="py-2 px-2 text-right">CR Сен</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100 dark:divide-slate-700/60 font-medium">
                  <tr>
                    <td class="py-2 px-3 flex items-center space-x-1.5">
                      <span class="w-2 h-2 rounded-full bg-blue-400"></span>
                      <span>1. Просмотры витрины</span>
                    </td>
                    <td class="py-2 px-2 text-right font-mono">259 301</td>
                    <td class="py-2 px-2 text-right font-mono">206 620</td>
                    <td class="py-2 px-2 text-right text-slate-400">100%</td>
                    <td class="py-2 px-2 text-right text-slate-400">100%</td>
                  </tr>
                  <tr>
                    <td class="py-2 px-3 flex items-center space-x-1.5">
                      <span class="w-2 h-2 rounded-full bg-blue-500"></span>
                      <span>2. Клики по карточке авто</span>
                    </td>
                    <td class="py-2 px-2 text-right font-mono">1 280</td>
                    <td class="py-2 px-2 text-right font-mono">745</td>
                    <td class="py-2 px-2 text-right font-mono">7.7%*</td>
                    <td class="py-2 px-2 text-right font-mono">7.4%*</td>
                  </tr>
                  <tr>
                    <td class="py-2 px-3 flex items-center space-x-1.5">
                      <span class="w-2 h-2 rounded-full bg-indigo-500"></span>
                      <span>3. Отправка оффера (заявка)</span>
                    </td>
                    <td class="py-2 px-2 text-right font-mono">720</td>
                    <td class="py-2 px-2 text-right font-mono">422</td>
                    <td class="py-2 px-2 text-right font-mono">98.4%</td>
                    <td class="py-2 px-2 text-right font-mono">97.7%</td>
                  </tr>
                  <tr>
                    <td class="py-2 px-3 flex items-center space-x-1.5">
                      <span class="w-2 h-2 rounded-full bg-violet-500"></span>
                      <span>4. Входящие лиды (CRM)</span>
                    </td>
                    <td class="py-2 px-2 text-right font-mono">280</td>
                    <td class="py-2 px-2 text-right font-mono text-emerald-600 font-bold">426</td>
                    <td class="py-2 px-2 text-right font-mono">38.9%</td>
                    <td class="py-2 px-2 text-right font-mono font-bold text-emerald-600">100.9%</td>
                  </tr>
                  <tr>
                    <td class="py-2 px-3 flex items-center space-x-1.5">
                      <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                      <span>5. Квалифицированные лиды</span>
                    </td>
                    <td class="py-2 px-2 text-right font-mono">118</td>
                    <td class="py-2 px-2 text-right font-mono text-emerald-600 font-bold">312</td>
                    <td class="py-2 px-2 text-right font-mono">42.1%</td>
                    <td class="py-2 px-2 text-right font-mono font-bold text-emerald-600">73.2%</td>
                  </tr>
                  <tr>
                    <td class="py-2 px-3 flex items-center space-x-1.5">
                      <span class="w-2 h-2 rounded-full bg-amber-500"></span>
                      <span>6. Расчет калькулятора</span>
                    </td>
                    <td class="py-2 px-2 text-right font-mono">134</td>
                    <td class="py-2 px-2 text-right font-mono">204</td>
                    <td class="py-2 px-2 text-right font-mono">47.9%</td>
                    <td class="py-2 px-2 text-right font-mono">47.9%</td>
                  </tr>
                  <tr class="bg-emerald-50/50 dark:bg-emerald-950/30">
                    <td class="py-2 px-3 flex items-center space-x-1.5 font-bold text-emerald-800 dark:text-emerald-300">
                      <span class="w-2 h-2 rounded-full bg-emerald-600"></span>
                      <span>7. Передано лидов дилерам</span>
                    </td>
                    <td class="py-2 px-2 text-right font-mono font-bold">34</td>
                    <td class="py-2 px-2 text-right font-mono font-bold text-emerald-600">40</td>
                    <td class="py-2 px-2 text-right font-mono">28.8%</td>
                    <td class="py-2 px-2 text-right font-mono">12.8%</td>
                  </tr>
                  <tr>
                    <td class="py-2 px-3 flex items-center space-x-1.5">
                      <span class="w-2 h-2 rounded-full bg-cyan-500"></span>
                      <span>8. Заявки ФДЦ (Кредит)</span>
                    </td>
                    <td class="py-2 px-2 text-right font-mono">28</td>
                    <td class="py-2 px-2 text-right font-mono">41</td>
                    <td class="py-2 px-2 text-right font-mono">10.0%</td>
                    <td class="py-2 px-2 text-right font-mono">9.6%</td>
                  </tr>
                  <tr class="bg-slate-100/70 dark:bg-slate-700/70 font-bold">
                    <td class="py-2.5 px-3 flex items-center space-x-1.5 text-slate-900 dark:text-white">
                      <span class="w-2.5 h-2.5 rounded-full bg-rose-600"></span>
                      <span>9. Закрытые сделки (Факт)</span>
                    </td>
                    <td class="py-2.5 px-2 text-right font-mono text-sm">41</td>
                    <td class="py-2.5 px-2 text-right font-mono text-sm text-emerald-600 dark:text-emerald-400">45</td>
                    <td class="py-2.5 px-2 text-right font-mono text-emerald-700">120.6%**</td>
                    <td class="py-2.5 px-2 text-right font-mono text-emerald-700">112.5%**</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div class="text-[11px] text-slate-400 mt-3 border-t border-slate-100 dark:border-slate-700 pt-2">
            * Конверсия из показов карточек в клики (CTR витрины). ** CR Сделки / Передано превышает 100%, так как 95%+ продаж проходят по прямому витринному каналу МП2.
          </div>
        </div>
      </div>

    </div>

    <!-- TAB 2: DETAILED FUNNEL VIEW -->
    <div id="tab-funnel" class="tab-content hidden space-y-6">
      <div class="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-200 dark:border-slate-700/60 shadow-sm">
        <h3 class="font-bold text-base text-slate-900 dark:text-white mb-2">Архитектура сквозной воронки BELGEE (Витрина PostHog ➔ CRM ➔ ДЦ)</h3>
        <p class="text-xs text-slate-500 dark:text-slate-400 mb-6">Сравнительный анализ этапов привлечения, скоринга и доведения до сделки за Август и Сентябрь 2026 г.</p>

        <!-- Funnel Step Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <!-- Step 1 -->
          <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/50">
            <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Уровень 1: Витрина</div>
            <div class="font-bold text-slate-800 dark:text-slate-100 text-sm">Офферы и Трафик</div>
            <div class="mt-3 space-y-1.5 text-xs">
              <div class="flex justify-between"><span class="text-slate-500">Показы витрины:</span> <span class="font-mono font-bold">206.6k</span> (авг: 259.3k)</div>
              <div class="flex justify-between"><span class="text-slate-500">Показы карточек:</span> <span class="font-mono font-bold">10 072</span> (авг: 16 599)</div>
              <div class="flex justify-between"><span class="text-slate-500">Клики по авто:</span> <span class="font-mono font-bold">745</span> (CTR: 7.4%)</div>
              <div class="flex justify-between"><span class="text-slate-500">Успешные заявки:</span> <span class="font-mono font-bold text-emerald-600">422</span> (CR: 97.7%)</div>
            </div>
          </div>

          <!-- Step 2 -->
          <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/50">
            <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Уровень 2: CRM & Скоринг</div>
            <div class="font-bold text-slate-800 dark:text-slate-100 text-sm">Обработка и Квалификация</div>
            <div class="mt-3 space-y-1.5 text-xs">
              <div class="flex justify-between"><span class="text-slate-500">Входящие лиды:</span> <span class="font-mono font-bold text-emerald-600">426</span> (+52.1% к авг)</div>
              <div class="flex justify-between"><span class="text-slate-500">Квалифицировано:</span> <span class="font-mono font-bold text-emerald-600">312</span> (CR: 73.2%)</div>
              <div class="flex justify-between"><span class="text-slate-500">Калькуляторы:</span> <span class="font-mono font-bold">204</span> (авг: 134)</div>
              <div class="flex justify-between"><span class="text-slate-500">Матчинг оффера:</span> <span class="font-mono font-bold">82</span> (авг: 54)</div>
            </div>
          </div>

          <!-- Step 3 -->
          <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/50">
            <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Уровень 3: Передача & Кредит</div>
            <div class="font-bold text-slate-800 dark:text-slate-100 text-sm">Дилеры и ФДЦ</div>
            <div class="mt-3 space-y-1.5 text-xs">
              <div class="flex justify-between"><span class="text-slate-500">Передано дилерам:</span> <span class="font-mono font-bold text-emerald-600">40 лидов</span> (авг: 34)</div>
              <div class="flex justify-between"><span class="text-slate-500">Заявки ФДЦ (Кредит):</span> <span class="font-mono font-bold">41 заявка</span> (авг: 28)</div>
              <div class="flex justify-between"><span class="text-slate-500">Одобрено ФДЦ:</span> <span class="font-mono font-bold">16 заявок</span> (CR: 39.0%)</div>
              <div class="flex justify-between"><span class="text-slate-500">Лидов с предоплатой:</span> <span class="font-mono font-bold">0</span> (авг: 4)</div>
            </div>
          </div>

          <!-- Step 4 -->
          <div class="p-4 rounded-xl border border-emerald-300 dark:border-emerald-800 bg-emerald-50/40 dark:bg-emerald-950/30">
            <div class="text-xs font-semibold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider mb-1">Уровень 4: Финал</div>
            <div class="font-bold text-emerald-950 dark:text-emerald-200 text-sm">Сделки и Финансы</div>
            <div class="mt-3 space-y-1.5 text-xs">
              <div class="flex justify-between"><span class="text-slate-600 dark:text-slate-400">Закрыто сделок:</span> <span class="font-mono font-bold text-emerald-700 dark:text-emerald-400">45 авто</span> (+9.8%)</div>
              <div class="flex justify-between"><span class="text-slate-600 dark:text-slate-400">Товарооборот:</span> <span class="font-mono font-bold">109.63 млн ₽</span></div>
              <div class="flex justify-between"><span class="text-slate-600 dark:text-slate-400">Комиссия СберАвто:</span> <span class="font-mono font-bold">1.47 млн ₽</span></div>
              <div class="flex justify-between"><span class="text-slate-600 dark:text-slate-400">Сделок с предоплатой:</span> <span class="font-mono font-bold text-emerald-600">43 (95.6%)</span></div>
            </div>
          </div>
        </div>

        <!-- Sources Breakdown -->
        <div class="mt-6 pt-6 border-t border-slate-200 dark:border-slate-700">
          <h4 class="font-bold text-xs uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-3">Источники входящего трафика BELGEE (CRM)</h4>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div class="p-3 bg-slate-100 dark:bg-slate-700/50 rounded-xl">
              <div class="text-slate-400">ОМ + Баннеры + Лендинги</div>
              <div class="text-lg font-black text-slate-900 dark:text-white mt-1">342</div>
              <div class="text-[11px] text-slate-500">80.3% от объема</div>
            </div>
            <div class="p-3 bg-slate-100 dark:bg-slate-700/50 rounded-xl">
              <div class="text-slate-400">Без источника / Прямой</div>
              <div class="text-lg font-black text-slate-900 dark:text-white mt-1">79</div>
              <div class="text-[11px] text-slate-500">18.5% от объема</div>
            </div>
            <div class="p-3 bg-slate-100 dark:bg-slate-700/50 rounded-xl">
              <div class="text-slate-400">Органика СберАвто</div>
              <div class="text-lg font-black text-slate-900 dark:text-white mt-1">4</div>
              <div class="text-[11px] text-slate-500">0.9% от объема</div>
            </div>
            <div class="p-3 bg-slate-100 dark:bg-slate-700/50 rounded-xl">
              <div class="text-slate-400">Органика СБОЛ</div>
              <div class="text-lg font-black text-slate-900 dark:text-white mt-1">2</div>
              <div class="text-[11px] text-slate-500">0.5% от объема</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 3: MODELS BREAKDOWN -->
    <div id="tab-models" class="tab-content hidden space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Models Donut Chart -->
        <div class="bg-white dark:bg-slate-800 rounded-2xl p-5 border border-slate-200 dark:border-slate-700/60 shadow-sm flex flex-col justify-between">
          <div>
            <h3 class="font-bold text-sm text-slate-900 dark:text-white">Структура продаж по моделям</h3>
            <p class="text-xs text-slate-500 dark:text-slate-400">Сентябрь 2026 MTD (Всего 45 авто)</p>
            <div class="h-60 mt-4">
              <canvas id="chartModelsDonut"></canvas>
            </div>
          </div>
          <div class="mt-4 pt-3 border-t border-slate-100 dark:border-slate-700 text-xs text-slate-500 flex justify-between">
            <span>Доминирование X50: <strong class="text-slate-900 dark:text-white">86.7%</strong></span>
            <span>Седан S50: <strong class="text-slate-900 dark:text-white">4.4%</strong></span>
          </div>
        </div>

        <!-- Models Comparison Table (Aug vs Sep) -->
        <div class="lg:col-span-2 bg-white dark:bg-slate-800 rounded-2xl p-5 border border-slate-200 dark:border-slate-700/60 shadow-sm">
          <h3 class="font-bold text-sm text-slate-900 dark:text-white mb-1">Сравнительная аналитика моделей BELGEE</h3>
          <p class="text-xs text-slate-500 dark:text-slate-400 mb-4">Объемы продаж, товарооборот, средний чек и комиссия (Август vs Сентябрь)</p>

          <div class="overflow-x-auto">
            <table class="w-full text-xs text-left">
              <thead class="bg-slate-50 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400 uppercase font-semibold">
                <tr>
                  <th class="py-2.5 px-3">Модель</th>
                  <th class="py-2.5 px-2 text-right">Сделки Авг</th>
                  <th class="py-2.5 px-2 text-right">Сделки Сен</th>
                  <th class="py-2.5 px-2 text-right">Доля Сен</th>
                  <th class="py-2.5 px-2 text-right">Ср. чек Сен</th>
                  <th class="py-2.5 px-2 text-right">Оборот Сен</th>
                  <th class="py-2.5 px-2 text-right">Комиссия Сен</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 dark:divide-slate-700/60 font-medium">
                <!-- X50 -->
                <tr class="hover:bg-slate-50/50 dark:hover:bg-slate-700/30">
                  <td class="py-3 px-3">
                    <div class="font-bold text-slate-900 dark:text-white flex items-center space-x-1.5">
                      <span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                      <span>BELGEE X50 / X50+</span>
                    </div>
                    <div class="text-[10px] text-slate-400">Компактный городской кроссовер</div>
                  </td>
                  <td class="py-3 px-2 text-right font-mono">28 шт (68.3%)</td>
                  <td class="py-3 px-2 text-right font-mono font-bold text-emerald-600 dark:text-emerald-400">39 шт</td>
                  <td class="py-3 px-2 text-right font-mono font-bold">86.7%</td>
                  <td class="py-3 px-2 text-right font-mono">2 396 612 ₽</td>
                  <td class="py-3 px-2 text-right font-mono font-bold">93.47 млн ₽</td>
                  <td class="py-3 px-2 text-right font-mono text-emerald-600">1 280 871 ₽</td>
                </tr>

                <!-- X70 -->
                <tr class="hover:bg-slate-50/50 dark:hover:bg-slate-700/30">
                  <td class="py-3 px-3">
                    <div class="font-bold text-slate-900 dark:text-white flex items-center space-x-1.5">
                      <span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span>
                      <span>BELGEE X70 / X70 FL</span>
                    </div>
                    <div class="text-[10px] text-slate-400">Семейный среднеразмерный SUV</div>
                  </td>
                  <td class="py-3 px-2 text-right font-mono">11 шт (26.8%)</td>
                  <td class="py-3 px-2 text-right font-mono font-bold text-blue-600 dark:text-blue-400">4 шт</td>
                  <td class="py-3 px-2 text-right font-mono font-bold">8.9%</td>
                  <td class="py-3 px-2 text-right font-mono">2 821 500 ₽</td>
                  <td class="py-3 px-2 text-right font-mono font-bold">11.29 млн ₽</td>
                  <td class="py-3 px-2 text-right font-mono text-blue-600">137 000 ₽</td>
                </tr>

                <!-- S50 -->
                <tr class="hover:bg-slate-50/50 dark:hover:bg-slate-700/30">
                  <td class="py-3 px-3">
                    <div class="font-bold text-slate-900 dark:text-white flex items-center space-x-1.5">
                      <span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
                      <span>BELGEE S50 / S50+</span>
                    </div>
                    <div class="text-[10px] text-slate-400">Новый седан бренда</div>
                  </td>
                  <td class="py-3 px-2 text-right font-mono">2 шт (4.9%)</td>
                  <td class="py-3 px-2 text-right font-mono font-bold text-amber-600 dark:text-amber-400">2 шт</td>
                  <td class="py-3 px-2 text-right font-mono font-bold">4.4%</td>
                  <td class="py-3 px-2 text-right font-mono">2 435 000 ₽</td>
                  <td class="py-3 px-2 text-right font-mono font-bold">4.87 млн ₽</td>
                  <td class="py-3 px-2 text-right font-mono text-amber-600">53 308 ₽</td>
                </tr>

                <!-- Total -->
                <tr class="bg-slate-50 dark:bg-slate-700/50 font-bold text-slate-900 dark:text-white">
                  <td class="py-3 px-3">ИТОГО BELGEE</td>
                  <td class="py-3 px-2 text-right font-mono">41 шт</td>
                  <td class="py-3 px-2 text-right font-mono text-emerald-600">45 шт</td>
                  <td class="py-3 px-2 text-right font-mono">100.0%</td>
                  <td class="py-3 px-2 text-right font-mono">2 436 131 ₽</td>
                  <td class="py-3 px-2 text-right font-mono text-emerald-600">109.63 млн ₽</td>
                  <td class="py-3 px-2 text-right font-mono text-emerald-600">1.47 млн ₽</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 4: DEALERS & KAM MATRIX -->
    <div id="tab-dealers" class="tab-content hidden space-y-6">
      
      <!-- KAM Distribution Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <!-- Kuznetsov -->
        <div class="bg-white dark:bg-slate-800 rounded-2xl p-4 border border-slate-200 dark:border-slate-700/60 shadow-sm">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-slate-500 uppercase">Ведущий КАМ</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">75.6% продаж</span>
          </div>
          <div class="mt-2 text-base font-black text-slate-900 dark:text-white">Андрей Кузнецов</div>
          <div class="mt-2 text-xs space-y-1">
            <div class="flex justify-between"><span class="text-slate-400">Сделки Сен:</span> <span class="font-bold text-emerald-600">34 шт</span> (авг: 32)</div>
            <div class="flex justify-between"><span class="text-slate-400">Лиды Сен:</span> <span class="font-bold">3 шт</span> (авг: 8)</div>
            <div class="flex justify-between"><span class="text-slate-400">Комиссия Сен:</span> <span class="font-mono font-bold">1.10 млн ₽</span></div>
            <div class="text-[11px] text-slate-400 mt-2 truncate">Партнеры: РОЛЬФ, Автомир, Fresh Auto</div>
          </div>
        </div>

        <!-- Chikharev -->
        <div class="bg-white dark:bg-slate-800 rounded-2xl p-4 border border-slate-200 dark:border-slate-700/60 shadow-sm">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-slate-500 uppercase">Ведущий КАМ</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300">15.6% продаж</span>
          </div>
          <div class="mt-2 text-base font-black text-slate-900 dark:text-white">Алексей Чихарев</div>
          <div class="mt-2 text-xs space-y-1">
            <div class="flex justify-between"><span class="text-slate-400">Сделки Сен:</span> <span class="font-bold text-blue-600">7 шт</span> (авг: 7)</div>
            <div class="flex justify-between"><span class="text-slate-400">Лиды Сен:</span> <span class="font-bold text-blue-600">17 шт</span> (авг: 17)</div>
            <div class="flex justify-between"><span class="text-slate-400">Комиссия Сен:</span> <span class="font-mono font-bold">231.8 тыс ₽</span></div>
            <div class="text-[11px] text-slate-400 mt-2 truncate">Партнеры: АвтоГермес, Кунцево, У Сервис</div>
          </div>
        </div>

        <!-- Soldatova -->
        <div class="bg-white dark:bg-slate-800 rounded-2xl p-4 border border-slate-200 dark:border-slate-700/60 shadow-sm">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-slate-500 uppercase">КАМ Юг/Черноземье</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-800 dark:bg-purple-950 dark:text-purple-300">8.9% продаж</span>
          </div>
          <div class="mt-2 text-base font-black text-slate-900 dark:text-white">Валерия Солдатова</div>
          <div class="mt-2 text-xs space-y-1">
            <div class="flex justify-between"><span class="text-slate-400">Сделки Сен:</span> <span class="font-bold text-purple-600">4 шт</span> (авг: 2)</div>
            <div class="flex justify-between"><span class="text-slate-400">Лиды Сен:</span> <span class="font-bold text-purple-600">6 шт</span> (авг: 1)</div>
            <div class="flex justify-between"><span class="text-slate-400">Комиссия Сен:</span> <span class="font-mono font-bold">133.5 тыс ₽</span></div>
            <div class="text-[11px] text-slate-400 mt-2 truncate">Партнеры: БАКРА (Краснодар), Темп Авто</div>
          </div>
        </div>

        <!-- Darienko & Dobrolyubova -->
        <div class="bg-white dark:bg-slate-800 rounded-2xl p-4 border border-slate-200 dark:border-slate-700/60 shadow-sm">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-slate-500 uppercase">СЗФО & Урал</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300">Лидогенерация</span>
          </div>
          <div class="mt-2 text-base font-black text-slate-900 dark:text-white">Дариенко / Добролюбова</div>
          <div class="mt-2 text-xs space-y-1">
            <div class="flex justify-between"><span class="text-slate-400">Дариенко (Лиды):</span> <span class="font-bold">8 шт</span> (Максимум, СЗФО)</div>
            <div class="flex justify-between"><span class="text-slate-400">Добролюбова (Лиды):</span> <span class="font-bold">6 шт</span> (Эксперт Авто, Урал)</div>
            <div class="flex justify-between"><span class="text-slate-400">Сделки Сен:</span> <span class="font-mono font-bold">0 шт</span> (воронка в работе)</div>
            <div class="text-[11px] text-slate-400 mt-2 truncate">Потенциал сделок в октябре</div>
          </div>
        </div>
      </div>

      <!-- Top Dealers Bar Chart -->
      <div class="bg-white dark:bg-slate-800 rounded-2xl p-5 border border-slate-200 dark:border-slate-700/60 shadow-sm">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h3 class="font-bold text-sm text-slate-900 dark:text-white">Топ дилерских центров по объему продаж BELGEE</h3>
            <p class="text-xs text-slate-500 dark:text-slate-400">Сравнение продаж: Август vs Сентябрь 2026</p>
          </div>
        </div>
        <div class="h-64">
          <canvas id="chartDealersBar"></canvas>
        </div>
      </div>

      <!-- Comprehensive Partners Matrix Table -->
      <div class="bg-white dark:bg-slate-800 rounded-2xl p-5 border border-slate-200 dark:border-slate-700/60 shadow-sm">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <div>
            <h3 class="font-bold text-sm text-slate-900 dark:text-white">Сводный реестр партнеров BELGEE (Август / Сентябрь 2026)</h3>
            <p class="text-xs text-slate-500 dark:text-slate-400">Все дилерские центры с активностью по переданным лидам или сделкам</p>
          </div>
          <div class="flex items-center space-x-2">
            <input type="text" id="partnerSearch" oninput="filterPartnerTable()" placeholder="Поиск по партнеру или КАМу..." class="px-3 py-1.5 text-xs rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500">
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-xs text-left" id="partnersTable">
            <thead class="bg-slate-50 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400 uppercase font-semibold">
              <tr>
                <th class="py-2.5 px-3 cursor-pointer" onclick="sortPartnerTable(0)">Дилер / Партнер ⬍</th>
                <th class="py-2.5 px-2 cursor-pointer" onclick="sortPartnerTable(1)">КАМ ⬍</th>
                <th class="py-2.5 px-2 text-right cursor-pointer" onclick="sortPartnerTable(2)">Лиды Авг ⬍</th>
                <th class="py-2.5 px-2 text-right cursor-pointer" onclick="sortPartnerTable(3)">Лиды Сен ⬍</th>
                <th class="py-2.5 px-2 text-right cursor-pointer" onclick="sortPartnerTable(4)">Сделки Авг ⬍</th>
                <th class="py-2.5 px-2 text-right cursor-pointer" onclick="sortPartnerTable(5)">Сделки Сен ⬍</th>
                <th class="py-2.5 px-2 text-right cursor-pointer" onclick="sortPartnerTable(6)">Динамика ⬍</th>
                <th class="py-2.5 px-2 text-right cursor-pointer" onclick="sortPartnerTable(7)">Оборот Сен ⬍</th>
                <th class="py-2.5 px-2 text-right cursor-pointer" onclick="sortPartnerTable(8)">Комиссия Сен ⬍</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-slate-700/60 font-medium" id="partnersTableBody">
              <!-- Rendered via JavaScript -->
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- TAB 5: TRANSACTION REGISTRIES (Searchable/Sortable) -->
    <div id="tab-registries" class="tab-content hidden space-y-6">
      
      <!-- Controls -->
      <div class="bg-white dark:bg-slate-800 rounded-2xl p-5 border border-slate-200 dark:border-slate-700/60 shadow-sm space-y-4">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 class="font-bold text-sm text-slate-900 dark:text-white">Реестр транзакций BELGEE</h3>
            <p class="text-xs text-slate-500 dark:text-slate-400">Полный список всех 86 сделок и 74 переданных лидов за август и сентябрь</p>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <!-- Record Type Toggle -->
            <div class="inline-flex rounded-lg border border-slate-300 dark:border-slate-700 p-0.5 bg-slate-100 dark:bg-slate-900 text-xs">
              <button onclick="setRegistryType('deals')" id="regTypeDeals" class="px-3 py-1 font-semibold rounded-md bg-white dark:bg-slate-800 shadow-sm text-slate-900 dark:text-white">Сделки (86)</button>
              <button onclick="setRegistryType('leads')" id="regTypeLeads" class="px-3 py-1 font-medium rounded-md text-slate-600 dark:text-slate-400">Лиды (74)</button>
            </div>
            <!-- Month Filter -->
            <select id="regMonthFilter" onchange="filterRegistryTable()" class="px-3 py-1.5 text-xs rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white">
              <option value="all">Все месяцы (Авг + Сен)</option>
              <option value="2026-09" selected>Сентябрь 2026</option>
              <option value="2026-08">Август 2026</option>
            </select>
            <!-- Search -->
            <input type="text" id="regSearch" oninput="filterRegistryTable()" placeholder="Поиск по ID, модели, дилеру, VIN..." class="px-3 py-1.5 text-xs rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white w-56 focus:outline-none focus:ring-2 focus:ring-emerald-500">
          </div>
        </div>

        <!-- Dynamic Registry Table -->
        <div class="overflow-x-auto max-h-[600px] overflow-y-auto border border-slate-200 dark:border-slate-700 rounded-xl">
          <table class="w-full text-xs text-left" id="registryTable">
            <thead class="bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-200 sticky top-0 uppercase font-semibold">
              <tr id="registryTableHead">
                <!-- Injected via JS -->
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-slate-700/60 font-medium" id="registryTableBody">
              <!-- Injected via JS -->
            </tbody>
          </table>
        </div>
        <div class="text-xs text-slate-400 flex justify-between items-center" id="registrySummary">
          <!-- Count summary -->
        </div>
      </div>

    </div>

    <!-- TAB 6: PRICING & DISCOUNTS -->
    <div id="tab-pricing" class="tab-content hidden space-y-6">
      <div class="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-200 dark:border-slate-700/60 shadow-sm">
        <h3 class="font-bold text-base text-slate-900 dark:text-white mb-2">Анализ цен, скидок и коммерческих условий BELGEE</h3>
        <p class="text-xs text-slate-500 dark:text-slate-400 mb-6">Данные модуля discount_analytics: структура средней скидки и финальной стоимости</p>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/50">
            <div class="text-xs text-slate-500">Средняя РРЦ бренда</div>
            <div class="text-2xl font-black text-slate-900 dark:text-white mt-1">2 739 455 ₽</div>
            <div class="text-xs text-slate-400 mt-2">Базовая рекомендованная розничная цена</div>
          </div>
          <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/50">
            <div class="text-xs text-slate-500">Средняя финальная цена сделки</div>
            <div class="text-2xl font-black text-emerald-600 dark:text-emerald-400 mt-1">2 513 631 ₽</div>
            <div class="text-xs text-slate-400 mt-2">Фактическая цена покупки клиентом</div>
          </div>
          <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/50">
            <div class="text-xs text-slate-500">Средний размер суммарной скидки</div>
            <div class="text-2xl font-black text-rose-600 dark:text-rose-400 mt-1">225 824 ₽</div>
            <div class="text-xs text-slate-400 mt-2">8.24% средняя глубина дисконта</div>
          </div>
          <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/50">
            <div class="text-xs text-slate-500">Средняя комиссия СберАвто</div>
            <div class="text-2xl font-black text-blue-600 dark:text-blue-400 mt-1">32 693 ₽</div>
            <div class="text-xs text-slate-400 mt-2">1.34% от финального чека автомобиля</div>
          </div>
        </div>

        <!-- Discount Breakdown -->
        <div class="mt-6 pt-6 border-t border-slate-200 dark:border-slate-700">
          <h4 class="font-bold text-xs uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-3">Структура формирования скидки на автомобиль BELGEE</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="p-4 rounded-xl bg-slate-50 dark:bg-slate-700/40 border border-slate-200 dark:border-slate-600 flex items-center justify-between">
              <div>
                <div class="text-xs font-semibold text-slate-500">Скидка дилерского центра (ДЦ)</div>
                <div class="text-xl font-black text-slate-900 dark:text-white mt-1">147 662 ₽</div>
                <div class="text-xs text-slate-400 mt-1">Прямая скидка салона при покупке</div>
              </div>
              <div class="text-2xl font-extrabold text-blue-600">65.4%</div>
            </div>
            <div class="p-4 rounded-xl bg-slate-50 dark:bg-slate-700/40 border border-slate-200 dark:border-slate-600 flex items-center justify-between">
              <div>
                <div class="text-xs font-semibold text-slate-500">Скидка сервиса (СберАвто)</div>
                <div class="text-xl font-black text-slate-900 dark:text-white mt-1">78 162 ₽</div>
                <div class="text-xs text-slate-400 mt-1">Субсидия платформы и программы лояльности</div>
              </div>
              <div class="text-2xl font-extrabold text-emerald-600">34.6%</div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </main>

  <!-- Footer -->
  <footer class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 text-xs text-slate-400 border-t border-slate-200 dark:border-slate-800 flex flex-col sm:flex-row justify-between items-center gap-2">
    <div>
      Сгенерировано автоматически из аналитического ядра СберАвто • Бренд: <strong class="text-slate-600 dark:text-slate-300">BELGEE</strong>
    </div>
    <div class="font-mono">
      Данные: Август 2026 (факт) | Сентябрь 2026 (MTD факт 01–28.09)
    </div>
  </footer>

  <!-- Embedded Analytics Dataset -->
  <script>
    window.BELGEE_DATA = {embedded_json};
  </script>

  <!-- Application Logic & Interactive Charts -->
  <script>
    // Theme toggle
    const themeToggleBtn = document.getElementById('themeToggle');
    if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {{
      document.documentElement.classList.add('dark');
    }} else {{
      document.documentElement.classList.remove('dark');
    }}
    themeToggleBtn.addEventListener('click', () => {{
      document.documentElement.classList.toggle('dark');
      localStorage.theme = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
    }});

    // Tab Navigation
    function switchTab(tabId) {{
      document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
      document.querySelectorAll('.tab-btn').forEach(el => {{
        el.className = 'tab-btn px-3 py-1.5 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800';
      }});
      
      const target = document.getElementById('tab-' + tabId);
      if (target) target.classList.remove('hidden');
      const activeBtn = document.getElementById('tab-btn-' + tabId);
      if (activeBtn) {{
        activeBtn.className = 'tab-btn px-3 py-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 font-semibold border border-emerald-200 dark:border-emerald-800';
      }}
    }}

    // State for registries
    let currentRegType = 'deals'; // 'deals' or 'leads'
    let partnerSortCol = 5; // default Sep Deals
    let partnerSortAsc = false;

    // Render Partners Table
    function renderPartnersTable(dataList) {{
      const tbody = document.getElementById('partnersTableBody');
      tbody.innerHTML = '';
      if (!dataList || dataList.length === 0) {{
        tbody.innerHTML = '<tr><td colspan="9" class="py-4 text-center text-slate-400">Нет данных</td></tr>';
        return;
      }}
      dataList.forEach(p => {{
        const delta = p.deals_delta;
        const deltaClass = delta > 0 ? 'text-emerald-600 font-bold' : (delta < 0 ? 'text-rose-500 font-bold' : 'text-slate-400');
        const deltaSign = delta > 0 ? `+${{delta}}` : `${{delta}}`;

        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-50/80 dark:hover:bg-slate-700/40 transition-colors';
        tr.innerHTML = `
          <td class="py-2.5 px-3 font-bold text-slate-900 dark:text-white">
            ${{p.partner}}
            ${{p.raw_names ? `<div class="text-[10px] text-slate-400 truncate max-w-xs font-normal" title="${{p.raw_names}}">${{p.raw_names}}</div>` : ''}}
          </td>
          <td class="py-2.5 px-2 text-slate-600 dark:text-slate-300">${{p.kam}}</td>
          <td class="py-2.5 px-2 text-right font-mono">${{p.leads_aug}}</td>
          <td class="py-2.5 px-2 text-right font-mono font-bold text-blue-600 dark:text-blue-400">${{p.leads_sep}}</td>
          <td class="py-2.5 px-2 text-right font-mono">${{p.deals_aug}}</td>
          <td class="py-2.5 px-2 text-right font-mono font-bold text-emerald-600 dark:text-emerald-400">${{p.deals_sep}}</td>
          <td class="py-2.5 px-2 text-right font-mono text-xs ${{deltaClass}}">${{deltaSign}}</td>
          <td class="py-2.5 px-2 text-right font-mono font-bold">${{p.turnover_sep > 0 ? (p.turnover_sep / 1e6).toFixed(2) + ' млн ₽' : '-'}}</td>
          <td class="py-2.5 px-2 text-right font-mono text-emerald-600 dark:text-emerald-400 font-bold">${{p.revenue_sep > 0 ? Math.round(p.revenue_sep).toLocaleString('ru-RU') + ' ₽' : '-'}}</td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    function filterPartnerTable() {{
      const q = document.getElementById('partnerSearch').value.toLowerCase().trim();
      const list = window.BELGEE_DATA.partner_matrix.filter(p => {{
        return p.partner.toLowerCase().includes(q) || p.kam.toLowerCase().includes(q) || (p.raw_names && p.raw_names.toLowerCase().includes(q));
      }});
      renderPartnersTable(list);
    }}

    function sortPartnerTable(colIndex) {{
      if (partnerSortCol === colIndex) {{
        partnerSortAsc = !partnerSortAsc;
      }} else {{
        partnerSortCol = colIndex;
        partnerSortAsc = false;
      }}
      const keys = ['partner', 'kam', 'leads_aug', 'leads_sep', 'deals_aug', 'deals_sep', 'deals_delta', 'turnover_sep', 'revenue_sep'];
      const key = keys[colIndex];
      window.BELGEE_DATA.partner_matrix.sort((a, b) => {{
        let vA = a[key];
        let vB = b[key];
        if (typeof vA === 'string') {{
          return partnerSortAsc ? vA.localeCompare(vB) : vB.localeCompare(vA);
        }}
        return partnerSortAsc ? (vA - vB) : (vB - vA);
      }});
      filterPartnerTable();
    }}

    // Registry Table Handling
    function setRegistryType(type) {{
      currentRegType = type;
      const btnD = document.getElementById('regTypeDeals');
      const btnL = document.getElementById('regTypeLeads');
      if (type === 'deals') {{
        btnD.className = 'px-3 py-1 font-semibold rounded-md bg-white dark:bg-slate-800 shadow-sm text-slate-900 dark:text-white';
        btnL.className = 'px-3 py-1 font-medium rounded-md text-slate-600 dark:text-slate-400';
      }} else {{
        btnL.className = 'px-3 py-1 font-semibold rounded-md bg-white dark:bg-slate-800 shadow-sm text-slate-900 dark:text-white';
        btnD.className = 'px-3 py-1 font-medium rounded-md text-slate-600 dark:text-slate-400';
      }}
      renderRegistryHeaders();
      filterRegistryTable();
    }}

    function renderRegistryHeaders() {{
      const head = document.getElementById('registryTableHead');
      if (currentRegType === 'deals') {{
        head.innerHTML = `
          <th class="py-2.5 px-3">Дата</th>
          <th class="py-2.5 px-2">ID сделки</th>
          <th class="py-2.5 px-2">Модель</th>
          <th class="py-2.5 px-2">Дилер / Партнер</th>
          <th class="py-2.5 px-2">КАМ</th>
          <th class="py-2.5 px-2">Канал B2C</th>
          <th class="py-2.5 px-2 text-right">Сумма авто</th>
          <th class="py-2.5 px-2 text-right">Комиссия</th>
          <th class="py-2.5 px-2 text-center">Предоплата</th>
          <th class="py-2.5 px-2">VIN / Менеджер</th>
        `;
      }} else {{
        head.innerHTML = `
          <th class="py-2.5 px-3">Дата</th>
          <th class="py-2.5 px-2">ID лида</th>
          <th class="py-2.5 px-2">Client ID</th>
          <th class="py-2.5 px-2">Дилер / Партнер</th>
          <th class="py-2.5 px-2">КАМ</th>
          <th class="py-2.5 px-2">Бренд</th>
          <th class="py-2.5 px-2 text-center">Предоплата</th>
          <th class="py-2.5 px-2">Исходный партнер</th>
        `;
      }}
    }}

    function filterRegistryTable() {{
      const monthFilter = document.getElementById('regMonthFilter').value;
      const q = document.getElementById('regSearch').value.toLowerCase().trim();
      const tbody = document.getElementById('registryTableBody');
      tbody.innerHTML = '';

      let items = [];
      if (currentRegType === 'deals') {{
        if (monthFilter === 'all') items = [...window.BELGEE_DATA.deals_sep, ...window.BELGEE_DATA.deals_aug];
        else if (monthFilter === '2026-09') items = [...window.BELGEE_DATA.deals_sep];
        else items = [...window.BELGEE_DATA.deals_aug];
      }} else {{
        if (monthFilter === 'all') items = [...window.BELGEE_DATA.leads_sep, ...window.BELGEE_DATA.leads_aug];
        else if (monthFilter === '2026-09') items = [...window.BELGEE_DATA.leads_sep];
        else items = [...window.BELGEE_DATA.leads_aug];
      }}

      // Apply Search
      const filtered = items.filter(r => {{
        const str = Object.values(r).join(' ').toLowerCase();
        return str.includes(q);
      }});

      document.getElementById('registrySummary').innerHTML = `
        <span>Показано записей: <strong>${{filtered.length}}</strong> из ${{items.length}}</span>
        <span>Фильтр: ${{monthFilter === 'all' ? 'Все месяцы' : (monthFilter === '2026-09' ? 'Сентябрь 2026' : 'Август 2026')}}</span>
      `;

      if (filtered.length === 0) {{
        tbody.innerHTML = '<tr><td colspan="10" class="py-6 text-center text-slate-400">Ничего не найдено по заданным критериям</td></tr>';
        return;
      }}

      filtered.forEach(r => {{
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-50/80 dark:hover:bg-slate-700/40 transition-colors';

        if (currentRegType === 'deals') {{
          const prepayBadge = r.HasPrepay ? '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">ДА</span>' : '<span class="px-2 py-0.5 rounded-full text-[10px] bg-slate-100 text-slate-500">НЕТ</span>';
          tr.innerHTML = `
            <td class="py-2.5 px-3 font-mono text-slate-600 dark:text-slate-300">${{r.DateFormatted || '-'}}</td>
            <td class="py-2.5 px-2 font-mono font-bold text-slate-900 dark:text-white">#${{r.DealId || '-'}}</td>
            <td class="py-2.5 px-2 font-bold text-emerald-600 dark:text-emerald-400">${{r.ModelClean || r.Model}}</td>
            <td class="py-2.5 px-2 font-semibold text-slate-800 dark:text-slate-200">${{r.Partner || '-'}}</td>
            <td class="py-2.5 px-2 text-slate-600 dark:text-slate-300">${{r.KAM || '-'}}</td>
            <td class="py-2.5 px-2"><span class="px-2 py-0.5 rounded text-[10px] font-mono bg-blue-100 dark:bg-blue-950 text-blue-800 dark:text-blue-300">${{r.B2C || '-'}}</span></td>
            <td class="py-2.5 px-2 text-right font-mono font-bold">${{r.Price ? r.Price.toLocaleString('ru-RU') + ' ₽' : '-'}}</td>
            <td class="py-2.5 px-2 text-right font-mono font-bold text-emerald-600">${{r.Comm ? Math.round(r.Comm).toLocaleString('ru-RU') + ' ₽' : '-'}}</td>
            <td class="py-2.5 px-2 text-center">${{prepayBadge}}</td>
            <td class="py-2.5 px-2 text-slate-500 font-mono text-[11px] truncate max-w-[140px]" title="${{r.VIN}} / ${{r.Manager}}">${{r.VIN ? r.VIN.slice(-6) : ''}} / ${{r.Manager || '-'}}</td>
          `;
        }} else {{
          const prepayBadge = r.HasPrepay ? '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">ДА</span>' : '<span class="px-2 py-0.5 rounded-full text-[10px] bg-slate-100 text-slate-500">НЕТ</span>';
          tr.innerHTML = `
            <td class="py-2.5 px-3 font-mono text-slate-600 dark:text-slate-300">${{r.DateFormatted || '-'}}</td>
            <td class="py-2.5 px-2 font-mono font-bold text-blue-600">#${{r.LeadId || '-'}}</td>
            <td class="py-2.5 px-2 font-mono text-slate-600 dark:text-slate-300">${{r.ClientId || '-'}}</td>
            <td class="py-2.5 px-2 font-semibold text-slate-800 dark:text-slate-200">${{r.Partner || '-'}}</td>
            <td class="py-2.5 px-2 text-slate-600 dark:text-slate-300">${{r.KAM || '-'}}</td>
            <td class="py-2.5 px-2 text-slate-700 dark:text-slate-200">${{r.Brand || 'BELGEE'}}</td>
            <td class="py-2.5 px-2 text-center">${{prepayBadge}}</td>
            <td class="py-2.5 px-2 text-slate-400 text-[11px] truncate max-w-[180px]" title="${{r.RawPartner}}">${{r.RawPartner || '-'}}</td>
          `;
        }}
        tbody.appendChild(tr);
      }});
    }}

    // Export CSV
    function exportAllToCSV() {{
      const items = currentRegType === 'deals' 
        ? [...window.BELGEE_DATA.deals_sep, ...window.BELGEE_DATA.deals_aug]
        : [...window.BELGEE_DATA.leads_sep, ...window.BELGEE_DATA.leads_aug];
      
      if (!items || items.length === 0) return alert('Нет данных для экспорта');

      const headers = Object.keys(items[0]);
      let csv = headers.join(';') + '\\n';
      items.forEach(row => {{
        csv += headers.map(h => `"${{String(row[h] || '').replace(/"/g, '""')}}"`).join(';') + '\\n';
      }});

      const blob = new Blob(["\\ufeff" + csv], {{ type: 'text/csv;charset=utf-8;' }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `belgee_${{currentRegType}}_${{new Date().toISOString().slice(0,10)}}.csv`;
      a.click();
    }}

    // Initialize Charts & Tables
    document.addEventListener('DOMContentLoaded', () => {{
      renderPartnersTable(window.BELGEE_DATA.partner_matrix);
      renderRegistryHeaders();
      filterRegistryTable();

      // 1. Funnel Chart
      const ctxFunnel = document.getElementById('chartFunnel');
      if (ctxFunnel) {{
        new Chart(ctxFunnel, {{
          type: 'bar',
          data: {{
            labels: ['Карточки', 'Клики', 'Заявки', 'Вход Лиды', 'Квалиф', 'Калькулятор', 'Передано', 'Сделки'],
            datasets: [
              {{
                label: 'Август 2026',
                data: [16599, 1280, 720, 280, 118, 134, 34, 41],
                backgroundColor: 'rgba(148, 163, 184, 0.7)',
                borderColor: '#94a3b8',
                borderWidth: 1,
                borderRadius: 4
              }},
              {{
                label: 'Сентябрь 2026',
                data: [10072, 745, 422, 426, 312, 204, 40, 45],
                backgroundColor: 'rgba(16, 185, 129, 0.85)',
                borderColor: '#10b981',
                borderWidth: 1,
                borderRadius: 4
              }}
            ]
          }},
          options: {{
            responsive: true,
            maintainAspectRatio: false,
            scales: {{
              y: {{
                type: 'logarithmic',
                grid: {{ color: 'rgba(148, 163, 184, 0.1)' }}
              }},
              x: {{
                grid: {{ display: false }}
              }}
            }},
            plugins: {{
              legend: {{ position: 'top' }}
            }}
          }}
        }});
      }}

      // 2. Models Donut Chart
      const ctxModels = document.getElementById('chartModelsDonut');
      if (ctxModels) {{
        new Chart(ctxModels, {{
          type: 'doughnut',
          data: {{
            labels: ['BELGEE X50 / X50+ (39 шт)', 'BELGEE X70 (4 шт)', 'BELGEE S50 седан (2 шт)'],
            datasets: [{{
              data: [39, 4, 2],
              backgroundColor: ['#10b981', '#3b82f6', '#f59e0b'],
              borderWidth: 2,
              borderColor: '#ffffff'
            }}]
          }},
          options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
              legend: {{ position: 'bottom', labels: {{ boxWidth: 12, font: {{ size: 11 }} }} }}
            }}
          }}
        }});
      }}

      // 3. Top Dealers Bar Chart
      const ctxDealers = document.getElementById('chartDealersBar');
      if (ctxDealers) {{
        new Chart(ctxDealers, {{
          type: 'bar',
          data: {{
            labels: ['РОЛЬФ', 'АвтоГермес', 'ГК Автомир', 'Бакра (Юг)', 'Geely У Сервис', 'Диалог Авто', 'Автохолдинг Максимум', 'БорисХоф'],
            datasets: [
              {{
                label: 'Сделки Август',
                data: [22, 7, 3, 2, 4, 1, 0, 0],
                backgroundColor: '#94a3b8',
                borderRadius: 4
              }},
              {{
                label: 'Сделки Сентябрь',
                data: [18, 11, 5, 4, 4, 1, 0, 0],
                backgroundColor: '#10b981',
                borderRadius: 4
              }},
              {{
                label: 'Лиды Сентябрь',
                data: [1, 3, 0, 3, 0, 2, 7, 3],
                backgroundColor: '#3b82f6',
                borderRadius: 4
              }}
            ]
          }},
          options: {{
            responsive: true,
            maintainAspectRatio: false,
            scales: {{
              y: {{ beginAtZero: true, grid: {{ color: 'rgba(148, 163, 184, 0.1)' }} }},
              x: {{ grid: {{ display: false }} }}
            }},
            plugins: {{
              legend: {{ position: 'top' }}
            }}
          }}
        }});
      }}
    }});
  </script>
</body>
</html>
'''

    # Save to root and site/
    dest_files = [
        os.path.join(PROJECT_ROOT, 'belgee_dashboard.html'),
        os.path.join(PROJECT_ROOT, 'site', 'belgee_dashboard.html')
    ]

    for p in dest_files:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"[3/3] Successfully generated HTML dashboard: {p}")

if __name__ == '__main__':
    generate_dashboard()
