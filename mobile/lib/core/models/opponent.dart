class Opponent {
  final String id;
  final String firstName;
  final String lastName;
  final String? avatarUrl;
  final int experienceLevel;
  final double rating;
  final String? city;
  final List<OpponentCategory> categories;
  final int compatibilityScore;
  final DateTime? lastActive;

  Opponent({
    required this.id,
    required this.firstName,
    required this.lastName,
    this.avatarUrl,
    required this.experienceLevel,
    required this.rating,
    this.city,
    required this.categories,
    required this.compatibilityScore,
    this.lastActive,
  });

  factory Opponent.fromJson(Map<String, dynamic> json) {
    return Opponent(
      id: json['id'],
      firstName: json['first_name'] ?? '',
      lastName: json['last_name'] ?? '',
      avatarUrl: json['avatar_url'],
      experienceLevel: json['experience_level'] ?? 1,
      rating: (json['rating'] as num?)?.toDouble() ?? 0.0,
      city: json['city'],
      categories: (json['categories'] as List?)
              ?.map((c) => OpponentCategory.fromJson(c))
              .toList() ??
          [],
      compatibilityScore: json['compatibility_score'] ?? 0,
      lastActive: json['last_active'] != null
          ? DateTime.parse(json['last_active'])
          : null,
    );
  }

  String get fullName => '$firstName $lastName'.trim();

  String get experienceLevelName {
    const levels = [
      'Beginner',
      'Novice',
      'Intermediate',
      'Advanced',
      'Expert',
      'Professional',
      'Master'
    ];
    if (experienceLevel >= 1 && experienceLevel <= 7) {
      return levels[experienceLevel - 1];
    }
    return 'Unknown';
  }
}

class OpponentCategory {
  final String id;
  final String name;

  OpponentCategory({
    required this.id,
    required this.name,
  });

  factory OpponentCategory.fromJson(Map<String, dynamic> json) {
    return OpponentCategory(
      id: json['id'],
      name: json['name'],
    );
  }
}

