# Huggingface 数据集下载器

一个基于 PyQt5 的图形界面工具，方便地从 Huggingface 下载数据集或模型，支持断点续传、代理设置、主题切换等功能。

## 功能特性
- 支持 Huggingface 数据集和模型的批量下载
- 支持断点续传，下载中断可继续
- 支持 SOCKS5 代理设置，适应国内网络环境
- 支持浅色/深色主题切换
- 简洁易用的图形界面

## 安装方法
1. 克隆本项目或下载源码：

```bash
# 克隆仓库
 git clone <your_repo_url>
 cd huggingface_dataset_download
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 准备资源：
- 请将 `huggingface_download.ico` 图标文件放入 `resources/` 目录下。

## 使用方法

```bash
python main.py
```

### 主要界面参数说明
- **数据集ID（repo_id）**：如 `FreedomIntelligence/huatuo_knowledge_graph_qa`
- **类型（repo_type）**：选择 `dataset` 或 `model`
- **访问令牌（token）**：你的 Huggingface 访问令牌（以 `hf_` 开头），可在 https://huggingface.co/settings/tokens 获取
- **保存路径**：选择本地保存数据集的文件夹
- **使用符号链接**：是否使用符号链接（可选）
- **断点续传**：下载中断后可继续（推荐开启）

### 系统设置
- 可设置 SOCKS5 代理（如需科学上网）
- 可切换浅色/深色主题

## 常见问题
- 若遇到 PyQt5 或 huggingface_hub 相关导入错误，请确认依赖已正确安装。
- 若网络检测失败，请检查代理/VPN 设置。

## 作者信息
- 作者：Accelemate
- GitHub：[https://github.com/Accelemate](https://github.com/Accelemate)
- CSDN：[https://blog.csdn.net/m0_60610428](https://blog.csdn.net/m0_60610428)
- 掘金：[https://juejin.cn/user/1479280118214153](https://juejin.cn/user/1479280118214153)

---

如有建议或问题，欢迎在 Issues 区留言反馈！ 