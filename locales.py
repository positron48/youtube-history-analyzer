# -*- coding: utf-8 -*-
"""
Файл локализации для YouTube History Analyzer
Содержит все текстовые строки на разных языках
"""

LOCALES = {
    'ru': {
        # Основные сообщения
        'welcome': 'Добро пожаловать в YouTube History Analyzer!',
        'select_language': 'Выберите язык / Select language:',
        'language_ru': '🇷🇺 Русский',
        'language_en': '🇺🇸 English',
        'invalid_choice': '❌ Неверный выбор. Попробуйте снова.',
        
        # TUI меню
        'main_menu_title': '📊 YouTube History Analyzer - Главное меню',
        'menu_option_1': '1. Загрузить данные из Takeout',
        'menu_option_2': '2. Получить длительность видео',
        'menu_option_3': '3. Сгенерировать HTML отчет',
        'menu_option_4': '4. Экспорт данных в CSV',
        'menu_option_5': '5. Открыть отчет в браузере',
        'menu_option_0': '0. Выход',
        'enter_choice': 'Введите ваш выбор (0-5): ',
        'goodbye': '👋 До свидания!',
        'press_enter': 'Нажмите Enter для продолжения...',
        'app_title': 'YouTube History Analyzer',
        'app_subtitle': 'Анализатор истории просмотров YouTube',
        
        # Загрузка данных
        'loading_data': 'Загрузка данных из Takeout',
        'found_history_file': 'Найден файл истории: {path}',
        'found_my_activity': 'Найден файл My Activity: {path}',
        'load_watch_history': 'Загрузить файл истории просмотров? [y/n]: ',
        'load_my_activity': 'Загрузить файл My Activity? [y/n]: ',
        'loaded_records': '✓ Загружено {count} записей из {source}',
        'processing_data': 'Обрабатываю данные...',
        'merging_sources': 'Объединяю данные из разных источников...',
        'merged_unique': '✓ Объединено {count} уникальных записей',
        'found_duplicates': 'Найдено и удалено {count} дублей',
        'deduplication': '  Дедупликация записей...',
        'processing_records': '  Обработка записей...',
        'processed_records': '✓ Обработано {count} записей',
        
        # Получение длительности
        'getting_durations': 'Получаю длительность для {count} видео...',
        'selected_videos': 'Выбрано {count} видео с доступными каналами',
        'total_available': 'Всего доступных видео: {count}',
        'using_api': '✓ Используется YouTube Data API v3',
        'total_videos': '📋 Всего видео для обработки: {count}',
        'duration_progress': '✓ {title}... ({duration}) | Среднее: {avg_duration}',
        'current_average': '📊 Текущее среднее: {avg_duration} (на основе {count} видео)',
        'processed_count': '✅ Обработано: {processed}/{total} видео ({percent:.1f}%) | Осталось: {remaining}',
        'duration_complete': '✓ Получена длительность для {processed} из {total} видео',
        'duration_saved': '✓ Длительности сохранены в: {path}',
        'file_size': 'Размер файла: {size}',
        
        # Прогрессия среднего значения
        'average_progression_saved': '✓ Данные о прогрессии среднего сохранены:',
        'average_progression_json': '  JSON: {path}',
        'average_progression_csv': '  CSV: {path}',
        'average_progression_size': '  Размер: {size}',
        'average_convergence_chart': '📊 Создан график сходимости среднего: {path}',
        'average_progression_data': '📊 Данные о прогрессии сохранены в {csv} и {json}',
        
        # Сообщения об ошибках
        'error_file_not_list': 'Ошибка: файл {source} не содержит список',
        'error_loading_source': 'Ошибка загрузки {source}: {error}',
        'yt_dlp_usage': 'Используется yt-dlp для получения длительности...',
        'cookies_used': '✓ Используются cookies для авторизации',
        'temp_cookies_created': 'Создана временная копия cookies для yt-dlp',
        'cookies_file_not_found': '⚠️ Файл youtube_cookies.txt не найден!',
        'cookies_instructions': 'Создайте файл youtube_cookies.txt для обхода блокировок',
        'yt_dlp_not_installed': 'yt-dlp не установлен! Установите: pip install yt-dlp',
        'yt_dlp_error': 'Ошибка при использовании yt-dlp: {error}',
        'yt_dlp_try_vpn': 'Попробуйте обновить cookies или использовать VPN',
        'getting_duration': 'Получение длительности...',
        'getting_info_for': '🔍 Получаю информацию для: {title}...',
        'duration_not_found': '❌ {title}... (длительность не найдена)',
        'duration_error': '❌ {title}... (ошибка: {error})',
        'duration_obtained': '✓ Получена длительность для {obtained} из {total} видео',
        'temp_cookies_removed': '✓ Временный файл cookies удален',
        'no_duration_videos': '⚠️ Не удалось получить длительность ни для одного видео',
        'no_duration_reasons': 'Возможные причины:',
        'google_blocking': '  - Google блокирует запросы',
        'wrong_cookies': '  - Неправильные cookies',
        'videos_unavailable': '  - Видео недоступны',
        
        # Инструкции
        'cookies_setup_title': '🍪 Инструкция по настройке cookies:',
        'cookies_step1': '1. Установите расширение \'Get cookies.txt\' в браузере',
        'cookies_step2': '2. Зайдите на YouTube и войдите в аккаунт',
        'cookies_step3': '3. Экспортируйте cookies в файл youtube_cookies.txt',
        'cookies_step4': '4. Поместите файл в папку проекта',
        'cookies_step5': '5. Перезапустите анализатор',
        'cookies_instructions_file': 'Подробные инструкции: см. файл COOKIES_INSTRUCTIONS.md',
        'api_key_not_found': '❌ Файл youtube_api_key.txt не найден!',
        'api_key_instructions': 'Создайте файл с API ключом YouTube Data API v3',
        'api_key_empty': '❌ API ключ пустой!',
        'api_key_invalid': 'API ключ недействителен или превышен лимит',
        'api_request_invalid': 'Неверный запрос',
        'api_check_key': 'Проверьте API ключ и лимиты',
        'api_error': 'Ошибка API',
        'api_module_error': 'Ошибка при использовании API: {error}',
        'api_install_requests': 'Убедитесь, что установлен модуль requests',
        
        # Общие сообщения об ошибках
        'timeout': 'таймаут',
        'network_error': 'ошибка сети',
        'error': 'ошибка',
        
        # Другие сообщения
        'selenium_usage': 'Используется Selenium для получения длительности...',
        'selenium_slower': 'Этот метод медленнее, но более надежен для обхода блокировок',
        'cookies_found': '✓ Найден файл cookies.txt - будет использован для авторизации',
        'cookies_loaded': '✓ Cookies загружены в браузер',
        'getting_duration_browser': 'Получение длительности через браузер...',
        'browser_error': 'Ошибка при запуске браузера: {error}',
        'browser_install_chrome': 'Попробуйте установить Chrome или использовать другой метод',
        'selenium_not_installed': 'Selenium не установлен! Установите: pip install selenium webdriver-manager',
        'selenium_error': 'Ошибка при использовании Selenium: {error}',
        'manual_mode': 'Ручной режим для тестирования...',
        'manual_duration_format': 'Введите длительность в формате MM:SS или H:MM:SS',
        'manual_duration_input': 'Длительность (MM:SS или Enter для пропуска): ',
        'manual_duration_success': '✓ Длительность: {input} ({duration} сек)',
        'manual_duration_invalid': '❌ Неверный формат длительности',
        'manual_duration_skipped': 'Пропущено',
        'manual_processed': '✓ Обработано {processed} видео',
        'pattern_found': 'Паттерн {num}: {pattern} -> {matches}',
        'patterns_found': 'Найдены паттерны: {patterns}',
        'duration_hours_minutes': '✓ Длительность найдена: {hours}ч {minutes}м {seconds}с = {result}с',
        'duration_minutes_seconds': '✓ Длительность найдена: {minutes}м {seconds}с = {result}с',
        'duration_seconds': '✓ Длительность найдена: {result}с',
        'pattern_parse_error': '⚠️ Ошибка парсинга паттерна {pattern}: {error}',
        'duration_no_patterns': '❌ Длительность не найдена ни одним паттерном',
        'extract_html_error': '❌ Ошибка в extract_duration_from_html: {error}',
        'time_format_hours': '{hours}ч {minutes}м {seconds}с',
        'time_format_minutes': '{minutes}м {seconds}с',
        
        # Дополнительные сообщения
        'language_selected_ru': '✓ Выбран русский язык',
        'getting_duration': 'Получение длительности...',
        'getting_info_for': '🔍 Получаю информацию для: {title}...',
        'duration_not_found': '❌ {title}... (длительность не найдена)',
        'duration_error': '❌ {title}... (ошибка: {error})',
        'duration_obtained': '✓ Получена длительность для {obtained} из {total} видео',
        'temp_cookies_removed': '✓ Временный файл cookies удален',
        'no_duration_videos': '⚠️ Не удалось получить длительность ни для одного видео',
        'no_duration_reasons': 'Возможные причины:',
        'google_blocking': '  - Google блокирует запросы',
        'wrong_cookies': '  - Неправильные cookies',
        'videos_unavailable': '  - Видео недоступны',
        'iso_parse_error': '❌ Ошибка парсинга ISO длительности: {error}',
        'parsing_error': '❌ {title}... (ошибка парсинга)',
        'video_unavailable': '❌ {title}... (видео недоступно)',
        'no_data_for_watch_time': 'Нет данных о длительности для подсчета общего времени',
        'no_data_for_export': 'Нет данных для экспорта!',
        'average_value': 'Среднее значение',
        
        # Меню выбора языка
        'select_language_input': 'Выберите язык / Select language (1-2): ',
        
        # Описание CSV файла
        'csv_main_file_description': 'Основной файл с данными истории просмотров YouTube.',
        'csv_columns_header': '**Колонки:**',
        'csv_video_id_desc': ' - уникальный идентификатор видео',
        'csv_title_desc': ' - название просмотренного видео',
        'csv_channel_desc': ' - название канала (Unknown = удаленный/приватный канал)',
        'csv_url_desc': ' - прямая ссылка на видео',
        'csv_date_desc': ' - дата в формате YYYY-MM-DD',
        'csv_time_desc': ' - время в формате HH:MM:SS',
        'csv_source_desc': ' - откуда получены данные (watch_history/my_activity)',
        'csv_datetime_utc_desc': ' - полная дата и время в UTC',
        'csv_summary_description': 'Сводная статистика по всем данным.',
        'csv_html_description': 'HTML отчет с графиками и визуализацией.',
        'csv_youtube_music_excluded': ' - YouTube Music: полностью исключен',
        'csv_my_activity_desc': ' - My Activity: только "Watched" записи (без лайков, дизлайков, поиска)',
        'csv_duplicates_desc': ' - Дубли: удалены автоматически',
        'csv_unknown_channels_desc': ' - Каналы "Unknown" - это удаленные или приватные каналы',
        'csv_time_utc_desc': ' - Время указано в UTC',
        'csv_merged_sources_desc': ' - Данные объединены из двух источников: история просмотров + My Activity',
        
        # Дополнительные ключи для CSV
        'youtube_history_export': 'Экспорт истории YouTube',
        'export_files': 'Файлы экспорта',
        'general_information': 'Общая информация',
        'notes': 'Примечания',
        
        # Дополнительные ключи для CSV описания
        'year_month_format': ' - год и месяц в формате YYYY-MM',
        'day_of_week_format': ' - день недели на',
        'hour_format': ' - час просмотра (0-23)',
        
        # Графики и заголовки
        'average_convergence_title': 'Сходимость среднего значения длительности видео (каждое видео)',
        'average_convergence_xaxis': 'Количество видео',
        'average_convergence_yaxis': 'Средняя длительность (минуты)',
        'average_convergence_final': 'Финальное среднее: {value} мин',
        'average_convergence_trend': 'Скользящий тренд (окно {window})',
        'average_convergence_section': '📊 Сходимость среднего значения длительности (каждое видео)',
        
        # Статистика
        'duration_stats_title': '📊 Статистика по длительности видео',
        'total_videos_with_duration': 'Всего видео с длительностью',
        'total_watch_time': 'Общее время просмотра',
        'average_duration': 'Средняя длительность',
        'shortest_video': 'Самое короткое видео',
        'longest_video': 'Самое длинное видео',
        'duration_distribution': '📈 Распределение по длительности',
        'duration_range_0_5': '0-5 мин: {count} видео ({percent:.1f}%)',
        'duration_range_5_15': '5-15 мин: {count} видео ({percent:.1f}%)',
        'duration_range_15_30': '15-30 мин: {count} видео ({percent:.1f}%)',
        'duration_range_30_60': '30-60 мин: {count} видео ({percent:.1f}%)',
        'duration_range_60_plus': '60+ мин: {count} видео ({percent:.1f}%)',
        
        # Сводка по времени
        'watch_time_summary': '⏰ СВОДКА ПО ВРЕМЕНИ ПРОСМОТРА',
        'total_videos_in_history': 'Всего видео в истории',
        'videos_with_duration': 'Видео с известной длительностью',
        'videos_without_duration': 'Видео без данных о длительности',
        'total_time_known': 'Общее время (известные видео)',
        'average_duration_videos': 'Средняя длительность видео',
        'estimated_total_time': 'Оценка общего времени',
        'data_coverage': '📊 Покрытие данных: {percent:.1f}%',
        'duration_unknown_warning': '⚠️ Для {count} видео длительность неизвестна',
        'estimated_time_note': '   Общее время рассчитано с учетом оценки на основе средней длительности',
        
        # HTML отчет
        'generating_html': 'Генерирую HTML отчет...',
        'creating_plots': 'Создаю графики...',
        'plots_saved': '✓ Графики сохранены',
        'html_saved': '✓ HTML отчет сохранен: {path}',
        'youtube_analysis': 'Анализ истории YouTube',
        'video_duration_statistics': 'Статистика по длительности видео',
        'videos_with_duration': 'Видео с известной длительностью',
        'videos_without_duration': 'Видео без данных о длительности',
        'data_coverage': 'Покрытие данных',
        'average_duration': 'Средняя длительность',
        'total_time_known_videos': 'Общее время (известные видео)',
        'estimated_total_time': 'Оценка общего времени',
        'duration_data_not_available': 'Данные о длительности видео не были получены. Используйте функцию "Получить длительность видео" для анализа времени просмотра.',
        
        # Экспорт CSV
        'exporting_csv': 'Экспортирую данные в CSV...',
        'csv_saved': '✓ CSV файл сохранен: {path}',
        
        # Ошибки и предупреждения
        'error_loading_file': '❌ Ошибка загрузки файла: {error}',
        'error_processing': '❌ Ошибка обработки данных: {error}',
        'error_api': '❌ Ошибка YouTube API: {error}',
        'error_creating_report': '❌ Ошибка создания отчета: {error}',
        'no_data_loaded': '❌ Данные не загружены. Сначала загрузите данные из Takeout.',
        'no_duration_data': '❌ Данные о длительности не найдены. Сначала получите длительность видео.',
        
        # API инструкции
        'api_instructions_title': '📋 Инструкции по настройке YouTube Data API',
        'api_step_1': '1. Перейдите в Google Cloud Console: https://console.cloud.google.com/',
        'api_step_2': '2. Создайте новый проект или выберите существующий',
        'api_step_3': '3. Включите YouTube Data API v3',
        'api_step_4': '4. Создайте учетные данные (API ключ)',
        'api_step_5': '5. Скопируйте ключ в файл youtube_api_key.txt',
        'api_quota_info': '📊 Квота API: 10,000 единиц в день (1 единица на видео)',
        'api_recommendation': '💡 Рекомендация: начинайте с выборки 100-1000 видео',
        
        # Форматирование времени
        'seconds': 'секунд',
        'minutes': 'минут',
        'hours': 'часов',
        'time_format': '{hours}ч {minutes}м {seconds}с',
        
        # CSV колонки
        'csv_video_id': 'ID_видео',
        'csv_title': 'Название_видео',
        'csv_channel': 'Канал',
        'csv_url': 'Ссылка_на_видео',
        'csv_date': 'Дата_формат',
        'csv_time': 'Время_формат',
        'csv_day_of_week': 'День_недели_РУ',
        'csv_source': 'Источник_данных',
        'csv_duration_seconds': 'Длительность_секунды',
        'csv_duration_formatted': 'Длительность_формат',
        'csv_duration_minutes': 'Длительность_минуты',
        'main_statistics': 'Основная статистика',
        'top_channels': 'Топ каналов',
        'parameter': 'Параметр',
        'value': 'Значение',
        'channel': 'Канал',
        'video': 'Видео',
        'sample_size_prompt': 'Размер выборки для анализа длительности (по умолчанию 100): ',
        'total_videos_label': 'Всего видео',
        'active_days_label': 'Дней активности',
        'avg_videos_per_day_label': 'Среднее видео в день',
        'no_available_videos': 'Нет доступных видео с известными каналами!',
        'report_not_created': 'Отчет еще не создан!',
        'no_files_loaded': 'Не удалось загрузить ни один файл!',
        'program_interrupted': 'Программа прервана пользователем',
        'monthly_activity': 'Активность по месяцам',
        'day_of_week_activity': 'Активность по дням недели',
        'hourly_activity': 'Активность по часам суток',
        'cumulative_time': 'Накопительное время просмотра',
        'watch_time': 'Время просмотра',
        'additional_statistics': 'Дополнительная статистика',
        'analysis_period': 'Период анализа',
        'data_sources': 'Источники данных',
        'records': 'записей',
        'export_summary': 'Краткая статистика экспорта',
        'unique_channels': 'Уникальных каналов',
        'file_ready_for_import': 'Файл готов для импорта в Excel/Google Sheets',
        'total_records': 'Всего записей',
        'period': 'Период',
        'summary_statistics': 'Сводная статистика',
        'readme_file': 'README файл',
        'csv_file_size': 'Размер CSV файла',
        'error': 'Ошибка',
        'month': 'Месяц',
        'video_count': 'Количество видео',
        'day_of_week': 'День недели',
        'hour': 'Час',
        'year_month': 'Год_месяц',
        'hours_minutes': 'часов 0 минут',
        'no_data_for_plots': 'Нет данных для создания графиков!',
        'unknown': 'Неизвестно',
        'datetime_utc': 'Дата_время_UTC',
        'date': 'Дата',
        'time_seconds': 'Время (секунды)',
        'year': 'Год',
        'day_of_week_en': 'День_недели_EN',
        'top_10_channels': 'Топ_10_каналов',
        'statistics_by_sources': 'Статистика_по_источникам',
        'statistics_by_days': 'Статистика_по_дням_недели',
        'statistics_by_hours': 'Статистика_по_часам',
        'general_statistics': 'Общая_статистика',
        'total_records_key': 'Всего_записей',
        'period_start': 'Период_начала',
        'period_end': 'Период_окончания',
        'days_count': 'Количество_дней',
        
        # Дни недели
        'monday': 'Понедельник',
        'tuesday': 'Вторник',
        'wednesday': 'Среда',
        'thursday': 'Четверг',
        'friday': 'Пятница',
        'saturday': 'Суббота',
        'sunday': 'Воскресенье',
        
        # Месяцы
        'january': 'Январь',
        'february': 'Февраль',
        'march': 'Март',
        'april': 'Апрель',
        'may': 'Май',
        'june': 'Июнь',
        'july': 'Июль',
        'august': 'Август',
        'september': 'Сентябрь',
        'october': 'Октябрь',
        'november': 'Ноябрь',
        'december': 'Декабрь',
    },
    
    'en': {
        # Main messages
        'welcome': 'Welcome to YouTube History Analyzer!',
        'select_language': 'Select language / Выберите язык:',
        'language_ru': '🇷🇺 Русский',
        'language_en': '🇺🇸 English',
        'invalid_choice': '❌ Invalid choice. Please try again.',
        
        # TUI menu
        'main_menu_title': '📊 YouTube History Analyzer - Main Menu',
        'menu_option_1': '1. Load data from Takeout',
        'menu_option_2': '2. Get video duration',
        'menu_option_3': '3. Generate HTML report',
        'menu_option_4': '4. Export data to CSV',
        'menu_option_5': '5. Open report in browser',
        'menu_option_0': '0. Exit',
        'enter_choice': 'Enter your choice (0-5): ',
        'goodbye': '👋 Goodbye!',
        'press_enter': 'Press Enter to continue...',
        'app_title': 'YouTube History Analyzer',
        'app_subtitle': 'YouTube History Analyzer',
        
        # Data loading
        'loading_data': 'Loading data from Takeout',
        'found_history_file': 'Found history file: {path}',
        'found_my_activity': 'Found My Activity file: {path}',
        'load_watch_history': 'Load watch history file? [y/n]: ',
        'load_my_activity': 'Load My Activity file? [y/n]: ',
        'loaded_records': '✓ Loaded {count} records from {source}',
        'processing_data': 'Processing data...',
        'merging_sources': 'Merging data from different sources...',
        'merged_unique': '✓ Merged {count} unique records',
        'found_duplicates': 'Found and removed {count} duplicates',
        'deduplication': '  Deduplicating records...',
        'processing_records': '  Processing records...',
        'processed_records': '✓ Processed {count} records',
        
        # Getting duration
        'getting_durations': 'Getting duration for {count} videos...',
        'selected_videos': 'Selected {count} videos with available channels',
        'total_available': 'Total available videos: {count}',
        'using_api': '✓ Using YouTube Data API v3',
        'total_videos': '📋 Total videos to process: {count}',
        'duration_progress': '✓ {title}... ({duration}) | Average: {avg_duration}',
        'current_average': '📊 Current average: {avg_duration} (based on {count} videos)',
        'processed_count': '✅ Processed: {processed}/{total} videos ({percent:.1f}%) | Remaining: {remaining}',
        'duration_complete': '✓ Got duration for {processed} out of {total} videos',
        'duration_saved': '✓ Durations saved to: {path}',
        'file_size': 'File size: {size}',
        
        # Average progression
        'average_progression_saved': '✓ Average progression data saved:',
        'average_progression_json': '  JSON: {path}',
        'average_progression_csv': '  CSV: {path}',
        'average_progression_size': '  Size: {size}',
        'average_convergence_chart': '📊 Average convergence chart created: {path}',
        'average_progression_data': '📊 Progression data saved to {csv} and {json}',
        
        # Error messages
        'error_file_not_list': 'Error: file {source} does not contain a list',
        'error_loading_source': 'Error loading {source}: {error}',
        'yt_dlp_usage': 'Using yt-dlp to get duration...',
        'cookies_used': '✓ Cookies used for authorization',
        'temp_cookies_created': 'Temporary cookies copy created for yt-dlp',
        'cookies_file_not_found': '⚠️ youtube_cookies.txt file not found!',
        'cookies_instructions': 'Create youtube_cookies.txt file to bypass blocks',
        'yt_dlp_not_installed': 'yt-dlp not installed! Install: pip install yt-dlp',
        'yt_dlp_error': 'Error using yt-dlp: {error}',
        'yt_dlp_try_vpn': 'Try updating cookies or using VPN',
        'getting_duration': 'Getting duration...',
        'getting_info_for': '🔍 Getting info for: {title}...',
        'duration_not_found': '❌ {title}... (duration not found)',
        'duration_error': '❌ {title}... (error: {error})',
        'duration_obtained': '✓ Got duration for {obtained} out of {total} videos',
        'temp_cookies_removed': '✓ Temporary cookies file removed',
        'no_duration_videos': '⚠️ Could not get duration for any video',
        'no_duration_reasons': 'Possible reasons:',
        'google_blocking': '  - Google blocking requests',
        'wrong_cookies': '  - Wrong cookies',
        'videos_unavailable': '  - Videos unavailable',
        
        # Instructions
        'cookies_setup_title': '🍪 Cookies setup instructions:',
        'cookies_step1': '1. Install \'Get cookies.txt\' extension in browser',
        'cookies_step2': '2. Go to YouTube and log in to account',
        'cookies_step3': '3. Export cookies to youtube_cookies.txt file',
        'cookies_step4': '4. Place file in project folder',
        'cookies_step5': '5. Restart analyzer',
        'cookies_instructions_file': 'Detailed instructions: see COOKIES_INSTRUCTIONS.md file',
        'api_key_not_found': '❌ youtube_api_key.txt file not found!',
        'api_key_instructions': 'Create file with YouTube Data API v3 key',
        'api_key_empty': '❌ API key is empty!',
        'api_key_invalid': 'API key invalid or limit exceeded',
        'api_request_invalid': 'Invalid request',
        'api_check_key': 'Check API key and limits',
        'api_error': 'API Error',
        'api_module_error': 'Error using API: {error}',
        'api_install_requests': 'Make sure requests module is installed',
        
        # General error messages
        'timeout': 'timeout',
        'network_error': 'network error',
        'error': 'error',
        
        # Other messages
        'selenium_usage': 'Using Selenium to get duration...',
        'selenium_slower': 'This method is slower but more reliable for bypassing blocks',
        'cookies_found': '✓ cookies.txt file found - will be used for authorization',
        'cookies_loaded': '✓ Cookies loaded into browser',
        'getting_duration_browser': 'Getting duration through browser...',
        'browser_error': 'Error starting browser: {error}',
        'browser_install_chrome': 'Try installing Chrome or use another method',
        'selenium_not_installed': 'Selenium not installed! Install: pip install selenium webdriver-manager',
        'selenium_error': 'Error using Selenium: {error}',
        'manual_mode': 'Manual mode for testing...',
        'manual_duration_format': 'Enter duration in MM:SS or H:MM:SS format',
        'manual_duration_input': 'Duration (MM:SS or Enter to skip): ',
        'manual_duration_success': '✓ Duration: {input} ({duration} sec)',
        'manual_duration_invalid': '❌ Invalid duration format',
        'manual_duration_skipped': 'Skipped',
        'manual_processed': '✓ Processed {processed} videos',
        'pattern_found': 'Pattern {num}: {pattern} -> {matches}',
        'patterns_found': 'Patterns found: {patterns}',
        'duration_hours_minutes': '✓ Duration found: {hours}h {minutes}m {seconds}s = {result}s',
        'duration_minutes_seconds': '✓ Duration found: {minutes}m {seconds}s = {result}s',
        'duration_seconds': '✓ Duration found: {result}s',
        'pattern_parse_error': '⚠️ Pattern parsing error {pattern}: {error}',
        'duration_no_patterns': '❌ Duration not found by any pattern',
        'extract_html_error': '❌ Error in extract_duration_from_html: {error}',
        'time_format_hours': '{hours}h {minutes}m {seconds}s',
        'time_format_minutes': '{minutes}m {seconds}s',
        
        # Additional messages
        'language_selected_ru': '✓ Russian language selected',
        'getting_duration': 'Getting duration...',
        'getting_info_for': '🔍 Getting info for: {title}...',
        'duration_not_found': '❌ {title}... (duration not found)',
        'duration_error': '❌ {title}... (error: {error})',
        'duration_obtained': '✓ Got duration for {obtained} out of {total} videos',
        'temp_cookies_removed': '✓ Temporary cookies file removed',
        'no_duration_videos': '⚠️ Could not get duration for any video',
        'no_duration_reasons': 'Possible reasons:',
        'google_blocking': '  - Google blocking requests',
        'wrong_cookies': '  - Wrong cookies',
        'videos_unavailable': '  - Videos unavailable',
        'iso_parse_error': '❌ ISO duration parsing error: {error}',
        'parsing_error': '❌ {title}... (parsing error)',
        'video_unavailable': '❌ {title}... (video unavailable)',
        'no_data_for_watch_time': 'No duration data for total time calculation',
        'no_data_for_export': 'No data for export!',
        'average_value': 'Average value',
        
        # Language selection menu
        'select_language_input': 'Select language / Выберите язык (1-2): ',
        
        # Charts and titles
        'average_convergence_title': 'Average Duration Convergence (every video)',
        'average_convergence_xaxis': 'Number of videos',
        'average_convergence_yaxis': 'Average duration (minutes)',
        'average_convergence_final': 'Final average: {value} min',
        'average_convergence_trend': 'Moving trend (window {window})',
        'average_convergence_section': '📊 Average Duration Convergence (every video)',
        
        # Statistics
        'duration_stats_title': '📊 Video Duration Statistics',
        'total_videos_with_duration': 'Total videos with duration',
        'total_watch_time': 'Total watch time',
        'average_duration': 'Average duration',
        'shortest_video': 'Shortest video',
        'longest_video': 'Longest video',
        'duration_distribution': '📈 Duration distribution',
        'duration_range_0_5': '0-5 min: {count} videos ({percent:.1f}%)',
        'duration_range_5_15': '5-15 min: {count} videos ({percent:.1f}%)',
        'duration_range_15_30': '15-30 min: {count} videos ({percent:.1f}%)',
        'duration_range_30_60': '30-60 min: {count} videos ({percent:.1f}%)',
        'duration_range_60_plus': '60+ min: {count} videos ({percent:.1f}%)',
        
        # Watch time summary
        'watch_time_summary': '⏰ WATCH TIME SUMMARY',
        'total_videos_in_history': 'Total videos in history',
        'videos_with_duration': 'Videos with known duration',
        'videos_without_duration': 'Videos without duration data',
        'total_time_known': 'Total time (known videos)',
        'average_duration_videos': 'Average video duration',
        'estimated_total_time': 'Estimated total time',
        'data_coverage': '📊 Data coverage: {percent:.1f}%',
        'duration_unknown_warning': '⚠️ Duration unknown for {count} videos',
        'estimated_time_note': '   Total time calculated using average duration estimate',
        
        # HTML report
        'generating_html': 'Generating HTML report...',
        'creating_plots': 'Creating plots...',
        'plots_saved': '✓ Plots saved',
        'html_saved': '✓ HTML report saved to: {path}',
        'youtube_analysis': 'YouTube History Analysis',
        'video_duration_statistics': 'Video Duration Statistics',
        'videos_with_duration': 'Videos with known duration',
        'videos_without_duration': 'Videos without duration data',
        'data_coverage': 'Data coverage',
        'average_duration': 'Average duration',
        'total_time_known_videos': 'Total time (known videos)',
        'estimated_total_time': 'Estimated total time',
        'duration_data_not_available': 'Video duration data was not obtained. Use the "Get video duration" function to analyze watch time.',
        
        # CSV export
        'exporting_csv': 'Exporting data to CSV...',
        'csv_saved': '✓ CSV file saved to: {path}',
        
        # Errors and warnings
        'error_loading_file': '❌ Error loading file: {error}',
        'error_processing': '❌ Error processing data: {error}',
        'error_api': '❌ YouTube API error: {error}',
        'error_creating_report': '❌ Error creating report: {error}',
        'no_data_loaded': '❌ No data loaded. Please load data from Takeout first.',
        'no_duration_data': '❌ No duration data found. Please get video duration first.',
        
        # API instructions
        'api_instructions_title': '📋 YouTube Data API Setup Instructions',
        'api_step_1': '1. Go to Google Cloud Console: https://console.cloud.google.com/',
        'api_step_2': '2. Create a new project or select existing one',
        'api_step_3': '3. Enable YouTube Data API v3',
        'api_step_4': '4. Create credentials (API key)',
        'api_step_5': '5. Copy the key to youtube_api_key.txt file',
        'api_quota_info': '📊 API quota: 10,000 units per day (1 unit per video)',
        'api_recommendation': '💡 Recommendation: start with 100-1000 video sample',
        
        # Time formatting
        'seconds': 'seconds',
        'minutes': 'minutes',
        'hours': 'hours',
        'time_format': '{hours}h {minutes}m {seconds}s',
        
        # CSV columns
        'csv_video_id': 'Video_ID',
        'csv_title': 'Video_Title',
        'csv_channel': 'Channel',
        'csv_url': 'Video_URL',
        'csv_date': 'Date_Format',
        'csv_time': 'Time_Format',
        'csv_day_of_week': 'Day_of_Week_EN',
        'csv_source': 'Data_Source',
        'csv_duration_seconds': 'Duration_Seconds',
        'csv_duration_formatted': 'Duration_Formatted',
        'csv_duration_minutes': 'Duration_Minutes',
        
        # CSV file description
        'csv_main_file_description': 'Main file with YouTube watch history data.',
        'csv_columns_header': '**Columns:**',
        'csv_video_id_desc': ' - unique video identifier',
        'csv_title_desc': ' - title of watched video',
        'csv_channel_desc': ' - channel name (Unknown = deleted/private channel)',
        'csv_url_desc': ' - direct link to video',
        'csv_date_desc': ' - date in YYYY-MM-DD format',
        'csv_time_desc': ' - time in HH:MM:SS format',
        'csv_source_desc': ' - data source (watch_history/my_activity)',
        'csv_datetime_utc_desc': ' - full date and time in UTC',
        'csv_summary_description': 'Summary statistics for all data.',
        'csv_html_description': 'HTML report with charts and visualization.',
        'csv_youtube_music_excluded': ' - YouTube Music: completely excluded',
        'csv_my_activity_desc': ' - My Activity: only "Watched" records (no likes, dislikes, search)',
        'csv_duplicates_desc': ' - Duplicates: automatically removed',
        'csv_unknown_channels_desc': ' - "Unknown" channels are deleted or private channels',
        'csv_time_utc_desc': ' - Time is in UTC',
        'csv_merged_sources_desc': ' - Data merged from two sources: watch history + My Activity',
        
        # Additional keys for CSV
        'youtube_history_export': 'YouTube History Export',
        'export_files': 'Export Files',
        'general_information': 'General Information',
        'notes': 'Notes',
        
        # Additional keys for CSV description
        'year_month_format': ' - year and month in YYYY-MM format',
        'day_of_week_format': ' - day of week in',
        'hour_format': ' - hour of viewing (0-23)',
        
        'main_statistics': 'Main Statistics',
        'top_channels': 'Top Channels',
        'parameter': 'Parameter',
        'value': 'Value',
        'channel': 'Channel',
        'video': 'Video',
        'sample_size_prompt': 'Sample size for duration analysis (default 100): ',
        'total_videos_label': 'Total Videos',
        'active_days_label': 'Active Days',
        'avg_videos_per_day_label': 'Average Videos per Day',
        'no_available_videos': 'No available videos with known channels!',
        'report_not_created': 'Report not created yet!',
        'no_files_loaded': 'Failed to load any files!',
        'program_interrupted': 'Program interrupted by user',
        'monthly_activity': 'Monthly Activity',
        'day_of_week_activity': 'Day of Week Activity',
        'hourly_activity': 'Hourly Activity',
        'cumulative_time': 'Cumulative Watch Time',
        'watch_time': 'Watch Time',
        'additional_statistics': 'Additional Statistics',
        'analysis_period': 'Analysis Period',
        'data_sources': 'Data Sources',
        'records': 'records',
        'export_summary': 'Export Summary',
        'unique_channels': 'Unique Channels',
        'file_ready_for_import': 'File ready for import to Excel/Google Sheets',
        'total_records': 'Total Records',
        'period': 'Period',
        'summary_statistics': 'Summary Statistics',
        'readme_file': 'README file',
        'csv_file_size': 'CSV file size',
        'error': 'Error',
        'month': 'Month',
        'video_count': 'Video Count',
        'day_of_week': 'Day of Week',
        'hour': 'Hour',
        'year_month': 'Year_Month',
        'hours_minutes': 'hours 0 minutes',
        'no_data_for_plots': 'No data for creating plots!',
        'unknown': 'Unknown',
        'datetime_utc': 'DateTime_UTC',
        'date': 'Date',
        'time_seconds': 'Time (seconds)',
        'year': 'Year',
        'day_of_week_en': 'Day_of_Week_EN',
        'top_10_channels': 'Top_10_Channels',
        'statistics_by_sources': 'Statistics_by_Sources',
        'statistics_by_days': 'Statistics_by_Days',
        'statistics_by_hours': 'Statistics_by_Hours',
        'general_statistics': 'General_Statistics',
        'total_records_key': 'Total_Records',
        'period_start': 'Period_Start',
        'period_end': 'Period_End',
        'days_count': 'Days_Count',
        
        # Days of week
        'monday': 'Monday',
        'tuesday': 'Tuesday',
        'wednesday': 'Wednesday',
        'thursday': 'Thursday',
        'friday': 'Friday',
        'saturday': 'Saturday',
        'sunday': 'Sunday',
        
        # Months
        'january': 'January',
        'february': 'February',
        'march': 'March',
        'april': 'April',
        'may': 'May',
        'june': 'June',
        'july': 'July',
        'august': 'August',
        'september': 'September',
        'october': 'October',
        'november': 'November',
        'december': 'December',
    }
}

