class UserModel {
  final String id;
  final String phone;
  final String? email;
  final String? firstName;
  final String? lastName;
  final DateTime? birthDate;
  final String? gender;
  final String? city;
  final List<double>? location;
  final int experienceLevel;
  final String? preferredBall;
  final List<String> goals;
  final double rating;
  final String? avatarUrl;
  final List<String> categories;
  
  UserModel({
    required this.id,
    required this.phone,
    this.email,
    this.firstName,
    this.lastName,
    this.birthDate,
    this.gender,
    this.city,
    this.location,
    this.experienceLevel = 1,
    this.preferredBall,
    this.goals = const [],
    this.rating = 0.0,
    this.avatarUrl,
    this.categories = const [],
  });
  
  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] as String,
      phone: json['phone'] as String,
      email: json['email'] as String?,
      firstName: json['first_name'] as String?,
      lastName: json['last_name'] as String?,
      birthDate: json['birth_date'] != null
          ? DateTime.parse(json['birth_date'] as String)
          : null,
      gender: json['gender'] as String?,
      city: json['city'] as String?,
      location: json['location'] != null
          ? List<double>.from(json['location'] as List)
          : null,
      experienceLevel: json['experience_level'] as int? ?? 1,
      preferredBall: json['preferred_ball'] as String?,
      goals: json['goals'] != null
          ? List<String>.from(json['goals'] as List)
          : [],
      rating: (json['rating'] as num?)?.toDouble() ?? 0.0,
      avatarUrl: json['avatar_url'] as String?,
      categories: json['categories'] != null
          ? List<String>.from(json['categories'] as List)
          : [],
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'phone': phone,
      'email': email,
      'first_name': firstName,
      'last_name': lastName,
      'birth_date': birthDate?.toIso8601String(),
      'gender': gender,
      'city': city,
      'location': location,
      'experience_level': experienceLevel,
      'preferred_ball': preferredBall,
      'goals': goals,
      'rating': rating,
      'avatar_url': avatarUrl,
      'categories': categories,
    };
  }
}

