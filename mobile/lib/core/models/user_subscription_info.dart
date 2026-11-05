class UserSubscriptionInfo {
  final String id;
  final String planId;
  final Map<String, String> planName; // i18n map
  final Map<String, dynamic> planFeatures; // feature flags
  final DateTime? startDate;
  final DateTime? endDate;
  final String status;
  final String? paymentMethod;

  UserSubscriptionInfo({
    required this.id,
    required this.planId,
    required this.planName,
    required this.planFeatures,
    this.startDate,
    this.endDate,
    required this.status,
    this.paymentMethod,
  });

  factory UserSubscriptionInfo.fromJson(Map<String, dynamic> json) {
    return UserSubscriptionInfo(
      id: json['id'] as String,
      planId: json['plan_id'] as String,
      planName: json['plan_name'] != null
          ? Map<String, String>.from(json['plan_name'] as Map)
          : {'en': 'Unknown'},
      planFeatures: json['plan_features'] != null
          ? Map<String, dynamic>.from(json['plan_features'] as Map)
          : {},
      startDate: json['start_date'] != null
          ? DateTime.parse(json['start_date'] as String)
          : null,
      endDate: json['end_date'] != null
          ? DateTime.parse(json['end_date'] as String)
          : null,
      status: json['status'] as String,
      paymentMethod: json['payment_method'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'plan_id': planId,
      'plan_name': planName,
      'plan_features': planFeatures,
      'start_date': startDate?.toIso8601String(),
      'end_date': endDate?.toIso8601String(),
      'status': status,
      'payment_method': paymentMethod,
    };
  }

  bool get isActive => status == 'active' && (endDate?.isAfter(DateTime.now()) ?? false);
  
  int get daysRemaining {
    if (endDate == null) return 0;
    final diff = endDate!.difference(DateTime.now());
    return diff.inDays > 0 ? diff.inDays : 0;
  }
  
  String getLocalizedPlanName(String languageCode) {
    return planName[languageCode] ?? planName['en'] ?? 'Unknown Plan';
  }
  
  List<String> getFeaturesList() {
    return planFeatures.entries
        .where((entry) => entry.value == true)
        .map((entry) => entry.key.replaceAll('_', ' ').toUpperCase())
        .toList();
  }
  
  /// Get localized feature names for enabled features
  List<String> getLocalizedFeaturesList(String languageCode) {
    final featureNames = {
      'court_booking': {
        'en': 'Court Booking',
        'ru': 'Аренда площадки',
        'tk': 'Meýdança ärendasy',
      },
      'opponent_matching': {
        'en': 'Opponent Matching',
        'ru': 'Подбор соперника',
        'tk': 'Garşydaş gözleg',
      },
      'weekend_booking': {
        'en': 'Weekend Booking',
        'ru': 'Бронирование в выходные',
        'tk': 'Dynç günleri bronlaş',
      },
      'tournament_registration': {
        'en': 'Tournament Registration',
        'ru': 'Регистрация на турниры',
        'tk': 'Ýaryşlara gatnaşmak',
      },
      'equipment_rental': {
        'en': 'Equipment Rental',
        'ru': 'Аренда экипировки',
        'tk': 'Enjam ärendasy',
      },
      'advanced_statistics': {
        'en': 'Advanced Statistics',
        'ru': 'Расширенная статистика',
        'tk': 'Giňişleýin statistika',
      },
      'discount_court_booking': {
        'en': 'Court Booking Discount',
        'ru': 'Скидка на аренду',
        'tk': 'Arzanladyş (ärendä)',
      },
    };
    
    return planFeatures.entries
        .where((entry) => entry.value == true)
        .map((entry) {
          final featureKey = entry.key;
          final names = featureNames[featureKey];
          if (names != null) {
            return names[languageCode] ?? names['en'] ?? featureKey.replaceAll('_', ' ').toUpperCase();
          }
          return featureKey.replaceAll('_', ' ').toUpperCase();
        })
        .toList();
  }
}

