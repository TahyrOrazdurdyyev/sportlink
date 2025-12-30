class Court {
  final String id;
  final Map<String, String> nameI18n;
  final Map<String, String>? descriptionI18n;
  final String? address;
  final List<double>? location;
  final String? type; // Category ID
  final double? pricePerHour;
  final List<String>? images;
  final Map<String, dynamic>? features;
  final bool? isActive;
  final CategoryInfo? categoryInfo; // Added category info with equipment

  Court({
    required this.id,
    required this.nameI18n,
    this.descriptionI18n,
    this.address,
    this.location,
    this.type,
    this.pricePerHour,
    this.images,
    this.features,
    this.isActive,
    this.categoryInfo,
  });

  factory Court.fromJson(Map<String, dynamic> json) {
    return Court(
      id: json['id'] as String,
      nameI18n: Map<String, String>.from(json['name_i18n'] ?? {}),
      descriptionI18n: json['description_i18n'] != null
          ? Map<String, String>.from(json['description_i18n'])
          : null,
      address: json['address'] as String?,
      location: json['location'] != null
          ? List<double>.from(json['location'] as List)
          : null,
      type: json['type'] as String?,
      pricePerHour: json['price_per_hour'] != null
          ? (json['price_per_hour'] as num).toDouble()
          : null,
      images: json['images'] != null
          ? List<String>.from(json['images'] as List)
          : null,
      features: json['features'] as Map<String, dynamic>?,
      isActive: json['is_active'] != null
          ? (json['is_active'] is bool 
              ? json['is_active'] as bool
              : (json['is_active'] as num) != 0)
          : null,
      categoryInfo: json['category_info'] != null
          ? CategoryInfo.fromJson(json['category_info'] as Map<String, dynamic>)
          : null,
    );
  }

  String getName(String locale) {
    return nameI18n[locale] ?? nameI18n['en'] ?? nameI18n['ru'] ?? '';
  }

  String? getDescription(String locale) {
    return descriptionI18n?[locale] ?? descriptionI18n?['en'] ?? descriptionI18n?['ru'];
  }
  
  List<EquipmentItem> getAvailableEquipment() {
    return categoryInfo?.availableEquipment ?? [];
  }
}

// Category info with equipment
class CategoryInfo {
  final String id;
  final Map<String, String> nameI18n;
  final List<EquipmentItem> availableEquipment;

  CategoryInfo({
    required this.id,
    required this.nameI18n,
    required this.availableEquipment,
  });

  factory CategoryInfo.fromJson(Map<String, dynamic> json) {
    final equipmentList = json['available_equipment'] as List? ?? [];
    return CategoryInfo(
      id: json['id'] as String,
      nameI18n: Map<String, String>.from(json['name_i18n'] ?? {}),
      availableEquipment: equipmentList
          .map((e) => EquipmentItem.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}

// Equipment item (e.g., "balls", "rackets", "shin guards")
class EquipmentItem {
  final String key; // e.g., "balls", "rackets"
  final Map<String, String> nameI18n; // e.g., {"en": "Balls", "ru": "Мячи", "tk": "Toplar"}

  EquipmentItem({
    required this.key,
    required this.nameI18n,
  });

  factory EquipmentItem.fromJson(Map<String, dynamic> json) {
    return EquipmentItem(
      key: json['key'] as String,
      nameI18n: Map<String, String>.from(json['name_i18n'] ?? {}),
    );
  }

  String getName(String locale) {
    return nameI18n[locale] ?? nameI18n['en'] ?? nameI18n['ru'] ?? key;
  }
}

