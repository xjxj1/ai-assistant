# 使用官方Python基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libgl1 \
    procps \
    lsof \
    curl \
    vim-tiny \
    gcc \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 设置默认环境变量（可在运行时覆盖）
ENV OPENAI_API_KEY="dummy_default_key"
ENV OPENAI_BASE_URL="dummy_default_url"
ENV MODEL="dummy_default_model"
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_FILE_WATCHER_TYPE="none"
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0


# 复制依赖清单
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 容器健康检查
HEALTHCHECK --interval=30s --timeout=5s \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# 暴露Streamlit默认端口
EXPOSE 8501

# 带环境变量验证的启动脚本
CMD ["streamlit", "run", "ai-multi-assistant.py"]
