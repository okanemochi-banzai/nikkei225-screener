[README (2).md](https://github.com/user-attachments/files/25873571/README.2.md)
# 理想乖離ダッシュボード (Ideal Deviation Dashboard)

長期投資の**買い場**を一目で判断するためのPythonツール。  
主要株価指数の25日移動平均線乖離率を統計的に算出し、-2σ / -3σ の買いゾーンを可視化する。

## 出力イメージ

### サマリーカード
各指数の現在のゾーン（BUY ZONE / NEUTRAL等）、乖離率、-2σ到達価格を一覧表示。

### 乖離率チャート（直近2年）
- 青線 = 25日MA乖離率
- オレンジ点線 = -2σライン（95%圏外 → 買い検討）
- 赤点線 = -3σライン（99%圏外 → 強い買いシグナル）
- オレンジ点 / 赤点 = -2σ / -3σ 突入ポイント

### ヒストグラム
全期間の乖離率分布。黒線が現在位置。

## 対象指数

| 指数 | ティッカー | 備考 |
|------|----------|------|
| 日経225 | ^N225 | |
| ダウ平均 | ^DJI | |
| S&P500 | ^GSPC | |
| ナスダック | ^IXIC | |
| SOX半導体 | ^SOX | |

## ゾーン判定ロジック

| ゾーン | 条件 | アクション |
|--------|------|----------|
| **STRONG BUY (-3σ)** | 乖離率 ≤ -3σ | ナンピンしてでも買い（99%圏外） |
| **BUY ZONE (-2σ)** | 乖離率 ≤ -2σ | 仕込み検討（95%圏外） |
| MILD DIP | 乖離率 < 0 | 軽い押し目 |
| NEUTRAL / UP | 乖離率 ≤ +2σ | 平常〜上昇 |
| OVERBOUGHT (+2σ) | 乖離率 ≤ +3σ | 過熱気味 |
| EXTREME HIGH (+3σ) | 乖離率 > +3σ | 極端な高値圏 |

## セットアップ

### ローカル実行

```bash
# 1. リポジトリをクローン
git clone https://github.com/YOUR_USERNAME/ideal-deviation-dashboard.git
cd ideal-deviation-dashboard

# 2. 依存パッケージをインストール
pip install -r requirements.txt

# 3. 実行
python ideal_deviation_dashboard.py
```

PNG画像3枚（summary / charts / histograms）とCSVが出力される。

### GitHub Actions（自動実行）

1. このリポジトリをGitHubにpush
2. `.github/workflows/dashboard.yml` が毎週月曜朝7時(JST)に自動実行
3. `output/` フォルダに最新のダッシュボード画像がコミットされる
4. 手動実行: Actions → Ideal Deviation Dashboard → Run workflow

### 出力先ディレクトリの変更

```bash
OUTPUT_DIR=./my_output python ideal_deviation_dashboard.py
```

## カスタマイズ

### 銘柄の追加・変更

`ideal_deviation_dashboard.py` の `INDICES` 辞書を編集：

```python
INDICES = {
    "Nikkei 225":   {"ticker": "^N225",  "label_jp": "日経225"},
    "Dow Jones":    {"ticker": "^DJI",   "label_jp": "ダウ平均"},
    # 個別株を追加する場合:
    "Toyota":       {"ticker": "7203.T", "label_jp": "トヨタ"},
    "NVIDIA":       {"ticker": "NVDA",   "label_jp": "NVIDIA"},
}
```

日本株は証券コード + `.T`（例: `7203.T`）、米国株はそのままティッカー。

### チャート表示期間の変更

```python
CHART_YEARS = 3   # 直近3年表示に変更
```

## 技術詳細

- **理想乖離**: 全日足データの25日MA乖離率を算出し、平均±2σ（95%信頼区間）を「理想乖離」とする
- **統計期間**: yfinanceで取得可能な最大期間（指数により30〜50年）
- **データソース**: Yahoo Finance (yfinance)

## ライセンス

個人利用限定。投資判断は自己責任で行ってください。
