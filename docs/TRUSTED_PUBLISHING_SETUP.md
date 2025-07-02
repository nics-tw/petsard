# PyPI Trusted Publishing 設定指南

## 🎯 概述

PyPI Trusted Publishing 允許從 GitHub Actions 直接發布套件到 PyPI，無需使用 API tokens，提供更安全的發布流程。

## 📋 設定步驟

### 1. 在 PyPI 上設定 Trusted Publisher

1. 登入 [PyPI](https://pypi.org/) 作為套件擁有者
2. 前往你的套件管理頁面：`https://pypi.org/manage/project/petsard/`
3. 點擊 "Publishing" 標籤
4. 點擊 "Add a new pending publisher"
5. 填入以下資訊：
   - **Owner**: `nics-tw`
   - **Repository name**: `petsard`
   - **Workflow filename**: `semantic-release.yml`
   - **Environment name**: 留空 (除非你使用 GitHub Environment)

### 2. 在 TestPyPI 上設定 Trusted Publisher (可選)

1. 登入 [TestPyPI](https://test.pypi.org/)
2. 重複上述步驟

### 3. 驗證設定

設定完成後，下次發版時：
- ✅ 不再需要 `PYPI_API_TOKEN` 和 `TESTPYPI_API_TOKEN` secrets
- ✅ GitHub Actions 會自動使用 OIDC 認證
- ✅ 支援 attestations (套件完整性驗證)

## 🔧 GitHub Actions 變更

已更新 `.github/workflows/semantic-release.yml`：

```yaml
- name: Publish | Upload package to PyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  if: steps.release.outputs.released == 'true'
  with:
    skip-existing: true
    attestations: true
    # 使用 Trusted Publishing，移除 password 參數
```

## 🚨 重要注意事項

1. **首次設定**: 第一次使用 Trusted Publishing 時，PyPI 會自動建立套件 (如果不存在)
2. **權限**: 確保 GitHub Actions 有 `id-token: write` 權限 (已設定)
3. **安全性**: Trusted Publishing 比 API tokens 更安全，因為它使用短期的 OIDC tokens
4. **相容性**: 支援 PyPI 和 TestPyPI

## 🔍 故障排除

### 常見錯誤

1. **"No valid identity token found"**
   - 確認 `permissions.id-token: write` 已設定
   - 確認在 PyPI 上正確設定了 Trusted Publisher

2. **"Repository not configured for Trusted Publishing"**
   - 檢查 PyPI 上的 Publisher 設定
   - 確認 Owner、Repository name、Workflow filename 正確

3. **"Workflow not found"**
   - 確認 workflow 檔案名稱與 PyPI 設定一致
   - 確認 workflow 在 main 分支上存在

## 📚 參考資料

- [PyPI Trusted Publishers 官方文檔](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions PyPI Publish Action](https://github.com/pypa/gh-action-pypi-publish)
- [OpenID Connect in GitHub Actions](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)