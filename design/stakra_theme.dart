import 'package:flutter/material.dart';
import 'stakra_colors.dart';
import 'stakra_typography.dart';

/// StakraTech Design System - Theme
/// Dark-first, Electric Blue Gradient, Clean + Technical
class STTheme {
  /// Dark theme - primary theme for the application
  static ThemeData dark() {
    final colorScheme = ColorScheme.dark(
      primary: STColors.primary,
      secondary: STColors.accent,
      surface: STColors.surface,
      background: STColors.background,
      error: STColors.danger,
      onPrimary: Colors.white,
      onSecondary: Colors.white,
      onSurface: STColors.textPrimary,
      onBackground: STColors.textPrimary,
      onError: Colors.white,
    );

    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: STColors.background,
      textTheme: STTypography.textTheme,

      // App Bar
      appBarTheme: const AppBarTheme(
        backgroundColor: STColors.background,
        elevation: 0,
        titleTextStyle: STTypography.headlineMedium,
        iconTheme: IconThemeData(color: STColors.textPrimary),
      ),

      // Card
      cardTheme: CardTheme(
        color: STColors.surface,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(18),
          side: const BorderSide(color: STColors.border),
        ),
      ),

      // Elevated Button
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
          backgroundColor: STColors.primary,
          foregroundColor: Colors.white,
          textStyle: STTypography.labelLarge,
        ),
      ),

      // Outlined Button
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
          side: const BorderSide(color: STColors.border),
          foregroundColor: STColors.textPrimary,
          textStyle: STTypography.labelLarge,
        ),
      ),

      // Text Button
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: STColors.primary,
          textStyle: STTypography.labelLarge,
        ),
      ),

      // Input Decoration
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: STColors.surfaceAlt,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: STColors.border),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: STColors.border),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(
            color: STColors.primary,
            width: 1.5,
          ),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: STColors.danger),
        ),
        labelStyle: STTypography.bodyMedium,
        hintStyle: STTypography.bodyMedium.copyWith(
          color: STColors.textMuted,
        ),
      ),

      // Chip Theme
      chipTheme: ChipThemeData(
        backgroundColor: STColors.surfaceAlt,
        selectedColor: STColors.primary.withOpacity(0.2),
        labelStyle: STTypography.labelMedium,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
          side: const BorderSide(color: STColors.border),
        ),
      ),

      // Divider
      dividerTheme: const DividerThemeData(
        color: STColors.border,
        thickness: 1,
      ),

      // Scaffold background
      scaffoldBackgroundColor: STColors.background,
    );
  }

  /// Glass effect container
  static BoxDecoration glassContainer({
    double borderRadius = 18,
  }) {
    return BoxDecoration(
      gradient: STColors.surfaceGradient,
      borderRadius: BorderRadius.circular(borderRadius),
      border: Border.all(color: STColors.border.withOpacity(0.5)),
    );
  }

  /// Premium gradient border
  static BoxDecoration gradientBorder({
    double borderRadius = 18,
  }) {
    return BoxDecoration(
      borderRadius: BorderRadius.circular(borderRadius),
      border: Border.all(color: Colors.transparent),
      gradient: STColors.primaryGradient,
      boxShadow: [
        BoxShadow(
          color: STColors.primary.withOpacity(0.3),
          blurRadius: 10,
          offset: const Offset(0, 4),
        ),
      ],
    );
  }
}
