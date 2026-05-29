# POE2 Overlay Timer

**Language / 語言：** [English](#english) | [繁體中文](#繁體中文)

---

## English

A lightweight always-on-top Windows overlay for **Path of Exile 2** players.

Enter a map → the overlay automatically shows the notes you wrote for it. Scales to any screen resolution. One key copies the text to clipboard — handy for pasting your loot filter regex in town, or sharing boss tips with your party. A freely togglable stopwatch is always visible on top.

### How it works

- Reads PoE2's own `logs/Client.txt` — **read-only, no injection, no packet sniffing**
- You write notes for each map in plain `.txt` files inside the `notes/` folder
- When you enter a map the matching notes pop up in the overlay automatically
- When you alt-tab to a browser or Discord the overlay hides itself so it never blocks your screen

Just like Awakened PoE Trade and TradeMacro, this tool reads the Client log only. **GGG explicitly permits this kind of tool.**

### Features

- Floating stopwatch that **auto-pauses** when PoE2 loses focus and **auto-resumes** when you switch back
- Detects which **map / area** you just entered by reading `Client.txt`
- Displays your **personal notes** for that map in the overlay
- Press **V** to copy the notes straight to clipboard — paste into Discord, party chat, etc.
- Semi-transparent, draggable, stays on top of the game

### Screenshots

<img width="1369" height="945" alt="image" src="https://github.com/user-attachments/assets/e195e06d-e333-493d-97ac-d296b6399012" />


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

### Right-click Menu

Right-click anywhere on the overlay to open the context menu.

| Option | Action |
|--------|--------|
| Copy notes `[V]` | Copy the current map's notes to clipboard |
| Note files ▶ | Switch which notes `.txt` file is active (radio select) |
| Reload all notes | Re-read all `.txt` files from disk without restarting |
| Exit | Close the overlay |

The **Note files** submenu lists every `.txt` in your `notes/` folder. A filled dot `●` marks the currently active file; an empty dot `○` means inactive. Click a file to activate it exclusively — click it again to go back to loading all files.

### Fullscreen Mode

> **Recommended:** Run PoE2 in **Windowed Fullscreen (Borderless)** mode.

The overlay is designed to sit on top of PoE2 without stealing focus, so clicking or dragging it will not minimize the game. However, if PoE2 is running in **true exclusive fullscreen** (not borderless), some Windows versions may still minimize the game on interaction. Switching to Borderless Windowed in PoE2's display settings eliminates this completely.

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

The included `notes/tip_with_050.txt` is a sample file with Traditional Chinese act notes, and `notes/tip_with_050_EN.txt` is the English version. You can edit or delete them freely.

**Switching between note files:** Move any `.txt` file into `notes/disabled/` to deactivate it — the tool ignores that subfolder. Move it back to `notes/` to re-enable it. No restart needed; use *Reload notes* in the right-click menu.

```
notes/
    tip_with_050_EN.txt   ← active
    disabled/
        tip_with_050.txt  ← inactive (move here to disable)
```

### Troubleshooting

| Problem | Solution |
|---------|----------|
| Overlay doesn't appear | Make sure PoE2 is running; the overlay only shows when PoE2 is focused |
| Notes don't show for a map | Check the map name in `Client.txt` matches what's in your `.txt` note file |
| `python` not found error | Re-install Python and tick "Add Python to PATH" |
| Dependencies error | Run `install.bat` again |

### License

MIT License — free to use, modify, and share.

### Acknowledgements

- **蒼** (original concept & [original post](https://forum.gamer.com.tw/C.php?bsn=82273&snA=3119&tnum=2) on Bahamut) — [profile](https://home.gamer.com.tw/profile/index.php?owner=gsm902127)
- **小貓** (contributed `tip_with_050.txt` sample notes) — [profile](https://home.gamer.com.tw/profile/index.php?owner=pquint)

---

## 繁體中文

一個輕量的 Windows 懸浮視窗工具，專為 **流亡黯道 2（Path of Exile 2）** 玩家設計。

進地圖時，自動彈出你針對該地圖寫的筆記與小提醒，自適應螢幕解析度。一鍵複製文字貼到剪貼板，適合在城鎮貼上篩選正則、或提示隊友 Boss 機制。附有始終置頂、可自由開關的計時碼錶。

### 工作原理

- 讀取 PoE2 產生的 `logs/Client.txt`（**純讀檔、不注入、不抓封包**）
- 你在 `notes/` 資料夾的 `.txt` 檔案中，為每張地圖寫好筆記
- 進地圖時自動比對地圖名稱，將對應內容顯示在懸浮視窗
- 切換到其他程式（瀏覽器 / Discord）時自動隱藏，不擋畫面

與 Awakened PoE Trade、TradeMacro 相同，本工具只讀取 Client log，**GGG 公開允許此類工具**。

### 功能特色

- 懸浮計時碼錶，切離遊戲視窗時**自動暫停**，切回後**自動繼續**
- 透過讀取 `Client.txt` 自動偵測你進入的**地圖 / 地區**
- 在懸浮視窗中顯示你為該地圖寫的**個人筆記**
- 按 **V** 直接將筆記複製到剪貼板 — 方便貼到 Discord 或隊伍聊天
- 半透明、可拖曳、永遠置頂顯示於遊戲上方

### 截圖

<img width="1369" height="945" alt="image" src="https://github.com/user-attachments/assets/e195e06d-e333-493d-97ac-d296b6399012" />

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

### 右鍵選單

在懸浮視窗任意位置**按右鍵**即可開啟選單。

| 選項 | 功能 |
|------|------|
| 複製筆記 `[V]` | 將當前地圖筆記複製至剪貼板 |
| Note files ▶ | 切換使用哪個筆記 `.txt` 檔案（單選模式） |
| Reload all notes | 重新從硬碟讀取所有 `.txt` 檔案，不需重啟程式 |
| Exit | 關閉懸浮視窗 |

**Note files** 子選單會列出 `notes/` 資料夾中所有的 `.txt` 檔案。實心點 `●` 代表目前啟用的檔案，空心點 `○` 代表未啟用。點選某個檔案即可單獨啟用；再次點選則恢復為載入全部檔案。

### 全螢幕模式

> **建議：** 在 PoE2 的顯示設定中使用 **視窗化全螢幕（無邊框）** 模式。

本工具在設計上不會搶奪焦點，因此點擊或拖曳懸浮視窗時不會導致遊戲最小化。但若 PoE2 以**獨佔全螢幕**模式運行（非無邊框），部分 Windows 版本仍可能在互動時最小化遊戲。切換為無邊框視窗模式可完全避免此問題。

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

內附的 `notes/tip_with_050.txt` 為繁體中文版 Act 筆記範例，`notes/tip_with_050_EN.txt` 為英文版，可自由編輯或刪除。

**切換筆記檔案：** 將任何 `.txt` 檔案移入 `notes/disabled/` 資料夾即可停用，工具不會讀取該子資料夾。移回 `notes/` 即重新啟用。不需重啟，在右鍵選單選「重新載入筆記」即可。

```
notes/
    tip_with_050_EN.txt    ← 啟用中
    disabled/
        tip_with_050.txt   ← 停用（移到這裡即可關閉）
```

### 鳴謝

- **蒼**（原始構想 & [原帖](https://forum.gamer.com.tw/C.php?bsn=82273&snA=3119&tnum=2)，巴哈姆特）— [個人頁面](https://home.gamer.com.tw/profile/index.php?owner=gsm902127)
- **小貓**（提供 `tip_with_050.txt` 範例筆記）— [個人頁面](https://home.gamer.com.tw/profile/index.php?owner=pquint)

### 常見問題

| 問題 | 解決方法 |
|------|----------|
| 懸浮視窗沒有出現 | 確認 PoE2 正在執行；懸浮視窗只在 PoE2 為前景視窗時顯示 |
| 進入地圖但筆記沒有顯示 | 確認 `Client.txt` 中的地圖名稱與 `.txt` 筆記檔案中的名稱一致 |
| 出現「python 找不到」錯誤 | 重新安裝 Python，並在安裝時勾選「Add Python to PATH」 |
| 出現套件相關錯誤 | 再次執行 `install.bat` |

### 授權

MIT License — 可自由使用、修改及分享。
