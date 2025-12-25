import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/models/court.dart';
import '../../../../core/services/court_service.dart';

class CourtDetailScreen extends ConsumerStatefulWidget {
  final String courtId;
  
  const CourtDetailScreen({super.key, required this.courtId});

  @override
  ConsumerState<CourtDetailScreen> createState() => _CourtDetailScreenState();
}

class _CourtDetailScreenState extends ConsumerState<CourtDetailScreen> {
  Court? _court;
  bool _isLoading = true;
  String? _error;
  final CourtService _courtService = CourtService();

  @override
  void initState() {
    super.initState();
    _loadCourt();
  }

  Future<void> _loadCourt() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final court = await _courtService.getCourtById(widget.courtId);
      if (mounted) {
        setState(() {
          _court = court;
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
        title: Text(_court?.name ?? 'Court Details'),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text('Error: $_error'))
              : _court == null
                  ? const Center(child: Text('Court not found'))
                  : SingleChildScrollView(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            _court!.name,
                            style: Theme.of(context).textTheme.headlineSmall,
                          ),
                          const SizedBox(height: 16),
                          if (_court!.description != null) ...[
                            Text(_court!.description!),
                            const SizedBox(height: 16),
                          ],
                          ElevatedButton(
                            onPressed: () {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('Booking coming soon!')),
                              );
                            },
                            child: const Text('Book Now'),
                          ),
                        ],
                      ),
                    ),
    );
  }
}

