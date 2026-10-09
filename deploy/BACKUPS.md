# Резервные копии и обслуживание Ubuntu VPS

Файлы в этой папке — подготовленная настройка, а не уже включённая услуга.
Команды ниже выполняются **на арендованном Ubuntu-сервере**, после размещения сайта.
На рабочем компьютере Windows их запускать не нужно.

## Что сохраняется

- PostgreSQL целиком: заявки, товары, пользователи, настройки «О нас» и контакты.
- `backend/static`: загруженные фотографии товаров и страницы «О нас».
- `frontend/public`: логотип, фотографии карусели и другие статические материалы.
- Корневой и backend `.env`, если они есть, и `/etc/caddy/Caddyfile`.

Restic шифрует копии перед отправкой в отдельное S3-хранилище.
Код приложения и зависимости нужно хранить в отдельном Git-репозитории;
это резервная копия данных, не образ всего сервера. Сохраните также версию
PostgreSQL, используемый Git-коммит и systemd-конфигурацию backend.

Ежедневный запуск — 03:00 по часовому поясу VPS. Хранятся последние 7 дневных
и 4 недельных снимка (периоды могут пересекаться). Старые снимки удаляются только
после успешного создания новой копии. Удаление блоков выполняет restic; не задавайте
для S3 удаление файлов по возрасту, иначе можно повредить весь репозиторий.

**На время локального копирования backend останавливается.** Формы, API и кабинеты
в этот момент недоступны; он запускается снова перед сетевой отправкой, в том числе
при ошибке дампа или копирования. Продолжительность зависит от размера данных и
проверяется первым ручным запуском. В это время не запускайте миграции, деплой,
ручное редактирование базы или фотографий. Другие процессы записи тоже должны
быть остановлены. При аварийном отключении сервера обычный автозапуск backend должен
быть включён. Для работы без остановки потребуется отдельная схема со снимками томов.

Для временной копии нужно свободное место размером с фотографии и дамп базы,
плюс запас под кэш restic. Временные данные удаляются после завершения/обычной ошибки;
после аварийного выключения оставшиеся `snapshot-*` проверяют вручную.

## 1. Подготовить сервер и внешнее хранилище

Примеры предполагают проект `/var/www/furniture-shop`, Linux-пользователя `furniture`,
виртуальное окружение `backend/venv` и backend-службу `furniture-backend.service`.
Если у вас другие имена, замените их в env и service-файлах **до установки**.
Пользователь `furniture` должен читать `.env`, но другие пользователи — нет.
Backend должен запускаться systemd, а PostgreSQL — быть доступен по указанным PG-параметрам.

```bash
sudo apt update
sudo apt install restic postgresql-client
pg_dump --version
timedatectl
```

Версия `pg_dump` должна быть не ниже основной версии PostgreSQL на сервере.
При необходимости установите клиент нужной версии из репозитория PostgreSQL.

Создайте отдельный приватный S3 bucket у провайдера, предпочтительно в России,
и ключ доступа только к нему. Копии должны находиться вне диска этого VPS.
Потребуются HTTPS endpoint, название bucket, access key и secret key.

```bash
cd /var/www/furniture-shop
sudo install -m 600 deploy/backup.env.example /etc/furniture-backup.env
sudo nano /etc/furniture-backup.env
sudo install -m 600 /dev/null /etc/furniture-backup.pgpass
sudo nano /etc/furniture-backup.pgpass
```

В `.pgpass` поместите одну строку с настоящими реквизитами PostgreSQL:

```text
127.0.0.1:5432:furniture_shop:furniture:ПАРОЛЬ_БАЗЫ
```

Двоеточие и обратный слеш внутри пароля экранируются обратным слешем.
Роль должна иметь доступ ко всем таблицам/последовательностям приложения; обычно
используется владелец базы. Пароли не передаются аргументами командной строки.

Создайте отдельный длинный пароль шифрования restic и запишите его в
`/etc/furniture-restic-password` с правами `600` и владельцем `root`:

```bash
sudo install -m 600 /dev/null /etc/furniture-restic-password
sudo nano /etc/furniture-restic-password
```

Сохраните этот пароль и доступ к S3 также в менеджере паролей вне VPS:
без пароля зашифрованные копии не восстановить. Не загружайте файлы с ключами в Git.

Инициализируйте новое хранилище один раз:

```bash
sudo -i
set -a
. /etc/furniture-backup.env
set +a
restic init
exit
```

Если в bucket уже есть репозиторий этого сайта, используйте его прежний пароль
и `restic snapshots` вместо повторной инициализации.

