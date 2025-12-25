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
}

