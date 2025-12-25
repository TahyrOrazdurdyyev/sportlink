import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../../../core/models/court.dart';
import '../../../../core/models/subscription_plan.dart';
import '../../../../core/services/api_service.dart';
import '../../../../core/l10n/app_localizations.dart';
import '../../../auth/providers/auth_provider.dart';

class CreateBookingScreen extends ConsumerStatefulWidget {
  final Court court;

  const CreateBookingScreen({super.key, required this.court});

  @override
  ConsumerState<CreateBookingScreen> createState() => _CreateBookingScreenState();
}

class _CreateBookingScreenState extends ConsumerState<CreateBookingScreen> {
  DateTime? _selectedDate;
  TimeOfDay? _startTime;
  TimeOfDay? _endTime;
  int _numberOfPlayers = 1;
  bool _findOpponents = false;
  int _opponentsNeeded = 0;
  bool _equipmentNeeded = false;
  final Map<String, int> _equipmentDetails = {};
  String? _notes;
  bool _isLoading = false;
  String? _error;
  SubscriptionPlan? _userPlan;
  bool _hasEquipmentFeature = false;

  // Equipment items
  final Map<String, TextEditingController> _equipmentControllers = {
    'rackets': TextEditingController(text: '0'),
    'balls': TextEditingController(text: '0'),
  };

  @override
  void initState() {
    super.initState();
    _loadUserSubscription();
  }

  @override
  void dispose() {
    for (var controller in _equipmentControllers.values) {
      controller.dispose();
    }
    super.dispose();
  }

  Future<void> _loadUserSubscription() async {
    try {
      final authState = ref.read(authProvider);
      if (authState.user?.activeSubscription != null) {
        final apiService = ref.read(apiServiceProvider);
        final response = await apiService.get(
          '/subscriptions/plans/${authState.user!.activeSubscription!.planId}/',
        );
        
        if (response.statusCode == 200) {
          setState(() {
            _userPlan = SubscriptionPlan.fromJson(response.data);
            _hasEquipmentFeature = _userPlan?.features['equipment_rental'] ?? false;
          });
        }
      }
    } catch (e) {
      // Silently fail, user might not have subscription
    }
  }

