import 'package:dio/dio.dart';
import 'package:sportlink/core/models/tournament.dart';

class TournamentService {
  final Dio dio;

  TournamentService(this.dio);

  /// Get all tournaments (public access)
  Future<List<Tournament>> getTournaments() async {
    try {
      final response = await dio.get('/tournaments/');
      
      if (response.data is Map && response.data['results'] != null) {
        // Paginated response
        final results = response.data['results'] as List;
        return results.map((json) => Tournament.fromJson(json)).toList();
      } else if (response.data is List) {
        // Direct list response
        return (response.data as List).map((json) => Tournament.fromJson(json)).toList();
      } else {
        return [];
      }
    } on DioException catch (e) {
      throw Exception('Failed to load tournaments: ${e.message}');
    }
  }

  /// Get tournament by ID
  Future<Tournament> getTournamentById(String id) async {
    try {
      final response = await dio.get('/tournaments/$id/');
      return Tournament.fromJson(response.data);
    } on DioException catch (e) {
      throw Exception('Failed to load tournament: ${e.message}');
    }
  }

  /// Register for tournament (requires authentication)
  Future<void> registerForTournament(String tournamentId, {String? notes}) async {
    try {
      await dio.post(
        '/tournaments/$tournamentId/register/',
        data: {
          if (notes != null) 'notes': notes,
        },
      );
    } on DioException catch (e) {
      if (e.response?.data != null && e.response?.data is Map) {
        final errorData = e.response?.data as Map;
        throw Exception(errorData['error'] ?? 'Failed to register for tournament');
      }
      throw Exception('Failed to register for tournament: ${e.message}');
    }
  }

  /// Cancel tournament registration (requires authentication)
  Future<void> cancelRegistration(String tournamentId) async {
    try {
      await dio.post('/tournaments/$tournamentId/cancel-registration/');
    } on DioException catch (e) {
      if (e.response?.data != null && e.response?.data is Map) {
        final errorData = e.response?.data as Map;
        throw Exception(errorData['error'] ?? 'Failed to cancel registration');
      }
      throw Exception('Failed to cancel registration: ${e.message}');
    }
  }

  /// Get my tournament registrations (requires authentication)
  Future<List<TournamentRegistration>> getMyRegistrations() async {
    try {
      final response = await dio.get('/tournaments/my-registrations/');
      
      if (response.data is Map && response.data['tournaments'] != null) {
        final tournaments = response.data['tournaments'] as List;
        return tournaments.map((json) => TournamentRegistration.fromJson(json)).toList();
      }
      return [];
    } on DioException catch (e) {
      throw Exception('Failed to load registrations: ${e.message}');
    }
  }
}

/// Tournament registration model
class TournamentRegistration {
  final String id;
  final Map<String, String> name;
  final Map<String, String>? description;
  final DateTime? startDate;
  final DateTime? endDate;
  final String tournamentStatus;
  final String participantStatus;
  final DateTime? registrationDate;

  TournamentRegistration({
    required this.id,
    required this.name,
    this.description,
    this.startDate,
    this.endDate,
    required this.tournamentStatus,
    required this.participantStatus,
    this.registrationDate,
  });

  factory TournamentRegistration.fromJson(Map<String, dynamic> json) {
    return TournamentRegistration(
      id: json['id'] as String,
      name: Map<String, String>.from(json['name'] ?? {}),
      description: json['description'] != null 
          ? Map<String, String>.from(json['description'] ?? {})
          : null,
      startDate: json['start_date'] != null
          ? DateTime.parse(json['start_date'] as String)
          : null,
      endDate: json['end_date'] != null
          ? DateTime.parse(json['end_date'] as String)
          : null,
      tournamentStatus: json['status'] as String? ?? 'unknown',
      participantStatus: json['participant_status'] as String? ?? 'pending',
      registrationDate: json['registration_date'] != null
          ? DateTime.parse(json['registration_date'] as String)
          : null,
    );
  }

  String getName(String locale) {
    return name[locale] ?? name['en'] ?? name['ru'] ?? name['tk'] ?? 'Unknown';
  }

  String? getDescription(String locale) {
    if (description == null) return null;
    return description![locale] ?? description!['en'] ?? description!['ru'] ?? description!['tk'];
  }

  bool get isUpcoming {
    if (startDate == null) return false;
    return startDate!.isAfter(DateTime.now());
  }

  bool get isPast {
    if (endDate == null) return false;
    return endDate!.isBefore(DateTime.now());
  }

  bool get isActive {
    if (startDate == null || endDate == null) return false;
    final now = DateTime.now();
    return now.isAfter(startDate!) && now.isBefore(endDate!);
  }
}

