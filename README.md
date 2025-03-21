# W-Server
Web server for data exchange, local network.
Simple service with basic capabilities.

my_fastapi_app/
│── app/
│   │── __init__.py
│   │── main.py         # Основной файл приложения
│   │── config.py       # Конфигурация (пути, ограничения)
│   │── utils.py        # Вспомогательные функции (хеширование, MIME-проверка)
│   │── routes.py       # Роутеры (загрузка, скачивание, удаление файлов)
│── templates/
│   └── index.html      # HTML-шаблон для отображения загруженных файлов
│── static/             # Статические файлы (CSS, JS)
│── uploads/            # Папка для загруженных файлов
│── Cert/               # Папка для SSL-сертификатов
│── requirements.txt    # Зависимости проекта
│── run.py              # Скрипт запуска приложения
│── README.md           # Описание проекта
