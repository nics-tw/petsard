# AI-Assisted Development Documentation

This directory contains the complete AI-assisted development framework for PETsARD, including functional design documentation, development workflow automation, and Roo integration.

## 🎯 Overview

The `.ai/` directory provides:
- **Functional Design Documentation**: Current implementation reference for all modules
- **Development Workflow Automation**: Tools to ensure code-documentation synchronization
- **Roo Integration**: AI assistant configuration for consistent development practices
- **Architecture Enforcement**: Automated checks for design principle compliance

## 📁 Directory Structure

```
.ai/
├── README.md                    # This overview document
├── SETUP-GUIDE.md              # Quick setup guide for developers
├── development-workflow.md      # Detailed development process documentation
├── roo-config/                  # Roo AI assistant configuration
│   ├── project-context.md       # Project context and architecture principles
│   └── architecture-rules.md    # Architecture rules and development reminders
├── functional_design/           # Module functional design documents
│   ├── system.md               # Overall system architecture
│   ├── loader.md               # Data loading module design
│   ├── metadater.md            # Metadata management core design
│   ├── evaluator.md            # Evaluation module design
│   ├── processor.md            # Data processing module design
│   ├── synthesizer.md          # Data synthesis module design
│   ├── reporter.md             # Reporting module design
│   ├── constrainer.md          # Data constraint module design
│   ├── executor.md             # Execution orchestration design
│   ├── operator.md             # Data operation module design
│   └── config.md               # Configuration module design
├── scripts/                     # Development automation scripts
│   ├── development-assistant.py # Code-documentation sync checker
│   └── pre-commit-hook.sh       # Git pre-commit hook
└── templates/                   # Development templates
    ├── module-template.md       # New module development template
    ├── api-design-template.md   # API design template
    └── documentation-template.md # Documentation update template
```

## 🚀 Quick Start

### For New Developers

1. **Setup Development Environment**:
   ```bash
   # Follow the setup guide
   cat .ai/SETUP-GUIDE.md
   
   # Install pre-commit hook
   cp .ai/scripts/pre-commit-hook.sh .git/hooks/pre-commit
   chmod +x .git/hooks/pre-commit
   ```

2. **Configure Roo**:
   - Roo will automatically load `.roo/project.yaml`
   - Context files in `.ai/roo-config/` will be auto-loaded
   - Functional design documents will be referenced as needed

3. **Start Development**:
   ```
   # In Roo
   "我要修改 [模組名稱]，請載入相關的功能設計文檔"
   ```

### For Existing Developers

The development workflow now includes:
- **Automatic Documentation Sync**: Pre-commit hooks check code-documentation alignment
- **Architecture Compliance**: Automated checks for design principle adherence
- **AI-Assisted Development**: Roo integration with project-specific context

## 🔧 Key Features

### 1. Automated Code-Documentation Synchronization
- **Pre-commit Hooks**: Automatically check if functional design docs need updates
- **Development Assistant**: Python script that analyzes code changes and suggests documentation updates
- **Architecture Compliance**: Ensures adherence to established design patterns

### 2. Roo AI Assistant Integration
- **Project Context Loading**: Automatically loads architecture principles and coding standards
- **Module-Specific Guidance**: Provides targeted assistance based on which module is being modified
- **Architecture Rule Enforcement**: Reminds developers of module-specific design constraints

### 3. Comprehensive Documentation
- **Current Implementation Reference**: All docs reflect actual codebase state
- **Architecture Guidelines**: Clear principles for maintaining system consistency
- **Development Best Practices**: Standardized approaches for common development tasks

## 📋 Development Workflow

### Daily Development Process

1. **Before Coding**:
   ```
   # Roo automatically loads relevant functional design docs
   "我要修改 evaluator 模組，請載入相關設計文檔"
   ```

2. **During Development**:
   - Roo provides context-aware assistance
   - Architecture rules are automatically enforced
   - API consistency is maintained

3. **Before Committing**:
   ```bash
   git add .
   git commit -m "feat(evaluator): 新增隱私評估器"
   # Pre-commit hook automatically checks documentation sync
   ```

### Architecture Principles Enforced

- **Module Separation**: Clear boundaries between modules
- **Functional Programming**: Pure functions and immutable data structures
- **Type Safety**: Complete type annotations for all public APIs
- **Backward Compatibility**: API stability maintenance
- **Unified Interfaces**: Consistent patterns across modules

## 🎯 Benefits

### For Individual Developers
- **Faster Onboarding**: Complete context available through AI assistant
- **Consistent Development**: Automated enforcement of coding standards
- **Reduced Errors**: Architecture compliance checks prevent common mistakes

### For Team Collaboration
- **Synchronized Documentation**: Code and docs always stay in sync
- **Unified Architecture**: All developers follow the same design principles
- **Knowledge Sharing**: Functional design docs capture institutional knowledge

### for Project Maintenance
- **Living Documentation**: Docs automatically stay current with code
- **Architecture Integrity**: Systematic enforcement of design decisions
- **Quality Assurance**: Automated checks for common architectural violations

## 📖 Usage Examples

### Modifying Existing Modules
```
Developer: "我要在 loader 模組新增 Excel 支援"

Roo (auto-loads .ai/functional_design/loader.md):
"根據 loader 模組設計，新功能需要：
1. 繼承 LoaderBase
2. 實現統一的 load() 介面
3. 回傳 (data, metadata) 元組
4. 使用 Metadater 生成詮釋資料
我會確保遵循現有架構..."
```

### Adding New Evaluators
```
Developer: "我要新增一個機器學習效用評估器"

Roo (auto-loads .ai/functional_design/evaluator.md):
"新的評估器需要：
1. 繼承 BaseEvaluator
2. 實現 _eval() 方法
3. 回傳 dict[str, pd.DataFrame] 格式
4. 在 EvaluatorMap 中註冊
讓我幫您實現符合架構的評估器..."
```

## 🔗 Related Resources

- **[Setup Guide](.ai/SETUP-GUIDE.md)**: Quick start for new developers
- **[Development Workflow](.ai/development-workflow.md)**: Detailed process documentation
- **[Project Context](.ai/roo-config/project-context.md)**: Architecture principles and standards
- **[Architecture Rules](.ai/roo-config/architecture-rules.md)**: Specific compliance requirements

## 📞 Support

For questions about the AI-assisted development framework:
1. Check the [Setup Guide](.ai/SETUP-GUIDE.md) for common issues
2. Review the [Development Workflow](.ai/development-workflow.md) for detailed processes
3. Consult the functional design docs for module-specific guidance

---

🎉 **Welcome to AI-Assisted PETsARD Development!**

This framework ensures consistent, high-quality development while maintaining architectural integrity across the entire team.