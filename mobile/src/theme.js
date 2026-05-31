export const colors = {
  background: '#0D0D0D',
  surface: '#1A1A1A',
  gold: '#FFD700',
  goldDark: '#B8860B',
  text: '#FFFFFF',
  textSecondary: '#CCCCCC',
  accent: '#FFD700',
};

export const theme = {
  colors,
  container: {
    flex: 1,
    backgroundColor: colors.background,
    padding: 16,
  },
  header: {
    color: colors.gold,
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  text: {
    color: colors.text,
  },
  button: {
    backgroundColor: colors.gold,
    color: '#000000',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
};