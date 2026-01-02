import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sportlink/core/models/availability_schedule.dart';
import 'package:sportlink/core/l10n/app_localizations.dart';
import 'package:sportlink/core/providers/locale_provider.dart';
import 'package:sportlink/features/auth/data/repositories/auth_repository.dart';
import 'package:sportlink/features/auth/data/models/user_model.dart';

class AvailabilityScheduleScreen extends ConsumerStatefulWidget {
  final UserModel user;

  const AvailabilityScheduleScreen({Key? key, required this.user}) : super(key: key);

  @override
  ConsumerState<AvailabilityScheduleScreen> createState() => _AvailabilityScheduleScreenState();
}

class _AvailabilityScheduleScreenState extends ConsumerState<AvailabilityScheduleScreen> {
  late List<DayAvailability> _schedule;
  bool _isSaving = false;

  final List<String> _daysOfWeek = [
    'monday',
    'tuesday',
    'wednesday',
    'thursday',
    'friday',
    'saturday',
    'sunday',
  ];

  @override
  void initState() {
    super.initState();
    _initializeSchedule();
  }

  void _initializeSchedule() {
    if (widget.user.availabilitySchedule.isNotEmpty) {
      _schedule = widget.user.availabilitySchedule.map((day) => day.copyWith()).toList();
    } else {
      // Initialize with default schedule (all days unavailable)
      _schedule = _daysOfWeek.map((day) {
        return DayAvailability(
          day: day,
          isAvailable: false,
          timeSlots: [],
        );
      }).toList();
    }
  }

  Future<void> _saveSchedule() async {
    setState(() {
      _isSaving = true;
    });

    try {
      final authRepo = ref.read(authRepositoryProvider);
      final updatedUser = await authRepo.updateUserProfile({
        'availability_schedule': _schedule.map((day) => day.toJson()).toList(),
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Schedule saved successfully'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.pop(context, updatedUser); // Return updated user model
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to save schedule: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSaving = false;
        });
      }
    }
  }

  void _toggleDayAvailability(int index) {
    setState(() {
      _schedule[index] = _schedule[index].copyWith(
        isAvailable: !_schedule[index].isAvailable,
      );
    });
  }

  void _addTimeSlot(int dayIndex) {
    setState(() {
      final currentSlots = List<TimeSlot>.from(_schedule[dayIndex].timeSlots);
      currentSlots.add(TimeSlot(startTime: '09:00', endTime: '18:00'));
      _schedule[dayIndex] = _schedule[dayIndex].copyWith(timeSlots: currentSlots);
    });
  }

  void _removeTimeSlot(int dayIndex, int slotIndex) {
    setState(() {
      final currentSlots = List<TimeSlot>.from(_schedule[dayIndex].timeSlots);
      currentSlots.removeAt(slotIndex);
      _schedule[dayIndex] = _schedule[dayIndex].copyWith(timeSlots: currentSlots);
    });
  }

  Future<void> _editTimeSlot(int dayIndex, int slotIndex) async {
    final slot = _schedule[dayIndex].timeSlots[slotIndex];
    
    final result = await showDialog<Map<String, String>>(
      context: context,
      builder: (context) => _TimeSlotDialog(
        startTime: slot.startTime,
        endTime: slot.endTime,
      ),
    );

    if (result != null) {
      setState(() {
        final currentSlots = List<TimeSlot>.from(_schedule[dayIndex].timeSlots);
        currentSlots[slotIndex] = TimeSlot(
          startTime: result['startTime']!,
          endTime: result['endTime']!,
        );
        _schedule[dayIndex] = _schedule[dayIndex].copyWith(timeSlots: currentSlots);
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final locale = ref.watch(localeProvider).languageCode;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.translate('availability_schedule')),
        actions: [
          if (_isSaving)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(16.0),
                child: SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              ),
            )
          else
            IconButton(
              icon: const Icon(Icons.save),
              onPressed: _saveSchedule,
            ),
        ],
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _schedule.length,
        itemBuilder: (context, index) {
          final dayAvailability = _schedule[index];
          return _buildDayCard(dayAvailability, index, locale);
        },
      ),
    );
  }

  Widget _buildDayCard(DayAvailability dayAvailability, int index, String locale) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    dayAvailability.getLocalizedDayName(locale),
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Switch(
                  value: dayAvailability.isAvailable,
                  onChanged: (_) => _toggleDayAvailability(index),
                  activeColor: Colors.green,
                ),
              ],
            ),
            if (dayAvailability.isAvailable) ...[
              const SizedBox(height: 16),
              const Divider(),
              const SizedBox(height: 8),
              if (dayAvailability.timeSlots.isEmpty)
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  child: Text(
                    'Available all day',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey[600],
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                )
              else
                ...dayAvailability.timeSlots.asMap().entries.map((entry) {
                  final slotIndex = entry.key;
                  final slot = entry.value;
                  return _buildTimeSlotItem(index, slotIndex, slot);
                }).toList(),
              const SizedBox(height: 8),
              OutlinedButton.icon(
                onPressed: () => _addTimeSlot(index),
                icon: const Icon(Icons.add, size: 18),
                label: const Text('Add Time Slot'),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildTimeSlotItem(int dayIndex, int slotIndex, TimeSlot slot) {
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
          const Icon(Icons.access_time, size: 20, color: Colors.blue),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              '${slot.startTime} - ${slot.endTime}',
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.edit, size: 20),
            onPressed: () => _editTimeSlot(dayIndex, slotIndex),
            padding: EdgeInsets.zero,
            constraints: const BoxConstraints(),
          ),
          const SizedBox(width: 8),
          IconButton(
            icon: const Icon(Icons.delete, size: 20, color: Colors.red),
            onPressed: () => _removeTimeSlot(dayIndex, slotIndex),
            padding: EdgeInsets.zero,
            constraints: const BoxConstraints(),
          ),
        ],
      ),
    );
  }
}

