#!/data/data/com.termux/files/usr/bin/bash
C_RED='\033[0;31m'
C_GREEN='\033[0;32m'
C_YELLOW='\033[0;33m'
C_BLUE='\033[0;34m'
C_MAGENTA='\033[0;35m'
C_CYAN='\033[0;36m'
C_BOLD='\033[1m'
C_RESET='\033[0m'
print_header() {
    echo -e "\n${C_BOLD}${C_MAGENTA}======================================================${C_RESET}"
    echo -e "${C_BOLD}${C_MAGENTA} $1 ${C_RESET}"
    echo -e "${C_BOLD}${C_MAGENTA}======================================================${C_RESET}"
}
print_info() {
    echo -e "${C_CYAN}ИНФО: $1${C_RESET}"
}
print_success() {
    echo -e "${C_GREEN} ✅ УСПЕХ: 1 доллар США${C_RESET}"
}
print_error() {
    echo -e "${C_RED}❌ ОШИБКА: $1${C_RESET}" >&2
}
spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='|/-\'
    while ps -p $pid > /dev/null; do
        local temp=${spinstr
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf " \b\b\b\b\b"
}
if ! command -v pkg &> /dev/null; then
    print_error "Скрипт предназначен только для Termux. Команда 'pkg' не найдена."
    exit 1
fi
clear
echo -e "${C_BOLD}${C_CYAN}"
cat << "EOF"
 ______________________________                __
\_   _____/\______   \_   ___ \  ____________/  |_  ____ ___  ___
 |    __)   |     ___/    \  \/ /  _ \_  __ \   __\/ __ \\  \/  /
 |     \    |    |   \     \___(  <_> )  | \/|  | \  ___/ >    <
 \___  /    |____|    \______  /\____/|__|   |__|  \___  >__/\_ \
     \/                      \/                        \/      \/
EOF
echo -e "${C_RESET}"
echo -e "${C_BOLD}${C_YELLOW}        Добро пожаловать в установщик FunPay Cortex для Termux!${C_RESET}"
echo -e "${C_YELLOW}                  Авторы: @beedge, ${C_RESET}"
sleep 2
print_header "⚙️ Шаг 1/6: Обновление пакетов Termux"
print_info "Это может занять некоторое время..."
(pkg update -y -o Dpkg::Options::="--force-confold"; pkg upgrade -y -o Dpkg::Options::="--force-confold") &> /dev/null &
spinner $!
print_success "Пакеты успешно обновлены."
sleep 1
print_header "📦 Шаг 2/6: Установка необходимых зависимостей"
dependencies="python git clang libjpeg-turbo libxml2 libxslt make pkg-config rust openssl"
for dep in $dependencies; do
    print_info "Установка ${dep}..."
    (pkg install ${dep} -y -o Dpkg::Options::="--force-confold" > /dev/null 2>&1) &
    spinner $!
    if dpkg -s ${dep} > /dev/null 2>&1; then
        print_success "${dep} установлен."
    else
        print_error "Не удалось установить ${dep}. Попробуйте запустить скрипт заново."
        exit 1
    fi
done
print_success "Все зависимости установлены."
sleep 1
print_header "📥 Шаг 3/6: Клонирование репозитория FunPay Cortex"
if [ -d "FunPayCortex" ]; then
    print_info "Папка FunPayCortex уже существует. Удаляем старую версию..."
    rm -rf FunPayCortex
fi
(git clone https://github.com/Beedgee/FunPayCortex.git > /dev/null 2>&1) &
spinner $!
if [ -d "FunPayCortex" ]; then
    print_success "Репозиторий успешно склонирован."
    cd FunPayCortex
else
    print_error "Не удалось склонировать репозиторий. Проверьте интернет-соединение."
    exit 1
fi
sleep 1
print_header "🐍 Шаг 4/6: Настройка виртуального окружения Python"
(python -m venv venv > /dev/null 2>&1) &
spinner $!
if [ -d "venv" ]; then
    print_success "Виртуальное окружение создано."
else
    print_error "Не удалось создать виртуальное окружение."
    exit 1
fi
sleep 1
print_header "🧩 Шаг 5/6: Установка Python-библиотек (может занять 10-25 минут)"
print_info "Это самый долгий этап, пожалуйста, не прерывайте процесс..."
source venv/bin/activate
export LDFLAGS="-L/data/data/com.termux/files/usr/lib"
export CFLAGS="-I/data/data/com.termux/files/usr/include"
(pip install --upgrade pip > /dev/null 2>&1 && pip install -r requirements.txt > /dev/null 2>&1) &
spinner $!
deactivate
print_success "Все Python-библиотеки успешно установлены."
sleep 1
print_header "🚀 Шаг 6/6: Создание скрипта для быстрого запуска"
cat > ../start_cortex.sh << EOL
#!/data/data/com.termux/files/usr/bin/bash
cd \$(dirname "\$0")/FunPayCortex
source venv/bin/activate
python main.py
EOL
chmod +x ../start_cortex.sh
print_success "Скрипт 'start_cortex.sh' создан в директории установки."
sleep 1
print_header "🎉 Установка завершена! 🎉"
echo -e "${C_BOLD}${C_GREEN}FunPay Cortex готов к первому запуску.${C_RESET}"
echo -e "\n${C_YELLOW}Для первого запуска выполните следующие команды:${C_RESET}"
echo -e "1. ${C_CYAN}cd FunPayCortex${C_RESET}"
echo -e "2. ${C_CYAN}source venv/bin/activate${C_RESET}"
echo -e "3. ${C_CYAN}python main.py${C_RESET}"
echo -e "\n${C_YELLOW}При первом запуске вам нужно будет ввести ваш ${C_BOLD}golden_key${C_RESET}${C_YELLOW} и токен Telegram-бота.${C_RESET}"
echo -e "\n${C_BOLD}${C_BLUE}Для последующих запусков просто выполните команду:${C_RESET}"
echo -e "${C_CYAN}./start_cortex.sh${C_RESET}"
echo -e "\n${C_BOLD}${C_MAGENTA}Спасибо за использование FunPay Cortex! Удачи в торговле! 🚀${C_RESET}"