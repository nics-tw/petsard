#!/usr/bin/env python3
"""
PETsARD 開發助手
自動檢查代碼修改與功能設計文檔的同步性
支援 GitHub Actions CI 模式
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


class DevelopmentAssistant:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.ai_dir = self.project_root / ".ai"

        # 模組與文檔的映射關係
        self.module_doc_map = {
            "petsard/loader/": "functional_design/loader.md",
            "petsard/metadater/": "functional_design/metadater.md",
            "petsard/evaluator/": "functional_design/evaluator.md",
            "petsard/processor/": "functional_design/processor.md",
            "petsard/synthesizer/": "functional_design/synthesizer.md",
            "petsard/reporter/": "functional_design/reporter.md",
            "petsard/constrainer/": "functional_design/constrainer.md",
            "petsard/executor/": "functional_design/executor.md",
            "petsard/operator/": "functional_design/operator.md",
            "petsard/config/": "functional_design/config.md",
        }

        # 架構規則檢查
        self.architecture_rules = {
            "petsard/loader/": [
                "確認 load() 方法回傳 tuple[pd.DataFrame, SchemaMetadata]",
                "檢查是否正確使用 Metadater.create_schema()",
                "驗證向後相容性",
            ],
            "petsard/metadater/": [
                "確認使用 @dataclass(frozen=True) 不可變設計",
                "檢查三層架構 (Metadata/Schema/Field) 完整性",
                "驗證純函數設計原則",
                "確認沒有依賴其他 PETsARD 模組",
            ],
            "petsard/evaluator/": [
                "確認新評估器繼承 BaseEvaluator",
                "檢查 _eval() 方法回傳格式一致性",
                "驗證是否正確使用 Metadater 進行資料處理",
            ],
        }

    def get_modified_files(
        self, base_ref: str = None, head_ref: str = "HEAD"
    ) -> list[str]:
        """獲取 git 中修改的文件"""
        try:
            # 在 CI 環境中使用不同的比較基準
            if os.getenv("GITHUB_ACTIONS"):
                # 在 GitHub Actions 中，使用 GITHUB_BASE_REF 作為比較基準
                github_base_ref = os.getenv("GITHUB_BASE_REF")
                if github_base_ref:
                    base_ref = f"origin/{github_base_ref}"
                else:
                    # 如果沒有 GITHUB_BASE_REF，回退到 main
                    base_ref = base_ref or "origin/main"

                cmd = [
                    "git",
                    "diff",
                    "--name-only",
                    "--diff-filter=ACM",
                    base_ref,
                    head_ref,
                ]
            else:
                # 本地開發環境：先檢查暫存區
                result = subprocess.run(
                    ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                )
                if result.returncode == 0 and result.stdout.strip():
                    return [
                        f
                        for f in result.stdout.strip().split("\n")
                        if f.endswith(".py")
                    ]

                # 如果沒有暫存區修改，檢查工作區修改
                cmd = ["git", "diff", "--name-only", "--diff-filter=ACM"]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            if result.returncode == 0:
                return [
                    f
                    for f in result.stdout.strip().split("\n")
                    if f and f.endswith(".py")
                ]

        except Exception as e:
            print(f"⚠️  無法獲取 git 修改文件: {e}")

        return []

    def check_modified_files(
        self, modified_files: list[str] | None = None
    ) -> dict[str, dict]:
        """檢查修改的文件並返回需要更新的文檔和規則"""
        if modified_files is None:
            modified_files = self.get_modified_files()

        docs_to_check = {}

        for file_path in modified_files:
            if file_path.endswith(".py"):
                for module_path, doc_path in self.module_doc_map.items():
                    if module_path in file_path:
                        docs_to_check[module_path] = {
                            "doc_path": doc_path,
                            "modified_files": docs_to_check.get(module_path, {}).get(
                                "modified_files", []
                            )
                            + [file_path],
                            "architecture_rules": self.architecture_rules.get(
                                module_path, []
                            ),
                        }
                        break

        return docs_to_check

    def check_api_changes(self, file_path: str) -> list[str]:
        """檢查文件中的 API 變更"""
        api_changes = []

        try:
            with open(self.project_root / file_path, encoding="utf-8") as f:
                content = f.read()

            # 簡單的 API 變更檢測
            if "class " in content and "def " in content:
                api_changes.append("檢測到類別或方法定義變更")

            if "@dataclass" in content:
                api_changes.append("檢測到資料類別變更")

            if "def __init__" in content:
                api_changes.append("檢測到建構函數變更")

        except Exception as e:
            api_changes.append(f"無法分析文件 {file_path}: {e}")

        return api_changes

    def generate_reminder_message(self, docs_to_check: dict[str, dict]) -> str:
        """生成提醒訊息"""
        if not docs_to_check:
            return "✅ 沒有檢測到需要檢查的模組修改"

        message = "🔔 **PETsARD 開發提醒**\n\n"
        message += "您修改了以下模組，請檢查對應的功能設計文檔是否需要更新：\n\n"

        for module_path, info in docs_to_check.items():
            doc_path = self.ai_dir / info["doc_path"]
            modified_files = info["modified_files"]
            architecture_rules = info["architecture_rules"]

            message += f"## 📁 模組: `{module_path}`\n\n"
            message += "**修改的文件**:\n"
            for file in modified_files:
                api_changes = self.check_api_changes(file)
                message += f"- `{file}`\n"
                if api_changes:
                    for change in api_changes:
                        message += f"  - ⚠️  {change}\n"

            message += f"\n**對應文檔**: [`{info['doc_path']}`]({doc_path})\n\n"

            if architecture_rules:
                message += "**架構檢查清單**:\n"
                for rule in architecture_rules:
                    message += f"- [ ] {rule}\n"
                message += "\n"

            # 檢查文檔是否存在
            if doc_path.exists():
                message += "📄 文檔存在，請檢查是否需要更新\n\n"
            else:
                message += "⚠️  **文檔不存在**，請創建對應的功能設計文檔\n\n"

        message += "---\n\n"
        message += "💡 **提醒事項**:\n"
        message += "1. 保持代碼與文檔同步是團隊協作的關鍵\n"
        message += "2. API 變更時請確保向後相容性\n"
        message += "3. 新增功能時請更新使用範例\n"
        message += "4. 重大架構變更請更新系統設計文檔\n\n"

        message += "🔗 **相關資源**:\n"
        message += f"- [開發流程文檔]({self.ai_dir / 'development-workflow.md'})\n"
        message += (
            f"- [專案上下文]({self.ai_dir / 'roo-config' / 'project-context.md'})\n"
        )
        message += (
            f"- [架構規則]({self.ai_dir / 'roo-config' / 'architecture-rules.md'})\n"
        )

        return message

    def generate_roo_prompt(self, docs_to_check: dict[str, dict]) -> str:
        """生成給 Roo 的提示訊息"""
        if not docs_to_check:
            return ""

        prompt = "請在協助開發時注意以下事項：\n\n"

        for module_path, info in docs_to_check.items():
            doc_path = self.ai_dir / info["doc_path"]

            prompt += f"正在修改 {module_path} 模組，請：\n"
            prompt += f"1. 參考 {doc_path} 中的功能設計\n"
            prompt += "2. 遵循既定的架構原則\n"

            if info["architecture_rules"]:
                prompt += "3. 特別注意以下架構規則：\n"
                for rule in info["architecture_rules"]:
                    prompt += f"   - {rule}\n"

            prompt += "\n"

        return prompt

    def save_analysis_result(self, docs_to_check: dict[str, dict]) -> None:
        """保存分析結果到文件"""
        result_file = self.ai_dir / "scripts" / "last_analysis.json"

        try:
            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "timestamp": str(
                            subprocess.run(
                                ["date"], capture_output=True, text=True
                            ).stdout.strip()
                        ),
                        "analysis": docs_to_check,
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
        except Exception as e:
            print(f"⚠️  無法保存分析結果: {e}")

    def check_compliance(
        self, docs_to_check: dict[str, dict], strict: bool = False
    ) -> bool:
        """檢查合規性"""
        compliance_issues = []

        for module_path, info in docs_to_check.items():
            # 檢查是否有對應的功能設計文檔
            doc_path = self.ai_dir / info["doc_path"]
            if not doc_path.exists():
                compliance_issues.append(f"模組 {module_path} 缺少功能設計文檔")

            # 檢查是否有測試檔案變更（嚴格模式）
            if strict:
                modified_files = info["modified_files"]
                test_files = [f for f in modified_files if f.startswith("tests/")]
                code_files = [f for f in modified_files if not f.startswith("tests/")]

                if code_files and not test_files:
                    compliance_issues.append(
                        f"模組 {module_path} 有代碼變更但沒有對應的測試更新"
                    )

        if compliance_issues:
            print("❌ 合規性檢查失敗:")
            for issue in compliance_issues:
                print(f"  - {issue}")
            return False

        print("✅ 合規性檢查通過")
        return True

    def generate_ci_report(
        self, docs_to_check: dict[str, dict], pr_number: str = None
    ) -> str:
        """生成 CI 報告"""
        if not docs_to_check:
            return """## 🎉 沒有檢測到 PETsARD 模組變更

