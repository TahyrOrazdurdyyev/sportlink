import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:sportlink/core/services/tournament_service.dart';
import 'package:sportlink/core/network/api_client.dart';
import 'package:sportlink/core/l10n/app_localizations.dart';
import 'package:sportlink/core/providers/locale_provider.dart';
import 'package:sportlink/features/tournaments/presentation/screens/tournaments_list_screen.dart';

class MyTournamentsScreen extends ConsumerStatefulWidget {
  const MyTournamentsScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<MyTournamentsScreen> createState() => _MyTournamentsScreenState();
}

class _MyTournamentsScreenState extends ConsumerState<MyTournamentsScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final TournamentService _tournamentService = TournamentService(ApiClient().dio);
  
  List<TournamentRegistration> _allRegistrations = [];
  List<TournamentRegistration> _registeredTournaments = [];
  List<TournamentRegistration> _participatedTournaments = [];
  
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadRegistrations();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadRegistrations() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final registrations = await _tournamentService.getMyRegistrations();
      
      if (mounted) {
        setState(() {
          _allRegistrations = registrations;
          _registeredTournaments = registrations.where((r) => r.isUpcoming || r.isActive).toList();
          _participatedTournaments = registrations.where((r) => r.isPast).toList();
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
    final l10n = AppLocalizations.of(context);
    final locale = ref.watch(localeProvider);
    final currentLocale = locale.languageCode;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.translate('my_tournaments')),
        bottom: TabBar(
          controller: _tabController,
          tabs: [
            Tab(text: l10n.translate('registered_tournaments')),
            Tab(text: l10n.translate('participated_tournaments')),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.error_outline, size: 64, color: Colors.red[300]),
                      const SizedBox(height: 16),
                      Text(
                        _error!,
                        style: TextStyle(color: Colors.red[700]),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: _loadRegistrations,
                        child: Text(l10n.translate('refresh')),
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadRegistrations,
                  child: TabBarView(
                    controller: _tabController,
                    children: [
                      _buildRegisteredTournamentsList(l10n, currentLocale),
                      _buildParticipatedTournamentsList(l10n, currentLocale),
                    ],
                  ),
                ),
    );
  }

  Widget _buildRegisteredTournamentsList(AppLocalizations l10n, String locale) {
    if (_registeredTournaments.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.emoji_events_outlined, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text(
              l10n.translate('no_tournaments_registered'),
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey[600],
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () {
                Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (context) => const TournamentsListScreen(),
                  ),
                );
              },
              icon: const Icon(Icons.search),
              label: Text(l10n.translate('tournaments')),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _registeredTournaments.length,
      itemBuilder: (context, index) {
        final registration = _registeredTournaments[index];
        return _buildTournamentCard(registration, l10n, locale, isRegistered: true);
      },
    );
  }

  Widget _buildParticipatedTournamentsList(AppLocalizations l10n, String locale) {
    if (_participatedTournaments.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.history, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text(
              l10n.translate('no_tournaments_participated'),
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey[600],
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _participatedTournaments.length,
      itemBuilder: (context, index) {
        final registration = _participatedTournaments[index];
        return _buildTournamentCard(registration, l10n, locale, isRegistered: false);
      },
    );
  }

  Widget _buildTournamentCard(
    TournamentRegistration registration,
    AppLocalizations l10n,
    String locale,
    {required bool isRegistered}
  ) {
    // Use locale-specific date format
    final dateFormat = locale == 'ru' 
        ? DateFormat('dd MMM yyyy', 'ru')
        : locale == 'tk'
        ? DateFormat('dd MMM yyyy', 'tk')
        : DateFormat('dd MMM yyyy', 'en');
    final timeFormat = DateFormat('HH:mm');

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 2,
      child: InkWell(
        onTap: () {
          // Navigate to tournament details
          Navigator.of(context).push(
            MaterialPageRoute(
              builder: (context) => TournamentsListScreen(),
            ),
          );
        },
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Tournament Name
              Text(
                registration.getName(locale),
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              
              if (registration.description != null) ...[
                const SizedBox(height: 8),
                Text(
                  registration.getDescription(locale) ?? '',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.grey[600],
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],

              const SizedBox(height: 16),

              // Dates
              if (registration.startDate != null) ...[
                Row(
                  children: [
                    Icon(Icons.calendar_today, size: 16, color: Colors.grey[600]),
                    const SizedBox(width: 8),
                    Text(
                      '${l10n.translate('tournament_start')}: ${dateFormat.format(registration.startDate!)} ${timeFormat.format(registration.startDate!)}',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ),
                const SizedBox(height: 8),
              ],

              if (registration.endDate != null) ...[
                Row(
                  children: [
                    Icon(Icons.event, size: 16, color: Colors.grey[600]),
                    const SizedBox(width: 8),
                    Text(
                      '${l10n.translate('tournament_end')}: ${dateFormat.format(registration.endDate!)} ${timeFormat.format(registration.endDate!)}',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ),
                const SizedBox(height: 8),
              ],

              if (registration.registrationDate != null) ...[
                Row(
                  children: [
                    Icon(Icons.how_to_reg, size: 16, color: Colors.grey[600]),
                    const SizedBox(width: 8),
                    Text(
                      '${l10n.translate('registration_date')}: ${dateFormat.format(registration.registrationDate!)}',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ),
                const SizedBox(height: 12),
              ],

              // Status
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: _getStatusColor(registration.participantStatus).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: _getStatusColor(registration.participantStatus),
                        width: 1,
                      ),
                    ),
                    child: Text(
                      _getStatusLabel(registration.participantStatus, l10n),
                      style: TextStyle(
                        color: _getStatusColor(registration.participantStatus),
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                  const Spacer(),
                  if (isRegistered && registration.isActive)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: Colors.green.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: Colors.green, width: 1),
                      ),
                      child: Text(
                        l10n.translate('active'),
                        style: TextStyle(
                          color: Colors.green[700],
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'confirmed':
      case 'accepted':
        return Colors.green;
      case 'pending':
        return Colors.orange;
      case 'cancelled':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  String _getStatusLabel(String status, AppLocalizations l10n) {
    switch (status.toLowerCase()) {
      case 'confirmed':
        return l10n.translate('confirmed');
      case 'accepted':
        return l10n.translate('accepted');
      case 'pending':
        return l10n.translate('pending');
      case 'cancelled':
        return l10n.translate('cancelled');
      default:
        return status;
    }
  }
}

