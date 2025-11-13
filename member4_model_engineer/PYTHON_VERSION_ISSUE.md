# ⚠️ Python 版本问题说明

## 问题

您的系统使用的是 **Python 3.14.0**，这是一个非常新的版本。

**PyTorch** (必需依赖) 目前还不支持 Python 3.14，导致无法安装项目依赖。

---

## ✅ 推荐解决方案

### 方案1：安装 Python 3.11（推荐）

```bash
# 1. 安装 Python 3.11
brew install python@3.11

# 2. 删除现有虚拟环境
rm -rf venv

# 3. 使用 Python 3.11 创建新虚拟环境
python3.11 -m venv venv

# 4. 激活虚拟环境
source venv/bin/activate

# 5. 安装依赖
pip install -r requirements.txt

# 6. 运行测试
python test_setup.py
```

**支持的Python版本**：
- ✅ Python 3.9
- ✅ Python 3.10
- ✅ Python 3.11
- ✅ Python 3.12（部分支持）
- ❌ Python 3.14（不支持）

---

### 方案2：使用 pyenv 管理多个Python版本

```bash
# 1. 安装 pyenv
brew install pyenv

# 2. 安装 Python 3.11
pyenv install 3.11.10

# 3. 在项目中使用 Python 3.11
cd member4_model_engineer
pyenv local 3.11.10

# 4. 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 5. 安装依赖
pip install -r requirements.txt
```

---

### 方案3：使用 Conda（如果已安装）

```bash
# 1. 创建 conda 环境
conda create -n memematch python=3.11 -y

# 2. 激活环境
conda activate memematch

# 3. 进入项目目录
cd member4_model_engineer

# 4. 安装依赖
pip install -r requirements.txt

# 5. 运行测试
python test_setup.py
```

---

## 🔍 检查当前Python版本

```bash
python --version
python3 --version
python3.11 --version
python3.10 --version
```

---

## 📦 临时方案（不推荐）

如果您暂时无法更换Python版本，可以先安装部分依赖：

```bash
cd member4_model_engineer
source venv/bin/activate
pip install -r requirements-simplified.txt
```

但这样会缺少核心依赖（sentence-transformers），**无法运行完整功能**。

---

## ❓ FAQ

### Q: 为什么不能用 Python 3.14？
**A**: PyTorch是深度学习的核心库，它的编译版本需要时间适配新Python。Python 3.14刚发布，PyTorch官方还没有提供支持。

### Q: 我必须卸载 Python 3.14 吗？
**A**: 不需要！可以同时安装多个Python版本，使用虚拟环境隔离。

### Q: 项目以后会支持 Python 3.14 吗？
**A**: 会的！等 PyTorch 官方发布支持 Python 3.14 的版本后（预计几个月内），就可以正常使用了。

---

## 🚀 推荐做法（最快）

```bash
# 一键安装并设置（使用 Python 3.11）
brew install python@3.11
cd /Applications/MyWorkPlace/7607/memematch/member4_model_engineer
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python test_setup.py
```

---

## 💡 需要帮助？

如果遇到问题，可以：
1. 检查系统上可用的Python版本：`ls /usr/local/bin/python*`
2. 查看 Homebrew 安装的Python：`brew list | grep python`
3. 联系我获取进一步帮助

---

**建议：使用 Python 3.11，这是目前最稳定且兼容性最好的版本。** ✨


