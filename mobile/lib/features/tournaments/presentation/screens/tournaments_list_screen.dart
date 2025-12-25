import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:sportlink/core/models/tournament.dart';
import 'package:sportlink/core/models/subscription_plan.dart';
import 'package:sportlink/core/services/tournament_service.dart';
import 'package:sportlink/core/services/subscription_service.dart';
import 'package:sportlink/core/network/api_client.dart';
import 'package:sportlink/core/providers/locale_provider.dart';

class TournamentsListScreen extends ConsumerStatefulWidget {
  const TournamentsListScreen({super.key});

  @override
  ConsumerState<TournamentsListScreen> createState() => _TournamentsListScreenState();
}

class _TournamentsListScreenState extends ConsumerState<TournamentsListScreen> {
  late TournamentService _tournamentService;
  late SubscriptionService _subscriptionService;
  List<Tournament> _tournaments = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    // Defer initialization until after first build
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final apiClient = ref.read(apiClientProvider);
      _tournamentService = TournamentService(apiClient.dio);
      _subscriptionService = SubscriptionService(apiClient.dio);
      _loadTournaments();
    });
  }

  Future<void> _loadTournaments() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final tournaments = await _tournamentService.getTournaments();
      if (mounted) {
        setState(() {
          _tournaments = tournaments;
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
    final locale = ref.watch(localeProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Tournaments'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadTournaments,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.error_outline, size: 64, color: Colors.red),
                        const SizedBox(height: 16),
                        Text(
                          _error!,
                          textAlign: TextAlign.center,
                          style: const TextStyle(color: Colors.red),
                        ),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: _loadTournaments,
                          child: const Text('Retry'),
                        ),
                      ],
                    ),
                  ),
                )
              : _tournaments.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.emoji_events_outlined,
                            size: 80,
                            color: Colors.grey[400],
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'No tournaments available',
                            style: TextStyle(
                              fontSize: 18,
                              color: Colors.grey[600],
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Check back later for upcoming tournaments',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey[500],
                            ),
                          ),
                        ],
                      ),
                    )
                  : RefreshIndicator(
                      onRefresh: _loadTournaments,
                      child: ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: _tournaments.length,
                        itemBuilder: (context, index) {
                          final tournament = _tournaments[index];
                          return _buildTournamentCard(tournament, locale);
                        },
                      ),
                    ),
    );
  }

  Widget _buildTournamentCard(Tournament tournament, Locale locale) {
    final DateFormat dateFormatter = DateFormat('dd MMM yyyy', locale.languageCode);
    final DateFormat timeFormatter = DateFormat('HH:mm', locale.languageCode);

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () => _showTournamentDetails(tournament, locale),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Tournament Image
            if (tournament.imageUrl != null && tournament.imageUrl!.isNotEmpty)
              Image.network(
                tournament.imageUrl!,
                width: double.infinity,
                height: 200,
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) {
                  return Container(
                    height: 200,
                    color: Colors.grey[300],
                    child: const Center(
                      child: Icon(Icons.broken_image, size: 48, color: Colors.grey),
                    ),
                  );
                },
                loadingBuilder: (context, child, loadingProgress) {
                  if (loadingProgress == null) return child;
                  return Container(
                    height: 200,
                    color: Colors.grey[200],
                    child: Center(
                      child: CircularProgressIndicator(
                        value: loadingProgress.expectedTotalBytes != null
                            ? loadingProgress.cumulativeBytesLoaded / loadingProgress.expectedTotalBytes!
                            : null,
                      ),
                    ),
                  );
                },
              ),

            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Header with status
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          tournament.getName(locale),
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                        decoration: BoxDecoration(
                          color: tournament.getStatusColor().withOpacity(0.1),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: tournament.getStatusColor()),
                        ),
                        child: Text(
                          tournament.getStatusLabel(),
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: tournament.getStatusColor(),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),

                  // Description
                  if (tournament.getDescription(locale).isNotEmpty) ...[
                    Text(
                      tournament.getDescription(locale),
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey[700],
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 12),
                  ],

              // Date and Location
              Row(
                children: [
                  Icon(Icons.calendar_today, size: 16, color: Colors.grey[600]),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      '${dateFormatter.format(tournament.startDate)} - ${dateFormatter.format(tournament.endDate)}',
                      style: TextStyle(fontSize: 13, color: Colors.grey[700]),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),

              if (tournament.city != null) ...[
                Row(
                  children: [
                    Icon(Icons.location_on, size: 16, color: Colors.grey[600]),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        '${tournament.city}${tournament.country != null ? ', ${tournament.country}' : ''}',
                        style: TextStyle(fontSize: 13, color: Colors.grey[700]),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
              ],

              // Participants
              Row(
                children: [
                  Icon(Icons.people, size: 16, color: Colors.grey[600]),
                  const SizedBox(width: 8),
                  Text(
                    '${tournament.participantCount}/${tournament.maxParticipants} participants',
                    style: TextStyle(fontSize: 13, color: Colors.grey[700]),
                  ),
                  if (tournament.canRegister()) ...[
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                      decoration: BoxDecoration(
                        color: Colors.green.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        '${tournament.getSpotsLeft()} spots left',
                        style: const TextStyle(
                          fontSize: 11,
                          color: Colors.green,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ],
              ),

              // Registration Fee
              if (tournament.registrationFee > 0) ...[
                const SizedBox(height: 8),
                Row(
                  children: [
                    Icon(Icons.attach_money, size: 16, color: Colors.grey[600]),
                    const SizedBox(width: 8),
                    Text(
                      'Registration Fee: ${tournament.registrationFee.toStringAsFixed(2)} TMT',
                      style: TextStyle(
                        fontSize: 13,
                        color: Colors.grey[700],
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ],

              // Registration Deadline
              if (tournament.registrationDeadline != null) ...[
                const SizedBox(height: 8),
                Row(
                  children: [
                    Icon(Icons.timer, size: 16, color: Colors.orange[700]),
                    const SizedBox(width: 8),
                    Text(
                      'Register by: ${dateFormatter.format(tournament.registrationDeadline!)}',
                      style: TextStyle(
                        fontSize: 13,
                        color: Colors.orange[700],
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ],

              // Action Buttons
              const SizedBox(height: 12),
              Row(
                children: [
                  // Details Button
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => _showTournamentDetails(tournament, locale),
                      icon: const Icon(Icons.info_outline, size: 18),
                      label: const Text('Details'),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                    ),
                  ),
                  
                  // Register Button (only if can register)
                  if (tournament.canRegister()) ...[
                    const SizedBox(width: 12),
                    Expanded(
                      flex: 2,
                      child: ElevatedButton.icon(
                        onPressed: () => _handleRegistration(tournament),
                        icon: const Icon(Icons.how_to_reg, size: 18),
                        label: const Text('Register'),
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 12),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                      ),
                    ),
                  ],
                ],
              ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showTournamentDetails(Tournament tournament, Locale locale) {
    final DateFormat fullDateFormatter = DateFormat('dd MMMM yyyy HH:mm', locale.languageCode);

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) {
        return DraggableScrollableSheet(
          initialChildSize: 0.7,
          minChildSize: 0.5,
          maxChildSize: 0.95,
          expand: false,
          builder: (BuildContext context, ScrollController scrollController) {
            return SingleChildScrollView(
              controller: scrollController,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Drag Handle
                  Center(
                    child: Container(
                      margin: const EdgeInsets.symmetric(vertical: 12),
                      width: 40,
                      height: 5,
                      decoration: BoxDecoration(
                        color: Colors.grey[300],
                        borderRadius: BorderRadius.circular(10),
                      ),
                    ),
                  ),

                  // Tournament Image
                  if (tournament.imageUrl != null && tournament.imageUrl!.isNotEmpty)
                    ClipRRect(
                      borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
                      child: Image.network(
                        tournament.imageUrl!,
                        width: double.infinity,
                        height: 250,
                        fit: BoxFit.cover,
                        errorBuilder: (context, error, stackTrace) {
                          return Container(
                            height: 250,
                            color: Colors.grey[300],
                            child: const Center(
                              child: Icon(Icons.broken_image, size: 64, color: Colors.grey),
                            ),
                          );
                        },
                        loadingBuilder: (context, child, loadingProgress) {
                          if (loadingProgress == null) return child;
                          return Container(
                            height: 250,
                            color: Colors.grey[200],
                            child: Center(
                              child: CircularProgressIndicator(
                                value: loadingProgress.expectedTotalBytes != null
                                    ? loadingProgress.cumulativeBytesLoaded / loadingProgress.expectedTotalBytes!
                                    : null,
                              ),
                            ),
                          );
                        },
                      ),
                    ),

                  Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Title and Status
                        Row(
                          children: [
                            Expanded(
                              child: Text(
                                tournament.getName(locale),
                                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                                      fontWeight: FontWeight.bold,
                                    ),
                              ),
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                              decoration: BoxDecoration(
                                color: tournament.getStatusColor().withOpacity(0.1),
                                borderRadius: BorderRadius.circular(20),
                                border: Border.all(color: tournament.getStatusColor()),
                              ),
                              child: Text(
                                tournament.getStatusLabel(),
                                style: TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.bold,
                                  color: tournament.getStatusColor(),
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),

                  // Description
                  if (tournament.getDescription(locale).isNotEmpty) ...[
                    Text(
                      tournament.getDescription(locale),
                      style: TextStyle(fontSize: 15, color: Colors.grey[700]),
                    ),
                    const SizedBox(height: 20),
                  ],

                  // Details
                  _buildDetailRow('Start Date', fullDateFormatter.format(tournament.startDate), Icons.calendar_today),
                  _buildDetailRow('End Date', fullDateFormatter.format(tournament.endDate), Icons.calendar_today),
                  if (tournament.registrationDeadline != null)
                    _buildDetailRow('Registration Deadline', fullDateFormatter.format(tournament.registrationDeadline!), Icons.timer),
                  if (tournament.city != null)
                    _buildDetailRow('Location', '${tournament.city}${tournament.country != null ? ', ${tournament.country}' : ''}', Icons.location_on),
                  if (tournament.organizerName != null)
                    _buildDetailRow('Organizer', tournament.organizerName!, Icons.business),
                  _buildDetailRow('Participants', '${tournament.participantCount}/${tournament.maxParticipants}', Icons.people),
                  if (tournament.registrationFee > 0)
                    _buildDetailRow('Registration Fee', '${tournament.registrationFee.toStringAsFixed(2)} TMT', Icons.attach_money),
                  
                  // External Registration Link
                  if (tournament.hasExternalRegistration())
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 8.0),
                      child: Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.blue.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: Colors.blue.withOpacity(0.3)),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.link, color: Colors.blue, size: 20),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Text(
                                    'External Registration',
                                    style: TextStyle(
                                      fontSize: 13,
                                      fontWeight: FontWeight.bold,
                                      color: Colors.blue,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    'Registration is handled by external organizer',
                                    style: TextStyle(
                                      fontSize: 12,
                                      color: Colors.grey[700],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),

                  // Categories
                  if (tournament.categories != null && tournament.categories!.isNotEmpty) ...[
                    const SizedBox(height: 20),
                    Text(
                      'Categories',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: tournament.categories!.map((category) {
                        return Chip(
                          label: Text(category),
                          backgroundColor: Colors.blue.withOpacity(0.1),
                        );
                      }).toList(),
                    ),
                  ],

                  // Rules
                  if (tournament.rules != null && tournament.rules!.isNotEmpty) ...[
                    const SizedBox(height: 20),
                    Text(
                      'Rules',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      tournament.rules!,
                      style: TextStyle(fontSize: 14, color: Colors.grey[700]),
                    ),
                  ],

                  // Register Button
                  if (tournament.canRegister()) ...[
                    const SizedBox(height: 24),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: () {
                          Navigator.pop(context);
                          _handleRegistration(tournament);
                        },
                        icon: const Icon(Icons.how_to_reg),
                        label: Text(tournament.hasExternalRegistration() 
                            ? 'Register (External Link)' 
                            : 'Register for Tournament'),
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                      ),
                    ),
                  ],
                      ],
                    ),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }

  Widget _buildDetailRow(String label, String value, IconData icon) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 20, color: Colors.grey[600]),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w500,
                    color: Colors.grey[600],
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  value,
                  style: const TextStyle(
                    fontSize: 15,
                    color: Colors.black87,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _handleRegistration(Tournament tournament) async {
    // Check if user has tournament_registration feature
    final hasAccess = await _checkTournamentRegistrationAccess();
    
    if (!hasAccess) {
      // Show upgrade dialog
      await _showUpgradeDialog();
      return;
    }

    if (tournament.hasExternalRegistration()) {
      // Open external registration link
      await _openExternalRegistration(tournament);
    } else {
      // Show internal registration dialog
      _showRegistrationDialog(tournament);
    }
  }

  Future<bool> _checkTournamentRegistrationAccess() async {
    try {
      return await _subscriptionService.hasFeature('tournament_registration');
    } catch (e) {
      // If error checking, assume no access
      return false;
    }
  }

  Future<void> _showUpgradeDialog() async {
    try {
      // Get plans that include tournament registration
      final plansWithFeature = await _subscriptionService.getPlansWithFeature('tournament_registration');
      
      if (!mounted) return;

      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: Row(
            children: [
              Icon(Icons.lock, color: Colors.orange[700]),
              const SizedBox(width: 12),
              const Expanded(child: Text('Subscription Required')),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Tournament registration is not included in your current plan.',
                style: TextStyle(fontSize: 15),
              ),
              const SizedBox(height: 16),
              if (plansWithFeature.isNotEmpty) ...[
                const Text(
                  'Available plans with tournament registration:',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
                const SizedBox(height: 12),
                ...plansWithFeature.map((plan) {
                  final locale = ref.read(localeProvider);
                  return Container(
                    margin: const EdgeInsets.only(bottom: 8),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.blue.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.blue.withOpacity(0.3)),
                    ),
                    child: Row(
                      children: [
                        Icon(Icons.check_circle, color: Colors.blue[700], size: 20),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                plan.getLocalizedName(locale.languageCode),
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 14,
                                ),
                              ),
                              Text(
                                '${plan.monthlyPrice} ${plan.currency}/month',
                                style: TextStyle(
                                  fontSize: 13,
                                  color: Colors.grey[700],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ],
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                Navigator.pushNamed(context, '/subscription');
              },
              child: const Text('View Plans'),
            ),
          ],
        ),
      );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error loading subscription plans: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _openExternalRegistration(Tournament tournament) async {
    final url = tournament.registrationLink!;
    
    try {
      final uri = Uri.parse(url);
      if (await canLaunchUrl(uri)) {
        await launchUrl(
          uri,
          mode: LaunchMode.externalApplication,
        );
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Could not open registration link: $url'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Invalid registration link: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _showRegistrationDialog(Tournament tournament) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Register for Tournament'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Do you want to register for "${tournament.getName(ref.read(localeProvider))}"?'),
            if (tournament.registrationFee > 0) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.orange.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.info_outline, color: Colors.orange),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Registration fee: ${tournament.registrationFee.toStringAsFixed(2)} TMT\nPayment details will be provided after registration.',
                        style: const TextStyle(fontSize: 13),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(context);
              await _registerForTournament(tournament);
            },
            child: const Text('Register'),
          ),
        ],
      ),
    );
  }

  Future<void> _registerForTournament(Tournament tournament) async {
    try {
      await _tournamentService.registerForTournament(tournament.id);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Successfully registered for tournament!'),
            backgroundColor: Colors.green,
          ),
        );
        _loadTournaments(); // Refresh list
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(e.toString()),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }
}

