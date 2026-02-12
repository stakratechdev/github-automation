import 'package:flutter/material.dart';
import 'stakra_colors.dart';

/// StakraTech Design System - Typography
/// Clean, technical, highly readable
class STTypography {
  // Display styles
  static const TextStyle displaySmall = TextStyle(
    fontSize: 36,
    fontWeight: FontWeight.w700,
    color: STColors.textPrimary,
    letterSpacing: -0.5,
  );

  static const TextStyle displayMedium = TextStyle(
    fontSize: 48,
    fontWeight: FontWeight.w800,
    color: STColors.textPrimary,
    letterSpacing: -1.0,
  );

  // Headline styles
  static const TextStyle headlineMedium = TextStyle(
    fontSize: 24,
    fontWeight: FontWeight.w600,
    color: STColors.textPrimary,
  );

  static const TextStyle headlineLarge = TextStyle(
    fontSize: 32,
    fontWeight: FontWeight.w700,
    color: STColors.textPrimary,
  );

  // Title styles
  static const TextStyle titleLarge = TextStyle(
    fontSize: 18,
    fontWeight: FontWeight.w600,
    color: STColors.textPrimary,
  );

  static const TextStyle titleMedium = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.w600,
    color: STColors.textPrimary,
  );

  // Body styles
  static const TextStyle bodyLarge = TextStyle(
    fontSize: 16,
    color: STColors.textPrimary,
  );

  static const TextStyle bodyMedium = TextStyle(
    fontSize: 14,
    color: STColors.textMuted,
  );

  static const TextStyle bodySmall = TextStyle(
    fontSize: 12,
    color: STColors.textMuted,
  );

  // Label styles
  static const TextStyle labelLarge = TextStyle(
    fontSize: 14,
    fontWeight: FontWeight.w600,
    color: STColors.textPrimary,
  );

  static const TextStyle labelMedium = TextStyle(
    fontSize: 12,
    fontWeight: FontWeight.w500,
    color: STColors.textMuted,
  );

  // Complete text theme
  static const TextTheme textTheme = TextTheme(
    displaySmall: displaySmall,
    displayMedium: displayMedium,
    headlineMedium: headlineMedium,
    headlineLarge: headlineLarge,
    titleLarge: titleLarge,
    titleMedium: titleMedium,
    bodyLarge: bodyLarge,
    bodyMedium: bodyMedium,
    bodySmall: bodySmall,
    labelLarge: labelLarge,
    labelMedium: labelMedium,
  );
}
