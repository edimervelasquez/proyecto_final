import React, { useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaView, StyleSheet } from 'react-native';
import WelcomeScreen from './components/WelcomeScreen';
import LoginScreen from './components/LoginScreen';
import RegisterScreen from './components/RegisterScreen';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState('welcome');
  const [registeredUser, setRegisteredUser] = useState(null);

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" />
      {currentScreen === 'welcome' && (
        <WelcomeScreen onNavigate={setCurrentScreen} />
      )}
      {currentScreen === 'login' && (
        <LoginScreen onNavigate={setCurrentScreen} registeredUser={registeredUser} />
      )}
      {currentScreen === 'register' && (
        <RegisterScreen 
          onNavigate={setCurrentScreen} 
          onRegisterSuccess={user => setRegisteredUser(user)} 
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0A0A0A',
  },
});