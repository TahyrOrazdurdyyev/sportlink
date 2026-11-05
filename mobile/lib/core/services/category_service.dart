import 'package:dio/dio.dart';
import '../network/api_client.dart';
import '../models/category.dart';

class CategoryService {
  final ApiClient _apiClient = ApiClient();

  Future<List<Category>> getCategories() async {
    try {
      final response = await _apiClient.dio.get('/categories/');
      
      // Handle paginated response
      final data = response.data;
      final List<dynamic> results = data is Map 
          ? (data['results'] as List? ?? [])
          : (data as List? ?? []);
      
      return results.map((json) => Category.fromJson(json)).toList();
    } on DioException catch (e) {
      throw Exception('Failed to load categories: ${e.message}');
    }
  }
}

