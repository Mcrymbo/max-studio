import 'package:flutter/material.dart';
import 'package:graphql_flutter/graphql_flutter.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'screens/home_screen.dart';
import 'screens/login_screen.dart';
import 'services/auth_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await initHiveForFlutter();
  
  final prefs = await SharedPreferences.getInstance();
  final token = prefs.getString('token');
  
  runApp(MyApp(isLoggedIn: token != null));
}

class MyApp extends StatelessWidget {
  final bool isLoggedIn;
  
  const MyApp({super.key, required this.isLoggedIn});

  @override
  Widget build(BuildContext context) {
    final httpLink = HttpLink('http://10.0.2.2:8000/graphql/');
    
    final authLink = AuthLink(
      getToken: () async {
        final prefs = await SharedPreferences.getInstance();
        final token = prefs.getString('token');
        return token != null ? 'JWT $token' : null;
      },
    );
    
    final link = authLink.concat(httpLink);
    
    final client = ValueNotifier(
      GraphQLClient(
        link: link,
        cache: GraphQLCache(store: HiveStore()),
      ),
    );

    return GraphQLProvider(
      client: client,
      child: MaterialApp(
        title: 'Max Studio',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
          useMaterial3: true,
        ),
        home: isLoggedIn ? const HomeScreen() : const LoginScreen(),
      ),
    );
  }
}