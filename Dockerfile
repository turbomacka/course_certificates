# Använd samma Python-version som Render
FROM python:3.11-slim

# Installera nödvändiga systemberoenden
RUN apt-get update && apt-get install -y \
    libreoffice \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    libreoffice-writer \
    fonts-dejavu-core \
    xfonts-utils \
    libreoffice-core \
    libfontconfig1 \
    libxinerama1 \
    libxrandr2 \
    && apt-get clean

#testar libre-installationen
RUN libreoffice --version

#Säkerställ att LibreOffice finns i PATH när applikationen körs.
ENV PATH="/usr/bin:${PATH}"

# Sätt arbetskatalogen
WORKDIR /app

# Kopiera projektfiler till containern
COPY . /app

# Uppdatera pip för att säkerställa kompatibilitet
RUN pip install --upgrade pip

# Installera Python-bibliotek från requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Exponera Flask-porten
EXPOSE 5000

# Kör applikationen (Gunicorn är vanlig på Render)
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]