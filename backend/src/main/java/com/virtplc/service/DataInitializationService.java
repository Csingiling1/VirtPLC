package com.virtplc.service;

import com.virtplc.model.*;
import com.virtplc.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Slf4j
public class DataInitializationService implements CommandLineRunner {

        private final TenantRepository tenantRepository;
        private final ManufacturerRepository manufacturerRepository;
        private final CompanyRepository companyRepository;
        private final FactoryRepository factoryRepository;
        private final PLCRepository plcRepository;
        private final SensorRepository sensorRepository;
        private final UserRepository userRepository;
        private final PasswordEncoder passwordEncoder;

        @Override
        @Transactional
        public void run(String... args) throws Exception {
                if (userRepository.count() == 0) {
                        log.info("Initializing comprehensive test data...");
                        initializeComprehensiveTestData();
                        log.info("Comprehensive test data initialization completed");
                } else {
                        log.info("User data already exists, skipping initialization");
                }
        }

        private void initializeComprehensiveTestData() {
                createSystemAdmin();
                createAcmeManufacturing();
                createTechSolutions();
                createGlobalIndustries();
                printTestCredentials();
        }

        private void createSystemAdmin() {
                Company adminCompany = Company.builder()
                                .name("VirtPLC System")
                                .domain("virtplc-admin")
                                .displayName("VirtPLC System Administration")
                                .description("System administration company")
                                .active(true)
                                .build();
                adminCompany = companyRepository.save(adminCompany);

                User systemAdmin = User.builder()
                                .email("admin@virtplc.com")
                                .password(passwordEncoder.encode("admin123"))
                                .firstName("System")
                                .lastName("Administrator")
                                .role(User.Role.ADMIN)
                                .company(adminCompany)
                                .manufacturer(null)
                                .active(true)
                                .build();
                userRepository.save(systemAdmin);
        }

        private void createAcmeManufacturing() {
                Company company = Company.builder()
                                .name("Acme Manufacturing Corp")
                                .domain("acme-corp")
                                .displayName("Acme Manufacturing Corp")
                                .description("Leading manufacturer of industrial equipment")
                                .active(true)
                                .build();
                company = companyRepository.save(company);

                Tenant tenant = new Tenant("acme-corp", "Acme Manufacturing Corp",
                                "Leading manufacturer of industrial equipment");
                tenant = tenantRepository.save(tenant);

                Manufacturer manufacturer = new Manufacturer("acme-motors", "Acme Motor Division",
                                "High-performance motor manufacturing", tenant, company);
                manufacturer = manufacturerRepository.save(manufacturer);

                createUser("john.smith@acme.com", "acme123", "John", "Smith",
                                User.Role.MANUFACTURER_ADMIN, company, manufacturer);
                createUser("sarah.johnson@acme.com", "acme123", "Sarah", "Johnson",
                                User.Role.MANAGER, company, manufacturer);
                createUser("mike.wilson@acme.com", "acme123", "Mike", "Wilson",
                                User.Role.OPERATOR, company, manufacturer);

                Factory nyFactory = createFactory("acme-factory-ny", "New York Production Facility",
                                "Main production facility in NYC", manufacturer, "L", 120, 90, "#ef4444");
                Factory laFactory = createFactory("acme-factory-la", "Los Angeles Assembly Plant",
                                "West coast assembly facility", manufacturer, "rectangle", 100, 80, "#f59e0b");

                PLC nyPlc1 = createPLC("PLC-NY-001", "Siemens S7-1500 #1", "Assembly line controller",
                                nyFactory, 120.0, 720.0);
                createSensor(nyPlc1, "temp-ny-001", "Assembly Temperature", "temperature", "°C", 75.0, 5.0);
                createSensor(nyPlc1, "pressure-ny-001", "Hydraulic Pressure", "pressure", "bar", 150.0, 10.0);
                createSensor(nyPlc1, "vibration-ny-001", "Motor Vibration", "vibration", "mm/s", 2.5, 0.5);

                PLC nyPlc2 = createPLC("PLC-NY-002", "Allen-Bradley ControlLogix #1", "Quality control station",
                                nyFactory, 120.0, 90.0);
                createSensor(nyPlc2, "temp-ny-002", "QC Temperature", "temperature", "°C", 22.0, 1.0);
                createSensor(nyPlc2, "humidity-ny-002", "QC Humidity", "humidity", "%", 45.0, 5.0);

                PLC laPlc1 = createPLC("PLC-LA-001", "Schneider M580 #1", "Conveyor system controller",
                                laFactory, 50.0, 40.0);
                createSensor(laPlc1, "speed-la-001", "Conveyor Speed", "speed", "m/min", 15.0, 2.0);
                createSensor(laPlc1, "temp-la-001", "Motor Temperature", "temperature", "°C", 65.0, 8.0);
        }

