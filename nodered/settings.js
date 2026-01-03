/**
 * Node-RED Settings for VirtPLC MQTT to OPC-UA Bridge
 */

module.exports = {
    // Node-RED runtime settings
    uiPort: process.env.PORT || 1880,
    mqttReconnectTime: 15000,
    serialReconnectTime: 15000,
    debugMaxLength: 1000,
    
    // Flow File Name
    flowFile: 'flows/flows.json',

    // Flow File Pretty Print
    
    // User directory
    userDir: '/data',
    
    // Security - DISABLED for development
    // adminAuth: {
    //     type: "credentials",
    //     users: [{
    //         username: process.env.NODE_RED_USERNAME || "admin",
    //         password: process.env.NODE_RED_PASSWORD_HASH || "$2a$08$zZWtXTja0fB1pzD4sHCMyOCMYz2Z6dNbM6tl8sJogENOMcxWV9DN.",
    //         permissions: "*"
    //     }]
    // },
    
    // HTTPS settings (optional)
    // https: {
    //     key: require("fs").readFileSync('/data/certs/privkey.pem'),
    //     cert: require("fs").readFileSync('/data/certs/cert.pem')
    // },
    
    // Runtime settings
    functionGlobalContext: {
        mqtt_broker: process.env.MQTT_BROKER || 'mqtt',
        mqtt_port: process.env.MQTT_PORT || 1883
    },
    
    // Logging
    logging: {
        console: {
            level: "info",
            metrics: false,
            audit: false
        }
    },
    
    // Editor settings
    editorTheme: {
        projects: {
            enabled: false
        },
        palette: {
            editable: true
        }
    },
    
    // Function node settings
    functionExternalModules: true,
    
    // Context storage
    contextStorage: {
        default: {
            module: "memory"
        }
    },
    
    // Export settings
    exportGlobalContextKeys: false
}
