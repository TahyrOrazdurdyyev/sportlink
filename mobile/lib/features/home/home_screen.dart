import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sportlink/core/models/category.dart';
import 'package:sportlink/core/models/court.dart';
import 'package:sportlink/core/services/category_service.dart';
import 'package:sportlink/core/services/court_service.dart';
import 'package:sportlink/core/widgets/image_carousel.dart';
import 'package:sportlink/features/tournaments/presentation/screens/tournaments_list_screen.dart';
import 'package:sportlink/core/providers/locale_provider.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> with SingleTickerProviderStateMixin {
  final CategoryService _categoryService = CategoryService();
  final CourtService _courtService = CourtService();
  
  List<Category> _categories = [];
  Map<String, List<Court>> _courtsByCategory = {};
  bool _isLoading = true;
  String? _error;
  TabController? _tabController;
  int _currentBottomNavIndex = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadData();
    });
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      // Load categories
      final categories = await _categoryService.getCategories();
      
      // Load courts for each category
      final Map<String, List<Court>> courtsByCategory = {};
      for (var category in categories) {
        final courts = await _courtService.getCourts(categoryId: category.id);
        courtsByCategory[category.id] = courts;
      }

      if (mounted) {
        setState(() {
          _categories = categories;
          _courtsByCategory = courtsByCategory;
          _isLoading = false;
          
          // Initialize tab controller
          if (_categories.isNotEmpty) {
            _tabController = TabController(
              length: _categories.length,
              vsync: this,
            );
          }
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
  void dispose() {
    _tabController?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final locale = ref.watch(localeProvider);
    final currentLocale = locale.languageCode;
    
    return Scaffold(
      appBar: AppBar(
        titleSpacing: 16,
        title: const Text('Sportlink'),
        actions: [
          IconButton(
            icon: const Icon(Icons.language),
            onPressed: () {
              // Toggle language
              final newLocale = currentLocale == 'en' ? const Locale('ru') : const Locale('en');
              ref.read(localeProvider.notifier).state = newLocale;
            },
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
          ),
          IconButton(
            icon: const Icon(Icons.person),
            onPressed: () {
              Navigator.pushNamed(context, '/profile');
            },
          ),
        ],
        bottom: _tabController != null
            ? PreferredSize(
                preferredSize: const Size.fromHeight(48),
                child: Align(
                  alignment: Alignment.centerLeft,
                  child: TabBar(
                    controller: _tabController,
                    isScrollable: true,
                    padding: const EdgeInsets.only(left: 8),
                    labelPadding: const EdgeInsets.symmetric(horizontal: 16),
                    indicatorPadding: const EdgeInsets.only(left: 8),
                    tabAlignment: TabAlignment.start,
                    tabs: _categories.map((category) {
                      return Tab(
                        text: category.nameI18n[currentLocale] ?? category.nameI18n['en'] ?? 'Unknown',
                      );
                    }).toList(),
                  ),
                ),
              )
            : null,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text('Error: $_error'),
                      ElevatedButton(
                        onPressed: _loadData,
                        child: const Text('Retry'),
                      ),
                    ],
                  ),
                )
              : _categories.isEmpty
                  ? const Center(child: Text('No categories available'))
                  : TabBarView(
                      controller: _tabController,
                      children: _categories.map((category) {
                        final courts = _courtsByCategory[category.id] ?? [];
                        
                        if (courts.isEmpty) {
                          return const Center(
                            child: Text('No courts available in this category'),
                          );
                        }
                        
                        return ListView.builder(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          itemCount: courts.length,
                          itemBuilder: (context, index) {
                            final court = courts[index];
                            return _buildCourtCard(court);
                          },
                        );
                      }).toList(),
                    ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentBottomNavIndex,
        type: BottomNavigationBarType.fixed,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.sports_tennis),
            label: 'Courts',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.emoji_events),
            label: 'Tournaments',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: 'Profile',
          ),
        ],
        onTap: (index) {
          setState(() {
            _currentBottomNavIndex = index;
          });
          
          if (index == 2) {
            // Navigate to Tournaments
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => const TournamentsListScreen()),
            );
          } else if (index == 3) {
            // Navigate to Profile
            Navigator.pushNamed(context, '/profile');
          }
        },
      ),
    );
  }

  Widget _buildCourtCard(Court court) {
    final locale = ref.watch(localeProvider);
    final currentLocale = locale.languageCode;
    final courtName = court.nameI18n[currentLocale] ?? court.nameI18n['en'] ?? 'Unknown';
    
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 4, vertical: 6),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Court Image
          if (court.images != null && court.images!.isNotEmpty)
            Image.network(
              court.images!.first,
              height: 200,
              width: double.infinity,
              fit: BoxFit.cover,
              errorBuilder: (context, error, stackTrace) {
                return Container(
                  height: 200,
                  decoration: BoxDecoration(
                    color: Colors.grey[300],
                    borderRadius: const BorderRadius.vertical(top: Radius.circular(4)),
                  ),
                  child: const Center(
                    child: Icon(Icons.sports_tennis, size: 64, color: Colors.grey),
                  ),
                );
              },
            )
          else
            Container(
              height: 200,
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: const BorderRadius.vertical(top: Radius.circular(4)),
              ),
              child: const Center(
                child: Icon(Icons.sports_tennis, size: 64, color: Colors.grey),
              ),
            ),
          
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Court Name
                Text(
                  courtName,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                
                // Address
                if (court.address != null)
                  Row(
                    children: [
                      const Icon(Icons.location_on, size: 16, color: Colors.grey),
                      const SizedBox(width: 4),
                      Expanded(
                        child: Text(
                          court.address!,
                          style: const TextStyle(color: Colors.grey),
                        ),
                      ),
                    ],
                  ),
                
                const SizedBox(height: 12),
                
                // Book Button
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Booking coming soon!')),
                      );
                    },
                    child: const Text('Book Now'),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

