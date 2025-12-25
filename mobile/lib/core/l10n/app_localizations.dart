import 'package:flutter/material.dart';

class AppLocalizations {
  final Locale locale;

  AppLocalizations(this.locale);

  static AppLocalizations of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations)!;
  }

  static const LocalizationsDelegate<AppLocalizations> delegate = _AppLocalizationsDelegate();

  static final Map<String, Map<String, String>> _localizedValues = {
    'en': {
      'app_name': 'Sportlink',
      'login': 'Login',
      'sign_up': 'Sign Up',
      'first_name': 'First Name',
      'last_name': 'Last Name',
      'nickname': 'Nickname',
      'phone': 'Phone Number',
      'password': 'Password',
      'confirm_password': 'Confirm Password',
      'login_placeholder': 'Phone or Nickname',
      'nickname_helper': 'Unique username',
      'phone_helper': 'Format: +99365532570',
      'password_requirements': 'Min 8 characters, letters, numbers, symbols',
      'passwords_dont_match': 'Passwords do not match',
      'weak_password': 'Password must contain at least 8 characters, including letters, numbers and symbols',
      'login_button': 'Login',
      'signup_button': 'Sign Up',
      'all_fields_required': 'All fields are required',
      
      // Settings
      'settings_title': 'Settings',
      'notifications_section': 'Notifications',
      'push_notifications': 'Push Notifications',
      'push_notifications_subtitle': 'Receive notifications about bookings',
      'location_section': 'Location',
      'location_services': 'Location Services',
      'location_services_subtitle': 'Allow app to access your location',
      'language_section': 'Language',
      'language_label': 'Language',
      'select_language': 'Select Language',
      'account_section': 'Account',
      'change_password': 'Change Password',
      'privacy_policy': 'Privacy Policy',
      'terms_of_service': 'Terms of Service',
      'about_section': 'About',
      'app_version': 'App Version',
      'coming_soon': 'Coming soon!',
      
      // Booking
      'create_booking': 'Create Booking',
      'date_and_time': 'Date & Time',
      'select_date': 'Select Date',
      'select_start_time': 'Select Start Time',
      'select_end_time': 'Select End Time',
      'start_time': 'Start Time',
      'end_time': 'End Time',
      'number_of_players': 'Number of Players',
      'find_opponents': 'Find Opponents',
      'looking_for_opponents': 'Looking for opponents',
      'opponents_needed': 'Opponents Needed',
      'equipment_rental': 'Equipment Rental',
      'need_equipment': 'I need equipment',
      'equipment_not_in_plan': 'Equipment rental is not included in your subscription plan',
      'select_equipment': 'Select Equipment',
      'rackets': 'Rackets',
      'balls': 'Balls',
      'notes': 'Notes',
      'add_notes': 'Add notes (optional)',
      'please_select_date_time': 'Please select date and time',
      'end_time_must_be_after_start': 'End time must be after start time',
      'please_specify_opponents_needed': 'Please specify number of opponents needed',
      'please_specify_equipment': 'Please specify equipment quantity',
      'booking_created_successfully': 'Booking created successfully!',
      'booking_restrictions': 'Booking Restrictions',
      'bookings_per_week': 'bookings per week',
      'max_duration': 'Max duration',
      'hours': 'hours',
      'allowed_days': 'Allowed days',
    },
    'ru': {
      'app_name': 'Sportlink',
      'login': 'Вход',
      'sign_up': 'Регистрация',
      'first_name': 'Имя',
      'last_name': 'Фамилия',
      'nickname': 'Никнейм',
      'phone': 'Номер телефона',
      'password': 'Пароль',
      'confirm_password': 'Повторите пароль',
      'login_placeholder': 'Телефон или никнейм',
      'nickname_helper': 'Уникальное имя пользователя',
      'phone_helper': 'Формат: +99365532570',
      'password_requirements': 'Мин. 8 символов, буквы, цифры, символы',
      'passwords_dont_match': 'Пароли не совпадают',
      'weak_password': 'Пароль должен содержать минимум 8 символов, включая буквы, цифры и символы',
      'login_button': 'Войти',
      'signup_button': 'Зарегистрироваться',
      'all_fields_required': 'Все поля обязательны',
      
      // Settings
      'settings_title': 'Настройки',
      'notifications_section': 'Уведомления',
      'push_notifications': 'Push-уведомления',
      'push_notifications_subtitle': 'Получать уведомления о бронированиях',
      'location_section': 'Местоположение',
      'location_services': 'Службы геолокации',
      'location_services_subtitle': 'Разрешить приложению доступ к вашему местоположению',
      'language_section': 'Язык',
      'language_label': 'Язык',
      'select_language': 'Выберите язык',
      'account_section': 'Аккаунт',
      'change_password': 'Изменить пароль',
      'privacy_policy': 'Политика конфиденциальности',
      'terms_of_service': 'Условия использования',
      'about_section': 'О приложении',
      'app_version': 'Версия приложения',
      'coming_soon': 'Скоро будет!',
      
      // Booking
      'create_booking': 'Создать бронирование',
      'date_and_time': 'Дата и время',
      'select_date': 'Выберите дату',
      'select_start_time': 'Выберите время начала',
      'select_end_time': 'Выберите время окончания',
      'start_time': 'Время начала',
      'end_time': 'Время окончания',
      'number_of_players': 'Количество игроков',
      'find_opponents': 'Найти соперников',
      'looking_for_opponents': 'Ищу соперников',
      'opponents_needed': 'Нужно соперников',
      'equipment_rental': 'Аренда экипировки',
      'need_equipment': 'Нужна экипировка',
      'equipment_not_in_plan': 'Аренда экипировки не включена в ваш тарифный план',
      'select_equipment': 'Выберите экипировку',
      'rackets': 'Ракетки',
      'balls': 'Мячи',
      'notes': 'Заметки',
      'add_notes': 'Добавить заметки (необязательно)',
      'please_select_date_time': 'Пожалуйста, выберите дату и время',
      'end_time_must_be_after_start': 'Время окончания должно быть после времени начала',
      'please_specify_opponents_needed': 'Пожалуйста, укажите количество нужных соперников',
      'please_specify_equipment': 'Пожалуйста, укажите количество экипировки',
      'booking_created_successfully': 'Бронирование успешно создано!',
      'booking_restrictions': 'Ограничения бронирования',
      'bookings_per_week': 'бронирований в неделю',
      'max_duration': 'Макс. длительность',
      'hours': 'часов',
      'allowed_days': 'Разрешенные дни',
    },
    'tk': {
      'app_name': 'Sportlink',
      'login': 'Giriş',
      'sign_up': 'Hasaba al',
      'first_name': 'Ady',
      'last_name': 'Familiýasy',
      'nickname': 'Lakamy',
      'phone': 'Telefon nomeri',
      'password': 'Parol',
      'confirm_password': 'Paroly gaýtalaň',
      'login_placeholder': 'Telefon ýa-da lakam',
      'nickname_helper': 'Üýtgeşik ulanyjy ady',
      'phone_helper': 'Format: +99365532570',
      'password_requirements': 'Min 8 nyşan, harplar, sanlar, simwollar',
      'passwords_dont_match': 'Parollar gabat gelmeýär',
      'weak_password': 'Parol azyndan 8 nyşany öz içine almalydyr, şol sanda harplar, sanlar we simwollar',
      'login_button': 'Gir',
      'signup_button': 'Hasaba al',
      'all_fields_required': 'Ähli meýdançalar hökmany',
      
      // Settings
      'settings_title': 'Sazlamalar',
      'notifications_section': 'Habarnamalar',
      'push_notifications': 'Push habarnamalary',
      'push_notifications_subtitle': 'Bronlaşlar barada habarnamalary almak',
      'location_section': 'Ýerleşiş',
      'location_services': 'Ýerleşiş hyzmatlary',
      'location_services_subtitle': 'Programmanyň ýerleşişiňize girmegine rugsat beriň',
      'language_section': 'Dil',
      'language_label': 'Dil',
      'select_language': 'Dili saýlaň',
      'account_section': 'Hasap',
      'change_password': 'Paroly üýtget',
      'privacy_policy': 'Gizlinlik syýasaty',
      'terms_of_service': 'Ulanyş şertleri',
      'about_section': 'Programma hakda',
      'app_version': 'Programma wersiýasy',
      'coming_soon': 'Geljekde!',
      
      // Booking
      'create_booking': 'Bronlaş döret',
      'date_and_time': 'Sene we wagt',
      'select_date': 'Senäni saýlaň',
      'select_start_time': 'Başlangyç wagtyny saýlaň',
      'select_end_time': 'Gutaryş wagtyny saýlaň',
      'start_time': 'Başlangyç wagty',
      'end_time': 'Gutaryş wagty',
      'number_of_players': 'Oýunçylaryň sany',
      'find_opponents': 'Garşydaşlary tap',
      'looking_for_opponents': 'Garşydaş gözleýärin',
      'opponents_needed': 'Garşydaş gerek',
      'equipment_rental': 'Enjam kärendesi',
      'need_equipment': 'Enjam gerek',
      'equipment_not_in_plan': 'Enjam kärendesi siziň tarif meýilnamaňyza girmeýär',
      'select_equipment': 'Enjamy saýlaň',
      'rackets': 'Raketler',
      'balls': 'Toplar',
      'notes': 'Bellikler',
      'add_notes': 'Bellik goş (hökmany däl)',
      'please_select_date_time': 'Senäni we wagty saýlaň',
      'end_time_must_be_after_start': 'Gutaryş wagty başlangyç wagtyndan soň bolmaly',
      'please_specify_opponents_needed': 'Gerekli garşydaşlaryň sanyny görkeziň',
      'please_specify_equipment': 'Enjamyň mukdaryny görkeziň',
      'booking_created_successfully': 'Bronlaş üstünlikli döredildi!',
      'booking_restrictions': 'Bronlaş çäklendirmeleri',
      'bookings_per_week': 'hepdede bronlaş',
      'max_duration': 'Maks. dowamlylygy',
      'hours': 'sagat',
      'allowed_days': 'Rugsat berlen günler',
    },
  };

  String translate(String key) {
    return _localizedValues[locale.languageCode]?[key] ?? key;
  }

  String get appName => translate('app_name');
  String get login => translate('login');
  String get signUp => translate('sign_up');
  String get firstName => translate('first_name');
  String get lastName => translate('last_name');
  String get nickname => translate('nickname');
  String get phone => translate('phone');
  String get password => translate('password');
  String get confirmPassword => translate('confirm_password');
  String get loginPlaceholder => translate('login_placeholder');
  String get nicknameHelper => translate('nickname_helper');
  String get phoneHelper => translate('phone_helper');
  String get passwordRequirements => translate('password_requirements');
  String get passwordsDontMatch => translate('passwords_dont_match');
  String get weakPassword => translate('weak_password');
  String get loginButton => translate('login_button');
  String get signupButton => translate('signup_button');
  String get allFieldsRequired => translate('all_fields_required');
  
  // Settings
  String get settingsTitle => translate('settings_title');
  String get notificationsSection => translate('notifications_section');
  String get pushNotifications => translate('push_notifications');
  String get pushNotificationsSubtitle => translate('push_notifications_subtitle');
  String get locationSection => translate('location_section');
  String get locationServices => translate('location_services');
  String get locationServicesSubtitle => translate('location_services_subtitle');
  String get languageSection => translate('language_section');
  String get languageLabel => translate('language_label');
  String get selectLanguage => translate('select_language');
  String get accountSection => translate('account_section');
  String get changePassword => translate('change_password');
  String get privacyPolicy => translate('privacy_policy');
  String get termsOfService => translate('terms_of_service');
  String get aboutSection => translate('about_section');
  String get appVersion => translate('app_version');
  String get comingSoon => translate('coming_soon');
  
  // Booking
  String get createBooking => translate('create_booking');
  String get dateAndTime => translate('date_and_time');
  String get selectDate => translate('select_date');
  String get selectStartTime => translate('select_start_time');
  String get selectEndTime => translate('select_end_time');
  String get startTime => translate('start_time');
  String get endTime => translate('end_time');
  String get numberOfPlayers => translate('number_of_players');
  String get findOpponents => translate('find_opponents');
  String get lookingForOpponents => translate('looking_for_opponents');
  String get opponentsNeeded => translate('opponents_needed');
  String get equipmentRental => translate('equipment_rental');
  String get needEquipment => translate('need_equipment');
  String get equipmentNotInPlan => translate('equipment_not_in_plan');
  String get selectEquipment => translate('select_equipment');
  String get rackets => translate('rackets');
  String get balls => translate('balls');
  String get notes => translate('notes');
  String get addNotes => translate('add_notes');
  String get pleaseSelectDateTime => translate('please_select_date_time');
  String get endTimeMustBeAfterStart => translate('end_time_must_be_after_start');
  String get pleaseSpecifyOpponentsNeeded => translate('please_specify_opponents_needed');
  String get pleaseSpecifyEquipment => translate('please_specify_equipment');
  String get bookingCreatedSuccessfully => translate('booking_created_successfully');
  String get bookingRestrictions => translate('booking_restrictions');
  String get bookingsPerWeek => translate('bookings_per_week');
  String get maxDuration => translate('max_duration');
  String get hours => translate('hours');
  String get allowedDays => translate('allowed_days');
}

class _AppLocalizationsDelegate extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) {
    return ['en', 'ru', 'tk'].contains(locale.languageCode);
  }

  @override
  Future<AppLocalizations> load(Locale locale) async {
    return AppLocalizations(locale);
  }

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

