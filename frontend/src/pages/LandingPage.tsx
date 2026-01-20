import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Factory,
  Database,
  Cpu,
  Network,
  Layers,
  Cloud,
  Lock,
  BarChart3,
  Zap,
  Settings,
  Code,
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
  RefreshCw
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

// Service status checking hook
const useServiceStatus = () => {
  const [statuses, setStatuses] = useState<Record<string, 'ready' | 'checking' | 'error'>>({});
  const [lastChecked, setLastChecked] = useState<Date | null>(null);
  const [isChecking, setIsChecking] = useState(false);

  const checkService = async (name: string, url: string) => {
    try {
      const response = await fetch(url, { 
        method: 'GET',
        headers: { 'Accept': 'application/json' }
      });
      return response.ok ? 'ready' : 'error';
    } catch {
      return 'error';
    }
  };

  const checkAllServices = async () => {
    setIsChecking(true);
    setStatuses(prev => ({ ...prev, 'Backend': 'checking', 'AI Service': 'checking', 'Database': 'checking' }));

    const results = await Promise.all([
      checkService('Backend', 'http://localhost:18080/actuator/health'),
      checkService('AI Service', 'http://localhost:3001/health'),
      checkService('Database', 'http://localhost:18080/actuator/health'), // Backend health includes DB
    ]);

    setStatuses({
      'Backend': results[0],
      'AI Service': results[1],
      'Database': results[2],
    });
    setLastChecked(new Date());
    setIsChecking(false);
  };

  useEffect(() => {
    checkAllServices();
    const interval = setInterval(checkAllServices, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  return { statuses, checkAllServices, lastChecked, isChecking };
};

const LandingPage = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { statuses, checkAllServices, lastChecked, isChecking } = useServiceStatus();

  const systemCapabilities = [
    {
      icon: <Factory className="h-8 w-8 text-blue-500" />,
      title: "PLC Device Integration",
      description: "Connect to industrial PLC devices via MQTT, OPC-UA, and custom protocols",
      tech: "Python, MQTT, OPC-UA"
    },
    {
      icon: <Database className="h-8 w-8 text-green-500" />,
      title: "Time-Series Data Storage",
      description: "High-performance TimescaleDB for efficient sensor data storage and querying",
      tech: "PostgreSQL + TimescaleDB"
    },
    {
      icon: <Cpu className="h-8 w-8 text-purple-500" />,
      title: "AI-Powered Analytics",
      description: "Machine learning models for anomaly detection and predictive maintenance",
      tech: "Python, FastAPI, gRPC, Scikit-learn"
    },
    {
      icon: <Network className="h-8 w-8 text-orange-500" />,
      title: "Real-time Communication",
      description: "WebSocket and MQTT for live data streaming and device control",
      tech: "WebSockets, MQTT, RabbitMQ"
    },
    {
      icon: <BarChart3 className="h-8 w-8 text-cyan-500" />,
      title: "Interactive Dashboards",
      description: "Real-time monitoring with customizable charts and alerts",
      tech: "React, TypeScript, Chart.js"
    },
    {
      icon: <Workflow className="h-8 w-8 text-red-500" />,
      title: "Node-RED Integration",
      description: "Visual programming for IoT workflows and data processing pipelines",
      tech: "Node-RED, MQTT, JavaScript"
    }
  ];

  const architectureLayers = [
    {
      layer: "Frontend Layer",
      icon: <Monitor className="h-6 w-6" />,
      components: [
        { name: "React Dashboard", tech: "TypeScript, Tailwind CSS", status: "ready" },
        { name: "Real-time Charts", tech: "Chart.js, WebSockets", status: "ready" },
        { name: "Device Manager", tech: "React, REST API", status: "ready" },
        { name: "AI Assistant", tech: "Claude API, React", status: "ready" }
      ]
    },
    {
      layer: "API Gateway",
      icon: <Network className="h-6 w-6" />,
      components: [
        { name: "Spring Boot Backend", tech: "Java 21, REST + gRPC", status: statuses['Backend'] || 'checking' },
        { name: "AI Service", tech: "Python, FastAPI + gRPC", status: statuses['AI Service'] || 'checking' },
        { name: "Authentication", tech: "JWT, Spring Security", status: "ready" },
        { name: "API Gateway", tech: "Nginx, Load Balancing", status: "ready" }
      ]
    },
    {
      layer: "Data Layer",
      icon: <Database className="h-6 w-6" />,
      components: [
        { name: "TimescaleDB", tech: "Time-series optimized", status: statuses['Database'] || 'checking' },
        { name: "PostgreSQL", tech: "Relational data", status: statuses['Database'] || 'checking' },
        { name: "Redis Cache", tech: "Session & data cache", status: "ready" },
        { name: "Data Migration", tech: "Automated scripts", status: "ready" }
      ]
    },
    {
      layer: "IoT & Processing",
      icon: <Settings className="h-6 w-6" />,
      components: [
        { name: "Go Collector", tech: "Data ingestion service", status: "ready" },
        { name: "MQTT Broker", tech: "RabbitMQ, Device comms", status: "ready" },
        { name: "Node-RED", tech: "Workflow automation", status: "ready" },
        { name: "OPC-UA Server", tech: "Industrial protocols", status: "ready" }
      ]
    },
    {
      layer: "Infrastructure",
      icon: <Server className="h-6 w-6" />,
      components: [
        { name: "Docker Compose", tech: "Container orchestration", status: "ready" },
        { name: "Kubernetes", tech: "Production deployment", status: "ready" },
        { name: "Jenkins CI/CD", tech: "Automated pipelines", status: "ready" },
        { name: "Monitoring", tech: "Health checks, logs", status: "ready" }
      ]
    }
  ];

  const quickActions = [
    {
      title: "Start Monitoring",
      description: "Launch the real-time dashboard",
      icon: <Activity className="h-5 w-5" />,
      action: () => navigate(isAuthenticated ? '/monitoring' : '/login'),
      color: "bg-blue-500 hover:bg-blue-600"
    },
    {
      title: "View Factory Layout",
      description: "Interactive 3D factory visualization",
      icon: <Eye className="h-5 w-5" />,
      action: () => navigate(isAuthenticated ? '/factory' : '/login'),
      color: "bg-green-500 hover:bg-green-600"
    },
    {
      title: "AI Analysis",
      description: "Predictive maintenance insights",
      icon: <Bot className="h-5 w-5" />,
      action: () => navigate(isAuthenticated ? '/ai-assistant' : '/login'),
      color: "bg-purple-500 hover:bg-purple-600"
    },
    {
      title: "API Reference",
      description: "Explore REST, gRPC, and WebSocket APIs",
      icon: <Code className="h-5 w-5" />,
      action: () => navigate('/api-reference'),
      color: "bg-indigo-500 hover:bg-indigo-600"
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <Factory className="h-8 w-8 text-primary" />
            <span className="text-2xl font-bold">VirtPLC</span>
            <Badge variant="outline" className="ml-2">v4.0</Badge>
          </div>
          <div className="flex items-center space-x-4">
            <Button variant="ghost" onClick={() => navigate('/documentation')}>
              Documentation
            </Button>
            <Button variant="ghost" onClick={() => navigate('/login')}>
              Sign In
            </Button>
            <Button onClick={() => navigate(isAuthenticated ? '/dashboard' : '/register')}>
              {isAuthenticated ? 'Dashboard' : 'Get Started'}
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-16 px-4">
        <div className="container mx-auto text-center">
          <div className="flex justify-center mb-6">
            <Badge variant="secondary" className="px-4 py-2 text-sm">
              <Code className="h-4 w-4 mr-2" />
              Industrial IoT Platform
            </Badge>
          </div>
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            Complete Factory
            <span className="text-primary block">Automation Platform</span>
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto">
            A comprehensive industrial IoT solution with PLC integration, real-time monitoring,
            AI-powered analytics, and modern web interfaces for factory automation.
          </p>

          {/* Quick Actions */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8 max-w-4xl mx-auto">
            {quickActions.map((action, index) => (
              <Card key={index} className="cursor-pointer hover:shadow-lg transition-all"
                onClick={action.action}>
                <CardContent className="p-4 text-center">
                  <div className={`inline-flex p-3 rounded-lg ${action.color} text-white mb-3`}>
                    {action.icon}
                  </div>
                  <h3 className="font-semibold mb-1">{action.title}</h3>
                  <p className="text-sm text-muted-foreground">{action.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" onClick={() => navigate(isAuthenticated ? '/monitoring' : '/login')} className="text-lg px-8">
              <Play className="mr-2 h-5 w-5" />
              Start Monitoring
            </Button>
            <Button size="lg" variant="outline" onClick={() => navigate('/documentation')} className="text-lg px-8">
              View Architecture
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </div>
        </div>
      </section>

      {/* System Capabilities */}
      <section className="py-16 px-4 bg-muted/30">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">System Capabilities</h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Comprehensive industrial automation platform with modern protocols and AI integration
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {systemCapabilities.map((capability, index) => (
              <Card key={index} className="border-0 shadow-sm hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-center space-x-3">
                    {capability.icon}
                    <div>
                      <CardTitle className="text-lg">{capability.title}</CardTitle>
                      <Badge variant="secondary" className="text-xs mt-1">
                        {capability.tech}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">{capability.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Architecture Overview */}
      <section className="py-16 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">System Architecture</h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Multi-layered architecture designed for scalability, reliability, and modern development practices
            </p>
          </div>

          <Tabs defaultValue="overview" className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-8">
              <TabsTrigger value="overview">Architecture Layers</TabsTrigger>
              <TabsTrigger value="deployment">Deployment Options</TabsTrigger>
            </TabsList>

            <TabsContent value="overview">
              <div className="space-y-6">
                {/* Service Status Controls */}
                <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
                  <div className="flex items-center space-x-4">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={checkAllServices}
                      disabled={isChecking}
                      className="flex items-center space-x-2"
                    >
                      <RefreshCw className={`h-4 w-4 ${isChecking ? 'animate-spin' : ''}`} />
                      <span>{isChecking ? 'Checking...' : 'Refresh Status'}</span>
                    </Button>
                    {lastChecked && (
                      <span className="text-sm text-muted-foreground">
                        Last checked: {lastChecked.toLocaleTimeString()}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center space-x-2 text-sm">
                    <div className="flex items-center space-x-1">
                      <div className="w-2 h-2 rounded-full bg-green-500"></div>
                      <span>Ready</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
                      <span>Checking</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <div className="w-2 h-2 rounded-full bg-red-500"></div>
                      <span>Error</span>
                    </div>
                  </div>
                </div>

                {architectureLayers.map((layer, index) => (
                  <Card key={index} className="border-l-4 border-l-primary">
                    <CardHeader>
                      <div className="flex items-center space-x-3">
                        <div className="p-2 bg-primary/10 rounded-lg">
                          {layer.icon}
                        </div>
                        <CardTitle className="text-xl">{layer.layer}</CardTitle>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                        {layer.components.map((component, compIndex) => (
                          <div key={compIndex} className="p-3 border rounded-lg">
                            <div className="font-medium text-sm mb-1">{component.name}</div>
                            <Badge variant="outline" className="text-xs mb-2">
                              {component.tech}
                            </Badge>
                            <div className="flex items-center">
                              <div className={`w-2 h-2 rounded-full mr-2 ${
                                component.status === 'ready' ? 'bg-green-500' :
                                component.status === 'error' ? 'bg-red-500' :
                                'bg-yellow-500'
                              }`}></div>
                              <span className="text-xs text-muted-foreground capitalize">
                                {component.status}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="deployment">
              <div className="grid md:grid-cols-2 gap-8">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Container className="h-5 w-5 mr-2 text-blue-500" />
                      Development (Docker Compose)
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground mb-4">
                      Single-machine deployment for development and testing
                    </p>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center">
                        <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                        All services in containers
                      </div>
                      <div className="flex items-center">
                        <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                        Hot reload for development
                      </div>
                      <div className="flex items-center">
                        <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                        Local databases included
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Server className="h-5 w-5 mr-2 text-green-500" />
                      Production (Kubernetes)
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground mb-4">
                      Distributed deployment for production environments
                    </p>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center">
                        <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                        Multi-node scaling
                      </div>
                      <div className="flex items-center">
                        <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                        High availability
                      </div>
                      <div className="flex items-center">
                        <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                        Automated deployments
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </section>

      {/* Technology Stack */}
      <section className="py-16 px-4 bg-muted/30">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Technology Stack</h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Modern, scalable technologies chosen for industrial reliability and performance
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="text-center">
              <CardContent className="p-6">
                <div className="text-4xl mb-4">🐳</div>
                <h3 className="font-semibold mb-2">Containerization</h3>
                <p className="text-sm text-muted-foreground">Docker for consistent deployments</p>
              </CardContent>
            </Card>

            <Card className="text-center">
              <CardContent className="p-6">
                <div className="text-4xl mb-4">☸️</div>
                <h3 className="font-semibold mb-2">Orchestration</h3>
                <p className="text-sm text-muted-foreground">Kubernetes for production scaling</p>
              </CardContent>
            </Card>

            <Card className="text-center">
              <CardContent className="p-6">
                <div className="text-4xl mb-4">🔧</div>
                <h3 className="font-semibold mb-2">CI/CD</h3>
                <p className="text-sm text-muted-foreground">Jenkins pipelines for automation</p>
              </CardContent>
            </Card>

            <Card className="text-center">
              <CardContent className="p-6">
                <div className="text-4xl mb-4">🤖</div>
                <h3 className="font-semibold mb-2">AI/ML</h3>
                <p className="text-sm text-muted-foreground">Python ecosystem for intelligence</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Getting Started */}
      <section className="py-16 px-4">
        <div className="container mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Explore?</h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            Dive into the VirtPLC platform and see how it can transform your factory operations
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" onClick={() => navigate(isAuthenticated ? '/monitoring' : '/login')} className="text-lg px-8">
              <Activity className="mr-2 h-5 w-5" />
              Launch Dashboard
            </Button>
            <Button size="lg" variant="outline" onClick={() => navigate('/documentation')} className="text-lg px-8">
              <GitBranch className="mr-2 h-5 w-5" />
              View Documentation
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-8 px-4">
        <div className="container mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <Factory className="h-6 w-6 text-primary" />
              <span className="text-lg font-semibold">VirtPLC</span>
              <Badge variant="outline">Open Source</Badge>
            </div>
            <div className="flex space-x-6 text-sm text-muted-foreground">
              <a href="https://github.com/Dedzsinator/VirtPLC" className="hover:text-primary">GitHub</a>
              <a href="/docs" className="hover:text-primary">Documentation</a>
              <a href="/api" className="hover:text-primary">API Reference</a>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t text-center text-sm text-muted-foreground">
            Built with modern industrial IoT technologies
          </div>
        </div>
      </footer>
    </div>
  );
  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <Factory className="h-8 w-8 text-primary" />
            <span className="text-2xl font-bold">VirtPLC</span>
          </div>
          <div className="flex items-center space-x-4">
            <Button variant="ghost" onClick={() => navigate('/login')}>
              Sign In
            </Button>
            <Button onClick={() => navigate(isAuthenticated ? '/dashboard' : '/register')}>
              {isAuthenticated ? 'Go to Dashboard' : 'Get Started'}
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto text-center">
          <Badge variant="secondary" className="mb-4">
            🚀 Now with AI-Powered Factory Intelligence
          </Badge>
          <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
            Smart Factory Monitoring for the Modern Age
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Transform your factory operations with real-time monitoring, predictive maintenance,
            and AI-driven insights. Scale effortlessly with our multi-tenant architecture.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" onClick={() => navigate(isAuthenticated ? '/dashboard' : '/register')} className="text-lg px-8">
              {isAuthenticated ? 'Go to Dashboard' : 'Start Free Trial'}
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
            <Button size="lg" variant="outline" onClick={() => navigate('/api-reference')} className="text-lg px-8">
              API Reference
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 bg-muted/50">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">Everything you need to optimize your factory</h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              From real-time monitoring to predictive maintenance, VirtPLC provides comprehensive
              factory intelligence solutions.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="border-0 shadow-lg hover:shadow-xl transition-shadow">
                <CardHeader>
                  <div className="mb-4">{feature.icon}</div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-primary mb-2">99.9%</div>
              <div className="text-muted-foreground">Uptime</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary mb-2">500+</div>
              <div className="text-muted-foreground">Factories Monitored</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary mb-2">10M+</div>
              <div className="text-muted-foreground">Data Points Daily</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary mb-2">24/7</div>
              <div className="text-muted-foreground">AI Monitoring</div>
            </div>
          </div>
        </div>
      </section>

      {/* Architecture Section */}
      <section className="py-20 px-4 bg-muted/50">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">Enterprise-Grade Architecture</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
              Built for scale and reliability, our multi-tenant architecture ensures each company
              operates in complete isolation while sharing the robust underlying infrastructure.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {architectureComponents.map((component, index) => (
              <Card key={index} className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                <CardHeader className="text-center">
                  <div className="flex justify-center mb-4">{component.icon}</div>
                  <CardTitle className="text-xl">{component.title}</CardTitle>
                  <Badge variant="secondary" className="w-fit mx-auto mt-2">
                    {component.tech}
                  </Badge>
                </CardHeader>
                <CardContent className="text-center">
                  <p className="text-muted-foreground">{component.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Architecture Benefits */}
          <div className="mt-16 grid md:grid-cols-2 gap-8">
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Layers className="h-6 w-6 text-primary mr-3" />
                  Multi-Tenant Isolation
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground mb-4">
                  Each company gets dedicated resources and complete data isolation,
                  ensuring security and performance guarantees.
                </p>
                <ul className="space-y-2">
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    Separate databases per tenant
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    Isolated Kubernetes namespaces
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    Independent scaling per company
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Cloud className="h-6 w-6 text-primary mr-3" />
                  Cloud-Native Design
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground mb-4">
                  Built for the cloud with containerization, orchestration, and
                  automated deployment pipelines.
                </p>
                <ul className="space-y-2">
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    Docker containerization
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    Kubernetes orchestration
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    Automated CI/CD pipelines
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to modernize your factory operations?</h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-3xl mx-auto">
            Join leading manufacturers who trust VirtPLC for their critical factory monitoring needs.
            Our enterprise-grade, multi-tenant architecture ensures reliability, security, and scalability.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" onClick={() => navigate(isAuthenticated ? '/dashboard' : '/register')} className="text-lg px-8">
              {isAuthenticated ? 'Go to Dashboard' : 'Start Free Trial'}
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
            <Button size="lg" variant="outline" onClick={() => navigate('/login')} className="text-lg px-8">
              Sign In to Existing Account
            </Button>
          </div>
          <p className="text-sm text-muted-foreground mt-4">
            No credit card required • Full enterprise features included • 30-day free trial
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-12 px-4">
        <div className="container mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <Factory className="h-6 w-6 text-primary" />
              <span className="text-lg font-semibold">VirtPLC</span>
            </div>
            <div className="flex space-x-6 text-sm text-muted-foreground">
              <a href="#" className="hover:text-primary">Privacy Policy</a>
              <a href="#" className="hover:text-primary">Terms of Service</a>
              <a href="#" className="hover:text-primary">Contact</a>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t text-center text-sm text-muted-foreground">
            © 2025 VirtPLC. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;