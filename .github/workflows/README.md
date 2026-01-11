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

- `GHCR_TOKEN` - Personal Access Token (classic) с правами `write:packages` и `read:packages`.
- `SSH_HOST` - IP адрес или доменное имя сервера.
- `SSH_USER` - Имя пользователя для SSH подключения.
- `SSH_PRIVATE_KEY` - Приватный SSH ключ для подключения к серверу.
- `SSH_PORT` - Порт SSH (опционально, по умолчанию 22).
- `TELEGRAM_BOT_TOKEN` - Токен Telegram бота.
- `OPENAI_API_KEY` - API ключ для ProxyAPI.

### Проверка развертывания

После развертывания проверьте логи контейнера:
```bash
ssh deploy@your-server-ip
docker logs telegram-ai-bot
docker ps | grep telegram-ai-bot
```

