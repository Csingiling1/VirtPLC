import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useSensorData } from '../hooks/useSensorData';

function LiveMetrics() {
  const { data, loading, error } = useSensorData();
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    if (data) {
      setHistory(prev => {
        const updated = [...prev, {
          time: new Date(data.timestamp).toLocaleTimeString(),
          motor1Speed: data.motor1Speed,
          motor1Temp: data.motor1Temp,
          motor2Speed: data.motor2Speed,
          conveyor: data.conveyor1Speed,
        }];
        // Keep last 20 data points
        return updated.slice(-20);
      });
    }
  }, [data]);

  if (loading && !data) return <div className="container">Loading...</div>;
  if (error) return <div className="container">Error: {error}</div>;
  if (!data) return <div className="container">No data available</div>;

  return (
    <div className="container">
      <h1>Live Factory Metrics</h1>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem', marginTop: '2rem' }}>
        <div className="card">
          <h3>Motor 1</h3>
          <p>Speed: {data.motor1Speed?.toFixed(1)} RPM</p>
          <p>Temperature: {data.motor1Temp?.toFixed(1)} °C</p>
          <p>Status: {data.motor1Run ? '🟢 Running' : '🔴 Stopped'}</p>
        </div>

        <div className="card">
          <h3>Motor 2</h3>
          <p>Speed: {data.motor2Speed?.toFixed(1)} RPM</p>
          <p>Temperature: {data.motor2Temp?.toFixed(1)} °C</p>
          <p>Status: {data.motor2Run ? '🟢 Running' : '🔴 Stopped'}</p>
        </div>

        <div className="card">
          <h3>Conveyor 1</h3>
          <p>Speed: {data.conveyor1Speed?.toFixed(1)} cm/s</p>
          <p>Status: {data.conveyor1Run ? '🟢 Running' : '🔴 Stopped'}</p>
        </div>

        <div className="card">
          <h3>Sensors</h3>
          <p>Sensor 1: {data.sensor1Value?.toFixed(2)}</p>
          <p>Sensor 2: {data.sensor2Value ? '🟢 Active' : '⚪ Inactive'}</p>
        </div>
      </div>

      <div className="card" style={{ marginTop: '2rem' }}>
        <h2>Speed Trends</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={history}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="motor1Speed" stroke="#8884d8" name="Motor 1 Speed" />
            <Line type="monotone" dataKey="motor2Speed" stroke="#82ca9d" name="Motor 2 Speed" />
            <Line type="monotone" dataKey="conveyor" stroke="#ffc658" name="Conveyor Speed" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="card" style={{ marginTop: '2rem' }}>
        <h2>Temperature Trends</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={history}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="motor1Temp" stroke="#ff7300" name="Motor 1 Temp" />
            <Line type="monotone" dataKey="motor1Temp" stroke="#ff0000" name="Motor 2 Temp" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default LiveMetrics;
