# 吉祥号海报生成器 (Lucky Number Poster Generator)

这是一个基于 AI 的自动化工具，旨在从一个包含众多号码的 Excel 表格中，智能筛选出具有“吉祥”寓意的号码，并为之自动生成精美的营销海报。项目在开发过程中深度借助了 AI 编程助手（如 Codex 和 Claude）来辅助代码编写和逻辑实现。

## 核心功能

*   **智能号码筛选**: 能够根据预设规则（可能包括数字组合、谐音、特殊纪念日等）从 `吉祥号码.xlsx` 文件中自动挑选号码。
*   **AI 文案生成**: 利用 `openai` 库，为选出的号码自动生成富有吸引力的营销文案。
*   **自动化海报设计**: 使用 `Pillow` 库，将号码、AI 生成的文案、以及可能的节日主题元素合成为一张完整的海报图片。
*   **节日主题集成**: `holidays_util.py` 的存在表明，程序能够识别节假日，并可能在海报上添加相关主题元素，增强时效性。
*   **Web 应用界面**: 通过 `Flask` 框架提供一个简单的网页界面 (`web_app.py` 和 `templates/index.html`)，方便用户交互和触发海报生成。
*   **状态追踪**: `used_numbers.json` 用于记录已经使用过的号码，确保每次生成的都是新号码，避免重复。

## 技术栈

*   **核心逻辑**: Python 3
*   **数据处理**: `pandas`, `openpyxl` (用于读写 Excel 文件)
*   **图像处理**: `Pillow` (PIL)
*   **Web 框架**: `Flask`
*   **AI 服务**: `openai`
*   **日期与节日**: `holidays`, `pytz`
*   **定时任务**: `APScheduler` (可能用于定时自动生成)

## 工作流程

1.  **加载数据**: `data_loader.py` 启动，使用 `pandas` 读取 `吉祥号码.xlsx` 中的数据。
2.  **筛选号码**: `selection.py` 中的逻辑被调用，根据特定算法挑选出一个“吉祥号”。
3.  **生成文案**: `ai_copy.py` 连接 OpenAI API，将选定的号码发送给 AI 模型，获取一段创意的描述文案。
4.  **生成海报**: `poster_generator.py` 或其更高版本 (`poster_generator_v2.py`) 作为核心的图像引擎，它创建一个画布，将号码、文案、以及 `holidays_util.py` 提供的节日信息绘制到海报模板上。
5.  **保存与记录**: 生成的海报图片被保存到 `output/` 目录下，同时 `used_storage.py` 会更新 `used_numbers.json` 文件，将刚使用的号码记录在案。
6.  **前端展示 (可选)**: 如果通过 Web 界面操作，`web_app.py` 会调用以上流程，并在 `index.html` 页面上展示结果或提供操作按钮。

## 文件结构说明

```
luck/
├── 吉祥号码.xlsx           # 数据源：存储待选的号码
├── main.py                 # 主程序入口（可能用于命令行操作）
├── web_app.py              # Flask Web 应用的后端逻辑
├── start_web.bat           # 在 Windows 上一键启动 Web 服务的脚本
├── requirements.txt        # Python 依赖库列表
├── used_numbers.json       # 已使用的号码记录，防止重复
├── app/                    # 核心应用逻辑目录
│   ├── data_loader.py      # 数据加载模块
│   ├── selection.py        # 号码筛选算法
│   ├── ai_copy.py          # AI 文案生成模块
│   ├── poster_generator.py # 海报生成模块
│   ├── holidays_util.py    # 节假日工具
│   └── used_storage.py     # 已用号码的存储管理
├── output/                 # 存放生成的海报图片
│   └── 20251006_1146.jpg   # 海报示例
└── templates/
    └── index.html          # Web 界面的 HTML 模板
```

## 如何运行

1.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **配置**:
    检查 `app/config.py` 文件，确保 OpenAI API 密钥等配置正确。
3.  **运行 Web 应用**:
    直接双击 `start_web.bat` 文件，或在命令行中运行：
    ```bash
    python web_app.py
    ```
    然后浏览器访问 `http://127.0.0.1:5000` (或其他指定端口)。
4.  **直接生成 (如果支持)**:
    ```bash
    python main.py
    ```

## 开发历程

本项目的许多核心模块，从文件读取到图像合成，再到与 OpenAI API 的交互，其初始代码框架和关键逻辑都是在与 **Codex** 和 **Claude** 等大型语言模型的对话中逐步构建和完善的。AI 极大地加速了从想法到实现的过程，尤其是在快速原型设计和解决特定技术问题方面提供了巨大帮助。

## 效果展示

程序运行后，会在 `output` 文件夹内生成如下风格的海报：

*(请在此处插入一张 `output` 文件夹中的海报图片作为示例)*

![示例海报](output/20251006_1146.jpg)
