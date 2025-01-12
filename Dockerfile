# Använd samma Python-version som Render
FROM python:3.11-slim

# Installera nödvändiga systemberoenden
RUN apt-get update && apt-get install -y \
    libreoffice \
    libreoffice-writer \
    fonts-dejavu-core \
    xfonts-utils \
    libfontconfig1 \
    libxinerama1 \
    libxrandr2 \
    && libreoffice --version \
    && apt-get clean

# Sätt arbetskatalogen
WORKDIR /app

# Kopiera projektfiler till containern
COPY . /app

# Uppdatera pip för att säkerställa kompatibilitet
RUN pip install --upgrade pip

# Installera Python-bibliotek från requirements.txt
RUN pip install --no-cache-dir -r requirements.txt --root-user-action=ignore

# Kontrollera att LibreOffice är korrekt installerat
RUN which libreoffice
RUN libreoffice --version

# Säkerställ att LibreOffice finns i PATH när applikationen körs
ENV PATH="/usr/bin:${PATH}"

# Exponera Flask-porten
EXPOSE 5000

# Kör applikationen med Gunicorn och optimera inställningarna
CMD ["gunicorn", "-b", "0.0.0.0:5000", "--timeout", "600", "--workers", "3", "app:app"]
