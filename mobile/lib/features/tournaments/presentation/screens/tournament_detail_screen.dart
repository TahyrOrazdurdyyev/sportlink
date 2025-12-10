import 'package:flutter/material.dart';

class TournamentDetailScreen extends StatelessWidget {
  final String tournamentId;
  
  const TournamentDetailScreen({super.key, required this.tournamentId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Tournament Details'),
      ),
      body: Center(
        child: Text('Tournament Detail Screen: $tournamentId'),
      ),
    );
  }
}