def get_text(lang: str, key: str, **kwargs) -> str:
    """
    Получает текст на указанном языке с подстановкой параметров
    
    Args:
        lang: Код языка ('ru' или 'en')
        key: Ключ текста
        **kwargs: Параметры для подстановки в текст
    
    Returns:
        Текст на указанном языке с подставленными параметрами
    """
    if lang not in LOCALES:
        lang = 'en'  # Fallback to English
    
    if key not in LOCALES[lang]:
        # Fallback to English if key not found in current language
        if key in LOCALES['en']:
            return LOCALES['en'][key].format(**kwargs) if kwargs else LOCALES['en'][key]
        return key  # Return key if not found in any language
    
    text = LOCALES[lang][key]
    return text.format(**kwargs) if kwargs else text

def get_csv_columns(lang: str) -> dict:
    """
    Получает названия колонок CSV для указанного языка
    
    Args:
        lang: Код языка ('ru' или 'en')
    
    Returns:
        Словарь с названиями колонок
    """
    return {
        'video_id': get_text(lang, 'csv_video_id'),
        'title': get_text(lang, 'csv_title'),
        'channel': get_text(lang, 'csv_channel'),
        'url': get_text(lang, 'csv_url'),
        'date': get_text(lang, 'csv_date'),
        'time': get_text(lang, 'csv_time'),
        'day_of_week': get_text(lang, 'csv_day_of_week'),
        'source': get_text(lang, 'csv_source'),
        'duration_seconds': get_text(lang, 'csv_duration_seconds'),
        'duration_formatted': get_text(lang, 'csv_duration_formatted'),
        'duration_minutes': get_text(lang, 'csv_duration_minutes'),
    }

def get_day_of_week(lang: str, day_num: int) -> str:
    """
    Получает название дня недели на указанном языке
    
    Args:
        lang: Код языка ('ru' или 'en')
        day_num: Номер дня недели (0=понедельник, 6=воскресенье)
    
    Returns:
        Название дня недели на указанном языке
    """
    days = {
        0: 'monday',
        1: 'tuesday', 
        2: 'wednesday',
        3: 'thursday',
        4: 'friday',
        5: 'saturday',
        6: 'sunday'
    }
    
    if day_num in days:
        return get_text(lang, days[day_num])
    return str(day_num)

def get_month_name(lang: str, month_num: int) -> str:
    """
    Получает название месяца на указанном языке
    
    Args:
        lang: Код языка ('ru' или 'en')
        month_num: Номер месяца (1-12)
    
    Returns:
        Название месяца на указанном языке
    """
    months = {
        1: 'january',
        2: 'february',
        3: 'march',
        4: 'april',
        5: 'may',
        6: 'june',
        7: 'july',
        8: 'august',
        9: 'september',
        10: 'october',
        11: 'november',
        12: 'december'
    }
    
    if month_num in months:
        return get_text(lang, months[month_num])
    return str(month_num)
