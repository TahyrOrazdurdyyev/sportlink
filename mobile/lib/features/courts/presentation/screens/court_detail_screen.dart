import 'package:flutter/material.dart';

class CourtDetailScreen extends StatelessWidget {
  final String courtId;
  
  const CourtDetailScreen({super.key, required this.courtId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Court Details'),
      ),
      body: Center(
        child: Text('Court Detail Screen: $courtId'),
      ),
    );
  }
}

