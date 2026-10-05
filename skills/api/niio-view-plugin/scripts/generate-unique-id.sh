#!/bin/bash

# 生成唯一的專案ID字尾
# 用法: ./generate-unique-id.sh [字首]

# 字首應為你自己的 worksheet/應用 ID（從niio取得），透過參數傳入
PREFIX="${1:-你的worksheetID}"
TIMESTAMP=$(date +%s)
RANDOM_SUFFIX=$(openssl rand -hex 4 2>/dev/null || echo $RANDOM)

# 組合生成唯一ID
UNIQUE_ID="${PREFIX}-${TIMESTAMP}-${RANDOM_SUFFIX}"

echo "生成的唯一外掛ID: $UNIQUE_ID"
echo "建議的專案目錄名: mdye_view_${TIMESTAMP}_${RANDOM_SUFFIX}"