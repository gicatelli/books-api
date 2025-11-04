# 1️⃣ Imagem base
FROM python:3.11-slim

# 2️⃣ Define diretório de trabalho
WORKDIR /app

# 3️⃣ Copia os arquivos de requirements
COPY requirements.txt .

# 4️⃣ Instala dependências
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

# 5️⃣ Copia o restante do código
COPY . .

# 6️⃣ Define variáveis de ambiente padrão
ENV PORT=8000

# 7️⃣ Expõe a porta para o Render
EXPOSE 8000

# 8️⃣ Comando de inicialização
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
