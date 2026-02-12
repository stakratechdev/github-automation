import 'package:flutter/material.dart';

/// StakraTech Design System - Colors
/// Dark-first, Electric Blue Gradient, Clean + Technical
class STColors {
  // Brand Colors
  static const Color primary = Color(0xFF1E6CFF);
  static const Color primaryDark = Color(0xFF0D47A1);
  static const Color accent = Color(0xFF00B3FF);

  // Backgrounds
  static const Color background = Color(0xFF0A0F1C);
  static const Color surface = Color(0xFF111827);
  static const Color surfaceAlt = Color(0xFF1F2937);

  // Text
  static const Color textPrimary = Color(0xFFE5E7EB);
  static const Color textMuted = Color(0xFF9CA3AF);

  // Status
  static const Color success = Color(0xFF22C55E);
  static const Color warning = Color(0xFFF59E0B);
  static const Color danger = Color(0xFFEF4444);

  // Borders
  static const Color border = Color(0xFF1F2937);

  // Gradients
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [
      Color(0xFF1E6CFF),
      Color(0xFF00B3FF),
    ],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient surfaceGradient = LinearGradient(
    colors: [
      Color(0xFF111827),
      Color(0xFF0A0F1C),
    ],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );
}
