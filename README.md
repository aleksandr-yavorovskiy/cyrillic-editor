# Cyrillic-editor

Веб-редактор кириллических (церковнославянских, старославянских) текстов с поддержкой глаголицы, виртуальными клавиатурами, словарями для конвертации, компиляцией в PDF через TeX и экспортом в DOCX.

## Развертывание
Пререквизиты: 
1. Docker и Docker Compose.
2. в `./backend/.env` заполнить значение:
```
DJANGO_SECRET_KEY=<your_value>
```

### Production
Чтобы развернуть проект для использования, необходимо в корне проекта использовать команду:
```sh
make deploy
```
Сайт будет доступен на порту `8080`.


### Development
```
make build-dev
make up-dev
```
Сайт будет доступен локально:
- frontend: http://localhost:5173
- backend: http://localhost:8001


## Разработка
### Линтеры

```sh
make lint          # Весь проект
make lint-backend  # ruff
make lint-frontend # eslint
make format        # prettier (frontend)
```

### Тесты

```sh
make test
```

### Зависимости
#### Frontend
```sh
make deps-frontend
```

#### Backend
```sh
python -m venv backend/.venv
source backend/.venv/bin/activate
make deps-backend
```


