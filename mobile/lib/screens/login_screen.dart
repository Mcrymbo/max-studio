import 'package:flutter/material.dart';
import 'package:graphql_flutter/graphql_flutter.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'home_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  final _emailController = TextEditingController();
  bool _isLogin = true;

  static const loginMutation = '''
    mutation Login(\$username: String!, \$password: String!) {
      tokenAuth(username: \$username, password: \$password) {
        token
      }
    }
  ''';

  static const registerMutation = '''
    mutation Register(\$username: String!, \$password: String!, \$email: String) {
      register(username: \$username, password: \$password, email: \$email) {
        ok
      }
    }
  ''';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_isLogin ? 'Login' : 'Register'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextField(
              controller: _usernameController,
              decoration: const InputDecoration(labelText: 'Username'),
            ),
            if (!_isLogin) ...[
              const SizedBox(height: 16),
              TextField(
                controller: _emailController,
                decoration: const InputDecoration(labelText: 'Email'),
              ),
            ],
            const SizedBox(height: 16),
            TextField(
              controller: _passwordController,
              decoration: const InputDecoration(labelText: 'Password'),
              obscureText: true,
            ),
            const SizedBox(height: 24),
            Mutation(
              options: MutationOptions(
                document: gql(_isLogin ? loginMutation : registerMutation),
                onCompleted: (data) async {
                  if (_isLogin) {
                    final token = data?['tokenAuth']?['token'];
                    if (token != null) {
                      final prefs = await SharedPreferences.getInstance();
                      await prefs.setString('token', token);
                      if (mounted) {
                        Navigator.of(context).pushReplacement(
                          MaterialPageRoute(builder: (_) => const HomeScreen()),
                        );
                      }
                    }
                  } else {
                    if (data?['register']?['ok'] == true) {
                      setState(() => _isLogin = true);
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Registration successful! Please login.')),
                      );
                    }
                  }
                },
              ),
              builder: (runMutation, result) {
                return ElevatedButton(
                  onPressed: result?.isLoading == true ? null : () {
                    if (_isLogin) {
                      runMutation({
                        'username': _usernameController.text,
                        'password': _passwordController.text,
                      });
                    } else {
                      runMutation({
                        'username': _usernameController.text,
                        'password': _passwordController.text,
                        'email': _emailController.text,
                      });
                    }
                  },
                  child: result?.isLoading == true
                      ? const CircularProgressIndicator()
                      : Text(_isLogin ? 'Login' : 'Register'),
                );
              },
            ),
            const SizedBox(height: 16),
            TextButton(
              onPressed: () => setState(() => _isLogin = !_isLogin),
              child: Text(_isLogin ? 'Need an account? Register' : 'Have an account? Login'),
            ),
          ],
        ),
      ),
    );
  }
}

