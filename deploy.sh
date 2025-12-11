
#!/bin/bash
set -e

echo ">>> Venv yoqilmoqda..."
source /var/www/document_oborot/venv/bin/activate

echo ">>> Kod yangilanmoqda (git pull)..."
cd /var/www/document_oborot
git pull

echo ">>> Paketlar yangilanmoqda (requirements)..."
pip install -r requirements.txt

echo ">>> Migratsiyalar..."
python manage.py migrate --noinput

echo ">>> Static fayllar..."
python manage.py collectstatic --noinput

echo ">>> Gunicorn qayta ishga tushirilmoqda..."
systemctl restart gunicorn_doc_oborot

echo ">>> Nginx tekshirilmoqda va reload qilinmoqda..."
nginx -t
systemctl reload nginx

echo ">>> TAYYOR! 🚀"
