# 持久進度狀態

以 build/scripts/build_checkpoint.py 為唯一進度寫入入口，操作方式見 build/SKILL.md。buildState.version=1；steps 包含 1、2、3、4、5、6、5b、7、8、9、10、11、12；每步 status 為 pending、running 或 done，done 必須附 evidence。

| 完成步驟 | progress |
|---|---|
| 1 | app_created |
| 2 | worksheets_created |
| 3 | fields_refreshed |
| 4 | actions_created |
| 5 | views_created |
| 6 | sample_data_created |
| 5b | page_shells_created |
| 7、8、9 全部 | config_completed |
| 10、11 全部 | workflows_deployed |
| 12 | completed |

只按上表順序執行。7/8/9 與 10/11 各自有落盤狀態，不使用記憶體判斷；其中已完成者恢復後不重跑。views_created 下一步為 6。completed 不派發新步驟。未知狀態、failed、跳步及 progress 與檢查點不一致時停止核對；不得直接清空進度。

begin 在呼叫工具前落盤；finish 在實際產物驗證後原子保存步驟證據與 progress。中斷保留 running，不自動重試，不寫 failed 覆蓋最後成功進度。退出碼及部分完成核對方式見 build/SKILL.md。
