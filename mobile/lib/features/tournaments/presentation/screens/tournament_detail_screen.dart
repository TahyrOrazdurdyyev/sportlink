import 'package:flutter/material.dart';
import 'package:sportlink/core/l10n/app_localizations.dart';

class TournamentDetailScreen extends StatelessWidget {
  final String tournamentId;
  
  const TournamentDetailScreen({super.key, required this.tournamentId});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    
    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.translate('tournament_details')),
      ),
      body: Center(
        child: Text('Tournament Detail Screen: $tournamentId'),
      ),
    );
  }
}

