# 理想乖離ダッシュボード — プロジェクト概要書
# 新しいClaudeの会話で、このファイルをそのまま貼り付けて使ってください。

## リポジトリ
- GitHub: kanemotokaneya/nikkei225-screener (Public)
- GitHub Pages: https://kanemotokaneya.github.io/nikkei225-screener/

## 目的
日本株・米国株の長期投資における「買い場」を自動スクリーニングし、
毎営業日更新のWebダッシュボード＋Excelで可視化するツール。

## 対象銘柄（約400銘柄）
- 日経225（全225銘柄）
- ダウ30
- NASDAQ100
- S&P500配当貴族（25年以上連続増配、約67銘柄）
※ 重複は自動除外

## 主要ファイル構成
```
nikkei225-screener/
├── stock_deviation_screener.py    ← メインスクリーナー（データ取得・計算・Excel/CSV/PNG出力）
├── generate_web_dashboard.py      ← HTMLダッシュボード生成（GitHub Pages用）
├── ideal_deviation_dashboard.py   ← 指数ダッシュボード（日経/ダウ/SP500/NASDAQ/SOX）
├── jp_dividends.csv               ← 日本株の1株配当データ（手動管理、年2-3回更新）
├── requirements.txt
├── .github/workflows/
│   ├── dashboard.yml              ← 指数ダッシュボード（毎営業日16:00 JST）
│   └── stock_screener.yml         ← 個別株スクリーナー（毎営業日16:30 JST）
└── output/                        ← 自動生成される出力
    ├── docs/index.html            ← GitHub Pagesに公開されるHTML
    ├── stock_deviation_YYYY-MM-DD.xlsx
    ├── stock_deviation_YYYY-MM-DD.csv
    └── *.png
```

## コア機能
1. **理想乖離**: 25日移動平均線乖離率を全日足データから統計し、-2σ(95%)/-3σ(99%)を算出
2. **買いスコア(0-100)**: 乖離率+配当+テクニカルシグナル+安定性の総合点数（Excelのみ表示）
3. **配当利回り**: 日本株はCSV管理、米国株はyfinance配当履歴から自前計算
4. **配当@-2σ**: 株価が-2σまで下落した場合の想定配当利回り
5. **連続増配年数**: yfinanceの配当履歴から年ごと合算して連続増加を自動カウント

## シグナル（6種類）
| シグナル | 条件 |
|---------|------|
| 高配当 | 日本株4%超、米国株6%超 |
| 半値 | 過去最高値(ATH)から50%以上下落 |
| 日足25MA上抜け | 前日は25日線の下、当日に上抜け |
| 月足陽転 | 前2ヶ月陰線→直近月が陽線に転換 |
| 月足GC | 月足9MA(短期)が24MA(中期)をゴールデンクロス |
| セクター唯一安 | 同セクター内で唯一のマイナス乖離銘柄 |

## 元ネタ
「まだ株・奥義継承」トレードマニュアル（PDF）
- 理想乖離（2σ/3σの統計的買い場判定）
- 乖離率トレード手法（25日MA乖離率ベース）
- 手法12（月足ゴールデンクロス・底打ち手法）
- 月別アノマリー（7-10月弱い、11-4月強い）

## 技術スタック
- Python 3.12 / yfinance / pandas / matplotlib / openpyxl
- GitHub Actions（自動実行）
- GitHub Pages（Webダッシュボード公開）

## 既知の注意点
- yfinanceの日本株配当データ(dividendRate等)は信用できない → CSVで管理
- 米国株の配当はyfinance配当履歴から自前計算（trailingAnnualDividendRateを参照）
- 日経225銘柄リストは入れ替えがあるため定期的な更新が必要
- jp_dividends.csvは決算期後（3月/9月頃）に配当額を手動更新

## 改善アイデア（未実装）
- 5日MA乖離率（スイングトレード用）
- 日経25日線の地合い判定（マイナス圏かどうか）
- 月別アノマリー（当月が買い有利か売り有利か）
- PER/PBR（割安度）
- ワンクリックフィルター（買いゾーンのみ/高配当のみ等）
- カラム表示切替（普段は主要列だけ、展開で全列表示）
