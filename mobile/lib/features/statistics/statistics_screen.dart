import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../core/network/api_client.dart';
import '../../../core/models/user_statistics.dart';
import '../../../core/services/statistics_service.dart';
import '../subscription/subscription_plans_screen.dart';

class StatisticsScreen extends StatefulWidget {
  const StatisticsScreen({super.key});

  @override
  State<StatisticsScreen> createState() => _StatisticsScreenState();
}

class _StatisticsScreenState extends State<StatisticsScreen> {
  final ApiClient _apiClient = ApiClient();
  late StatisticsService _statisticsService;

  UserStatistics? _statistics;
  List<Achievement> _achievements = [];
  bool _isLoading = true;
  int _selectedDays = 30;

  @override
  void initState() {
    super.initState();
    _statisticsService = StatisticsService(_apiClient.dio);
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);

    try {
      final stats =
          await _statisticsService.getUserStatistics(days: _selectedDays);
      final achievements = await _statisticsService.getAchievements();

      setState(() {
        _statistics = stats;
        _achievements = achievements;
        _isLoading = false;
      });
    } on FeatureNotAvailableException catch (e) {
      setState(() => _isLoading = false);
      _showUpgradeDialog();
    } catch (e) {
      setState(() => _isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Ошибка: $e')),
      );
    }
  }

  void _showUpgradeDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Требуется подписка'),
        content: const Text(
          'Расширенная статистика доступна только с подпиской ProSport или выше',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Отмена'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => const SubscriptionPlansScreen(),
                ),
              );
            },
            child: const Text('Оформить'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Моя статистика'),
        actions: [
          PopupMenuButton<int>(
            tooltip: 'Период',
            icon: const Icon(Icons.calendar_today),
            onSelected: (days) {
              setState(() => _selectedDays = days);
              _loadData();
            },
            itemBuilder: (context) => [
              const PopupMenuItem(value: 7, child: Text('7 дней')),
              const PopupMenuItem(value: 30, child: Text('30 дней')),
              const PopupMenuItem(value: 90, child: Text('90 дней')),
              const PopupMenuItem(value: 365, child: Text('Год')),
            ],
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _statistics == null
              ? const Center(child: Text('Нет данных'))
              : RefreshIndicator(
                  onRefresh: _loadData,
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Summary Cards
                        _buildSummaryCards(),
                        const SizedBox(height: 24),

                        // Performance Metrics
                        _buildPerformanceSection(),
                        const SizedBox(height: 24),

                        // Activity by Day Chart
                        _buildActivityByDaySection(),
                        const SizedBox(height: 24),

                        // Tournaments
                        _buildTournamentsSection(),
                        const SizedBox(height: 24),

                        // Achievements
                        _buildAchievementsSection(),
                        const SizedBox(height: 24),

                        // Recent Activity
                        _buildRecentActivitySection(),
                      ],
                    ),
                  ),
                ),
    );
  }

  Widget _buildSummaryCards() {
    return Row(
      children: [
        Expanded(
          child: _buildSummaryCard(
            'Всего игр',
            _statistics!.bookings.total.toString(),
            Icons.sports_tennis,
            Colors.blue,
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: _buildSummaryCard(
            'Часов',
            _statistics!.bookings.totalHours.toStringAsFixed(1),
            Icons.access_time,
            Colors.orange,
          ),
        ),
      ],
    );
  }

  Widget _buildSummaryCard(
      String label, String value, IconData icon, Color color) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(icon, size: 32, color: color),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(color: Colors.grey[600], fontSize: 14),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPerformanceSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Показатели',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _buildPerformanceItem(
              'Среднее в неделю',
              '${_statistics!.performance.averageBookingsPerWeek} игр',
              _statistics!.performance.averageBookingsPerWeek / 7,
            ),
            const SizedBox(height: 12),
            _buildPerformanceItem(
              'Завершено',
              '${_statistics!.performance.completionRate.toStringAsFixed(1)}%',
              _statistics!.performance.completionRate / 100,
            ),
            const SizedBox(height: 12),
            _buildPerformanceItem(
              'Отменено',
              '${_statistics!.performance.cancellationRate.toStringAsFixed(1)}%',
              _statistics!.performance.cancellationRate / 100,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPerformanceItem(String label, String value, double progress) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: const TextStyle(fontSize: 14)),
            Text(
              value,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ],
        ),
        const SizedBox(height: 4),
        LinearProgressIndicator(
          value: progress > 1 ? 1 : progress,
          backgroundColor: Colors.grey[200],
        ),
      ],
    );
  }

  Widget _buildActivityByDaySection() {
    if (_statistics!.activityPatterns.byDayOfWeek.isEmpty) {
      return const SizedBox.shrink();
    }

    final days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
      'Saturday', 'Sunday'];
    final dayNames = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
    
    final data = days.asMap().entries.map((entry) {
      final count = _statistics!.activityPatterns.byDayOfWeek[entry.value] ?? 0;
      return BarChartGroupData(
        x: entry.key,
        barRods: [
          BarChartRodData(
            toY: count.toDouble(),
            color: Colors.blue,
            width: 20,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(4)),
          ),
        ],
      );
    }).toList();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Активность по дням',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 20),
            SizedBox(
              height: 200,
              child: BarChart(
                BarChartData(
                  barGroups: data,
                  titlesData: FlTitlesData(
                    leftTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: true, reservedSize: 30),
                    ),
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        getTitlesWidget: (value, meta) {
                          if (value.toInt() >= 0 && value.toInt() < dayNames.length) {
                            return Text(dayNames[value.toInt()]);
                          }
                          return const Text('');
                        },
                      ),
                    ),
                    rightTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    topTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                  ),
                  borderData: FlBorderData(show: false),
                  gridData: const FlGridData(show: true),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTournamentsSection() {
    if (_statistics!.tournaments.totalParticipated == 0) {
      return const SizedBox.shrink();
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Турниры (${_statistics!.tournaments.totalParticipated})',
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            ..._statistics!.tournaments.list.take(3).map((tournament) {
              return ListTile(
                contentPadding: EdgeInsets.zero,
                leading: const Icon(Icons.emoji_events, color: Colors.amber),
                title: Text(tournament.name),
                subtitle: Text(tournament.status),
              );
            }),
          ],
        ),
      ),
    );
  }

  Widget _buildAchievementsSection() {
    if (_achievements.isEmpty) {
      return const SizedBox.shrink();
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Достижения (${_achievements.where((a) => a.unlocked).length}/${_achievements.length})',
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 12,
              runSpacing: 12,
              children: _achievements.map((achievement) {
                return Tooltip(
                  message: achievement.description,
                  child: Container(
                    width: 60,
                    height: 60,
                    decoration: BoxDecoration(
                      color: achievement.unlocked
                          ? Colors.amber.withOpacity(0.2)
                          : Colors.grey.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Center(
                      child: Text(
                        achievement.icon,
                        style: TextStyle(
                          fontSize: 32,
                          color: achievement.unlocked ? null : Colors.grey,
                        ),
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentActivitySection() {
    if (_statistics!.recentActivity.isEmpty) {
      return const SizedBox.shrink();
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Недавняя активность',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            ..._statistics!.recentActivity.take(5).map((activity) {
              return ListTile(
                contentPadding: EdgeInsets.zero,
                leading: _getStatusIcon(activity.status),
                title: Text(activity.courtName),
                subtitle: Text(
                  activity.startTime != null
                      ? '${activity.startTime!.day}.${activity.startTime!.month}.${activity.startTime!.year}'
                      : 'Дата не указана',
                ),
                trailing: _getStatusChip(activity.status),
              );
            }),
          ],
        ),
      ),
    );
  }

  Icon _getStatusIcon(String status) {
    switch (status) {
      case 'completed':
        return const Icon(Icons.check_circle, color: Colors.green);
      case 'confirmed':
        return const Icon(Icons.schedule, color: Colors.blue);
      case 'cancelled':
        return const Icon(Icons.cancel, color: Colors.red);
      default:
        return const Icon(Icons.help, color: Colors.grey);
    }
  }

  Widget _getStatusChip(String status) {
    final statusNames = {
      'completed': 'Завершено',
      'confirmed': 'Подтверждено',
      'cancelled': 'Отменено',
      'pending': 'В ожидании',
    };

    final colors = {
      'completed': Colors.green,
      'confirmed': Colors.blue,
      'cancelled': Colors.red,
      'pending': Colors.orange,
    };

    return Chip(
      label: Text(
        statusNames[status] ?? status,
        style: const TextStyle(fontSize: 12),
      ),
      backgroundColor: colors[status]?.withOpacity(0.1),
      side: BorderSide.none,
    );
  }
}

