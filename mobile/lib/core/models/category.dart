class Category {
  final String id;
  final Map<String, String> nameI18n;
  final Map<String, String>? descriptionI18n;
  final String? icon;

  Category({
    required this.id,
    required this.nameI18n,
    this.descriptionI18n,
    this.icon,
  });

  factory Category.fromJson(Map<String, dynamic> json) {
    return Category(
      id: json['id'] as String,
      nameI18n: Map<String, String>.from(json['name_i18n'] ?? {}),
      descriptionI18n: json['description_i18n'] != null
          ? Map<String, String>.from(json['description_i18n'])
          : null,
      icon: json['icon'] as String?,
    );
  }

  String getName(String locale) {
    return nameI18n[locale] ?? nameI18n['en'] ?? nameI18n['ru'] ?? '';
  }
}

