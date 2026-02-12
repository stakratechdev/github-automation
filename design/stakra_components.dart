import 'package:flutter/material.dart';
import 'stakra_colors.dart';
import 'stakra_typography.dart';

/// StakraTech Design System - Premium Components
/// Gradient Button - Corporate Look
class STGradientButton extends StatelessWidget {
  final String text;
  final VoidCallback onPressed;
  final double? width;
  final double? height;

  const STGradientButton({
    super.key,
    required this.text,
    required this.onPressed,
    this.width,
    this.height,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      borderRadius: BorderRadius.circular(14),
      onTap: onPressed,
      child: Ink(
        width: width,
        height: height ?? 56,
        decoration: BoxDecoration(
          gradient: STColors.primaryGradient,
          borderRadius: BorderRadius.circular(14),
          boxShadow: [
            BoxShadow(
              color: STColors.primary.withOpacity(0.4),
              blurRadius: 12,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 24),
          alignment: Alignment.center,
          child: Text(
            text,
            style: STTypography.labelLarge.copyWith(
              color: Colors.white,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ),
    );
  }
}

/// Gradient Icon Button
class STGradientIconButton extends StatelessWidget {
  final IconData icon;
  final VoidCallback onPressed;
  final double size;

  const STGradientIconButton({
    super.key,
    required this.icon,
    required this.onPressed,
    this.size = 56,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      borderRadius: BorderRadius.circular(14),
      onTap: onPressed,
      child: Ink(
        width: size,
        height: size,
        decoration: BoxDecoration(
          gradient: STColors.primaryGradient,
          borderRadius: BorderRadius.circular(14),
        ),
        child: Icon(
          icon,
          color: Colors.white,
          size: size * 0.5,
        ),
      ),
    );
  }
}

/// Glass Card - Enterprise Look
class STGlassCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final double borderRadius;

  const STGlassCard({
    super.key,
    required this.child,
    this.padding,
    this.borderRadius = 18,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: padding ?? const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: STColors.surfaceGradient,
        borderRadius: BorderRadius.circular(borderRadius),
        border: Border.all(
          color: STColors.border.withOpacity(0.5),
        ),
      ),
      child: child,
    );
  }
}

/// KPI Card - Dashboard Style
class STKpiCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData? icon;
  final Color? accentColor;
  final String? change;

  const STKpiCard({
    super.key,
    required this.title,
    required this.value,
    this.icon,
    this.accentColor,
    this.change,
  });

  @override
  Widget build(BuildContext context) {
    return STGlassCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                title,
                style: STTypography.bodyMedium.copyWith(
                  color: STColors.textMuted,
                ),
              ),
              if (icon != null)
                Icon(
                  icon,
                  color: accentColor ?? STColors.accent,
                  size: 24,
                ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            value,
            style: STTypography.headlineLarge.copyWith(
              fontSize: 32,
            ),
          ),
          if (change != null)
            Text(
              change!,
              style: STTypography.bodySmall.copyWith(
                color: change!.startsWith('+')
                    ? STColors.success
                    : STColors.danger,
              ),
            ),
        ],
      ),
    );
  }
}

/// Issue Card - GitHub Style
class STIssueCard extends StatelessWidget {
  final String number;
  final String title;
  final String status;
  final List<String> labels;
  final VoidCallback onTap;

  const STIssueCard({
    super.key,
    required this.number,
    required this.title,
    required this.status,
    required this.labels,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      borderRadius: BorderRadius.circular(12),
      onTap: onTap,
      child: Ink(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: STColors.surface,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: STColors.border),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(
                  '#$number',
                  style: STTypography.bodyMedium.copyWith(
                    color: STColors.primary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    title,
                    style: STTypography.bodyLarge.copyWith(
                      fontWeight: FontWeight.w500,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: labels.map((label) {
                return Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: _getLabelColor(label).withOpacity(0.2),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Text(
                    label,
                    style: STTypography.labelMedium.copyWith(
                      color: _getLabelColor(label),
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

  Color _getLabelColor(String label) {
    switch (label.toLowerCase()) {
      case 'frontend':
        return const Color(0xFF22C55E);
      case 'backend':
        return const Color(0xFF3B82F6);
      case 'qa':
        return const Color(0xFFF59E0B);
      case 'bug':
        return const Color(0xFFEF4444);
      case 'feature':
        return const Color(0xFF8B5CF6);
      default:
        return STColors.primary;
    }
  }
}

/// Status Badge
class STStatusBadge extends StatelessWidget {
  final String status;

  const STStatusBadge({
    super.key,
    required this.status,
  });

  @override
  Widget build(BuildContext context) {
    final (color, text) = _getStatusConfig(status);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.2),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Text(
        text,
        style: STTypography.labelMedium.copyWith(
          color: color,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  (Color, String) _getStatusConfig(String status) {
    switch (status.toLowerCase()) {
      case 'ready_for_dev':
        return (const Color(0xFF22C55E), 'Ready for Dev');
      case 'in_progress':
        return (const Color(0xFF3B82F6), 'In Progress');
      case 'ready_for_qa':
        return (const Color(0xFFF59E0B), 'Ready for QA');
      case 'done':
        return (const Color(0xFF10B981), 'Done');
      case 'blocked':
        return (const Color(0xFFEF4444), 'Blocked');
      case 'waiting_for_clarification':
        return (const Color(0xFFF59E0B), 'Needs Clarification');
      default:
        return (STColors.textMuted, status);
    }
  }
}