class _TimeSlotDialog extends StatefulWidget {
  final String startTime;
  final String endTime;

  const _TimeSlotDialog({
    required this.startTime,
    required this.endTime,
  });

  @override
  State<_TimeSlotDialog> createState() => _TimeSlotDialogState();
}

class _TimeSlotDialogState extends State<_TimeSlotDialog> {
  late TextEditingController _startController;
  late TextEditingController _endController;

  @override
  void initState() {
    super.initState();
    _startController = TextEditingController(text: widget.startTime);
    _endController = TextEditingController(text: widget.endTime);
  }

  @override
  void dispose() {
    _startController.dispose();
    _endController.dispose();
    super.dispose();
  }

  Future<void> _pickTime(TextEditingController controller) async {
    final parts = controller.text.split(':');
    final initialTime = TimeOfDay(
      hour: int.tryParse(parts[0]) ?? 9,
      minute: int.tryParse(parts[1]) ?? 0,
    );

    final time = await showTimePicker(
      context: context,
      initialTime: initialTime,
    );

    if (time != null) {
      controller.text = '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Edit Time Slot'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          TextField(
            controller: _startController,
            decoration: const InputDecoration(
              labelText: 'Start Time',
              hintText: 'HH:MM',
              suffixIcon: Icon(Icons.access_time),
            ),
            readOnly: true,
            onTap: () => _pickTime(_startController),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _endController,
            decoration: const InputDecoration(
              labelText: 'End Time',
              hintText: 'HH:MM',
              suffixIcon: Icon(Icons.access_time),
            ),
            readOnly: true,
            onTap: () => _pickTime(_endController),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: () {
            Navigator.pop(context, {
              'startTime': _startController.text,
              'endTime': _endController.text,
            });
          },
          child: const Text('Save'),
        ),
      ],
    );
  }
}

