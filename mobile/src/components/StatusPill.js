import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors } from '../theme';

/** Small gold/green/red status chip used across the JARVIS-style HUD. */
export default function StatusPill({ label, value, tone = 'gold' }) {
  const dot =
    tone === 'green' ? colors.green : tone === 'red' ? colors.red : colors.gold;
  return (
    <View style={styles.pill}>
      <View style={[styles.dot, { backgroundColor: dot }]} />
      <Text style={styles.label}>{label}</Text>
      {value != null && <Text style={styles.value}>{value}</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  pill: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 999,
    paddingVertical: 6,
    paddingHorizontal: 12,
    marginRight: 8,
    marginBottom: 8,
  },
  dot: { width: 8, height: 8, borderRadius: 4, marginRight: 8 },
  label: { color: colors.textSecondary, fontSize: 12, letterSpacing: 1, fontWeight: '600' },
  value: { color: colors.gold, fontSize: 12, marginLeft: 6, fontWeight: '700' },
});
