# Cyrillic-editor

[![CI](https://github.com/aleksandr-yavorovskiy/cyrillic-editor/actions/workflows/ci.yml/badge.svg)](https://github.com/aleksandr-yavorovskiy/cyrillic-editor/actions/workflows/ci.yml)
[![lint: backend](https://img.shields.io/github/actions/workflow/status/aleksandr-yavorovskiy/cyrillic-editor/ci.yml?label=lint%20backend&job=backend-lint)](https://github.com/aleksandr-yavorovskiy/cyrillic-editor/actions/workflows/ci.yml)
[![lint: frontend](https://img.shields.io/github/actions/workflow/status/aleksandr-yavorovskiy/cyrillic-editor/ci.yml?label=lint%20frontend&job=frontend-lint)](https://github.com/aleksandr-yavorovskiy/cyrillic-editor/actions/workflows/ci.yml)
[![tests: backend](https://img.shields.io/github/actions/workflow/status/aleksandr-yavorovskiy/cyrillic-editor/ci.yml?label=tests%20backend&job=backend-test)](https://github.com/aleksandr-yavorovskiy/cyrillic-editor/actions/workflows/ci.yml)

Веб-редактор кириллических (церковнославянских, старославянских) текстов с поддержкой глаголицы, виртуальной клавиатурой, словарями для корректной конвертации, компиляцией в PDF через TeX и экспортом в DOCX.

## Развертывание
Пререквизиты: 
1. Docker и Docker Compose.
2. в `./backend/.env` заполнить значение:
```
EXPERT_PASSWORD=<your_value>
```

### Production
Чтобы развернуть проект для использования, необходимо в корне проекта использовать команду:
```sh
make deploy
```
Сайт будет доступен на порту `8080`.

Можно добавить необходимые шрифты через кнопку «Добавить шрифт...» в веб-интерфейсе. Шрифты можно скачать, например, с [fonts-online.ru](https://fonts-online.ru/).

Шрифты, необходимые для полного функционала приложения (не могут быть распространены с кодом из-за несовместимости лицензий, поэтому необходимо добавить их руками при развертывании приложения):
- BukyVede.ttf
- FlavExpUniversal.ttf
- FlaviusUniversal.ttf


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


