import 'package:dio/dio.dart';
import '../network/api_client.dart';
import '../models/court.dart';

class CourtService {
  final ApiClient _apiClient = ApiClient();

  Future<List<Court>> getCourts({String? categoryId}) async {
    try {
      final queryParams = categoryId != null ? {'type': categoryId} : null;
      final response = await _apiClient.dio.get('/courts/', queryParameters: queryParams);
      
      // Handle paginated response
      final data = response.data;
      final List<dynamic> results = data is Map 
          ? (data['results'] as List? ?? [])
          : (data as List? ?? []);
      
      return results.map((json) => Court.fromJson(json)).toList();
    } on DioException catch (e) {
      throw Exception('Failed to load courts: ${e.message}');
    }
  }

  Future<Court> getCourtById(String id) async {
    try {
      final response = await _apiClient.dio.get('/courts/$id/');
      return Court.fromJson(response.data);
    } on DioException catch (e) {
      throw Exception('Failed to load court: ${e.message}');
    }
  }
}

