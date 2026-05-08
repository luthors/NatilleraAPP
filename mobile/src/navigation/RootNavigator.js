/**
 * Root navigation — switches between Auth stack and Main tab navigator
 * based on authentication state stored in SecureStore.
 */
import { NavigationContainer } from '@react-navigation/native'
import { createStackNavigator } from '@react-navigation/stack'
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs'
import { useEffect, useState } from 'react'
import * as SecureStore from 'expo-secure-store'

// Screens (imported lazily to avoid circular deps)
import LoginScreen from '../screens/auth/LoginScreen'
import RegisterScreen from '../screens/auth/RegisterScreen'
import NatillerasScreen from '../screens/natilleras/NatillerasScreen'

const AuthStack = createStackNavigator()
const Tab = createBottomTabNavigator()

function AuthNavigator() {
  return (
    <AuthStack.Navigator screenOptions={{ headerShown: false }}>
      <AuthStack.Screen name="Login" component={LoginScreen} />
      <AuthStack.Screen name="Register" component={RegisterScreen} />
    </AuthStack.Navigator>
  )
}

function MainTabs() {
  return (
    <Tab.Navigator screenOptions={{ headerShown: false }}>
      <Tab.Screen
        name="Natilleras"
        component={NatillerasScreen}
        options={{ tabBarLabel: 'Natilleras', tabBarIcon: () => null }}
      />
    </Tab.Navigator>
  )
}

export default function RootNavigator() {
  const [isLoggedIn, setIsLoggedIn] = useState(null)

  useEffect(() => {
    SecureStore.getItemAsync('access_token').then((token) => {
      setIsLoggedIn(Boolean(token))
    })
  }, [])

  if (isLoggedIn === null) return null  // splash while checking

  return (
    <NavigationContainer>
      {isLoggedIn ? <MainTabs /> : <AuthNavigator />}
    </NavigationContainer>
  )
}
