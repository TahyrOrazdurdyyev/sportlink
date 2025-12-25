import 'package:sportlink/core/models/favorite_sport.dart';

class UserModel {
  final String id;
  final String phone;
  final String? nickname;
  final String? email;
  final String? firstName;
  final String? lastName;
  final DateTime? birthDate;
  final int? age;
  final String? gender;
  final String? city;
  final List<double>? location;
  final List<FavoriteSport> favoriteSports;
  final int experienceLevel;
  final String? preferredBall;
  final List<String> goals;
  final double rating;
  final String? avatarUrl;
  
  UserModel({
    required this.id,
    required this.phone,
    this.nickname,
    this.email,
    this.firstName,
    this.lastName,
    this.birthDate,
    this.age,
    this.gender,
    this.city,
    this.location,
    this.favoriteSports = const [],
    this.experienceLevel = 1,
    this.preferredBall,
    this.goals = const [],
    this.rating = 0.0,
    this.avatarUrl,
  });
  
  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] as String,
      phone: json['phone'] as String,
      nickname: json['nickname'] as String?,
      email: json['email'] as String?,
      firstName: json['first_name'] as String?,
      lastName: json['last_name'] as String?,
      birthDate: json['birth_date'] != null
          ? DateTime.parse(json['birth_date'] as String)
          : null,
      age: (json['age'] as num?)?.toInt(),
      gender: json['gender'] as String?,
      city: json['city'] as String?,
      location: json['location'] != null
          ? List<double>.from(json['location'] as List)
          : null,
      favoriteSports: json['favorite_sports'] != null
          ? (json['favorite_sports'] as List)
              .map((sport) => FavoriteSport.fromJson(sport as Map<String, dynamic>))
              .toList()
          : [],
      experienceLevel: (json['experience_level'] as num?)?.toInt() ?? 1,
      preferredBall: json['preferred_ball'] as String?,
      goals: json['goals'] != null
          ? List<String>.from(json['goals'] as List)
          : [],
      rating: (json['rating'] as num?)?.toDouble() ?? 0.0,
      avatarUrl: json['avatar_url'] as String?,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'phone': phone,
      'nickname': nickname,
      'email': email,
      'first_name': firstName,
      'last_name': lastName,
      'birth_date': birthDate?.toIso8601String(),
      'age': age,
      'gender': gender,
      'city': city,
      'location': location,
      'favorite_sports': favoriteSports.map((sport) => sport.toJson()).toList(),
      'experience_level': experienceLevel,
      'preferred_ball': preferredBall,
      'goals': goals,
      'rating': rating,
      'avatar_url': avatarUrl,
    };
  }
  
  UserModel copyWith({
    String? id,
    String? phone,
    String? nickname,
    String? email,
    String? firstName,
    String? lastName,
    DateTime? birthDate,
    int? age,
    String? gender,
    String? city,
    List<double>? location,
    List<FavoriteSport>? favoriteSports,
    int? experienceLevel,
    String? preferredBall,
    List<String>? goals,
    double? rating,
    String? avatarUrl,
  }) {
    return UserModel(
      id: id ?? this.id,
      phone: phone ?? this.phone,
      nickname: nickname ?? this.nickname,
      email: email ?? this.email,
      firstName: firstName ?? this.firstName,
      lastName: lastName ?? this.lastName,
      birthDate: birthDate ?? this.birthDate,
      age: age ?? this.age,
      gender: gender ?? this.gender,
      city: city ?? this.city,
      location: location ?? this.location,
      favoriteSports: favoriteSports ?? this.favoriteSports,
      experienceLevel: experienceLevel ?? this.experienceLevel,
      preferredBall: preferredBall ?? this.preferredBall,
      goals: goals ?? this.goals,
      rating: rating ?? this.rating,
      avatarUrl: avatarUrl ?? this.avatarUrl,
    );
  }
}

