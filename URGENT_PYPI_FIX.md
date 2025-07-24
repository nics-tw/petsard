# 🚨 緊急修復：PyPI v1.4.0 發布失敗

## 🎯 問題診斷

**發現問題**：
- ✅ v1.4.0 標籤已建立
- ✅ GitHub Release 已建立
- ❌ PyPI 發布失敗 (仍停留在 v1.3.1)
- ❌ GitHub Actions 在 "Upload package to TestPyPI" 步驟失敗

**根本原因**：
我們更改了 GitHub Actions 使用 Trusted Publishing，但還沒有在 PyPI 上設定 Trusted Publisher。

## 🔧 立即修復方案

### 選項 1：設定 Trusted Publishing (推薦)

1. **在 PyPI 設定 Trusted Publisher**：
   - 登入 [PyPI](https://pypi.org/) 
   - 前往 [petsard 專案管理](https://pypi.org/manage/project/petsard/)
   - 點擊 "Publishing" 標籤
   - 點擊 "Add a new pending publisher"
   - 填入：
     - **Owner**: `nics-tw`
     - **Repository name**: `petsard`
     - **Workflow filename**: `semantic-release.yml`
     - **Environment name**: 留空

2. **在 TestPyPI 設定 Trusted Publisher**：
   - 登入 [TestPyPI](https://test.pypi.org/)
   - 重複上述步驟

3. **重新觸發發布**：
   ```bash
   # 重新推送標籤以觸發 GitHub Actions
   git push origin --delete v1.4.0
   git tag -d v1.4.0
   git tag v1.4.0
   git push origin v1.4.0
   ```

### 選項 2：暫時回退到 API Token (快速修復)

如果需要立即發布，可以暫時回退：

```yaml
# 在 .github/workflows/semantic-release.yml 中
- name: Publish | Upload package to TestPyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  if: steps.release.outputs.released == 'true'
  with:
    repository-url: https://test.pypi.org/legacy/
    password: ${{ secrets.TESTPYPI_API_TOKEN }}
    skip-existing: true

- name: Publish | Upload package to PyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  if: steps.release.outputs.released == 'true'
  with:
    password: ${{ secrets.PYPI_API_TOKEN }}
    skip-existing: true
```

## 🚀 建議執行步驟

1. **立即執行**：設定 PyPI Trusted Publisher
2. **重新觸發發布**：重新推送 v1.4.0 標籤
3. **驗證結果**：確認 PyPI 上出現 v1.4.0

## 📋 檢查清單

- [ ] PyPI Trusted Publisher 已設定
- [ ] TestPyPI Trusted Publisher 已設定  
- [ ] 重新觸發 GitHub Actions
- [ ] 驗證 PyPI 上的 v1.4.0 版本
- [ ] 確認 GitHub Actions 執行成功

## 🔍 驗證指令

```bash
# 檢查 PyPI 最新版本
curl -s "https://pypi.org/pypi/petsard/json" | grep '"version"'

# 檢查 GitHub Actions 狀態
curl -s "https://api.github.com/repos/nics-tw/petsard/actions/runs?per_page=1"