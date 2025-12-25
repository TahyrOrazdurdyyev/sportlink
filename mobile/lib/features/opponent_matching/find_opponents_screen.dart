import 'package:flutter/material.dart';
import '../../../core/network/api_client.dart';
import '../../../core/models/opponent.dart';
import '../../../core/services/opponent_matching_service.dart';
import '../subscription/subscription_plans_screen.dart';

class FindOpponentsScreen extends StatefulWidget {
  const FindOpponentsScreen({super.key});

  @override
  State<FindOpponentsScreen> createState() => _FindOpponentsScreenState();
}

class _FindOpponentsScreenState extends State<FindOpponentsScreen> {
  final ApiClient _apiClient = ApiClient();
  late OpponentMatchingService _matchingService;

  List<Opponent> _opponents = [];
  bool _isLoading = false;
  int? _selectedExperienceLevel;

  @override
  void initState() {
    super.initState();
    _matchingService = OpponentMatchingService(_apiClient.dio);
    _loadOpponents();
  }

  Future<void> _loadOpponents() async {
    setState(() => _isLoading = true);

    try {
      final loadedOpponents = await _matchingService.findOpponents(
        experienceLevel: _selectedExperienceLevel,
      );
      setState(() {
        _opponents = loadedOpponents;
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
          'Поиск соперников доступен только с подпиской ProSport или выше',
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

  Future<void> _sendInvitation(Opponent opponent) async {
    final message = await showDialog<String>(
      context: context,
      builder: (context) {
        String messageText = '';
        return AlertDialog(
          title: Text('Пригласить ${opponent.fullName}'),
          content: TextField(
            decoration: const InputDecoration(
              hintText: 'Напишите сообщение',
              border: OutlineInputBorder(),
            ),
            maxLines: 3,
            onChanged: (value) => messageText = value,
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Отмена'),
            ),
            ElevatedButton(
              onPressed: () => Navigator.pop(context, messageText),
              child: const Text('Отправить'),
            ),
          ],
        );
      },
    );

    if (message == null) return;

    try {
      await _matchingService.sendMatchInvitation(
        opponentId: opponent.id,
        message: message.isEmpty ? 'Давай сыграем!' : message,
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Приглашение отправлено!')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Ошибка: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Найти соперника'),
        actions: [
          PopupMenuButton<int>(
            icon: const Icon(Icons.filter_list),
            tooltip: 'Фильтр по уровню',
            onSelected: (level) {
              setState(() {
                _selectedExperienceLevel = level;
              });
              _loadOpponents();
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: null,
                child: Text('Все уровни'),
              ),
              ...List.generate(7, (index) {
                final level = index + 1;
                return PopupMenuItem(
                  value: level,
                  child: Text('Уровень $level'),
                );
              }),
            ],
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _opponents.isEmpty
              ? const Center(
                  child: Text('Соперники не найдены'),
                )
              : RefreshIndicator(
                  onRefresh: _loadOpponents,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _opponents.length,
                    itemBuilder: (context, index) {
                      final opponent = _opponents[index];
                      return _buildOpponentCard(opponent);
                    },
                  ),
                ),
    );
  }

  Widget _buildOpponentCard(Opponent opponent) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 30,
                  backgroundColor: Theme.of(context).primaryColor,
                  backgroundImage: opponent.avatarUrl != null
                      ? NetworkImage(opponent.avatarUrl!)
                      : null,
                  child: opponent.avatarUrl == null
                      ? Text(
                          opponent.firstName.isNotEmpty
                              ? opponent.firstName[0].toUpperCase()
                              : 'U',
                          style: const TextStyle(
                            fontSize: 24,
                            color: Colors.white,
                          ),
                        )
                      : null,
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        opponent.fullName,
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          Icon(
                            Icons.location_on,
                            size: 16,
                            color: Colors.grey[600],
                          ),
                          const SizedBox(width: 4),
                          Text(
                            opponent.city ?? 'Не указан',
                            style: TextStyle(color: Colors.grey[600]),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                // Compatibility Badge
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: _getCompatibilityColor(
                            opponent.compatibilityScore)
                        .withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Column(
                    children: [
                      Text(
                        '${opponent.compatibilityScore}%',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: _getCompatibilityColor(
                              opponent.compatibilityScore),
                        ),
                      ),
                      Text(
                        'совпадение',
                        style: TextStyle(
                          fontSize: 10,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Stats
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildStatChip(
                  'Уровень ${opponent.experienceLevel}',
                  Icons.star,
                  Colors.orange,
                ),
                _buildStatChip(
                  'Рейтинг ${opponent.rating.toStringAsFixed(1)}',
                  Icons.emoji_events,
                  Colors.blue,
                ),
              ],
            ),

            // Categories
            if (opponent.categories.isNotEmpty) ...[
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: opponent.categories.map((cat) {
                  return Chip(
                    label: Text(
                      cat.name,
                      style: const TextStyle(fontSize: 12),
                    ),
                    visualDensity: VisualDensity.compact,
                  );
                }).toList(),
              ),
            ],

            const SizedBox(height: 16),

            // Invite Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () => _sendInvitation(opponent),
                icon: const Icon(Icons.send),
                label: const Text('Пригласить'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatChip(String text, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: color),
          const SizedBox(width: 4),
          Text(
            text,
            style: TextStyle(color: color, fontWeight: FontWeight.w500),
          ),
        ],
      ),
    );
  }

  Color _getCompatibilityColor(int score) {
    if (score >= 80) return Colors.green;
    if (score >= 60) return Colors.orange;
    return Colors.red;
  }
}

