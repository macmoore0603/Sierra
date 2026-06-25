import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { NavigationContainer, DefaultTheme } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';

import { SierraProvider } from './src/context/SierraContext';
import DashboardScreen from './src/screens/DashboardScreen';
import ChatScreen from './src/screens/ChatScreen';
import AgentsScreen from './src/screens/AgentsScreen';
import SettingsScreen from './src/screens/SettingsScreen';
import { colors } from './src/theme';

const Tab = createBottomTabNavigator();

const navTheme = {
  ...DefaultTheme,
  colors: { ...DefaultTheme.colors, background: colors.background, card: colors.background },
};

const ICONS = {
  Dashboard: 'grid',
  Chat: 'chatbubbles',
  Agents: 'git-network',
  Settings: 'settings',
};

export default function App() {
  return (
    <SafeAreaProvider>
      <SierraProvider>
        <StatusBar style="light" />
        <NavigationContainer theme={navTheme}>
          <Tab.Navigator
            screenOptions={({ route }) => ({
              tabBarIcon: ({ color, size }) => (
                <Ionicons name={ICONS[route.name] || 'ellipse'} size={size} color={color} />
              ),
              tabBarStyle: { backgroundColor: colors.background, borderTopColor: colors.border },
              tabBarActiveTintColor: colors.gold,
              tabBarInactiveTintColor: colors.muted,
              headerStyle: { backgroundColor: colors.background },
              headerTintColor: colors.gold,
              headerTitleStyle: { fontWeight: '800', letterSpacing: 2 },
            })}
          >
            <Tab.Screen name="Dashboard" component={DashboardScreen} />
            <Tab.Screen name="Chat" component={ChatScreen} />
            <Tab.Screen name="Agents" component={AgentsScreen} />
            <Tab.Screen name="Settings" component={SettingsScreen} />
          </Tab.Navigator>
        </NavigationContainer>
      </SierraProvider>
    </SafeAreaProvider>
  );
}
