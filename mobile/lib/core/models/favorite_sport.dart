class FavoriteSport {
  final String categoryId;
  final int experienceLevel;
  final Map<String, String>? categoryName; // For displaying category name

  FavoriteSport({
    required this.categoryId,
    required this.experienceLevel,
    this.categoryName,
  });

  factory FavoriteSport.fromJson(Map<String, dynamic> json) {
    return FavoriteSport(
      categoryId: json['category_id'] as String,
      experienceLevel: (json['experience_level'] as num?)?.toInt() ?? 1,
      categoryName: json['category_name'] != null
          ? Map<String, String>.from(json['category_name'] as Map)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'category_id': categoryId,
      'experience_level': experienceLevel,
    };
  }

  FavoriteSport copyWith({
    String? categoryId,
    int? experienceLevel,
    Map<String, String>? categoryName,
  }) {
    return FavoriteSport(
      categoryId: categoryId ?? this.categoryId,
      experienceLevel: experienceLevel ?? this.experienceLevel,
      categoryName: categoryName ?? this.categoryName,
    );
  }
}

