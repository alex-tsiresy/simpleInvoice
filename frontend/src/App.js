import React from 'react';
import { ClerkProvider, SignedIn, SignedOut, SignIn, UserButton } from '@clerk/clerk-react';
import Dashboard from './components/Dashboard';
import './App.css';

const clerkPubKey = process.env.REACT_APP_CLERK_PUBLISHABLE_KEY;

function App() {
  if (!clerkPubKey) {
    return (
      <div className="error-container">
        <h1>Configuration Error</h1>
        <p>Missing Clerk Publishable Key</p>
        <p>Please set REACT_APP_CLERK_PUBLISHABLE_KEY in your .env file</p>
      </div>
    );
  }

  return (
    <ClerkProvider publishableKey={clerkPubKey}>
      <div className="App">
        <header className="app-header">
          <div className="header-content">
            <h1>Compass Document Processing</h1>
            <SignedIn>
              <UserButton afterSignOutUrl="/" />
            </SignedIn>
          </div>
        </header>

        <main className="main-content">
          <SignedIn>
            <Dashboard />
          </SignedIn>

          <SignedOut>
            <div className="sign-in-container">
              <div className="sign-in-card">
                <h2>Welcome to Compass</h2>
                <p>Sign in to upload and process documents</p>
                <SignIn routing="hash" />
              </div>
            </div>
          </SignedOut>
        </main>
      </div>
    </ClerkProvider>
  );
}

export default App;
