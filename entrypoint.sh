#!/bin/sh

# Appliquer les migrations de la base de données
python manage.py makemigrations
python manage.py migrate

# Créer un utilisateur administrateur si inexistant
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='androbiert').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'password')" | python manage.py shell

# Démarrer le serveur Django
exec "$@"
