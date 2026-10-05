#!/bin/bash

# 測試mdye-cli檢查邏輯的演示指令碼

echo "=== mdye-cli 檢查演示 ==="
echo ""

# 檢查mdye-cli是否安裝
if command -v mdye &> /dev/null; then
    MDYE_VERSION=$(mdye --version 2>/dev/null || echo "未知版本")
    echo "✅ mdye-cli 已安裝"
    echo "   版本: $MDYE_VERSION"
    echo ""
    echo "可以直接使用以下命令："
    echo "  mdye init view --id 外掛ID --template React"
else
    echo "❌ mdye-cli 未安裝"
    echo ""
    echo "需要先安裝 mdye-cli："
    echo ""

    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  # macOS系統"
        echo "  sudo npm install -g mdye-cli"
    else
        echo "  # Windows/Linux系統"
        echo "  npm install -g mdye-cli"
    fi

    echo ""
    echo "安裝完成後，使用以下命令驗證："
    echo "  mdye --version"
fi

echo ""
echo "=== 演示結束 ==="