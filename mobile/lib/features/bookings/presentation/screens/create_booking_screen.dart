import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:dio/dio.dart';
import '../../../../core/models/court.dart';
import '../../../../core/services/booking_service.dart';
import '../../../../core/providers/locale_provider.dart';
import '../../../../core/l10n/app_localizations.dart';

class CreateBookingScreen extends ConsumerStatefulWidget {
  final Court court;

  const CreateBookingScreen({super.key, required this.court});

  @override
  ConsumerState<CreateBookingScreen> createState() => _CreateBookingScreenState();
}

class _CreateBookingScreenState extends ConsumerState<CreateBookingScreen> {
  final BookingService _bookingService = BookingService();
  final _notesController = TextEditingController();
  final Map<String, TextEditingController> _equipmentControllers = {};
  
  DateTime _selectedDate = DateTime.now();
  TimeOfDay _startTime = TimeOfDay.now();
  TimeOfDay _endTime = TimeOfDay(hour: TimeOfDay.now().hour + 1, minute: TimeOfDay.now().minute);
  
  int _numberOfPlayers = 1;
  bool _findOpponents = false;
  int _opponentsNeeded = 0;
  bool _equipmentNeeded = false;
  
  bool _isLoading = false;
  bool _checkingAvailability = false;
  bool? _isAvailable;
  
  @override
  void initState() {
    super.initState();
    _initializeEquipmentControllers();
  }
  
  void _initializeEquipmentControllers() {
    // Create controllers for each available equipment item
    final equipment = widget.court.getAvailableEquipment();
    for (var item in equipment) {
      _equipmentControllers[item.key] = TextEditingController(text: '0');
    }
  }

  @override
  void dispose() {
    _notesController.dispose();
    for (var controller in _equipmentControllers.values) {
      controller.dispose();
    }
    super.dispose();
  }

  DateTime _combineDateAndTime(DateTime date, TimeOfDay time) {
    return DateTime(date.year, date.month, date.day, time.hour, time.minute);
  }