        private void createTechSolutions() {
                Company company = Company.builder()
                                .name("Tech Solutions Inc")
                                .domain("tech-solutions")
                                .displayName("Tech Solutions Inc")
                                .description("Advanced technology manufacturing")
                                .active(true)
                                .build();
                company = companyRepository.save(company);

                Tenant tenant = new Tenant("tech-solutions", "Tech Solutions Inc",
                                "Advanced technology manufacturing");
                tenant = tenantRepository.save(tenant);

                Manufacturer manufacturer = new Manufacturer("tech-electronics", "Electronics Division",
                                "PCB and electronics manufacturing", tenant, company);
                manufacturer = manufacturerRepository.save(manufacturer);

                createUser("emily.chen@techsolutions.com", "tech123", "Emily", "Chen",
                                User.Role.MANUFACTURER_ADMIN, company, manufacturer);
                createUser("david.rodriguez@techsolutions.com", "tech123", "David", "Rodriguez",
                                User.Role.MANAGER, company, manufacturer);
                createUser("anna.kim@techsolutions.com", "tech123", "Anna", "Kim",
                                User.Role.OPERATOR, company, manufacturer);

                Factory austinFactory = createFactory("tech-factory-austin", "Austin Tech Hub",
                                "R&D and production facility", manufacturer, "I", 80, 120, "#10b981");

                PLC austinPlc1 = createPLC("PLC-AUS-001", "Beckhoff CX9020 #1", "SMT line controller",
                                austinFactory, 40.0, 60.0);
                createSensor(austinPlc1, "temp-aus-001", "SMT Oven Temperature", "temperature", "°C", 240.0, 10.0);
                createSensor(austinPlc1, "pressure-aus-001", "Pick-Place Pressure", "pressure", "psi", 60.0, 5.0);
                createSensor(austinPlc1, "position-aus-001", "Component Position", "position", "mm", 0.05, 0.01);
        }

        private void createGlobalIndustries() {
                Company company = Company.builder()
                                .name("Global Industries Ltd")
                                .domain("global-industries")
                                .displayName("Global Industries Ltd")
                                .description("Heavy machinery and equipment")
                                .active(true)
                                .build();
                company = companyRepository.save(company);

                Tenant tenant = new Tenant("global-industries", "Global Industries Ltd",
                                "Heavy machinery and equipment");
                tenant = tenantRepository.save(tenant);

                Manufacturer manufacturer = new Manufacturer("global-machinery", "Heavy Machinery Division",
                                "Large-scale industrial equipment", tenant, company);
                manufacturer = manufacturerRepository.save(manufacturer);

                createUser("robert.brown@globalind.com", "global123", "Robert", "Brown",
                                User.Role.MANUFACTURER_ADMIN, company, manufacturer);
                createUser("lisa.martinez@globalind.com", "global123", "Lisa", "Martinez",
                                User.Role.MANAGER, company, manufacturer);
                createUser("james.anderson@globalind.com", "global123", "James", "Anderson",
                                User.Role.OPERATOR, company, manufacturer);

                Factory chicagoFactory = createFactory("global-factory-chicago", "Chicago Manufacturing Complex",
                                "Heavy equipment production", manufacturer, "Z", 150, 100, "#8b5cf6");

                PLC chiPlc1 = createPLC("PLC-CHI-001", "Mitsubishi Q Series #1", "Press machine controller",
                                chicagoFactory, 75.0, 50.0);
                createSensor(chiPlc1, "force-chi-001", "Press Force", "force", "kN", 500.0, 100.0);
                createSensor(chiPlc1, "temp-chi-001", "Die Temperature", "temperature", "°C", 180.0, 30.0);
                createSensor(chiPlc1, "hydraulic-chi-001", "Hydraulic Pressure (Unreliable)", "pressure", "bar", 200.0,
                                50.0);

                PLC chiPlc2 = createPLC("PLC-CHI-002", "Siemens S7-400 #1", "Welding station controller",
                                chicagoFactory, 75.0, 50.0);
                createSensor(chiPlc2, "current-chi-002", "Welding Current", "current", "A", 250.0, 25.0);
                createSensor(chiPlc2, "voltage-chi-002", "Welding Voltage", "voltage", "V", 28.0, 3.0);
                createSensor(chiPlc2, "temp-chi-002", "Weld Temp (Unstable)", "temperature", "°C", 1400.0, 200.0);
        }

