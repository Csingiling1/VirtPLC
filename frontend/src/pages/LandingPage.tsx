import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ArrowRight, BarChart3, Shield, Zap, Factory, TrendingUp, Users, CheckCircle, Database, Cloud, Lock, Cpu, Network, Layers } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

const LandingPage = () => {
    const navigate = useNavigate();
    const { isAuthenticated } = useAuth();

    const features = [
        {
            icon: <BarChart3 className="h-8 w-8 text-primary" />,
            title: "Real-time Monitoring",
            description: "Monitor your factory equipment with live sensor data and predictive analytics."
        },
        {
            icon: <Shield className="h-8 w-8 text-primary" />,
            title: "Multi-tenant Security",
            description: "Each company has isolated data and dedicated resources for maximum security."
        },
        {
            icon: <Zap className="h-8 w-8 text-primary" />,
            title: "AI-Powered Insights",
            description: "Get intelligent recommendations and automated maintenance alerts."
        },
        {
            icon: <Factory className="h-8 w-8 text-primary" />,
            title: "Factory Automation",
            description: "Connect and control PLC devices with modern web interfaces."
        },
        {
            icon: <TrendingUp className="h-8 w-8 text-primary" />,
            title: "Performance Analytics",
            description: "Track equipment performance trends and optimize operations."
        },
        {
            icon: <Users className="h-8 w-8 text-primary" />,
            title: "Team Collaboration",
            description: "Share insights and collaborate across your organization."
        }
    ];

    const architectureComponents = [
        {
            icon: <Factory className="h-10 w-10 text-primary" />,
            title: "HMI Interface",
            description: "Modern web-based Human-Machine Interface for factory operators and managers.",
            tech: "React, TypeScript, Tailwind CSS"
        },
        {
            icon: <Database className="h-10 w-10 text-primary" />,
            title: "Time-Series Database",
            description: "High-performance TimescaleDB for storing and querying sensor data efficiently.",
            tech: "PostgreSQL + TimescaleDB"
        },
        {
            icon: <Cloud className="h-10 w-10 text-primary" />,
            title: "Backend API",
            description: "RESTful API server handling business logic, authentication, and data processing.",
            tech: "Spring Boot, Java 17, JPA"
        },
        {
            icon: <Cpu className="h-10 w-10 text-primary" />,
            title: "AI Service",
            description: "Intelligent analysis engine providing predictive maintenance and insights.",
            tech: "Python FastAPI, Ollama, Machine Learning"
        },
        {
            icon: <Network className="h-10 w-10 text-primary" />,
            title: "OPC UA Server",
            description: "Industrial protocol gateway connecting to PLC devices and sensors.",
            tech: "Python, OPC UA, MQTT"
        },
        {
            icon: <Lock className="h-10 w-10 text-primary" />,
            title: "Multi-tenant Security",
            description: "Isolated environments per company with JWT authentication and RBAC.",
            tech: "JWT, Spring Security, Company Isolation"
        }
    ];

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
                        <Button size="lg" variant="outline" onClick={() => navigate('/demo')} className="text-lg px-8">
                            Watch Demo
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