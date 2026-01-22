/**
 * Dashboard Page
 *
 * Main authenticated dashboard with sidebar navigation.
 */

import { useState, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { LiveCamera } from '../components/LiveCamera';
import { ChatInterface } from '../components/ChatInterface';
import { VoiceControl } from '../components/VoiceControl';
import { GestureTeacher } from './GestureTeacher';
import { SystemHealth } from './SystemHealth';
import { VideoUpload } from '../components/VideoUpload';

type Page = 'dashboard' | 'upload' | 'gestures' | 'health';

export function Dashboard() {
  const [currentPage, setCurrentPage] = useState<Page>('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [activeCameras, setActiveCameras] = useState([0]);
  const { user, logout } = useAuth();

  return (
    <div className="flex h-screen bg-gray-900 text-white">
      {/* Sidebar Navigation */}
      <aside className={`${sidebarCollapsed ? 'w-16' : 'w-64'} bg-gray-800 border-r border-gray-700 transition-all duration-300 flex flex-col`}>
        {/* Logo / Title */}
        <div className="p-4 border-b border-gray-700 flex items-center justify-between">
          {!sidebarCollapsed && (
            <div>
              <h1 className="text-xl font-bold text-blue-400">SentinelAI</h1>
              <p className="text-xs text-gray-400">Real-time Surveillance</p>
            </div>
          )}
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="p-2 hover:bg-gray-700 rounded transition-colors"
            title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={sidebarCollapsed ? 'M13 5l7 7-7 7M5 5l7 7-7 7' : 'M11 19l-7-7 7-7m8 14l-7-7 7-7'} />
            </svg>
          </button>
        </div>

        {/* User Info */}
        {!sidebarCollapsed && user && (
          <div className="px-4 py-3 border-b border-gray-700">
            <p className="text-sm text-gray-400">Signed in as</p>
            <p className="text-white font-medium truncate">{user.username}</p>
          </div>
        )}

        {/* Navigation Links */}
        <nav className="flex-1 p-4 space-y-2">
          <NavButton
            icon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            }
            label="Live Cameras"
            active={currentPage === 'dashboard'}
            onClick={() => setCurrentPage('dashboard')}
            collapsed={sidebarCollapsed}
          />

          <NavButton
            icon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
            }
            label="Upload Video"
            active={currentPage === 'upload'}
            onClick={() => setCurrentPage('upload')}
            collapsed={sidebarCollapsed}
          />

          <NavButton
            icon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 11.5V14m0-2.5v-6a1.5 1.5 0 113 0m-3 6a1.5 1.5 0 00-3 0v2a7.5 7.5 0 0015 0v-5a1.5 1.5 0 00-3 0m-6-3V11m0-5.5v-1a1.5 1.5 0 013 0v1m0 0V11m0-5.5a1.5 1.5 0 013 0v3m0 0V11" />
              </svg>
            }
            label="Teach Gestures"
            active={currentPage === 'gestures'}
            onClick={() => setCurrentPage('gestures')}
            collapsed={sidebarCollapsed}
          />

          <NavButton
            icon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            }
            label="System Health"
            active={currentPage === 'health'}
            onClick={() => setCurrentPage('health')}
            collapsed={sidebarCollapsed}
          />
        </nav>

        {/* Logout Button */}
        {!sidebarCollapsed && (
          <div className="p-4 border-t border-gray-700">
            <button
              onClick={logout}
              className="w-full flex items-center space-x-2 p-3 text-gray-300 hover:bg-gray-700 hover:text-white rounded-lg transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span>Logout</span>
            </button>
          </div>
        )}

        {/* Status Footer */}
        {!sidebarCollapsed && (
          <div className="p-4 border-t border-gray-700 text-xs text-gray-400">
            <div className="flex items-center space-x-2 mb-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span>System Online</span>
            </div>
            <div className="flex justify-between">
              <span>Cameras: {activeCameras.length}</span>
              <span>Version 0.1.0</span>
            </div>
          </div>
        )}
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-hidden">
        {currentPage === 'dashboard' && <DashboardView />}
        {currentPage === 'upload' && <VideoUpload />}
        {currentPage === 'gestures' && <GestureTeacher />}
        {currentPage === 'health' && <SystemHealth />}
      </main>
    </div>
  );
}

/**
 * Navigation Button Component
 */
interface NavButtonProps {
  icon: React.ReactNode;
  label: string;
  active: boolean;
  onClick: () => void;
  collapsed: boolean;
}

function NavButton({ icon, label, active, onClick, collapsed }: NavButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center space-x-3 p-3 rounded-lg transition-all ${
        active
          ? 'bg-blue-600 text-white shadow-lg'
          : 'text-gray-300 hover:bg-gray-700 hover:text-white'
      }`}
      title={collapsed ? label : undefined}
    >
      {icon}
      {!collapsed && <span className="font-medium">{label}</span>}
    </button>
  );
}

/**
 * Dashboard View - Live Cameras + Chat Interface + Voice Control
 */
function DashboardView() {
  const [sendVoiceCommand, setSendVoiceCommand] = useState<((command: string) => void) | null>(null);
  const [voiceResponses, setVoiceResponses] = useState<any[]>([]);

  const handleVoiceCommand = (command: string) => {
    console.log('Voice command received:', command);
    if (sendVoiceCommand) {
      sendVoiceCommand(command);
    }
  };

  const handleVoiceResponse = (response: any) => {
    console.log('Voice response received:', response);
    setVoiceResponses((prev) => [response, ...prev].slice(0, 10)); // Keep last 10 responses
  };

  return (
    <div className="h-full flex relative">
      {/* Left: Live Camera Feed (2/3 width) */}
      <div className="flex-[2] flex flex-col bg-gray-900">
        {/* Camera Grid Header */}
        <div className="bg-gray-800 border-b border-gray-700 p-4 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-white">Live Cameras</h2>
            <p className="text-sm text-gray-400">Real-time monitoring with AI detection</p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="flex items-center space-x-2 bg-red-600 text-white px-3 py-1 rounded-full">
              <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
              <span className="text-sm font-medium">LIVE</span>
            </div>
          </div>
        </div>

        {/* Camera Grid */}
        <div className="flex-1 p-4 overflow-auto">
          <div className="grid grid-cols-1 gap-4 h-full">
            <div className="bg-black rounded-lg overflow-hidden shadow-xl">
              <LiveCamera
                cameraId={0}
                width={1280}
                height={720}
                onVoiceResponse={handleVoiceResponse}
                onVoiceCommandReady={setSendVoiceCommand}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Right: Chat Interface (1/3 width) */}
      <div className="flex-1 border-l border-gray-700 bg-gray-800 flex flex-col">
        <div className="bg-gray-800 border-b border-gray-700 p-4">
          <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
            <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            <span>AI Assistant</span>
          </h2>
          <p className="text-sm text-gray-400 mt-1">Ask questions about what you see</p>
        </div>
        <div className="flex-1 overflow-hidden">
          <ChatInterface voiceResponses={voiceResponses} />
        </div>
      </div>

      {/* Voice Control Overlay (bottom-right) */}
      <VoiceControl onCommand={handleVoiceCommand} enabled={true} />
    </div>
  );
}
