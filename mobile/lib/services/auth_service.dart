import 'package:shared_preferences/shared_preferences.dart';
import 'package:graphql_flutter/graphql_flutter.dart';

class AuthService {
  static const String _tokenKey = 'token';
  
  static Future<bool> login(String username, String password) async {
    const loginMutation = '''
      mutation Login(\$username: String!, \$password: String!) {
        tokenAuth(username: \$username, password: \$password) {
          token
        }
      }
    ''';
    
    // This would be called from a GraphQL client
    // For now, return false as placeholder
    return false;
  }
  
  static Future<bool> register(String username, String password, String email) async {
    const registerMutation = '''
      mutation Register(\$username: String!, \$password: String!, \$email: String) {
        register(username: \$username, password: \$password, email: \$email) {
          ok
        }
      }
    ''';
    
    // This would be called from a GraphQL client
    // For now, return false as placeholder
    return false;
  }
  
  static Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
  }
  
  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }
  
  static Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
  }
}


