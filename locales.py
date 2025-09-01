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
