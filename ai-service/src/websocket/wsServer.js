/**
 * WebSocket server for real-time AI predictions and alerts
 */
export function startWebSocketServer(wss) {
  wss.on('connection', (ws, req) => {
    const clientIp = req.socket.remoteAddress;
    console.log(`🔌 WebSocket client connected: ${clientIp}`);
    
    // Send welcome message
    ws.send(JSON.stringify({
      type: 'connected',
      message: 'Connected to VirtPLC AI Service',
      timestamp: new Date().toISOString()
    }));
    
    // Handle incoming messages
    ws.on('message', (message) => {
      try {
        const data = JSON.parse(message.toString());
        console.log('📨 Received message:', data);
        
        // Echo back for now (can add custom handlers)
        ws.send(JSON.stringify({
          type: 'ack',
          received: data,
          timestamp: new Date().toISOString()
        }));
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error.message);
      }
    });
    
    // Handle disconnection
    ws.on('close', () => {
      console.log(`🔌 WebSocket client disconnected: ${clientIp}`);
    });
    
    // Handle errors
    ws.on('error', (error) => {
      console.error('WebSocket error:', error.message);
    });
  });
  
  console.log('✅ WebSocket server initialized');
}
