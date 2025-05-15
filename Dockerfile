FROM python:3.10-slim

# Обновление системы и установка libGL для OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем всё содержимое проекта
COPY . .

# Устанавливаем pip и зависимости из requirements (если есть)
RUN pip install --upgrade pip \
#  && if [ -f "requirements.txt" ]; then pip install -r requirements.txt; fi \
 && if [ -f "requirements_online.txt" ]; then pip install -r requirements_online.txt; fi \
 && pip install streamlit opencv-python-headless

# Открываем порт Streamlit (по умолчанию 8501)
EXPOSE 8501

# Устанавливаем рабочую директорию в online
WORKDIR /app/online

# Запуск Streamlit-приложения
CMD ["streamlit", "run", "fresh_view/Demos/face_mesh_app.py"]