  Future<void> _selectDate(BuildContext context) async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate ?? now,
      firstDate: now,
      lastDate: now.add(const Duration(days: 90)),
    );

    if (picked != null) {
      setState(() {
        _selectedDate = picked;
      });
    }
  }

  Future<void> _selectStartTime(BuildContext context) async {
    final picked = await showTimePicker(
      context: context,
      initialTime: _startTime ?? TimeOfDay.now(),
    );

    if (picked != null) {
      setState(() {
        _startTime = picked;
      });
    }
  }

  Future<void> _selectEndTime(BuildContext context) async {
    final picked = await showTimePicker(
      context: context,
      initialTime: _endTime ?? (_startTime ?? TimeOfDay.now()),
    );

    if (picked != null) {
      setState(() {
        _endTime = picked;
      });
    }
  }

  DateTime _combineDateTime(DateTime date, TimeOfDay time) {
    return DateTime(date.year, date.month, date.day, time.hour, time.minute);
  }

  Future<void> _showMatchedOpponentsDialog(List matchedOpponents) async {
    return showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(Icons.people, color: Theme.of(context).primaryColor),
            const SizedBox(width: 12),
            const Text('Opponent(s) Found!'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Great news! We found opponent(s) for your match:',
              style: TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 16),
            ...matchedOpponents.map((opponent) {
              final nickname = opponent['nickname'] as String;
              final firstName = opponent['first_name'] as String? ?? '';
              final lastName = opponent['last_name'] as String? ?? '';
              final fullName = '$firstName $lastName'.trim();

              return Card(
                color: Colors.green[50],
                child: ListTile(
                  leading: CircleAvatar(
                    backgroundColor: Colors.green,
                    child: Text(
                      nickname[0].toUpperCase(),
                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                    ),
                  ),
                  title: Text(
                    '@$nickname',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  subtitle: fullName.isNotEmpty ? Text(fullName) : null,
                ),
              );
            }).toList(),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.blue[50],
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  Icon(Icons.info_outline, color: Colors.blue[700]),
                  const SizedBox(width: 12),
                  const Expanded(
                    child: Text(
                      'Both you and your opponent(s) have been notified about the match!',
                      style: TextStyle(fontSize: 14),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Got it!'),
          ),
        ],
      ),
    );
  }

  Future<void> _createBooking() async {
    // Validation
    if (_selectedDate == null || _startTime == null || _endTime == null) {
      setState(() {
        _error = AppLocalizations.of(context).pleaseSelectDateTime;
      });
      return;
    }

    final startDateTime = _combineDateTime(_selectedDate!, _startTime!);
    final endDateTime = _combineDateTime(_selectedDate!, _endTime!);

    if (endDateTime.isBefore(startDateTime) || endDateTime.isAtSameMomentAs(startDateTime)) {
      setState(() {
        _error = AppLocalizations.of(context).endTimeMustBeAfterStart;
      });
      return;
    }

    if (_findOpponents && _opponentsNeeded <= 0) {
      setState(() {
        _error = AppLocalizations.of(context).pleaseSpecifyOpponentsNeeded;
      });
      return;
    }

    // Validate equipment
    if (_equipmentNeeded) {
      _equipmentDetails.clear();
      for (var entry in _equipmentControllers.entries) {
        final quantity = int.tryParse(entry.value.text) ?? 0;
        if (quantity > 0) {
          _equipmentDetails[entry.key] = quantity;
        }
      }

      if (_equipmentDetails.isEmpty) {
        setState(() {
          _error = AppLocalizations.of(context).pleaseSpecifyEquipment;
        });
        return;
      }
    }

    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final apiService = ref.read(apiServiceProvider);
      final payload = {
        'court': widget.court.id,
        'start_time': startDateTime.toIso8601String(),
        'end_time': endDateTime.toIso8601String(),
        'number_of_players': _numberOfPlayers,
        'find_opponents': _findOpponents,
        'opponents_needed': _findOpponents ? _opponentsNeeded : 0,
        'equipment_needed': _equipmentNeeded,
        'equipment_details': _equipmentNeeded ? _equipmentDetails : {},
        'notes': _notes,
      };

      final response = await apiService.post('/bookings/', data: payload);

      if (response.statusCode == 201) {
        if (mounted) {
          // Check if opponents were matched
          final matchesFound = response.data['matches_found'] as int?;
          final matchedOpponents = response.data['matched_opponents'] as List?;

          if (matchesFound != null && matchesFound > 0 && matchedOpponents != null) {
            // Show dialog with matched opponents
            await _showMatchedOpponentsDialog(matchedOpponents);
          }

          Navigator.pop(context, true); // Return true to indicate success
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(AppLocalizations.of(context).bookingCreatedSuccessfully),
              backgroundColor: Colors.green,
            ),
          );
        }
      } else {
        throw Exception(response.data['error'] ?? 'Failed to create booking');
      }
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final locale = Localizations.localeOf(context);
    final courtName = widget.court.getName(locale.languageCode);

    return Scaffold(
      appBar: AppBar(
        title: Text(AppLocalizations.of(context).createBooking),
        elevation: 0,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Court Info
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Row(
                        children: [
                          Icon(Icons.sports_tennis, color: Theme.of(context).primaryColor, size: 40),
                          const SizedBox(width: 16),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  courtName,
                                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                                ),
                                if (widget.court.location != null)
                                  Text(
                                    widget.court.location!,
                                    style: TextStyle(color: Colors.grey[600]),
                                  ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Date & Time Selection
                  Text(
                    AppLocalizations.of(context).dateAndTime,
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 12),
                  
                  // Date
                  ListTile(
                    leading: const Icon(Icons.calendar_today),
                    title: Text(_selectedDate != null
                        ? DateFormat('EEEE, MMMM d, yyyy').format(_selectedDate!)
                        : AppLocalizations.of(context).selectDate),
                    trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                    onTap: () => _selectDate(context),
                    tileColor: Colors.grey[100],
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                  const SizedBox(height: 12),

                  // Start Time
                  ListTile(
                    leading: const Icon(Icons.access_time),
                    title: Text(_startTime != null
                        ? '${AppLocalizations.of(context).startTime}: ${_startTime!.format(context)}'
                        : AppLocalizations.of(context).selectStartTime),
                    trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                    onTap: () => _selectStartTime(context),
                    tileColor: Colors.grey[100],
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                  const SizedBox(height: 12),

                  // End Time
                  ListTile(
                    leading: const Icon(Icons.access_time),
                    title: Text(_endTime != null
                        ? '${AppLocalizations.of(context).endTime}: ${_endTime!.format(context)}'
                        : AppLocalizations.of(context).selectEndTime),
                    trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                    onTap: () => _selectEndTime(context),
                    tileColor: Colors.grey[100],
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                  const SizedBox(height: 24),

                  // Number of Players
                  Text(
                    AppLocalizations.of(context).numberOfPlayers,
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      IconButton(
                        icon: const Icon(Icons.remove_circle_outline),
                        onPressed: _numberOfPlayers > 1
                            ? () => setState(() => _numberOfPlayers--)
                            : null,
                      ),
                      Text(
                        '$_numberOfPlayers',
                        style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                      ),
                      IconButton(
                        icon: const Icon(Icons.add_circle_outline),
                        onPressed: () => setState(() => _numberOfPlayers++),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),

                  // Find Opponents
                  Text(
                    AppLocalizations.of(context).findOpponents,
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 12),
                  SwitchListTile(
                    value: _findOpponents,
                    onChanged: (value) {
                      setState(() {
                        _findOpponents = value;
                        if (!value) _opponentsNeeded = 0;
                      });
                    },
                    title: Text(AppLocalizations.of(context).lookingForOpponents),
                    tileColor: Colors.grey[100],
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                  if (_findOpponents) ...[
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Text(AppLocalizations.of(context).opponentsNeeded),
                        const SizedBox(width: 16),
                        IconButton(
                          icon: const Icon(Icons.remove_circle_outline),
                          onPressed: _opponentsNeeded > 0
                              ? () => setState(() => _opponentsNeeded--)
                              : null,
                        ),
                        Text(
                          '$_opponentsNeeded',
                          style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                        ),
                        IconButton(
                          icon: const Icon(Icons.add_circle_outline),
                          onPressed: () => setState(() => _opponentsNeeded++),
                        ),
                      ],
                    ),
                  ],
                  const SizedBox(height: 24),

                  // Equipment Rental
                  Text(
                    AppLocalizations.of(context).equipmentRental,
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 12),
                  
                  if (!_hasEquipmentFeature)
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.orange[50],
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.orange[200]!),
                      ),
                      child: Row(
                        children: [
                          Icon(Icons.info_outline, color: Colors.orange[700]),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              AppLocalizations.of(context).equipmentNotInPlan,
                              style: TextStyle(color: Colors.orange[900]),
                            ),
                          ),
                        ],
                      ),
                    )
                  else ...[
                    SwitchListTile(
                      value: _equipmentNeeded,
                      onChanged: (value) {
                        setState(() {
                          _equipmentNeeded = value;
                        });
                      },
                      title: Text(AppLocalizations.of(context).needEquipment),
                      tileColor: Colors.grey[100],
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                    ),
                    if (_equipmentNeeded) ...[
                      const SizedBox(height: 16),
                      Card(
                        color: Colors.blue[50],
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                AppLocalizations.of(context).selectEquipment,
                                style: const TextStyle(fontWeight: FontWeight.bold),
                              ),
                              const SizedBox(height: 12),
                              _buildEquipmentField(
                                AppLocalizations.of(context).rackets,
                                'rackets',
                                Icons.sports_tennis,
                              ),
                              const SizedBox(height: 12),
                              _buildEquipmentField(
                                AppLocalizations.of(context).balls,
                                'balls',
                                Icons.sports_baseball,
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ],
                  const SizedBox(height: 24),

                  // Notes
                  Text(
                    AppLocalizations.of(context).notes,
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    decoration: InputDecoration(
                      hintText: AppLocalizations.of(context).addNotes,
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                      filled: true,
                      fillColor: Colors.grey[100],
                    ),
                    maxLines: 3,
                    onChanged: (value) => _notes = value.isEmpty ? null : value,
                  ),
                  const SizedBox(height: 24),

                  // Error Message
                  if (_error != null)
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.red[50],
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.red[200]!),
                      ),
                      child: Row(
                        children: [
                          Icon(Icons.error_outline, color: Colors.red[700]),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              _error!,
                              style: TextStyle(color: Colors.red[900]),
                            ),
                          ),
                        ],
                      ),
                    ),
                  const SizedBox(height: 24),

                  // Create Button
                  SizedBox(
                    width: double.infinity,
                    height: 50,
                    child: ElevatedButton(
                      onPressed: _createBooking,
                      style: ElevatedButton.styleFrom(
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                      child: Text(
                        AppLocalizations.of(context).createBooking,
                        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ),
                  const SizedBox(height: 32),
                ],
              ),
            ),
    );
  }

  Widget _buildEquipmentField(String label, String key, IconData icon) {
    return Row(
      children: [
        Icon(icon, color: Theme.of(context).primaryColor),
        const SizedBox(width: 12),
        Expanded(
          child: Text(label, style: const TextStyle(fontSize: 16)),
        ),
        SizedBox(
          width: 80,
          child: TextField(
            controller: _equipmentControllers[key],
            keyboardType: TextInputType.number,
            textAlign: TextAlign.center,
            decoration: InputDecoration(
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
              contentPadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
              filled: true,
              fillColor: Colors.white,
            ),
          ),
        ),
      ],
    );
  }
}