        private User createUser(String email, String password, String firstName, String lastName,
                        User.Role role, Company company, Manufacturer manufacturer) {
                User user = User.builder()
                                .email(email)
                                .password(passwordEncoder.encode(password))
                                .firstName(firstName)
                                .lastName(lastName)
                                .role(role)
                                .company(company)
                                .manufacturer(manufacturer)
                                .active(true)
                                .build();
                return userRepository.save(user);
        }

        private Factory createFactory(String factoryId, String name, String description,
                        Manufacturer manufacturer, String shape, int width, int height, String color) {
                Factory factory = new Factory(factoryId, name, description, manufacturer);
                factory.setShape(shape);
                factory.setWidth(width);
                factory.setHeight(height);
                factory.setWidthMeters((double) width);
                factory.setHeightMeters((double) height);
                factory.setWireframeColor(color);
                return factoryRepository.save(factory);
        }

        private PLC createPLC(String plcId, String name, String description, Factory factory,
                        double xPosition, double yPosition) {
                PLC plc = new PLC(plcId, name, description, factory);
                plc.setXPosition(xPosition);
                plc.setYPosition(yPosition);
                return plcRepository.save(plc);
        }

        private void createSensor(PLC plc, String sensorId, String name, String type, String unit,
                        double mean, double stdDev) {
                SignalConfig signalConfig = SignalConfig.builder()
                                .name(type)
                                .unit(unit)
                                .value(mean)
                                .generator("normal")
                                .isRunning(true)
                                .mean(mean)
                                .stdDev(stdDev)
                                .minValue(mean - stdDev * 3)
                                .maxValue(mean + stdDev * 3)
                                .build();

                Sensor sensor = new Sensor(sensorId, name, plc, signalConfig);
                sensorRepository.save(sensor);
        }

        private void printTestCredentials() {
                String separator = "=".repeat(70);
                log.info("");
                log.info(separator);
                log.info("TEST USER CREDENTIALS");
                log.info(separator);
                log.info("");
                log.info("SYSTEM ADMIN (sees all data):");
                log.info("  Email: admin@virtplc.com");
                log.info("  Password: admin123");
                log.info("");
                log.info("ACME MANUFACTURING CORP (acme-motors manufacturer):");
                log.info("  Admin:    john.smith@acme.com / acme123");
                log.info("  Manager:  sarah.johnson@acme.com / acme123");
                log.info("  Operator: mike.wilson@acme.com / acme123");
                log.info("  Factories: New York, Los Angeles");
                log.info("");
                log.info("TECH SOLUTIONS INC (tech-electronics manufacturer):");
                log.info("  Admin:    emily.chen@techsolutions.com / tech123");
                log.info("  Manager:  david.rodriguez@techsolutions.com / tech123");
                log.info("  Operator: anna.kim@techsolutions.com / tech123");
                log.info("  Factories: Austin Tech Hub");
                log.info("");
                log.info("GLOBAL INDUSTRIES LTD (global-machinery manufacturer):");
                log.info("  Admin:    robert.brown@globalind.com / global123");
                log.info("  Manager:  lisa.martinez@globalind.com / global123");
                log.info("  Operator: james.anderson@globalind.com / global123");
                log.info("  Factories: Chicago (with failure-prone devices)");
                log.info("");
                log.info(separator);
                log.info("");
        }
}
