#!/usr/bin/env python3
"""
Coverage Report Generator
生成簡單易懂的測試覆蓋率報告
"""

import os
import sys
import xml.etree.ElementTree as ET


def parse_coverage_xml(xml_file):
    """解析 coverage.xml 文件"""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # 獲取整體覆蓋率
        line_rate = float(root.attrib.get("line-rate", 0))
        overall_coverage = line_rate * 100

        # 獲取各個包的覆蓋率
        packages = []
        for package in root.findall(".//package"):
            package_name = package.attrib.get("name", "Unknown")
            package_line_rate = float(package.attrib.get("line-rate", 0))
            package_coverage = package_line_rate * 100

            # 獲取類別覆蓋率
            classes = []
            for cls in package.findall(".//class"):
                class_name = cls.attrib.get("name", "Unknown")
                class_filename = cls.attrib.get("filename", "Unknown")
                class_line_rate = float(cls.attrib.get("line-rate", 0))
                class_coverage = class_line_rate * 100

                classes.append(
                    {
                        "name": class_name,
                        "filename": class_filename,
                        "coverage": class_coverage,
                    }
                )

            packages.append(
                {"name": package_name, "coverage": package_coverage, "classes": classes}
            )

        return {"overall_coverage": overall_coverage, "packages": packages}
    except Exception as e:
        print(f"Error parsing coverage.xml: {e}")
        return None


def get_coverage_grade(coverage):
    """根據覆蓋率返回等級"""
    if coverage >= 90:
        return "🎉 優秀 (Excellent)", "green"
    elif coverage >= 80:
        return "✅ 良好 (Good)", "yellow"
    elif coverage >= 70:
        return "⚠️ 尚可 (Fair)", "orange"
    else:
        return "❌ 需改進 (Needs Improvement)", "red"


def generate_markdown_report(coverage_data):
    """生成 Markdown 格式的覆蓋率報告"""
    if not coverage_data:
        return "❌ 無法生成覆蓋率報告 (Unable to generate coverage report)"

    overall_coverage = coverage_data["overall_coverage"]
    grade, color = get_coverage_grade(overall_coverage)

    report = []
    report.append("## 📊 測試覆蓋率報告 Test Coverage Report")
    report.append("")
    report.append("### 🎯 整體覆蓋率 Overall Coverage")
    report.append(f"**{overall_coverage:.1f}%** - {grade}")
    report.append("")

    # 覆蓋率解讀
    report.append("### 📖 覆蓋率解讀 Coverage Explanation")
    report.append("- **90%+**: 🎉 優秀 - 測試覆蓋非常完整")
    report.append("- **80-89%**: ✅ 良好 - 測試覆蓋良好，可考慮增加邊界測試")
    report.append("- **70-79%**: ⚠️ 尚可 - 建議增加更多測試案例")
    report.append("- **<70%**: ❌ 需改進 - 強烈建議增加測試覆蓋")
    report.append("")

    # 模組詳細覆蓋率
    if coverage_data["packages"]:
        report.append("### 📁 模組覆蓋率詳情 Module Coverage Details")
        report.append("")

        for package in coverage_data["packages"]:
            package_grade, _ = get_coverage_grade(package["coverage"])
            report.append(f"#### 📦 {package['name']}")
            report.append(f"**覆蓋率**: {package['coverage']:.1f}% - {package_grade}")
            report.append("")

            if package["classes"]:
                report.append("| 文件 File | 覆蓋率 Coverage | 狀態 Status |")
                report.append("|-----------|----------------|-------------|")

                for cls in package["classes"]:
                    filename = os.path.basename(cls["filename"])
                    cls_grade, _ = get_coverage_grade(cls["coverage"])
                    report.append(
                        f"| `{filename}` | {cls['coverage']:.1f}% | {cls_grade} |"
                    )

                report.append("")

    # 改進建議
    if overall_coverage < 80:
        report.append("### 💡 改進建議 Improvement Suggestions")
        report.append("")
        if overall_coverage < 70:
            report.append("- 🚨 **緊急**: 覆蓋率過低，請優先增加基本功能測試")
            report.append("- 📝 建議為每個公開方法編寫至少一個測試案例")
            report.append(
                "- 🔍 使用 `pytest --cov-report=html` 生成詳細報告查看未覆蓋代碼"
            )
        else:
            report.append("- 📈 建議增加邊界條件和異常情況的測試")
            report.append("- 🧪 考慮增加整合測試覆蓋更多使用場景")
            report.append("- 🎯 專注於提升核心模組的測試覆蓋率")
        report.append("")

    return "\n".join(report)


def main():
    """主函數"""
    if len(sys.argv) != 2:
        print("Usage: python coverage_report.py <coverage.xml>")
        sys.exit(1)

    xml_file = sys.argv[1]
    if not os.path.exists(xml_file):
        print(f"Error: {xml_file} not found")
        sys.exit(1)

    coverage_data = parse_coverage_xml(xml_file)
    report = generate_markdown_report(coverage_data)
    print(report)


if __name__ == "__main__":
    main()
