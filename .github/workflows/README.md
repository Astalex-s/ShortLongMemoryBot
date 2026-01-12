# GitHub Actions Workflows

## Deploy Workflow

Этот workflow автоматически собирает Docker образ и развертывает его на удаленном сервере.

### Триггеры

- Push в ветку `main`
- Ручной запуск через `workflow_dispatch`

### Джобы

1. **build-and-push** - Собирает Docker образ и пушит его в GitHub Container Registry (ghcr.io)
2. **deploy** - Подключается к удаленному серверу по SSH и развертывает новый образ

### Необходимые секреты

Настройте следующие секреты в настройках репозитория (**Settings -> Secrets and variables -> Actions**):

**Для Docker Registry:**
- `GHCR_TOKEN` - Personal Access Token (classic) с правами `write:packages` и `read:packages`.

**Для SSH подключения:**
- `SSH_HOST` - IP адрес или доменное имя сервера.
- `SSH_USER` - Имя пользователя для SSH подключения.
- `SSH_PRIVATE_KEY` - Приватный SSH ключ для подключения к серверу.
- `SSH_PORT` - Порт SSH (опционально, по умолчанию 22).

**Для работы бота:**
- `TELEGRAM_BOT_TOKEN` - Токен Telegram бота.
- `OPENAI_API_KEY` - API ключ для ProxyAPI.

**Для PostgreSQL:**
- `DB_HOST` - Хост PostgreSQL (например, `localhost` или IP сервера БД).
- `DB_PORT` - Порт PostgreSQL (по умолчанию `5432`).
- `DB_NAME` - Имя базы данных (например, `memorybot`).
- `DB_USER` - Пользователь PostgreSQL.
- `DB_PASSWORD` - Пароль PostgreSQL.

### Подготовка PostgreSQL на сервере

Перед первым деплоем настройте PostgreSQL на вашем сервере:

```bash
# На сервере установите PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib -y

# Запустите PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Создайте базу данных и пользователя
sudo -u postgres psql << 'SQL'
CREATE DATABASE memorybot;
CREATE USER botuser WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE memorybot TO botuser;
\q
SQL

# Настройте доступ для Docker контейнеров
# Отредактируйте /etc/postgresql/*/main/postgresql.conf
# Раскомментируйте и измените: listen_addresses = '*'

# Отредактируйте /etc/postgresql/*/main/pg_hba.conf
# Добавьте: host all all 172.17.0.0/16 md5

# Перезапустите PostgreSQL
sudo systemctl restart postgresql
```

**Для внешней БД (pgAdmin онлайн):**
Используйте параметры подключения из вашего облачного PostgreSQL и добавьте их как секреты в GitHub.

### Проверка развертывания

После развертывания проверьте логи контейнера:
```bash
ssh deploy@your-server-ip
docker logs telegram-ai-bot
docker ps | grep telegram-ai-bot

# Проверка подключения к БД
docker exec telegram-ai-bot python -c "from utils.db_manager import DBManager; DBManager()"
```

