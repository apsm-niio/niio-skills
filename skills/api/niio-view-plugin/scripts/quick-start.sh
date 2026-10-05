#!/bin/bash

# niio檢視外掛快速啟動指令碼
# 用法: ./quick-start.sh [專案目錄]

set -e

echo "=== niio檢視外掛快速啟動 ==="
echo ""

if [ -z "$1" ]; then
    # 如果沒有指定專案目錄，查詢目前目錄下的專案
    PROJECT_DIR=$(find . -maxdepth 1 -type d -name "mdye_view_*" | head -1)

    if [ -z "$PROJECT_DIR" ]; then
        echo "❌ 未找到niio檢視外掛專案"
        echo ""
        echo "請先建立專案或指定專案目錄:"
        echo "  ./quick-start.sh 專案目錄"
        echo ""
        echo "或者使用完整初始化:"
        echo "  ./init-niio-view-project.sh"
        exit 1
    fi
else
    PROJECT_DIR="$1"
fi

# 檢查專案目錄是否存在
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ 專案目錄不存在: $PROJECT_DIR"
    exit 1
fi

echo "📁 專案目錄: $PROJECT_DIR"

# 檢查專案結構
echo ""
echo "1. 檢查專案結構..."
if [ ! -f "$PROJECT_DIR/package.json" ]; then
    echo "❌ 專案目錄中未找到package.json檔案"
    exit 1
fi

if [ ! -d "$PROJECT_DIR/src" ]; then
    echo "❌ 專案目錄中未找到src目錄"
    exit 1
fi

echo "✅ 專案結構檢查透過"

# 檢查依賴是否安裝
echo ""
echo "2. 檢查專案依賴..."
cd "$PROJECT_DIR" || {
    echo "❌ 無法進入專案目錄"
    exit 1
}

if [ ! -d "node_modules" ]; then
    echo "⚠️  未找到node_modules目錄，開始安裝依賴..."
    npm i

    if [ $? -ne 0 ]; then
        echo "❌ 依賴安裝失敗"
        exit 1
    fi
    echo "✅ 依賴安裝完成"
else
    echo "✅ 依賴已安裝"
fi

# 啟動開發伺服器
echo ""
echo "3. 啟動開發伺服器..."
echo "執行命令: mdye start"
echo ""
echo "🚀 開發伺服器正在啟動..."
echo "📱 請稍後在瀏覽器中訪問開發伺服器地址"
echo "🔄 支援熱過載和即時預覽"
echo ""

# 啟動mdye開發伺服器
mdye start

# 如果mdye start失敗，顯示錯誤資訊
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 開發伺服器啟動失敗"
    echo ""
    echo "🔧 故障排除建議:"
    echo "  1. 檢查埠是否被佔用"
    echo "  2. 檢查依賴是否完整: npm i"
    echo "  3. 檢查mdye-cli版本: mdye --version"
    echo "  4. 檢視詳細錯誤日誌"
    exit 1
fi