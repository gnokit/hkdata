# 港數通 · hkdata

**香港政府開放數據 × AI Agent 技能** — 一個具備自我學習能力的數據發掘與查詢工具，
面向 [DATA.GOV.HK](https://data.gov.hk)（資料一線通）開放數據。

[![license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![datasets](https://img.shields.io/badge/datasets-3%2C822-blueviolet.svg)](https://data.gov.hk)
[![version](https://img.shields.io/badge/version-0.3.0-lightgrey.svg)](scripts/hkdata/__init__.py)

你可以問它 *「長沙灣有沒有政府健身室？」* 或者 *"what's the air quality right
now?"* — 它會找出正確的官方 dataset、查詢即時 API，而且**當數據確實不存在時，
會如實回答「沒有」**。

```text
你    : 觀塘有多少個公共屋邨？
港數通 : 14 個屋邨（截至 2026-06-22，香港時間）。
         來源：房屋署 PSI API
         Dataset：hk-housing-eslocator-eslocator
         Endpoint：https://data.housingauthority.gov.hk/psi/rest/export/prh-estates
         提示：區名使用「&」（如 Central & Western）— 進行 join 前須先標準化。
```

---

## 實戰示範

以下是 AI Agent (GrokBot) 真實回答的例子 —— 每個答案都註明背後的 data.gov.hk dataset。

| | | |
|---|---|---|
| <img src="docs/screenshots/parking-vacancy-nearby.webp" width="260" alt="商場附近即時停車場空位"> | <img src="docs/screenshots/library-new-books.webp" width="260" alt="圖書館新增館藏書名搜尋"> | <img src="docs/screenshots/sports-running-classes.webp" width="260" alt="社區康體活動跑步班及報名期"> |
| **即時停車場空位**<br>商場附近最近 5 個停車場，空位即時更新 | **圖書館新增館藏**<br>搜尋康文署最新入藏書籍，可按相關度或入藏日期排序 | **運動課程**<br>SmartPLAY 跑步班連報名期 |
| <img src="docs/screenshots/ferry-cheung-chau-eta.webp" width="260" alt="渡輪時間表結合即時船隻 ETA"> | <img src="docs/screenshots/film-fund-roi.webp" width="260" alt="電影發展基金資助性價比排行"> | <img src="docs/screenshots/kindergarten-enrolment-trend.webp" width="260" alt="2015 至 2025 年幼稚園及小學學生人數趨勢"> |
| **渡輪時間表 + 即時 ETA**<br>靜態時間表結合即時船隻位置 | **電影發展基金性價比**<br>票房 ÷ 資助，兩個 dataset 連結 | **學生人數趨勢**<br>幼稚園 → 小學系列，2015–2025 |

## 可以做什麼

港數通將自然語言問題轉化為有出處、即時的答案：

- **搜尋整個 catalog** — data.gov.hk 全部約 3,822 個 dataset，涵蓋英文與繁體中文，
  而非只有部分索引。
- **理解中文** — `康文署` 會解析為 `康樂及文化事務署`，中文查詢也能正確對應。
- **查詢即時 API** — 找出正確的 endpoint、進行測試，並自動偵測 JSON / XML / CSV
  以取得最新數據。
- **如實作答** — 每個答案都會列明 dataset ID、endpoint，以及數據本身的香港時間戳；
  當確實沒有數據時，會回答「沒有」。
- **具備記憶** — 每次發現都會儲存為正面／負面記憶卡，下一條類似問題便能立即回答。

背後它會將 data.gov.hk 爬取一次，建立本地、已清除個人資料的 catalog，再以混合檢索
（多語言稠密向量 + 關鍵字）進行搜尋：

```text
catalog-sync --full --lang en,tc    爬取完整 catalog（可續傳）
        │                            package_list 種子 → 每個 dataset package_show
        ▼
data/catalog/*.jsonl                8 個 shard，每個 500 個 dataset，已清除個人資料
        │
catalog-embed                       以本地（或遠端）模型進行嵌入
        ▼
.cache/catalog/chroma/              ChromaDB 資料庫（gitignored）
   ├── hkdata_datasets              「有哪些 dataset 存在」
   └── hkdata_experiences           「這條問題如何回答」  （正／負經驗）
```

## 與其他工具最大的不同：它會學習

每次發現都會寫回成一張**記憶卡**（正面或負面），因此下一條類似問題無須重新搜尋，
即可立即回答：

```text
1. experience-search "長沙灣 健身室"               → 沒有記錄
2. catalog-search   "gym room"                    → hk-lcsd-facility-facility-fit
3. info + test 個 endpoint                         → 即時 JSON，87 間
4. experience-log   --outcome located ...          → 寫入記憶
5. experience-search "深水埗 fitness room"         → 在第 1 步即可回答 ✓
```

過時的卡片帶有日期、可被取代；資料庫同時記錄**哪些可行**與**哪些是死路**，
因此不會重複犯下相同的錯誤。

| | 港數通 |
|---|---|
| **雙語** | 英文 + 繁體中文 metadata（`康文署` → `康樂及文化事務署`） |
| **混合檢索** | ChromaDB 稠密向量融合關鍵字 + 簡稱對照 |
| **自我學習** | 每次發現都記錄為正面／負面卡片 |
| **可插拔嵌入** | 預設本地 Ollama；亦可使用任何 OpenAI 相容 API（或自行撰寫 backend） |
| **誠實合約** | 必須列明 dataset ID、endpoint，以及數據本身的香港時間戳 |
| **謹守範圍** | 只處理香港政府數據——其餘一律轉交 |

## 快速開始

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-vectors.txt
ollama pull qwen3-embedding:0.6b

bash ./hk.sh catalog-embed                 # 約 10 分鐘（shard 已 committed，無須爬取）
bash ./hk.sh experience-embed
bash ./hk.sh catalog-search "badminton courts"
bash ./hk.sh catalog-search "康文署羽毛球場"
```

`data/catalog/` 的 shard 已經 committed，因此新 clone 下來**只需要建立向量庫**，
無須重新爬取。完整安裝請見 [SETUP.md](SETUP.md)。

## 用法

```bash
# 第 1 步 — 過往經驗（正面 + 負面）
bash ./hk.sh experience-search "gym room Cheung Sha Wan"

# 第 2 步 — 完整 catalog
bash ./hk.sh catalog-search "badminton courts"
bash ./hk.sh catalog-search "康文署羽毛球場" --top-n 5

# 查看 dataset + 測試 endpoint
bash ./hk.sh info hk-lcsd-facility-facility-fit
bash ./hk.sh test "http://www.lcsd.gov.hk/datagovhk/facility/facility-fitrm.json"

# 精選已驗證 dataset + 覆蓋率 + 嵌入 backend
bash ./hk.sh search-local "enrolment"
bash ./hk.sh catalog-status
bash ./hk.sh embed-status
```

### 命令

| 命令 | 用途 |
|---|---|
| `experience-search "<query>"` | 過往經驗語意搜尋（正／負）— 第 1 步 |
| `experience-log --kind positive\|negative …` | 記錄並索引經驗（第 5 步） |
| `experience-embed` / `experience-migrate` | 建立／重建經驗索引 |
| `catalog-search "<query>"` | 完整 catalog 混合檢索 — 第 2 步 |
| `catalog-sync [--full] [--refresh] [--lang en,tc]` | 種子／爬取／更新離線 catalog |
| `catalog-embed` | 建立 ChromaDB 向量庫 |
| `catalog-status` | 覆蓋率 + 向量庫報告 |
| `embed-status` | 現行嵌入 backend + 資料庫匹配情況 |
| `info "<id>"` | Dataset metadata（`package_show`） |
| `test "<url>"` | 測試 endpoint，自動偵測 JSON / XML / CSV |
| `search-local "<query>"` | 搜尋精選參考文件 |
| `reindex` | 由參考文件重建 `references/search-index.json` |
| `log-search` / `log-render` | 查詢／重新產生失敗與策略記錄 |

所有命令均經 `bash ./hk.sh` 執行，它會在需要 `chromadb` 時自動選用 `.venv`，
否則使用普通 `python3` —— 你無須自行選擇。

### 嵌入 backend

預設為本地 Ollama（`qwen3-embedding:0.6b`）。可以改用任何 OpenAI 相容 API，
或者透過 `Embedder` 介面接入自己的 backend：

```bash
export HKDATA_EMBED_PROVIDER=openai
export HKDATA_EMBED_MODEL=text-embedding-3-small
export HKDATA_EMBED_URL=https://api.openai.com/v1/embeddings
export HKDATA_EMBED_API_KEY=sk-...
bash ./hk.sh catalog-embed && bash ./hk.sh experience-embed
```

介面用法請見 [SETUP.md](SETUP.md) *「Integrating a new backend」*。

## 目錄結構

```
hk.sh                     單一 CLI 入口（自動選用 venv 或 python3）
SKILL.md                  發掘流程（agent 入口）
AGENTS.md                 供 agent 使用的筆記
scripts/hkdata/           CLI（catalog.py、vectors.py、embeddings.py、index.py …）
data/catalog/             已清除個人資料的 catalog shard（committed）
references/               精選 dataset 文件 + 登錄 + 簡稱對照
logs/                     渲染視圖（failure log = 負面、strategy registry = 正面）
tests/                    pytest 測試
```

## 範圍

**只處理 data.gov.hk 的香港政府數據。** 非香港數據、非政府來源、或一般網絡查詢均
超出範圍，會轉交予 agent 原生的網頁搜尋 —— 如此才能保持資料庫專注、答案可信。

## 數據來源與致謝

所有 dataset metadata 來自 **[DATA.GOV.HK](https://data.gov.hk)**，並受其
[條款及細則](https://data.gov.hk/en/terms-and-conditions)約束。
`data/catalog/` 中的 shard 是 `package_show` 回應的**去識別化投影**：個人聯絡資料
（作者／維護者的電郵與電話）會被剔除，只保留搜尋所需的欄位。JSONL 資料庫隨時可以
用 `catalog-sync` 重新產生。

## 測試

```bash
.venv/bin/python -m pytest tests/ -q
```

## 授權

程式碼與文件採用 [MIT](LICENSE)。底層政府數據受 DATA.GOV.HK 使用條款約束，
不屬於 MIT 授權範圍。

---

_港數通 · hkdata — 香港政府開放數據，問得準，答得真。_
