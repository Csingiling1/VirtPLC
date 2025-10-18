#include "OPCUAClientModule.h"
#include "Modules/ModuleManager.h"

#define LOCTEXT_NAMESPACE "FOPCUAClientModule"

void FOPCUAClientModule::StartupModule()
{
    UE_LOG(LogTemp, Log, TEXT("OPCUAClient: Module starting up"));
    // Initialize open62541 client here if needed
}

void FOPCUAClientModule::ShutdownModule()
{
    UE_LOG(LogTemp, Log, TEXT("OPCUAClient: Module shutting down"));
    // Cleanup open62541 resources here
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FOPCUAClientModule, OPCUAClient)