此 PR 沒有修改核心模組，無需額外的架構檢查。

---
*由 AI 輔助開發系統自動生成*"""

        report = []
        report.append(f"檢測到 **{len(docs_to_check)}** 個模組有變更")
        report.append("")

        for module_path, info in docs_to_check.items():
            module_name = module_path.replace("petsard/", "").replace("/", "")
            report.append(f"### 🔄 `{module_name}` 模組")

            # 相關文檔
            doc_path = self.ai_dir / info["doc_path"]
            if doc_path.exists():
                report.append(
                    f"**📚 對應文檔**: [{info['doc_path']}]({info['doc_path']})"
                )
            else:
                report.append("**⚠️ 警告**: 此模組缺少功能設計文檔")

            # 變更檔案
            modified_files = info["modified_files"]
            report.append(f"**📝 變更檔案**: {len(modified_files)} 個")
            for file_path in modified_files[:5]:  # 只顯示前5個
                report.append(f"  - `{file_path}`")
            if len(modified_files) > 5:
                report.append(f"  - *... 還有 {len(modified_files) - 5} 個檔案*")

            # 架構檢查清單
            architecture_rules = info["architecture_rules"]
            if architecture_rules:
                report.append("**🔍 架構檢查清單**:")
                for rule in architecture_rules:
                    report.append(f"- [ ] {rule}")

            report.append("")

        report.append("## 🤖 AI 輔助開發建議")
        report.append("")
        report.append("1. **使用 Roo 時請載入相關的功能設計文檔**")
        report.append("2. **確保代碼變更與文檔保持同步**")
        report.append("3. **運行相關的測試確保功能正常**")
        report.append("4. **考慮向後相容性影響**")

        return "\n".join(report)


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="PETsARD 開發助手")
    parser.add_argument(
        "--mode",
        choices=["interactive", "report", "ci", "compliance"],
        default="interactive",
        help="執行模式",
    )
    parser.add_argument("--pr-number", help="PR 編號（CI 模式使用）")
    parser.add_argument("--strict", action="store_true", help="嚴格模式（合規性檢查）")
    parser.add_argument("files", nargs="*", help="要檢查的檔案列表")

    args = parser.parse_args()

    assistant = DevelopmentAssistant()

    # 獲取修改的檔案
    if args.files:
        modified_files = args.files
    else:
        modified_files = assistant.get_modified_files()

    # 分析修改的文件
    docs_to_check = assistant.check_modified_files(modified_files)

    if args.mode == "ci":
        # CI 模式：輸出 JSON 格式供 GitHub Actions 使用
        ci_data = {
            "has_changes": bool(docs_to_check),
            "modules": list(docs_to_check.keys()),
            "total_files": sum(
                len(info["modified_files"]) for info in docs_to_check.values()
            ),
        }
        print(json.dumps(ci_data))
        # CI 模式應該總是返回 0，除非發生錯誤
        return 0

    elif args.mode == "report":
        # 報告模式：生成 Markdown 報告
        report = assistant.generate_ci_report(docs_to_check, args.pr_number)
        print(report)
        return 0  # 報告模式總是成功

    elif args.mode == "compliance":
        # 合規性檢查模式
        is_compliant = assistant.check_compliance(docs_to_check, args.strict)
        sys.exit(0 if is_compliant else 1)

    else:
        # 互動模式（原有功能）
        # 生成提醒訊息
        reminder = assistant.generate_reminder_message(docs_to_check)
        print(reminder)

        # 生成 Roo 提示
        roo_prompt = assistant.generate_roo_prompt(docs_to_check)
        if roo_prompt:
            print("\n" + "=" * 50)
            print("🤖 Roo 開發提示:")
            print("=" * 50)
            print(roo_prompt)

        # 保存分析結果
        assistant.save_analysis_result(docs_to_check)

    return len(docs_to_check)


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
