import 'package:flutter/material.dart';

class Tournament {
  final String id;
  final Map<String, String> nameI18n;
  final Map<String, String> descriptionI18n;
  final String? imageUrl;
  final String? locationDescription;
  final String? country;
  final String? city;
  final String? organizerName;
  final String? registrationLink;
  final DateTime startDate;
  final DateTime endDate;
  final DateTime? registrationDeadline;
  final int maxParticipants;
  final int minParticipants;
  final bool registrationOpen;
  final double registrationFee;
  final String status;
  final int participantCount;
  final List<String>? categories;
  final String? rules;
  final Map<String, dynamic>? prizes;

  Tournament({
    required this.id,
    required this.nameI18n,
    required this.descriptionI18n,
    this.imageUrl,
    this.locationDescription,
    this.country,
    this.city,
    this.organizerName,
    this.registrationLink,
    required this.startDate,
    required this.endDate,
    this.registrationDeadline,
    required this.maxParticipants,
    required this.minParticipants,
    required this.registrationOpen,
    required this.registrationFee,
    required this.status,
    required this.participantCount,
    this.categories,
    this.rules,
    this.prizes,
  });

  factory Tournament.fromJson(Map<String, dynamic> json) {
    return Tournament(
      id: json['id'] as String,
      nameI18n: Map<String, String>.from(json['name_i18n'] ?? {}),
      descriptionI18n: Map<String, String>.from(json['description_i18n'] ?? {}),
      imageUrl: json['image_url'] as String?,
      locationDescription: json['location_description'] as String?,
      country: json['country'] as String?,
      city: json['city'] as String?,
      organizerName: json['organizer_name'] as String?,
      registrationLink: json['registration_link'] as String?,
      startDate: DateTime.parse(json['start_date'] as String),
      endDate: DateTime.parse(json['end_date'] as String),
      registrationDeadline: json['registration_deadline'] != null
          ? DateTime.parse(json['registration_deadline'] as String)
          : null,
      maxParticipants: (json['max_participants'] as num).toInt(),
      minParticipants: (json['min_participants'] as num?)?.toInt() ?? 2,
      registrationOpen: json['registration_open'] as bool? ?? false,
      registrationFee: (json['registration_fee'] as num?)?.toDouble() ?? 0.0,
      status: json['status'] as String? ?? 'draft',
      participantCount: (json['participant_count'] as num?)?.toInt() ?? 0,
      categories: (json['categories'] as List?)?.map((e) => e as String).toList(),
      rules: json['rules'] as String?,
      prizes: json['prizes'] as Map<String, dynamic>?,
    );
  }

  String getName(Locale locale) {
    return nameI18n[locale.languageCode] ?? nameI18n['en'] ?? nameI18n['ru'] ?? 'Unknown Tournament';
  }

  String getDescription(Locale locale) {
    return descriptionI18n[locale.languageCode] ?? descriptionI18n['en'] ?? descriptionI18n['ru'] ?? '';
  }

  String getStatusLabel() {
    switch (status) {
      case 'draft':
        return 'Draft';
      case 'open':
        return 'Registration Open';
      case 'closed':
        return 'Registration Closed';
      case 'in_progress':
        return 'In Progress';
      case 'completed':
        return 'Completed';
      case 'cancelled':
        return 'Cancelled';
      default:
        return status;
    }
  }

  Color getStatusColor() {
    switch (status) {
      case 'open':
        return Colors.green;
      case 'closed':
        return Colors.orange;
      case 'in_progress':
        return Colors.blue;
      case 'completed':
        return Colors.grey;
      case 'cancelled':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  bool canRegister() {
    if (!registrationOpen) return false;
    if (status != 'open' && status != 'draft') return false;
    if (registrationDeadline != null && DateTime.now().isAfter(registrationDeadline!)) return false;
    if (participantCount >= maxParticipants) return false;
    return true;
  }

  int getSpotsLeft() {
    return maxParticipants - participantCount;
  }

  bool hasExternalRegistration() {
    return registrationLink != null && registrationLink!.isNotEmpty;
  }
}

