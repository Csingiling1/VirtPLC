import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import {
  Code,
  Database,
  Cpu,
  Network,
  Bot,
  Webhook,
  Search,
  Copy,
  ExternalLink,
  Play,
  CheckCircle,
  AlertCircle,
  Clock,
  FileText,
  Zap
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const APIReference = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');

  const apiServices = [
    {
      name: "Backend REST API",
      description: "Spring Boot REST API for data management and device control",
      baseUrl: "http://localhost:18080",
      swaggerUrl: "http://localhost:18080/swagger-ui.html",
      docsUrl: "http://localhost:18080/api-docs",
      endpoints: ["Data queries", "Device management", "Authentication", "Dashboard data"],
      icon: <Database className="h-6 w-6" />,
      color: "bg-blue-500"
    },
    {
      name: "AI Service API",
      description: "FastAPI service for machine learning and predictive analytics",
      baseUrl: "http://localhost:3001",
      swaggerUrl: "http://localhost:3001/docs", // FastAPI automatic docs
      docsUrl: "http://localhost:3001/openapi.json",
      endpoints: ["Model training", "Predictions", "Anomaly detection", "Analytics"],
      icon: <Bot className="h-6 w-6" />,
      color: "bg-purple-500"
    },
    {
      name: "gRPC Services",
      description: "High-performance RPC services for real-time data streaming",
      baseUrl: "localhost:9090 (Backend), localhost:9091 (AI)",
      docsUrl: "http://localhost:18080/api-docs", // Same as REST API docs
      endpoints: ["Streaming data", "Real-time analytics", "Device communication"],
      icon: <Zap className="h-6 w-6" />,
      color: "bg-green-500"
    },
    {
      name: "WebSocket APIs",
      description: "Real-time bidirectional communication for live updates",
      baseUrl: "ws://localhost:8080",
      endpoints: ["Live data streams", "Real-time alerts", "Device status updates"],
      icon: <Network className="h-6 w-6" />,
      color: "bg-orange-500"
    }
  ];

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const MethodBadge = ({ method }: { method: string }) => {
    const colors = {
      GET: "bg-green-100 text-green-800",
      POST: "bg-blue-100 text-blue-800",
      PUT: "bg-yellow-100 text-yellow-800",
      DELETE: "bg-red-100 text-red-800",
      gRPC: "bg-purple-100 text-purple-800"
    };

    return (
      <Badge className={`${colors[method as keyof typeof colors] || 'bg-gray-100 text-gray-800'}`}>
        {method}
      </Badge>
    );
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button variant="ghost" onClick={() => navigate('/')}>
                ← Back to Home
              </Button>
              <div className="flex items-center space-x-2">
                <Code className="h-6 w-6 text-primary" />
                <h1 className="text-2xl font-bold">API Reference</h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search services..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-64"
                />
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold mb-4">Interactive API Documentation</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Explore our comprehensive API documentation with interactive Swagger UI interfaces.
            Test endpoints directly from your browser and view detailed specifications.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {apiServices.filter(service =>
            service.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            service.description.toLowerCase().includes(searchTerm.toLowerCase())
          ).map((service, index) => (
            <Card key={index} className="hover:shadow-lg transition-all">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-lg ${service.color} text-white`}>
                      {service.icon}
                    </div>
                    <span>{service.name}</span>
                  </div>
                  {service.swaggerUrl && (
                    <Button
                      size="sm"
                      onClick={() => window.open(service.swaggerUrl, '_blank')}
                      className="shrink-0"
                    >
                      <ExternalLink className="h-4 w-4 mr-2" />
                      Open Docs
                    </Button>
                  )}
                </CardTitle>
                <p className="text-muted-foreground">{service.description}</p>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div>
                    <Badge variant="outline" className="mb-2">Base URL</Badge>
                    <code className="block text-sm bg-muted p-2 rounded">{service.baseUrl}</code>
                  </div>

                  <div>
                    <Badge variant="outline" className="mb-2">Endpoints</Badge>
                    <div className="flex flex-wrap gap-1">
                      {service.endpoints.map((endpoint, idx) => (
                        <Badge key={idx} variant="secondary" className="text-xs">
                          {endpoint}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {service.docsUrl && (
                    <div className="flex space-x-2 pt-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => window.open(service.docsUrl, '_blank')}
                      >
                        <FileText className="h-4 w-4 mr-2" />
                        OpenAPI JSON
                      </Button>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <Tabs defaultValue="getting-started" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="getting-started">Getting Started</TabsTrigger>
            <TabsTrigger value="authentication">Authentication</TabsTrigger>
            <TabsTrigger value="examples">Code Examples</TabsTrigger>
          </TabsList>

          <TabsContent value="getting-started" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Getting Started with VirtPLC APIs</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="font-semibold mb-2">1. Choose Your API</h4>
                  <p className="text-muted-foreground">
                    Select the appropriate API based on your use case:
                  </p>
                  <ul className="list-disc list-inside mt-2 space-y-1 text-sm">
                    <li><strong>REST API:</strong> Standard HTTP endpoints for data management and device control</li>
                    <li><strong>gRPC:</strong> High-performance streaming for real-time applications</li>
                    <li><strong>WebSocket:</strong> Bidirectional communication for live updates</li>
                    <li><strong>AI Service:</strong> Machine learning and predictive analytics</li>
                  </ul>
                </div>

                <div>
                  <h4 className="font-semibold mb-2">2. Interactive Documentation</h4>
                  <p className="text-muted-foreground">
                    Use the Swagger UI links above to explore and test API endpoints interactively.
                    Each service provides comprehensive documentation with request/response examples.
                  </p>
                </div>

                <div>
                  <h4 className="font-semibold mb-2">3. Authentication</h4>
                  <p className="text-muted-foreground">
                    Most endpoints require authentication. Use OAuth2 flows or API keys as documented
                    in the Swagger interfaces.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="authentication" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Authentication Methods</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="font-semibold mb-2">OAuth2 (Recommended)</h4>
                  <p className="text-muted-foreground mb-2">
                    Secure authentication using industry-standard OAuth2 flows.
                  </p>
                  <div className="bg-muted p-3 rounded-lg text-sm">
                    <strong>Supported Providers:</strong> Google, Microsoft, Ignition
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold mb-2">API Keys</h4>
                  <p className="text-muted-foreground mb-2">
                    Simple token-based authentication for service-to-service communication.
                  </p>
                  <div className="bg-muted p-3 rounded-lg text-sm">
                    <code>Authorization: Bearer {'{your-api-key}'}</code>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold mb-2">JWT Tokens</h4>
                  <p className="text-muted-foreground mb-2">
                    JSON Web Tokens for stateless authentication.
                  </p>
                  <div className="bg-muted p-3 rounded-lg text-sm">
                    <code>Authorization: Bearer {'{jwt-token}'}</code>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="examples" className="mt-6">
            <div className="grid md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">JavaScript/Node.js</CardTitle>
                </CardHeader>
                <CardContent>
                  <pre className="bg-muted p-4 rounded-lg text-sm overflow-x-auto">
                    <code>{`// REST API Example
const response = await fetch('/api/data/latest', {
  headers: {
    'Authorization': 'Bearer ' + token
  }
});
const data = await response.json();

// WebSocket Example
const ws = new WebSocket('ws://localhost:8080/ws/data');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('New data:', data);
};`}</code>
                  </pre>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Python</CardTitle>
                </CardHeader>
                <CardContent>
                  <pre className="bg-muted p-4 rounded-lg text-sm overflow-x-auto">
                    <code>{`# REST API Example
import requests

response = requests.get('/api/data/latest',
                       headers={'Authorization': f'Bearer {token}'})
data = response.json()

# gRPC Example
import grpc
from plc_service_pb2 import PlcDataRequest
from plc_service_pb2_grpc import PlcDataServiceStub

channel = grpc.insecure_channel('localhost:9090')
stub = PlcDataServiceStub(channel)
request = PlcDataRequest(device_id='PLC001')
response = stub.GetDataStream(request)`}</code>
                  </pre>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default APIReference;