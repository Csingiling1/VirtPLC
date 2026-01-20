import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Book,
  Code,
  Database,
  Cpu,
  Network,
  Layers,
  Cloud,
  Lock,
  BarChart3,
  Zap,
  Settings,
  GitBranch,
  Container,
  Server,
  Activity,
  Eye,
  Wrench,
  ArrowRight,
  Play,
  Monitor,
  Bot,
  Workflow,
  CheckCircle,
  ExternalLink,
  Download,
  FileText
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Documentation = () => {
  const navigate = useNavigate();

  const docs = [
    {
      title: "Getting Started",
      icon: <Play className="h-5 w-5" />,
      description: "Quick start guide for setting up VirtPLC",
      sections: [
        "System Requirements",
        "Installation Guide",
        "First Configuration",
        "Basic Operations"
      ]
    },
    {
      title: "Architecture Overview",
      icon: <Layers className="h-5 w-5" />,
      description: "Understanding the VirtPLC system architecture",
      sections: [
        "Component Overview",
        "Data Flow",
        "Network Topology",
        "Scalability Considerations"
      ]
    },
    {
      title: "PLC Integration",
      icon: <Cpu className="h-5 w-5" />,
      description: "Connecting and configuring PLC devices",
      sections: [
        "Supported Protocols",
        "Device Configuration",
        "Data Mapping",
        "Troubleshooting"
      ]
    },
    {
      title: "Database Management",
      icon: <Database className="h-5 w-5" />,
      description: "TimescaleDB configuration and optimization",
      sections: [
        "Schema Design",
        "Performance Tuning",
        "Backup & Recovery",
        "Data Retention Policies"
      ]
    },
    {
      title: "AI & Analytics",
      icon: <Bot className="h-5 w-5" />,
      description: "Using AI features for predictive maintenance",
      sections: [
        "Model Training",
        "Anomaly Detection",
        "Predictive Analytics",
        "Custom Models"
      ]
    },
    {
      title: "Deployment & Operations",
      icon: <Container className="h-5 w-5" />,
      description: "Production deployment and maintenance",
      sections: [
        "Docker Deployment",
        "Kubernetes Setup",
        "Monitoring & Logging",
        "Security Best Practices"
      ]
    }
  ];

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
                <Book className="h-6 w-6 text-primary" />
                <h1 className="text-2xl font-bold">Documentation</h1>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Download PDF
              </Button>
              <Button variant="outline" size="sm">
                <ExternalLink className="h-4 w-4 mr-2" />
                GitHub Wiki
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="container mx-auto px-4 py-8">
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="guides">Guides</TabsTrigger>
            <TabsTrigger value="reference">Reference</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="mt-6">
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {docs.map((doc, index) => (
                <Card key={index} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-primary/10 rounded-lg">
                        {doc.icon}
                      </div>
                      <CardTitle className="text-lg">{doc.title}</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground mb-4">{doc.description}</p>
                    <div className="space-y-2">
                      {doc.sections.map((section, idx) => (
                        <div key={idx} className="flex items-center text-sm">
                          <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                          {section}
                        </div>
                      ))}
                    </div>
                    <Button className="w-full mt-4" variant="outline">
                      <FileText className="h-4 w-4 mr-2" />
                      Read Guide
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="guides" className="mt-6">
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Play className="h-5 w-5 mr-2" />
                    Quick Start Guide
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="prose max-w-none">
                    <h3>1. System Requirements</h3>
                    <ul>
                      <li>Docker & Docker Compose</li>
                      <li>4GB RAM minimum</li>
                      <li>2 CPU cores minimum</li>
                      <li>10GB free disk space</li>
                    </ul>

                    <h3>2. Clone and Setup</h3>
                    <pre className="bg-muted p-4 rounded-lg">
                      <code>{`git clone https://github.com/Dedzsinator/VirtPLC.git
cd VirtPLC/essen-demo
chmod +x deploy-essen-demo.sh
./deploy-essen-demo.sh`}</code>
                    </pre>

                    <h3>3. Access the Application</h3>
                    <ul>
                      <li>Frontend: http://localhost:3000</li>
                      <li>Backend API: http://localhost:18080</li>
                      <li>AI Service: http://localhost:3001</li>
                    </ul>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Settings className="h-5 w-5 mr-2" />
                    Configuration Guide
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="prose max-w-none">
                    <h3>Environment Variables</h3>
                    <pre className="bg-muted p-4 rounded-lg">
                      <code>{`# Database
TIMESCALE_HOST=timescale
TIMESCALE_DB=virtplc_ts
TIMESCALE_USER=virtplc

# AI Service
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=qwen2:0.5b

# MQTT
MQTT_BROKER=mqtt
MQTT_USERNAME=virtplc`}</code>
                    </pre>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="reference" className="mt-6">
            <div className="grid gap-6 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>API Endpoints</CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-96">
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-semibold">Backend API</h4>
                        <div className="space-y-2 text-sm">
                          <div><code>GET /api/data</code> - Get PLC data</div>
                          <div><code>POST /api/devices</code> - Register device</div>
                          <div><code>GET /api/health</code> - Health check</div>
                        </div>
                      </div>

                      <div>
                        <h4 className="font-semibold">AI Service API</h4>
                        <div className="space-y-2 text-sm">
                          <div><code>POST /api/analyze</code> - Analyze data</div>
                          <div><code>GET /api/models</code> - List models</div>
                          <div><code>POST /api/train</code> - Train model</div>
                        </div>
                      </div>

                      <div>
                        <h4 className="font-semibold">WebSocket Endpoints</h4>
                        <div className="space-y-2 text-sm">
                          <div><code>ws://localhost:8080/ws/data</code> - Real-time data</div>
                          <div><code>ws://localhost:3001/ws/analysis</code> - AI analysis</div>
                        </div>
                      </div>
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Configuration Files</CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-96">
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-semibold">docker-compose.yml</h4>
                        <p className="text-sm text-muted-foreground mb-2">
                          Main service orchestration file
                        </p>
                        <Button size="sm" variant="outline">
                          View File
                        </Button>
                      </div>

                      <div>
                        <h4 className="font-semibold">.env</h4>
                        <p className="text-sm text-muted-foreground mb-2">
                          Environment configuration
                        </p>
                        <Button size="sm" variant="outline">
                          View Template
                        </Button>
                      </div>

                      <div>
                        <h4 className="font-semibold">nginx.conf</h4>
                        <p className="text-sm text-muted-foreground mb-2">
                          Reverse proxy configuration
                        </p>
                        <Button size="sm" variant="outline">
                          View Config
                        </Button>
                      </div>
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Documentation;