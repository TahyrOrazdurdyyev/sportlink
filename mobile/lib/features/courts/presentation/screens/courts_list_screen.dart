import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/models/court.dart';
import '../../../../core/services/court_service.dart';
import '../../../../core/l10n/app_localizations.dart';
import 'court_detail_screen.dart';

class CourtsListScreen extends ConsumerStatefulWidget {
  const CourtsListScreen({super.key});

  @override
  ConsumerState<CourtsListScreen> createState() => _CourtsListScreenState();
}

class _CourtsListScreenState extends ConsumerState<CourtsListScreen> {
  List<Court> _courts = [];
  bool _isLoading = true;
  String? _error;
  final CourtService _courtService = CourtService();

  @override
  void initState() {
    super.initState();
    _loadCourts();
  }

  Future<void> _loadCourts() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final courts = await _courtService.getCourts();
      if (mounted) {
        setState(() {
          _courts = courts;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Courts'),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text('Error: $_error'))
              : _courts.isEmpty
                  ? const Center(child: Text('No courts available'))
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: _courts.length,
                      itemBuilder: (context, index) {
                        final court = _courts[index];
                        return Card(
                          margin: const EdgeInsets.only(bottom: 16),
                          child: ListTile(
                            title: Text(court.name),
                            subtitle: Text(court.description ?? ''),
                            trailing: const Icon(Icons.arrow_forward_ios),
                            onTap: () {
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (context) => CourtDetailScreen(courtId: court.id),
                                ),
                              );
                            },
                          ),
                        );
                      },
                    ),
    );
  }
}
