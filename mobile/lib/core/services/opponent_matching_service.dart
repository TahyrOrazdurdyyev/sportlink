import 'package:dio/dio.dart';
import '../models/opponent.dart';

class OpponentMatchingService {
  final Dio _dio;

  OpponentMatchingService(this._dio);

  // Найти соперников
  Future<List<Opponent>> findOpponents({
    int? experienceLevel,
    String? categoryId,
    String? city,
    int limit = 20,
  }) async {
    try {
      final params = <String, dynamic>{
        'limit': limit,
        if (experienceLevel != null) 'experience_level': experienceLevel,
        if (categoryId != null) 'category_id': categoryId,
        if (city != null) 'city': city,
      };

      final response = await _dio.get(
        '/users/find-opponents/',
        queryParameters: params,
      );

      return (response.data['results'] as List)
          .map((json) => Opponent.fromJson(json))
          .toList();
    } catch (e) {
      if (e is DioException && e.response?.statusCode == 403) {
        throw FeatureNotAvailableException(
          'Opponent matching requires subscription',
          'opponent_matching',
        );
      }
      throw Exception('Failed to find opponents: $e');
    }
  }

  // Отправить приглашение
  Future<void> sendMatchInvitation({
    required String opponentId,
    String? courtId,
    DateTime? proposedTime,
    String? message,
  }) async {
    try {
      await _dio.post(
        '/users/match-invitation/',
        data: {
          'opponent_id': opponentId,
          if (courtId != null) 'court_id': courtId,
          if (proposedTime != null)
            'proposed_time': proposedTime.toIso8601String(),
          if (message != null) 'message': message,
        },
      );
    } catch (e) {
      if (e is DioException && e.response?.statusCode == 403) {
        throw FeatureNotAvailableException(
          'Sending invitations requires subscription',
          'opponent_matching',
        );
      }
      throw Exception('Failed to send invitation: $e');
    }
  }
}

class FeatureNotAvailableException implements Exception {
  final String message;
  final String featureKey;

  FeatureNotAvailableException(this.message, this.featureKey);

  @override
  String toString() => message;
}