## 2. Проверить и включить расписание

```bash
cd /var/www/furniture-shop
sudo install -d -m 755 /usr/local/lib/furniture-shop
sudo install -o root -g root -m 644 deploy/backup.py /usr/local/lib/furniture-shop/backup.py
sudo install -m 644 deploy/furniture-backup.service deploy/furniture-backup.timer /etc/systemd/system/
sudo install -m 644 deploy/furniture-cleanup.service deploy/furniture-cleanup.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemd-analyze verify /etc/systemd/system/furniture-{backup,cleanup}.{service,timer}
sudo systemctl start furniture-backup.service
sudo journalctl -u furniture-backup.service -n 80 --no-pager
```

Скрипт backup запускается от root из отдельного каталога, недоступного для записи
пользователю приложения. При обновлении `deploy/backup.py` повторите его установку
в `/usr/local/lib/furniture-shop/backup.py`.

Убедитесь, что копия успешно отправлена и backend снова отвечает. При ошибке
проверьте `systemctl status furniture-backend.service`, место на диске, доступ
к S3 и параметры базы; расписание включайте только после успешного пробного запуска.

Предварительный просмотр очистки, без удаления:

```bash
cd /var/www/furniture-shop/backend
sudo -u furniture ./venv/bin/python -m app.maintenance
```

После проверки:

```bash
sudo systemctl start furniture-cleanup.service
sudo systemctl enable --now furniture-backup.timer furniture-cleanup.timer
systemctl list-timers 'furniture-*'
```

Очистка в 04:00 удаляет только истёкшие сессии и счётчики ограничений входа/заявок.
Товары, фотографии, заявки и активные сессии остаются. Миграция для этих скриптов
не нужна; существующие миграции проекта должны быть применены.
`Persistent=true` запускает пропущенное задание после включения VPS, поэтому
после длительного простоя копирование может начаться днём.

## 3. Ограничить журналы и включить контроль

Если backend и Caddy пишут в systemd journal:

```bash
sudo mkdir -p /etc/systemd/journald.conf.d
sudo install -m 644 /var/www/furniture-shop/deploy/journald-furniture.conf /etc/systemd/journald.conf.d/furniture.conf
sudo systemctl restart systemd-journald
journalctl --disk-usage
```

Это общий лимит журналов VPS: 300 МБ на диске, 100 МБ временных журналов,
хранение до 14 дней. Файловые логи других программ этим не очищаются;
для них отдельно настраивается logrotate.

В панели провайдера настройте уведомления о заполнении диска на 80% и недоступности
сайта. Эти шаблоны пишут ошибки в journal, но **не отправляют уведомления сами**.
Подключите мониторинг ошибки backup-службы и отсутствия успешной копии более 26 часов
к используемой почте/системе мониторинга. Периодически проверяйте:

```bash
systemctl --failed
journalctl -u furniture-backup.service -u furniture-cleanup.service --since yesterday
```

## 4. Проверить восстановление

До запуска сайта и затем примерно раз в месяц проверяйте восстановление в
**отдельную тестовую базу и папку**, а не поверх работающих данных:

```bash
sudo -i
set -a
. /etc/furniture-backup.env
set +a
restic snapshots --tag furniture-shop
restic check --read-data
# Подставьте конкретный ID снимка из списка:
restic ls ID_СНИМКА
restic restore ID_СНИМКА --target /var/tmp/furniture-restore-test
exit
```

Найдите восстановленный `database.dump` в тестовой папке (расположение видно в
выводе `restic ls`). Создайте пустую тестовую PostgreSQL-базу и выполните:

```bash
# TEST_DATABASE — исключительно отдельная база для проверки.
# Реквизиты подключения задаются через PGHOST/PGUSER/PGPASSFILE.
pg_restore --exit-on-error --no-owner --no-privileges --dbname=TEST_DATABASE /путь/к/database.dump
```

Проверьте наличие товаров и заявок, откройте несколько восстановленных фотографий,
сопоставьте их пути с записями базы. Для полного восстановления установите ту же
версию приложения, верните `static` в `backend/static`, `public` в `frontend/public`,
восстановите конфигурацию с правами доступа и пересоберите frontend. Владелец
загруженных фото должен соответствовать пользователю backend. Рабочую базу
заменяют только при остановленном приложении после проверки копии.

Документация: [S3 и пароль restic](https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html),
[правила хранения снимков](https://restic.readthedocs.io/en/stable/060_forget.html).
