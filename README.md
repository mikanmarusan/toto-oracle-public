# toto予想Webアプリケーション

Jリーグを対象としたサッカーくじtoto（13試合の勝敗予想）の予想結果を表示するWebアプリケーション

## 概要

このアプリケーションは、Jリーグの試合データを基にtotoの勝敗予想を行い、モダンなWebインターフェースで結果を表示します。

## 技術スタック

- **フロントエンド**: Flask + HTML/CSS/JavaScript
- **バックエンド**: Python + Flask
- **スクレイピング**: requests + BeautifulSoup
- **コンテナ**: Docker + docker-compose

## プロジェクト構成

```
toto-oracle-public/
├── app/
│   ├── __init__.py
│   ├── main.py              # Flaskアプリケーションのエントリポイント
│   ├── batch/
│   │   ├── __init__.py
│   │   ├── scraper.py       # データスクレイピング機能
│   │   └── predictor.py     # 予想アルゴリズム
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        # API エンドポイント
│   └── templates/
│       └── index.html       # Webインターフェース
├── tests/
│   ├── __init__.py
│   └── test_app.py          # テストコード
├── requirements.txt         # Python依存関係
├── Dockerfile              # Dockerイメージ設定
├── docker-compose.yml      # Docker Compose設定
├── CLAUDE.md               # 開発指針・仕様書
└── README.md               # このファイル
```

## セットアップ・起動方法

### 1. リポジトリのクローン
```bash
git clone https://github.com/mikanmarusan/toto-oracle-public.git
cd toto-oracle-public
```

### 2. Dockerでの起動
```bash
docker-compose up
```

### 3. アプリケーションへのアクセス
ブラウザで http://localhost:5050 にアクセス

## 使用方法

### Web画面での操作
1. ブラウザで http://localhost:5050 にアクセス
2. 「最新予想を取得」ボタンをクリック
3. 予想結果が画面に表示されます

### バッチ処理の手動実行

#### APIエンドポイント
```bash
curl -X POST http://localhost:5050/api/run-batch
```

#### レスポンス例
```json
{
  "status": "success",
  "toto_info": {
    "round": "1234",
    "date": "2024/06/08",
    "deadline": "2024/06/08 19:00"
  },
  "predictions": [
    {
      "match_number": 1,
      "home_team": "浦和レッズ",
      "away_team": "鹿島アントラーズ",
      "prediction": "1"
    }
  ]
}
```

## 予想アルゴリズム

### 使用ファクター
1. **直近5試合の成績** (重要度: 高)
   - 勝ち点数: 勝利3点、引き分け1点、敗北0点
   - 得失点差: 5試合の平均得失点差

2. **ホーム/アウェイ優位性**
   - ホームチーム: +5pts程度の優位性付与

3. **順位差**
   - 現在の順位による優劣判定

4. **直前試合結果**
   - 直近の調子による補正

### 予想ロジック
- **勝敗予想**: 上記ファクターを総合的に判定
- **引き分け予想**: 各回の13試合中、両チームの力が拮抗している上位3試合を引き分け予想

## テスト

```bash
# 依存関係のインストール
pip install -r requirements.txt

# テスト実行
python -m pytest tests/ -v
```

## データソース

- **toto公式サイト**: くじ情報取得
- **Jリーグ公式データサイト**: https://data.j-league.or.jp/
  - チーム成績
  - 順位表
  - ホーム/アウェイ別成績

## エラーハンドリング

- **リトライ処理**: 3回、10秒間隔
- **ログ出力**: バッチ処理とエラーの詳細ログ
- **フォールバック**: スクレイピング失敗時はダミーデータで動作確認可能

## 開発

詳細な開発指針は `CLAUDE.md` を参照してください。

### コーディング規約
- PEP8準拠
- テスト・ドキュメントの同時更新
- セキュリティベストプラクティスの遵守

## ライセンス

MIT License - 詳細は `LICENSE` ファイルを参照