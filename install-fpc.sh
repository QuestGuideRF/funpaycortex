#!/бин/баш
REPO_URL="YOUR_GITHUB_REPOSITORY_URL/FunPayCortex.git"
BOT_DIR="FunPayCortex"
BOT_USER="cortexuser"
SERVICE_FILE_REPO="FunPayCortex@.service"
SERVICE_NAME="funpaycortex"
print_msg() {
    echo "--------------------------------------------------"
    echo "$1"
    echo "--------------------------------------------------"
}
if [ "$(рука -у)" -ne 0 ]; then
    print_msg "Этот скрипт должен быть запущен от имени суперпользователя (root). Используйте 'sudo bash install-fpc.sh'"
    exit 1
fi
print_msg "Обновление системы и установка зависимостей..."
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv git wget sudo
if id "$BOT_USER" &>/dev/null; then
    print_msg "Пользователь '$BOT_USER' уже существует."
else
    print_msg "Создание пользователя '$BOT_USER'..."
    adduser --disabled-password --gecos "" "$BOT_USER"
    print_msg "Пользователь '$BOT_USER' создан."
fi
USER_HOME=$(eval echo "~$BOT_USER")
cd "$USER_HOME" || { print_msg "Не удалось перейти в домашнюю директорию пользователя '$BOT_USER'."; exit 1; }
if [ -d "$BOT_DIR" ]; then
    print_msg "Директория '$BOT_DIR' уже существует. Пропуск клонирования."
    cd "$BOT_DIR" || { print_msg "Не удалось перейти в директорию '$BOT_DIR'."; exit 1; }
else
    print_msg "Клонирование репозитория '$REPO_URL'..."
    sudo -u "$BOT_USER" git clone "$REPO_URL" "$BOT_DIR"
    cd "$BOT_DIR" || { print_msg "Не удалось перейти в директорию '$BOT_DIR'."; exit 1; }
fi
print_msg "Создание виртуального окружения..."
sudo -u "$BOT_USER" python3 -m venv pyvenv
print_msg "Установка зависимостей из requirements.txt..."
sudo -u "$BOT_USER" "$USER_HOME/$BOT_DIR/pyvenv/bin/pip" install -r requirements.txt
if [ ! -f "configs/_main.cfg" ]; then
    print_msg "Основной конфигурационный файл не найден. Запускаем первичную настройку..."
    sudo -u "$BOT_USER" "$USER_HOME/$BOT_DIR/pyvenv/bin/python" main.py
    if [ $? -ne 0 ]; then
         print_msg "Ошибка во время первичной настройки. Пожалуйста, проверьте вывод выше."
    else
         print_msg "Первичная настройка завершена."
    fi
else
    print_msg "Конфигурационный файл найден, пропуск первичной настройки."
fi
print_msg "Настройка сервиса systemd..."
SERVICE_FILE_PATH="/etc/systemd/system/${SERVICE_NAME}@.service"
if [ ! -f "$SERVICE_FILE_REPO" ]; then
    print_msg "Ошибка: Файл сервиса '$SERVICE_FILE_REPO' не найден в репозитории!"
    exit 1
fi
cp "$SERVICE_FILE_REPO" "$SERVICE_FILE_PATH"
systemctl daemon-reload
systemctl enable "${SERVICE_NAME}@${BOT_USER}.service"
systemctl start "${SERVICE_NAME}@${BOT_USER}.service"
print_msg "Сервис '${SERVICE_NAME}@${BOT_USER}' настроен и запущен."
print_msg "Проверить статус: systemctl status ${SERVICE_NAME}@${BOT_USER}.service"
print_msg "Посмотреть логи: journalctl -u ${SERVICE_NAME}@${BOT_USER}.service -f"
print_msg "Установка завершена!"
exit 0