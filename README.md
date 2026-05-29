# POE2 Overlay Timer

**Language / 語言：** [English](#english) | [繁體中文](#繁體中文)

---

## English

A lightweight always-on-top Windows overlay for **Path of Exile 2** players.

- Floating stopwatch that **auto-pauses** when PoE2 loses focus and **auto-resumes** when you switch back
- Detects which **map / area** you just entered by reading `Client.txt`
- Displays your **personal notes** for that map in the overlay
- Press **V** to copy the notes straight to clipboard — paste into Discord, party chat, etc.
- Semi-transparent, draggable, stays on top of the game

### Screenshots

> *(Add your own screenshots here)*

### Requirements

| Item | Details |
|------|---------|
| OS | Windows 10 / 11 |
| Python | 3.8 or later — download from [python.org](https://www.python.org/downloads/) |

> **Important:** During Python installation, tick **"Add Python to PATH"** or the `.bat` files will not work.

### Installation (first time only)

1. Download or clone this repository
2. Double-click **`install.bat`** — this installs the required Python packages
3. Double-click **`run.bat`** — the overlay appears

That's it. No coding required.

### Hotkeys

These keys only work while Path of Exile 2 is in the foreground.

| Key | Action |
|-----|--------|
| `F4` | Start / Pause stopwatch |
| `Ctrl + 0` | Reset stopwatch to 0 |
| `V` | Copy current map notes to clipboard |
| `Home` | Show / Hide the notes panel |

Right-click the overlay for a context menu (Copy notes, Reload notes, Exit).

### Writing Your Own Notes

Notes are plain `.txt` files inside the `notes/` folder.  
Open `notes/template_empty.txt` for the full format guide.

**Quick format:**
```
[Map Name EN / 地圖名稱 ZH-TW]
{
Your note text here.
Boss mechanic reminder, item filter tip, etc.
}

[Another Map / 另一個地圖]
{
Second map notes.
}
```

- One file can contain any number of map blocks
- Lines starting with `#` are comments and are ignored
- Separate name variants with `/` — the tool matches whichever language your PoE2 client uses
- An empty `{ }` block means the map is known but you have no notes → overlay stays silent

The included `notes/tip_with_050.txt` is a sample file with Traditional Chinese act notes. You can edit or delete it freely.

### Troubleshooting

| Problem | Solution |
|---------|----------|
| Overlay doesn't appear | Make sure PoE2 is running; the overlay only shows when PoE2 is focused |
| Notes don't show for a map | Check the map name in `Client.txt` matches what's in your `.txt` note file |
| `python` not found error | Re-install Python and tick "Add Python to PATH" |
| Dependencies error | Run `install.bat` again |

### License

MIT License — free to use, modify, and share.

---

## 繁體中文

一個輕量的 Windows 懸浮視窗工具，專為 **流亡黯道 2（Path of Exile 2）** 玩家設計。

- 懸浮計時碼錶，切離遊戲視窗時**自動暫停**，切回後**自動繼續**
- 透過讀取 `Client.txt` 自動偵測你進入的**地圖 / 地區**
- 在懸浮視窗中顯示你為該地圖寫的**個人筆記**
- 按 **V** 直接將筆記複製到剪貼板 — 方便貼到 Discord 或隊伍聊天
- 半透明、可拖曳、永遠置頂顯示於遊戲上方

### 截圖

> *(可自行補上截圖)*

### 系統需求

| 項目 | 說明 |
|------|------|
| 作業系統 | Windows 10 / 11 |
| Python | 3.8 以上版本 — 至 [python.org](https://www.python.org/downloads/) 下載 |

> **重要：** 安裝 Python 時，請務必勾選 **「Add Python to PATH」**，否則 `.bat` 檔案將無法執行。

### 安裝方式（僅需執行一次）

1. 下載或 clone 此 repository
2. 雙擊 **`install.bat`** — 自動安裝所需的 Python 套件
3. 雙擊 **`run.bat`** — 懸浮視窗即會出現

完成。不需要任何程式設計知識。

### 快捷鍵

以下快捷鍵**僅在 Path of Exile 2 視窗為前景時**有效。

| 按鍵 | 功能 |
|------|------|
| `F4` | 開始 / 暫停計時碼錶 |
| `Ctrl + 0` | 重置計時碼錶為 0 |
| `V` | 複製當前地圖筆記至剪貼板 |
| `Home` | 顯示 / 隱藏筆記面板 |

在懸浮視窗上**按右鍵**可開啟選單（複製筆記、重新載入筆記、離開程式）。

### 撰寫個人筆記

筆記以普通 `.txt` 文字檔存放在 `notes/` 資料夾中。  
請開啟 `notes/template_empty.txt` 查看完整格式說明。

**快速格式範例：**
```
[Map Name EN / 地圖名稱 ZH-TW]
{
在這裡寫筆記。
Boss 機制提醒、物品濾鏡關鍵字等。
}

[Another Map / 另一個地圖]
{
第二個地圖的筆記。
}
```

- 一個檔案可以包含任意數量的地圖區塊
- 以 `#` 開頭的行為註解，會被忽略
- 用 `/` 分隔不同語言的名稱 — 工具會自動比對你的 PoE2 客戶端語言
- `{ }` 內容為空代表已知此地圖但無筆記 → 懸浮視窗保持靜默

內附的 `notes/tip_with_050.txt` 是一份含有繁體中文 Act 筆記的範例檔案，可自由編輯或刪除。

### 常見問題

| 問題 | 解決方法 |
|------|----------|
| 懸浮視窗沒有出現 | 確認 PoE2 正在執行；懸浮視窗只在 PoE2 為前景視窗時顯示 |
| 進入地圖但筆記沒有顯示 | 確認 `Client.txt` 中的地圖名稱與 `.txt` 筆記檔案中的名稱一致 |
| 出現「python 找不到」錯誤 | 重新安裝 Python，並在安裝時勾選「Add Python to PATH」 |
| 出現套件相關錯誤 | 再次執行 `install.bat` |

### 授權

MIT License — 可自由使用、修改及分享。
