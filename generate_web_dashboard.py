#!/usr/bin/env python3
"""
Web Dashboard Generator
=======================
stock_deviation_screener.py の結果から
GitHub Pages用の静的HTMLダッシュボードを自動生成する。
"""

import pandas as pd
import json
import os
from datetime import datetime
import glob

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "output")
PAGES_DIR = os.path.join(OUTPUT_DIR, "docs")


def generate_html(df, today):
    """メインHTML生成"""

    # マーケット別統計
    markets = {}
    for m in ["Nikkei225", "Dow30", "NASDAQ100"]:
        mdf = df[df["market"] == m]
        zones = {}
        for z in ["STRONG BUY", "BUY ZONE", "MILD DIP", "NEUTRAL", "OVERBOUGHT", "EXTREME HIGH"]:
            zones[z] = int(len(mdf[mdf["zone"] == z]))
        markets[m] = {"total": int(len(mdf)), "zones": zones}

    # Top30 買い候補
    top30 = df.head(30).to_dict("records")

    # BUY/STRONG BUY銘柄
    buy_list = df[df["zone"].isin(["STRONG BUY", "BUY ZONE"])].to_dict("records")

    # マーケット別全データ（JSON）
    all_data = {}
    for m in ["Nikkei225", "Dow30", "NASDAQ100"]:
        mdf = df[df["market"] == m].to_dict("records")
        all_data[m] = mdf

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ideal Deviation Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Noto+Sans+JP:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #0a0e17;
    --surface: #111827;
    --surface2: #1a2235;
    --border: #1e2a3a;
    --text: #e2e8f0;
    --text-dim: #64748b;
    --accent: #38bdf8;
    --red: #ef4444;
    --orange: #f97316;
    --yellow: #eab308;
    --green: #22c55e;
    --purple: #a855f7;
    --pink: #ec4899;
  }}

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    font-family: 'Noto Sans JP', 'JetBrains Mono', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    overflow-x: hidden;
  }}

  .grain {{
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none; z-index: 9999;
  }}

  .glow-top {{
    position: fixed; top: -200px; left: 50%; transform: translateX(-50%);
    width: 800px; height: 400px;
    background: radial-gradient(ellipse, rgba(56,189,248,0.08) 0%, transparent 70%);
    pointer-events: none; z-index: 0;
  }}

  header {{
    position: relative; padding: 2.5rem 2rem 1.5rem;
    border-bottom: 1px solid var(--border);
    background: linear-gradient(180deg, rgba(17,24,39,0.9) 0%, var(--bg) 100%);
  }}

  header h1 {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.6rem; font-weight: 700;
    background: linear-gradient(135deg, var(--accent), #818cf8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
  }}

  header .meta {{
    display: flex; gap: 1.5rem; margin-top: 0.5rem;
    font-size: 0.8rem; color: var(--text-dim);
    font-family: 'JetBrains Mono', monospace;
  }}

  header .meta span {{ display: flex; align-items: center; gap: 0.3rem; }}
  .pulse {{ width: 8px; height: 8px; border-radius: 50%; background: var(--green);
    animation: pulse 2s infinite; }}
  @keyframes pulse {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.3; }} }}

  .container {{ max-width: 1400px; margin: 0 auto; padding: 1.5rem; position: relative; z-index: 1; }}

  /* ─── Zone Cards ─── */
  .zone-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem; margin-bottom: 2rem;
  }}

  .zone-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px; padding: 1.2rem;
    transition: all 0.2s ease;
  }}

  .zone-card:hover {{
    border-color: var(--accent);
    box-shadow: 0 0 20px rgba(56,189,248,0.08);
    transform: translateY(-2px);
  }}

  .zone-card .market-name {{
    font-size: 0.75rem; font-weight: 600;
    color: var(--accent); text-transform: uppercase;
    letter-spacing: 1.5px; margin-bottom: 0.8rem;
    font-family: 'JetBrains Mono', monospace;
  }}

  .zone-bars {{ display: flex; flex-direction: column; gap: 0.35rem; }}

  .zone-bar {{
    display: flex; align-items: center; gap: 0.6rem;
    font-size: 0.78rem;
  }}

  .zone-bar .label {{ width: 100px; text-align: right; color: var(--text-dim);
    font-size: 0.7rem; font-family: 'JetBrains Mono', monospace; }}
  .zone-bar .bar-bg {{ flex: 1; height: 20px; background: var(--surface2); border-radius: 4px; overflow: hidden; position: relative; }}
  .zone-bar .bar-fill {{ height: 100%; border-radius: 4px; transition: width 1s ease;
    display: flex; align-items: center; justify-content: flex-end; padding-right: 6px;
    font-size: 0.7rem; font-weight: 700; color: white;
    font-family: 'JetBrains Mono', monospace; }}

  .bar-strong {{ background: linear-gradient(90deg, #dc2626, #ef4444); }}
  .bar-buy {{ background: linear-gradient(90deg, #ea580c, #f97316); }}
  .bar-mild {{ background: linear-gradient(90deg, #ca8a04, #eab308); }}
  .bar-neutral {{ background: linear-gradient(90deg, #16a34a, #22c55e); }}
  .bar-over {{ background: linear-gradient(90deg, #7c3aed, #a855f7); }}
  .bar-extreme {{ background: linear-gradient(90deg, #9d174d, #ec4899); }}

  /* ─── Summary Stats ─── */
  .stats-row {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 0.8rem; margin-bottom: 2rem;
  }}

  .stat-card {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 10px; padding: 1rem; text-align: center;
  }}

  .stat-card .num {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 2rem; font-weight: 700;
  }}

  .stat-card .lbl {{ font-size: 0.7rem; color: var(--text-dim); margin-top: 0.2rem;
    font-family: 'JetBrains Mono', monospace; text-transform: uppercase; letter-spacing: 1px; }}

  /* ─── Table ─── */
  .section-title {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.1rem; font-weight: 700; margin: 2rem 0 1rem;
    display: flex; align-items: center; gap: 0.5rem;
  }}

  .section-title .dot {{ width: 10px; height: 10px; border-radius: 50%; }}

  .table-wrap {{
    overflow-x: auto; border: 1px solid var(--border);
    border-radius: 10px; background: var(--surface);
  }}

  table {{ width: 100%; border-collapse: collapse; font-size: 0.8rem; }}

  th {{
    position: sticky; top: 0; z-index: 10;
    background: var(--surface2); padding: 0.7rem 0.8rem;
    text-align: left; font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem; text-transform: uppercase;
    letter-spacing: 0.5px; color: var(--text-dim);
    border-bottom: 1px solid var(--border);
    white-space: nowrap;
  }}

  td {{
    padding: 0.55rem 0.8rem; border-bottom: 1px solid var(--border);
    font-family: 'JetBrains Mono', monospace; font-size: 0.78rem;
    white-space: nowrap;
  }}

  tr:hover td {{ background: rgba(56,189,248,0.04); }}

  .zone-badge {{
    display: inline-block; padding: 2px 8px; border-radius: 4px;
    font-size: 0.65rem; font-weight: 700; letter-spacing: 0.3px;
  }}

  .z-strong {{ background: var(--red); color: white; }}
  .z-buy {{ background: var(--orange); color: white; }}
  .z-mild {{ background: rgba(234,179,8,0.2); color: var(--yellow); }}
  .z-neutral {{ background: rgba(34,197,94,0.15); color: var(--green); }}
  .z-over {{ background: rgba(168,85,247,0.2); color: var(--purple); }}
  .z-extreme {{ background: rgba(236,72,153,0.2); color: var(--pink); }}

  .neg {{ color: var(--red); }}
  .pos {{ color: var(--green); }}
  .hot {{ color: var(--orange); font-weight: 700; }}

  /* ─── Tabs ─── */
  .tabs {{
    display: flex; gap: 0.5rem; margin-bottom: 1rem;
    border-bottom: 1px solid var(--border); padding-bottom: 0.5rem;
  }}

  .tab-btn {{
    padding: 0.5rem 1rem; border: 1px solid var(--border);
    border-radius: 6px; background: transparent; color: var(--text-dim);
    font-family: 'JetBrains Mono', monospace; font-size: 0.75rem;
    cursor: pointer; transition: all 0.2s;
  }}

  .tab-btn:hover {{ border-color: var(--accent); color: var(--text); }}
  .tab-btn.active {{ background: var(--accent); color: var(--bg); border-color: var(--accent); font-weight: 700; }}

  .tab-panel {{ display: none; }}
  .tab-panel.active {{ display: block; }}

  /* ─── Search ─── */
  .search-box {{
    display: flex; gap: 0.5rem; margin-bottom: 1rem; align-items: center;
  }}

  .search-box input {{
    flex: 1; max-width: 400px; padding: 0.5rem 1rem;
    background: var(--surface2); border: 1px solid var(--border);
    border-radius: 8px; color: var(--text);
    font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;
    outline: none; transition: border 0.2s;
  }}

  .search-box input:focus {{ border-color: var(--accent); }}
  .search-box input::placeholder {{ color: var(--text-dim); }}

  /* ─── Footer ─── */
  footer {{
    text-align: center; padding: 2rem;
    font-size: 0.7rem; color: var(--text-dim);
    font-family: 'JetBrains Mono', monospace;
    border-top: 1px solid var(--border);
    margin-top: 3rem;
  }}

  @media (max-width: 768px) {{
    header h1 {{ font-size: 1.2rem; }}
    .container {{ padding: 1rem; }}
    .zone-grid {{ grid-template-columns: 1fr; }}
    .stats-row {{ grid-template-columns: repeat(2, 1fr); }}
  }}
</style>
</head>
<body>
<div class="grain"></div>
<div class="glow-top"></div>

<header>
  <h1>IDEAL DEVIATION DASHBOARD</h1>
  <div class="meta">
    <span><span class="pulse"></span> Updated: {today}</span>
    <span>Nikkei225 + Dow30 + NASDAQ100</span>
    <span>{len(df)} stocks tracked</span>
  </div>
</header>

<div class="container">

  <!-- Summary Stats -->
  <div class="stats-row" style="margin-top:1.5rem;">
    <div class="stat-card">
      <div class="num" style="color:var(--red)">{len(df[df['zone']=='STRONG BUY'])}</div>
      <div class="lbl">Strong Buy</div>
    </div>
    <div class="stat-card">
      <div class="num" style="color:var(--orange)">{len(df[df['zone']=='BUY ZONE'])}</div>
      <div class="lbl">Buy Zone</div>
    </div>
    <div class="stat-card">
      <div class="num" style="color:var(--yellow)">{len(df[df['dist_to_2s']<=3.0])}</div>
      <div class="lbl">Within 3% of -2σ</div>
    </div>
    <div class="stat-card">
      <div class="num" style="color:var(--green)">{len(df[df['zone']=='NEUTRAL'])}</div>
      <div class="lbl">Neutral</div>
    </div>
    <div class="stat-card">
      <div class="num" style="color:var(--purple)">{len(df[df['zone'].isin(['OVERBOUGHT','EXTREME HIGH'])])}</div>
      <div class="lbl">Overbought</div>
    </div>
  </div>

  <!-- Zone Distribution -->
  <div class="section-title"><span class="dot" style="background:var(--accent)"></span> Zone Distribution</div>
  <div class="zone-grid">
    {"".join(_zone_card_html(m, markets[m]) for m in ["Nikkei225", "Dow30", "NASDAQ100"])}
  </div>

  <!-- Top 30 Buy Candidates -->
  <div class="section-title"><span class="dot" style="background:var(--red)"></span> Top 30 — Closest to Buy Zone</div>
  <div class="table-wrap">
    <table>
      <thead><tr>
        <th>#</th><th>Zone</th><th>Ticker</th><th>Name</th><th>Market</th>
        <th>Price</th><th>Dev%</th><th>-2σ%</th><th>-3σ%</th>
        <th>Buy@-2σ</th><th>Dist to -2σ</th><th>Div%</th><th>Div@-2σ</th>
      </tr></thead>
      <tbody>
        {"".join(_row_html(i+1, r) for i, r in enumerate(top30))}
      </tbody>
    </table>
  </div>

  <!-- Full Data by Market -->
  <div class="section-title" style="margin-top:2.5rem;">
    <span class="dot" style="background:var(--green)"></span> Full Data
  </div>

  <div class="search-box">
    <input type="text" id="searchInput" placeholder="Search ticker or name..." oninput="filterTable()">
  </div>

  <div class="tabs">
    <button class="tab-btn active" onclick="switchTab('all')">ALL ({len(df)})</button>
    <button class="tab-btn" onclick="switchTab('nikkei')">Nikkei225 ({markets['Nikkei225']['total']})</button>
    <button class="tab-btn" onclick="switchTab('dow')">Dow30 ({markets['Dow30']['total']})</button>
    <button class="tab-btn" onclick="switchTab('nasdaq')">NASDAQ100 ({markets['NASDAQ100']['total']})</button>
  </div>

  <div id="tab-all" class="tab-panel active">
    {_full_table_html(df.to_dict('records'), "tbl-all")}
  </div>
  <div id="tab-nikkei" class="tab-panel">
    {_full_table_html(all_data['Nikkei225'], "tbl-nikkei")}
  </div>
  <div id="tab-dow" class="tab-panel">
    {_full_table_html(all_data['Dow30'], "tbl-dow")}
  </div>
  <div id="tab-nasdaq" class="tab-panel">
    {_full_table_html(all_data['NASDAQ100'], "tbl-nasdaq")}
  </div>

</div>

<footer>
  Ideal Deviation Dashboard &middot; Auto-updated via GitHub Actions<br>
  Data: Yahoo Finance &middot; Not financial advice
</footer>

<script>
function switchTab(id) {{
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  const map = {{'all':'tab-all','nikkei':'tab-nikkei','dow':'tab-dow','nasdaq':'tab-nasdaq'}};
  document.getElementById(map[id]).classList.add('active');
  event.target.classList.add('active');
}}

function filterTable() {{
  const q = document.getElementById('searchInput').value.toLowerCase();
  document.querySelectorAll('.tab-panel.active tbody tr').forEach(row => {{
    const text = row.textContent.toLowerCase();
    row.style.display = text.includes(q) ? '' : 'none';
  }});
}}

// Animate bars on load
window.addEventListener('load', () => {{
  document.querySelectorAll('.bar-fill').forEach(bar => {{
    const w = bar.getAttribute('data-width');
    bar.style.width = w + '%';
  }});
}});
</script>
</body>
</html>"""
    return html


def _zone_card_html(market, data):
    total = data["total"]
    zones_config = [
        ("STRONG BUY", "bar-strong", "z-strong"),
        ("BUY ZONE", "bar-buy", "z-buy"),
        ("MILD DIP", "bar-mild", "z-mild"),
        ("NEUTRAL", "bar-neutral", "z-neutral"),
        ("OVERBOUGHT", "bar-over", "z-over"),
        ("EXTREME HIGH", "bar-extreme", "z-extreme"),
    ]
    bars = ""
    for zname, bar_cls, _ in zones_config:
        cnt = data["zones"].get(zname, 0)
        pct = (cnt / total * 100) if total > 0 else 0
        display_w = max(pct, 2) if cnt > 0 else 0
        bars += f"""<div class="zone-bar">
          <span class="label">{zname}</span>
          <div class="bar-bg"><div class="bar-fill {bar_cls}" data-width="{display_w}" style="width:0%">{cnt if cnt>0 else ''}</div></div>
        </div>"""

    return f"""<div class="zone-card">
      <div class="market-name">{market} ({total})</div>
      <div class="zone-bars">{bars}</div>
    </div>"""


def _zone_badge(zone):
    cls_map = {
        "STRONG BUY": "z-strong", "BUY ZONE": "z-buy", "MILD DIP": "z-mild",
        "NEUTRAL": "z-neutral", "OVERBOUGHT": "z-over", "EXTREME HIGH": "z-extreme",
    }
    return f'<span class="zone-badge {cls_map.get(zone, "")}">{zone}</span>'


def _row_html(rank, r):
    dev_cls = "neg" if r["deviation"] < 0 else "pos"
    dist_cls = "neg hot" if r["dist_to_2s"] <= 0 else ("hot" if r["dist_to_2s"] <= 3 else "")
    div_val = r.get("div_yield", 0) or 0
    div2s_val = r.get("div_at_2s", 0) or 0
    # 日本株4%、米国株6%以上で緑ハイライト
    div_threshold = 4.0 if r.get("market") == "Nikkei225" else 6.0
    div_cls = "pos" if div_val >= div_threshold else ("" if div_val > 0 else "")
    div2s_cls = "pos" if div2s_val >= div_threshold else ""
    return f"""<tr>
      <td>{rank}</td>
      <td>{_zone_badge(r['zone'])}</td>
      <td><strong>{r['ticker']}</strong></td>
      <td>{r['name']}</td>
      <td>{r['market']}</td>
      <td>{r['price']:,.2f}</td>
      <td class="{dev_cls}">{r['deviation']:+.2f}%</td>
      <td>{r['sigma2_lower']:+.2f}%</td>
      <td>{r['sigma3_lower']:+.2f}%</td>
      <td>{r['price_at_2s']:,.0f}</td>
      <td class="{dist_cls}">{r['dist_to_2s']:+.1f}%</td>
      <td class="{div_cls}">{div_val:.2f}%</td>
      <td class="{div2s_cls}">{div2s_val:.2f}%</td>
    </tr>"""


def _full_table_html(records, table_id):
    rows = ""
    for i, r in enumerate(records):
        rows += _row_html(i + 1, r)
    return f"""<div class="table-wrap">
      <table id="{table_id}">
        <thead><tr>
          <th>#</th><th>Zone</th><th>Ticker</th><th>Name</th><th>Market</th>
          <th>Price</th><th>Dev%</th><th>-2σ%</th><th>-3σ%</th>
          <th>Buy@-2σ</th><th>Dist to -2σ</th><th>Div%</th><th>Div@-2σ</th>
        </tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>"""


def main():
    os.makedirs(PAGES_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")

    # CSVまたはExcelから最新データ読み込み
    csv_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "stock_deviation_*.csv")))
    xlsx_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "stock_deviation_*.xlsx")))

    if csv_files:
        df = pd.read_csv(csv_files[-1])
    elif xlsx_files:
        df = pd.read_excel(xlsx_files[-1], sheet_name="All Stocks")
        # Excelのヘッダー名をCSV名にマッピング
        col_map = {
            "Rank": "rank", "Zone": "zone", "Ticker": "ticker", "Name": "name",
            "Market": "market", "Price": "price", "SMA25": "sma25",
            "Dev%": "deviation", "-2σ%": "sigma2_lower", "-3σ%": "sigma3_lower",
            "Buy@-2σ": "price_at_2s", "Buy@-3σ": "price_at_3s",
            "Dist to -2σ%": "dist_to_2s", "Div%": "div_yield", "Div@-2σ%": "div_at_2s",
            "StdDev": "std", "StatDays": "stat_days",
        }
        df.rename(columns=col_map, inplace=True)
    else:
        print("  [ERROR] No data files found in output/")
        return

    # 配当カラムがない場合のフォールバック
    if "div_yield" not in df.columns:
        df["div_yield"] = 0.0
    if "div_at_2s" not in df.columns:
        df["div_at_2s"] = 0.0
    df["div_yield"] = df["div_yield"].fillna(0.0)
    df["div_at_2s"] = df["div_at_2s"].fillna(0.0)

    df.sort_values("dist_to_2s", ascending=True, inplace=True)
    df.reset_index(drop=True, inplace=True)

    html = generate_html(df, today)

    html_path = os.path.join(PAGES_DIR, "index.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  Saved: {html_path}")

    # .nojekyll (GitHub Pages用)
    nojekyll = os.path.join(PAGES_DIR, ".nojekyll")
    with open(nojekyll, "w") as f:
        pass

    print("  Web dashboard generated.")


if __name__ == "__main__":
    main()
