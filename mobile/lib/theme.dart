import 'package:flutter/material.dart';

ThemeData buildMaxTheme() {
  const seed = Color(0xFFD946EF); // fuchsia-600
  final scheme = ColorScheme.fromSeed(
    seedColor: seed,
    brightness: Brightness.dark,
    surface: const Color(0xFF0A0A0A),
    background: const Color(0xFF0A0A0A),
  );
  return ThemeData(
    colorScheme: scheme,
    useMaterial3: true,
    scaffoldBackgroundColor: const Color(0xFF0A0A0A),
    textTheme: const TextTheme(
      headlineLarge: TextStyle(fontWeight: FontWeight.w700),
      headlineMedium: TextStyle(fontWeight: FontWeight.w700),
      bodyMedium: TextStyle(color: Color(0xFFEDEDED)),
    ),
    cardColor: const Color(0xFF111111),
  );
}


