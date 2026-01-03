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
                createSensor(nyPlc1, "motor_speed_PLC-NY-001", "Motor Speed", "speed", "RPM", 1750.0, 25.0);
                createSensor(nyPlc1, "motor_temp_PLC-NY-001", "Motor Temperature", "temperature", "°C", 65.0, 5.0);
                createSensor(nyPlc1, "vibration_PLC-NY-001", "Motor Vibration", "vibration", "mm/s", 1.2, 0.1);
                createSensor(nyPlc1, "power_consumption_PLC-NY-001", "Power Consumption", "power", "kW", 50.0, 5.0);

                PLC nyPlc2 = createPLC("PLC-NY-002", "Allen-Bradley ControlLogix #1", "Quality control station",
                                nyFactory, 120.0, 90.0);
                createSensor(nyPlc2, "pressure_main_PLC-NY-002", "Main Pressure", "pressure", "bar", 150.0, 10.0);
                createSensor(nyPlc2, "flow_rate_PLC-NY-002", "Flow Rate", "flow", "L/min", 100.0, 10.0);
                createSensor(nyPlc2, "level_tank_PLC-NY-002", "Tank Level", "level", "m", 3.0, 0.5);
                createSensor(nyPlc2, "ph_level_PLC-NY-002", "pH Level", "ph", "pH", 7.0, 0.5);

                PLC laPlc1 = createPLC("PLC-LA-001", "Schneider M580 #1", "Conveyor system controller",
                                laFactory, 50.0, 40.0);
                createSensor(laPlc1, "conveyor_speed_PLC-LA-001", "Conveyor Speed", "speed", "m/min", 15.0, 2.0);
                createSensor(laPlc1, "load_weight_PLC-LA-001", "Load Weight", "weight", "kg", 500.0, 50.0);
                createSensor(laPlc1, "belt_tension_PLC-LA-001", "Belt Tension", "force", "N", 1500.0, 100.0);
                createSensor(laPlc1, "motor_current_PLC-LA-001", "Motor Current", "current", "A", 25.0, 3.0);
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
                createSensor(austinPlc1, "humidity_PLC-AUS-001", "Humidity", "humidity", "%", 45.0, 5.0);
                createSensor(austinPlc1, "temperature_oven_PLC-AUS-001", "Oven Temperature", "temperature", "°C", 180.0,
                                10.0);
                createSensor(austinPlc1, "air_quality_PLC-AUS-001", "Air Quality", "quality", "ppm", 2.0, 0.2);
                createSensor(austinPlc1, "static_charge_PLC-AUS-001", "Static Charge", "charge", "kV", 0.5, 0.1);

                PLC austinPlc2 = createPLC("PLC-AUS-002", "Beckhoff CX9020 #2", "Testing station",
                                austinFactory, 40.0, 108.0);
                createSensor(austinPlc2, "resistance_PLC-AUS-002", "Resistance", "resistance", "Ω", 1000.0, 50.0);
                createSensor(austinPlc2, "voltage_PLC-AUS-002", "Voltage", "voltage", "V", 5.0, 0.5);
                createSensor(austinPlc2, "current_test_PLC-AUS-002", "Test Current", "current", "mA", 50.0, 5.0);
                createSensor(austinPlc2, "frequency_PLC-AUS-002", "Frequency", "frequency", "Hz", 100.0, 5.0);
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
                createSensor(chiPlc1, "press_force_PLC-CHI-001", "Press Force", "force", "kN", 500.0, 50.0);
                createSensor(chiPlc1, "hydraulic_pressure_PLC-CHI-001", "Hydraulic Pressure", "pressure", "bar", 200.0,
                                20.0);
                createSensor(chiPlc1, "material_thickness_PLC-CHI-001", "Material Thickness", "thickness", "mm", 5.0,
                                0.5);
                createSensor(chiPlc1, "cycle_time_PLC-CHI-001", "Cycle Time", "time", "s", 30.0, 3.0);

                PLC chiPlc2 = createPLC("PLC-CHI-002", "Siemens S7-400 #1", "Welding station controller",
                                chicagoFactory, 75.0, 50.0);
                createSensor(chiPlc2, "weld_current_PLC-CHI-002", "Weld Current", "current", "A", 250.0, 25.0);
                createSensor(chiPlc2, "weld_voltage_PLC-CHI-002", "Weld Voltage", "voltage", "V", 28.0, 3.0);
                createSensor(chiPlc2, "wire_feed_PLC-CHI-002", "Wire Feed Speed", "speed", "m/min", 5.0, 0.5);
                createSensor(chiPlc2, "gas_flow_PLC-CHI-002", "Shield Gas Flow", "flow", "L/min", 18.0, 1.0);
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