  Future<void> _checkAvailability() async {
    final startDateTime = _combineDateAndTime(_selectedDate, _startTime);
    final endDateTime = _combineDateAndTime(_selectedDate, _endTime);

    if (endDateTime.isBefore(startDateTime) || endDateTime.isAtSameMomentAs(startDateTime)) {
      final l10n = AppLocalizations.of(context);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(l10n.translate('end_time_must_be_after_start'))),
      );
      return;
    }

    setState(() {
      _checkingAvailability = true;
      _isAvailable = null;
    });

    try {
      final available = await _bookingService.checkAvailability(
        courtId: widget.court.id,
        startTime: startDateTime,
        endTime: endDateTime,
      );
      
      if (mounted) {
        setState(() {
          _isAvailable = available;
          _checkingAvailability = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _checkingAvailability = false;
        });
        final l10n = AppLocalizations.of(context);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('${l10n.translate('error')}: $e')),
        );
      }
    }
  }

  Future<void> _createBooking() async {
    final l10n = AppLocalizations.of(context);
    final startDateTime = _combineDateAndTime(_selectedDate, _startTime);
    final endDateTime = _combineDateAndTime(_selectedDate, _endTime);

    if (endDateTime.isBefore(startDateTime) || endDateTime.isAtSameMomentAs(startDateTime)) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(l10n.translate('end_time_must_be_after_start'))),
      );
      return;
    }

    if (_isAvailable == false) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(l10n.translate('selected_time_not_available'))),
      );
      return;
    }

    // Validate opponents logic
    if (_findOpponents && _opponentsNeeded <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(l10n.translate('please_specify_opponents_needed'))),
      );
      return;
    }

    // Prepare equipment details if needed
    Map<String, int>? equipmentDetails;
    if (_equipmentNeeded) {
      // Only validate if court has available equipment
      if (widget.court.getAvailableEquipment().isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.translate('no_equipment_available'))),
        );
        return;
      }
      
      equipmentDetails = {};
      bool hasEquipment = false;
      
      for (var entry in _equipmentControllers.entries) {
        final quantity = int.tryParse(entry.value.text) ?? 0;
        if (quantity > 0) {
          equipmentDetails[entry.key] = quantity;
          hasEquipment = true;
        }
      }
      
      if (!hasEquipment) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.translate('please_specify_equipment'))),
        );
        return;
      }
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final booking = await _bookingService.createBooking(
        courtId: widget.court.id,
        startTime: startDateTime,
        endTime: endDateTime,
        numberOfPlayers: _numberOfPlayers,
        findOpponents: _findOpponents,
        opponentsNeeded: _findOpponents ? _opponentsNeeded : 0,
        equipmentNeeded: _equipmentNeeded,
        equipmentDetails: equipmentDetails,
        notes: _notesController.text.trim().isEmpty ? null : _notesController.text.trim(),
      );

      if (mounted) {
        // Check if opponents were found
        final matchesFound = booking.toJson()['matches_found'] as int? ?? 0;
        
        String successMessage = l10n.translate('booking_created_successfully');
        if (_findOpponents && matchesFound > 0) {
          successMessage += ' ${l10n.translate('opponents_found').replaceAll('{count}', matchesFound.toString())}';
        } else if (_findOpponents && matchesFound == 0) {
          successMessage += ' ${l10n.translate('no_opponents_found_yet')}';
        }
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(successMessage),
            duration: const Duration(seconds: 4),
          ),
        );
        Navigator.of(context).pop(true); // Return true to indicate success
      }
    } on DioException catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
        
        // Parse error message for better user feedback
        String errorMessage = 'Failed to create booking';
        
        // Try to get error from response
        if (e.response?.data != null) {
          final responseData = e.response!.data;
          if (responseData is Map) {
            errorMessage = responseData['error'] as String? ?? 
                          responseData['detail'] as String? ?? 
                          errorMessage;
            
            // Check validation errors
            if (responseData.containsKey('validation')) {
              final validation = responseData['validation'] as Map?;
              if (validation != null && validation.containsKey('errors')) {
                final errors = validation['errors'] as List?;
                if (errors != null && errors.isNotEmpty) {
                  final firstError = errors[0] as Map?;
                  if (firstError != null) {
                    final code = firstError['code'] as String? ?? '';
                    final msg = firstError['message'] as String? ?? '';
                    
                    // Map error codes to localized messages
                    if (code == 'WEEKLY_LIMIT_REACHED') {
                      errorMessage = l10n.translate('weekly_limit_reached');
                    } else if (code == 'DURATION_EXCEEDS_LIMIT') {
                      errorMessage = l10n.translate('duration_exceeds_limit');
                    } else if (code == 'DAY_NOT_ALLOWED') {
                      errorMessage = l10n.translate('day_not_allowed');
                    } else if (code == 'FEATURE_NOT_AVAILABLE') {
                      errorMessage = l10n.translate('subscription_does_not_include_court_booking');
                    } else if (code == 'TIME_SLOT_OCCUPIED' || code == 'COURT_NOT_AVAILABLE') {
                      errorMessage = l10n.translate('time_slot_not_available');
                    } else if (msg.isNotEmpty) {
                      errorMessage = msg;
                    }
                  }
                }
              }
            }
          }
        }
        
        // Fallback to checking error message string
        if (errorMessage == 'Failed to create booking') {
          final errorStr = e.toString();
          if (errorStr.contains('WEEKLY_LIMIT_REACHED')) {
            errorMessage = l10n.translate('weekly_limit_reached');
          } else if (errorStr.contains('DURATION_EXCEEDS_LIMIT')) {
            errorMessage = l10n.translate('duration_exceeds_limit');
          } else if (errorStr.contains('DAY_NOT_ALLOWED')) {
            errorMessage = l10n.translate('day_not_allowed');
          } else if (errorStr.contains('equipment_rental')) {
            errorMessage = l10n.translate('equipment_rental_not_included');
          }
        }
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(errorMessage)),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('${l10n.translate('error')}: ${e.toString()}')),
        );
      }
    }
  }

  Future<void> _selectDate() async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate,
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 90)),
    );
    
    if (picked != null && picked != _selectedDate) {
      setState(() {
        _selectedDate = picked;
        _isAvailable = null; // Reset availability when date changes
      });
    }
  }

  Future<void> _selectStartTime() async {
    final TimeOfDay? picked = await showTimePicker(
      context: context,
      initialTime: _startTime,
    );
    
    if (picked != null && picked != _startTime) {
      setState(() {
        _startTime = picked;
        _isAvailable = null; // Reset availability when time changes
      });
    }
  }

  Future<void> _selectEndTime() async {
    final TimeOfDay? picked = await showTimePicker(
      context: context,
      initialTime: _endTime,
    );
    
    if (picked != null && picked != _endTime) {
      setState(() {
        _endTime = picked;
        _isAvailable = null; // Reset availability when time changes
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final locale = ref.watch(localeProvider);
    final courtName = widget.court.nameI18n[locale.languageCode] ?? 
                      widget.court.nameI18n['en'] ?? 
                      'Unknown Court';
    final l10n = AppLocalizations.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.translate('book_court')),
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Court Info Card
            Card(
              elevation: 2,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      courtName,
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    if (widget.court.address != null) ...[
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          const Icon(Icons.location_on, size: 16, color: Colors.grey),
                          const SizedBox(width: 4),
                          Expanded(
                            child: Text(
                              widget.court.address!,
                              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: Colors.grey[600],
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 24),
            
            // Date Selection
            Text(
              l10n.translate('select_date'),
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            InkWell(
              onTap: _selectDate,
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey[300]!),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.calendar_today, color: Colors.blue),
                    const SizedBox(width: 12),
                    Text(
                      DateFormat('EEEE, MMMM d, yyyy').format(_selectedDate),
                      style: Theme.of(context).textTheme.bodyLarge,
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 24),
            
            // Time Selection
            Text(
              l10n.translate('select_time'),
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: InkWell(
                    onTap: _selectStartTime,
                    child: Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        border: Border.all(color: Colors.grey[300]!),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            l10n.translate('start_time'),
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: Colors.grey[600],
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            _startTime.format(context),
                            style: Theme.of(context).textTheme.titleMedium,
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: InkWell(
                    onTap: _selectEndTime,
                    child: Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        border: Border.all(color: Colors.grey[300]!),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            l10n.translate('end_time'),
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: Colors.grey[600],
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            _endTime.format(context),
                            style: Theme.of(context).textTheme.titleMedium,
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // Check Availability Button
            OutlinedButton.icon(
              onPressed: _checkingAvailability ? null : _checkAvailability,
              icon: _checkingAvailability 
                  ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.search),
              label: Text(_checkingAvailability ? l10n.translate('checking') : l10n.translate('check_availability')),
            ),
            
            if (_isAvailable != null) ...[
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: _isAvailable! ? Colors.green[50] : Colors.red[50],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: _isAvailable! ? Colors.green : Colors.red,
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      _isAvailable! ? Icons.check_circle : Icons.cancel,
                      color: _isAvailable! ? Colors.green : Colors.red,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _isAvailable! 
                            ? l10n.translate('time_slot_available')
                            : l10n.translate('time_slot_not_available'),
                        style: TextStyle(
                          color: _isAvailable! ? Colors.green[900] : Colors.red[900],
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
            
            const SizedBox(height: 24),
            
            // Number of Players
            Text(
              l10n.translate('number_of_players'),
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey[300]!),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  const Icon(Icons.people, color: Colors.blue),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      l10n.translate('how_many_people_in_group'),
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ),
                  IconButton(
                    onPressed: _numberOfPlayers > 1
                        ? () => setState(() => _numberOfPlayers--)
                        : null,
                    icon: const Icon(Icons.remove_circle_outline),
                    color: Colors.blue,
                  ),
                  Text(
                    '$_numberOfPlayers',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  IconButton(
                    onPressed: () => setState(() => _numberOfPlayers++),
                    icon: const Icon(Icons.add_circle_outline),
                    color: Colors.blue,
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 24),
            
            // Find Opponents
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey[300]!),
                borderRadius: BorderRadius.circular(8),
                color: _findOpponents ? Colors.blue[50] : null,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.person_search, color: Colors.blue),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          l10n.translate('find_opponents'),
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      Switch(
                        value: _findOpponents,
                        onChanged: (value) {
                          setState(() {
                            _findOpponents = value;
                            if (!value) _opponentsNeeded = 0;
                          });
                        },
                      ),
                    ],
                  ),
                  if (_findOpponents) ...[
                    const SizedBox(height: 12),
                    const Divider(),
                    const SizedBox(height: 12),
                    Text(
                      l10n.translate('how_many_opponents_needed'),
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        IconButton(
                          onPressed: _opponentsNeeded > 0
                              ? () => setState(() => _opponentsNeeded--)
                              : null,
                          icon: const Icon(Icons.remove_circle_outline),
                          color: Colors.blue,
                        ),
                        Text(
                          '$_opponentsNeeded',
                          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: Colors.blue,
                          ),
                        ),
                        IconButton(
                          onPressed: () => setState(() => _opponentsNeeded++),
                          icon: const Icon(Icons.add_circle_outline),
                          color: Colors.blue,
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            _opponentsNeeded > 0
                                ? l10n.translate('notify_when_opponents_found')
                                : l10n.translate('select_number_of_opponents'),
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: Colors.grey[600],
                              fontStyle: FontStyle.italic,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ],
              ),
            ),
            
            const SizedBox(height: 24),
            
            // Equipment Rental
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey[300]!),
                borderRadius: BorderRadius.circular(8),
                color: _equipmentNeeded ? Colors.orange[50] : null,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.sports, color: Colors.orange),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          l10n.translate('equipment_rental'),
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      Switch(
                        value: _equipmentNeeded,
                        onChanged: widget.court.getAvailableEquipment().isEmpty
                            ? null // Disable if no equipment available
                            : (value) {
                                setState(() {
                                  _equipmentNeeded = value;
                                  if (!value) {
                                    // Reset all equipment controllers
                                    for (var controller in _equipmentControllers.values) {
                                      controller.text = '0';
                                    }
                                  }
                                });
                              },
                      ),
                    ],
                  ),
                  if (widget.court.getAvailableEquipment().isEmpty) ...[
                    const SizedBox(height: 8),
                    Text(
                      l10n.translate('no_equipment_available'),
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Colors.grey[600],
                        fontStyle: FontStyle.italic,
                      ),
                    ),
                  ],
                  if (_equipmentNeeded && widget.court.getAvailableEquipment().isNotEmpty) ...[
                    const SizedBox(height: 12),
                    const Divider(),
                    const SizedBox(height: 12),
                    Text(
                      l10n.translate('specify_equipment_quantity'),
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 12),
                    ...widget.court.getAvailableEquipment().map((equipment) {
                      final locale = ref.watch(localeProvider);
                      final controller = _equipmentControllers[equipment.key]!;
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 12),
                        child: TextField(
                          controller: controller,
                          decoration: InputDecoration(
                            labelText: equipment.getName(locale.languageCode),
                            prefixIcon: const Icon(Icons.add_shopping_cart),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                            contentPadding: const EdgeInsets.symmetric(
                              horizontal: 12,
                              vertical: 16,
                            ),
                          ),
                          keyboardType: TextInputType.number,
                        ),
                      );
                    }).toList(),
                    const SizedBox(height: 8),
                    Text(
                      l10n.translate('equipment_depends_on_plan'),
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Colors.orange[900],
                        fontStyle: FontStyle.italic,
                      ),
                    ),
                  ],
                ],
              ),
            ),
            
            const SizedBox(height: 24),
            
            // Notes
            Text(
              l10n.translate('additional_notes'),
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _notesController,
              decoration: InputDecoration(
                hintText: l10n.translate('add_notes'),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              maxLines: 3,
            ),
            
            const SizedBox(height: 32),
            
            // Book Button
            ElevatedButton(
              onPressed: _isLoading ? null : _createBooking,
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: _isLoading
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                      ),
                    )
                  : Text(
                      l10n.translate('confirm_booking'),
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
            ),
          ],
        ),
      ),
    );
  }
}
