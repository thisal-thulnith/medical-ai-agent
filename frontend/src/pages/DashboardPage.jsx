import { useState, useEffect } from 'react';
import { dashboardAPI } from '../lib/api';
import { Activity, Pill, AlertCircle, TrendingUp } from 'lucide-react';

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await dashboardAPI.getStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-gray-600">Loading dashboard...</div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-red-600">Failed to load dashboard</div>
      </div>
    );
  }

  return (
    <div className="p-6 overflow-y-auto h-full bg-gray-50">
      <div className="max-w-7xl mx-auto space-y-6">
        <h2 className="text-2xl font-bold text-gray-900">Health Dashboard</h2>

        {/* Health Score */}
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-6 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-white/80 text-sm font-medium">Health Score</h3>
              <p className="text-4xl font-bold mt-2">{stats.health_score}</p>
              <p className="text-white/80 text-sm mt-1">out of 100</p>
            </div>
            <TrendingUp className="w-12 h-12 text-white/50" />
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg border p-4 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-100 rounded-lg">
                <AlertCircle className="w-6 h-6 text-red-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.total_symptoms}</p>
                <p className="text-sm text-gray-600">Recent Symptoms</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg border p-4 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Pill className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.active_medications}</p>
                <p className="text-sm text-gray-600">Active Medications</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg border p-4 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <Activity className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.recent_vitals_count}</p>
                <p className="text-sm text-gray-600">Vital Signs Logged</p>
              </div>
            </div>
          </div>
        </div>

        {/* Risk Alerts */}
        {stats.risk_alerts && stats.risk_alerts.length > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 shadow-sm">
            <h4 className="font-medium text-yellow-900 mb-2 flex items-center gap-2">
              <AlertCircle className="w-5 h-5" />
              Health Alerts
            </h4>
            <ul className="space-y-1">
              {stats.risk_alerts.map((alert, index) => (
                <li key={index} className="text-sm text-yellow-800">
                  • {alert}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Info Card */}
        <div className="bg-white rounded-lg border p-6 shadow-sm">
          <h3 className="font-semibold text-gray-900 mb-2">About Your Dashboard</h3>
          <p className="text-gray-600 text-sm mb-4">
            Your health dashboard automatically updates based on your conversations with the AI.
            All data is extracted from your chats and securely stored.
          </p>
          <div className="text-sm text-gray-500">
            <p>✅ Automatic symptom tracking</p>
            <p>✅ Vital signs monitoring</p>
            <p>✅ Medication management</p>
            <p>✅ AI-powered health insights</p>
          </div>
        </div>
      </div>
    </div>
  );
}
