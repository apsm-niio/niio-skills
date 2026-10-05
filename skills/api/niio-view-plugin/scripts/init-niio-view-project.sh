#!/bin/bash

# niio檢視外掛專案初始化指令碼
# 用法: ./init-niio-view-project.sh [專案名稱]

set -e

echo "=== niio檢視外掛專案初始化 ==="
echo ""

# 檢查Node.js版本
echo "1. 檢查Node.js版本..."
NODE_VERSION=$(node --version 2>/dev/null | cut -d'v' -f2)
if [ -z "$NODE_VERSION" ]; then
    echo "❌ 未檢測到Node.js，請先安裝Node.js 16.20或更高版本"
    exit 1
fi

REQUIRED_VERSION="16.20"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$NODE_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Node.js版本過低，目前版本: $NODE_VERSION，需要版本: $REQUIRED_VERSION 或更高"
    exit 1
fi
echo "✅ Node.js版本檢查透過: $NODE_VERSION"

# 檢查mdye-cli是否安裝
echo ""
echo "2. 檢查mdye-cli工具..."
if command -v mdye &> /dev/null; then
    # 已安裝，顯示版本
    MDYE_VERSION=$(mdye --version 2>/dev/null || echo "未知版本")
    echo "✅ mdye-cli已安裝，版本: $MDYE_VERSION"
else
    # 未安裝，詢問使用者是否安裝
    echo "❌ mdye-cli未安裝"
    echo ""
    echo "要安裝mdye-cli，請執行以下命令："
    echo ""

    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  # macOS系統"
        echo "  sudo npm install -g mdye-cli"
    else
        echo "  # Windows/Linux系統"
        echo "  npm install -g mdye-cli"
    fi

    echo ""
    echo "安裝完成後，請重新執行此指令碼。"
    echo ""
    echo "或者，您希望我現在為您安裝嗎？(y/N)"
    read -r INSTALL_CHOICE

    if [[ "$INSTALL_CHOICE" =~ ^[Yy]$ ]]; then
        echo "開始安裝mdye-cli..."

        if [[ "$OSTYPE" == "darwin"* ]]; then
            echo "檢測到macOS系統，使用sudo安裝..."
            sudo npm install -g mdye-cli
        else
            echo "檢測到其他系統，直接安裝..."
            npm install -g mdye-cli
        fi

        # 驗證安裝
        if command -v mdye &> /dev/null; then
            MDYE_VERSION=$(mdye --version 2>/dev/null || echo "未知版本")
            echo "✅ mdye-cli安裝成功，版本: $MDYE_VERSION"
        else
            echo "❌ mdye-cli安裝失敗"
            echo "請手動安裝: npm install -g mdye-cli"
            exit 1
        fi
    else
        echo "請先安裝mdye-cli，然後重新執行此指令碼。"
        exit 1
    fi
fi

# 生成專案名稱
echo ""
echo "3. 生成專案設定..."
if [ -n "$1" ]; then
    PROJECT_NAME="$1"
    echo "使用自訂專案名稱: $PROJECT_NAME"
else
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    RANDOM_SUFFIX=$(openssl rand -hex 3 2>/dev/null || echo $RANDOM)
    PROJECT_NAME="hap_view_${TIMESTAMP}_${RANDOM_SUFFIX}"
    echo "生成專案名稱: $PROJECT_NAME"
fi

# 生成外掛ID（PREFIX 請替換為你自己的 worksheet/應用 ID，可由環境變數傳入）
PREFIX="${PREFIX:-你的worksheetID}"
PLUGIN_ID="${PREFIX}-$(date +%s)-$(openssl rand -hex 4 2>/dev/null || echo $RANDOM)"
echo "生成外掛ID: $PLUGIN_ID"

# 建立專案
echo ""
echo "4. 建立專案..."
echo "執行命令: mdye init view --id $PLUGIN_ID --template React"
mdye init view --id "$PLUGIN_ID" --template React

# 檢查專案是否建立成功
if [ ! -d "mdye_view_${PLUGIN_ID##*-}" ]; then
    echo "❌ 專案建立失敗"
    exit 1
fi

PROJECT_DIR="mdye_view_${PLUGIN_ID##*-}"
echo "✅ 專案建立成功，目錄: $PROJECT_DIR"

# 進入專案目錄
echo ""
echo "5. 進入專案目錄..."
cd "$PROJECT_DIR" || {
    echo "❌ 無法進入專案目錄"
    exit 1
}
echo "目前目錄: $(pwd)"

# 安裝依賴
echo ""
echo "6. 安裝專案依賴..."
echo "執行命令: npm i"
npm i

if [ $? -ne 0 ]; then
    echo "⚠️  依賴安裝可能存在問題，請檢查網路或npm設定"
    echo "建議:"
    echo "  1. 檢查網路連線"
    echo "  2. 清理npm快取: npm cache clean --force"
    echo "  3. 使用淘寶映象: npm config set registry https://registry.npmmirror.com"
fi

# 顯示專案資訊
echo ""
echo "=== 專案初始化完成 ==="
echo ""
echo "📁 專案資訊:"
echo "  專案名稱: $PROJECT_NAME"
echo "  外掛ID: $PLUGIN_ID"
echo "  專案目錄: $PROJECT_DIR"
echo "  模板型別: React基礎示例"
echo ""
echo "🚀 啟動專案:"
echo "  cd $PROJECT_DIR"
echo "  mdye start"
echo ""
echo "🔧 常用命令:"
echo "  mdye start          # 啟動開發伺服器"
echo "  mdye build          # 建置專案"
echo "  npm run lint        # 程式碼檢查"
echo "  npm test           # 執行測試"
echo ""
echo "📚 專案結構:"
echo "  src/               # 原始碼目錄"
echo "    index.jsx        # 外掛入口"
echo "    App.jsx          # 主元件"
echo "    styles.css       # 樣式檔案"
echo "  public/            # 靜態資源"
echo "  package.json       # 專案設定"
echo ""
echo "💡 下一步:"
echo "  1. 進入專案目錄: cd $PROJECT_DIR"
echo "  2. 啟動開發伺服器: mdye start"
echo "  3. 在瀏覽器中訪問開發伺服器地址"
echo "  4. 開始開發你的niio檢視外掛"
echo ""
echo "⚠️  注意事項:"
echo "  - 確保使用唯一的外掛ID"
echo "  - 開發前請閱讀niio外掛開發文件"
echo "  - 定期備份重要程式碼"
echo ""
echo "🎉 祝你開發順利！"