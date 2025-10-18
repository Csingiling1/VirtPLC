function HMIEmbed() {
  return (
    <div className="container">
      <h1>HMI Interface</h1>
      
      <div className="card">
        <p style={{ marginBottom: '1rem' }}>
          Ignition HMI interface will be embedded here when Ignition Edge is running.
        </p>
        
        <div style={{ 
          width: '100%', 
          height: '600px', 
          background: '#2a2a2a', 
          border: '2px solid #444',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <div style={{ textAlign: 'center' }}>
            <h2 style={{ marginBottom: '1rem' }}>Ignition HMI Embed Placeholder</h2>
            <p>To embed Ignition HMI:</p>
            <ol style={{ textAlign: 'left', marginTop: '1rem' }}>
              <li>Start Ignition Edge gateway on port 8088</li>
              <li>Create a dashboard in Perspective module</li>
              <li>Configure tag bindings to OPC-UA server (opc.tcp://backend:4840)</li>
              <li>Publish the Perspective project</li>
              <li>Update iframe src below to: http://localhost:8088/data/perspective/client/YourProjectName</li>
            </ol>
            <div style={{ marginTop: '2rem', padding: '1rem', background: '#1a1a1a', borderRadius: '4px' }}>
              <code style={{ fontSize: '0.9rem' }}>
                {'<iframe src="http://localhost:8088/data/perspective/client/VirtPLC" ... />'}
              </code>
            </div>
          </div>
        </div>

        {/* Uncomment when Ignition is configured */}
        {/* <iframe 
          src="http://localhost:8088/data/perspective/client/VirtPLC"
          style={{
            width: '100%',
            height: '600px',
            border: 'none',
            borderRadius: '8px'
          }}
          title="Ignition HMI"
        /> */}
      </div>
    </div>
  );
}

export default HMIEmbed;
